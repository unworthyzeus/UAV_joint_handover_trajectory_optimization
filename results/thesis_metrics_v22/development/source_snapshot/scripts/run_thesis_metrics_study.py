"""Recover source motivated metrics and test the declared V2.2 supervisor."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys
import time

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from uav_joint_optimization.experiment_env import RadioMap, make_scenarios
from uav_joint_optimization.connectivity_env import ConnectivityBatch, ConnectivityConfig
from uav_joint_optimization.original_reward_env import RewardComparisonBatch
from uav_joint_optimization.service_reward_env import ServiceRewardBatch, ServiceRewardConfig
from uav_joint_optimization.connectivity_ppo import HybridPolicy, summarize
from uav_joint_optimization.connectivity_guard import guarded_action
from uav_joint_optimization.thesis_metrics import ThesisMetrics

SEEDS = [2101, 2102, 2103, 2104, 2105]
BASE = ROOT/'results/thesis_metrics_v22'
FREEZE = ROOT/'configs/frozen_thesis_metrics_v22.json'
SCENARIOS = ROOT/'configs/thesis_metrics_scenarios_v22.json'
SOURCES = ['src/uav_joint_optimization/thesis_metrics.py',
           'src/uav_joint_optimization/connectivity_guard.py',
           'scripts/run_thesis_metrics_study.py', 'scripts/analyze_thesis_metrics_study.py',
           'tests/test_thesis_metrics_guard.py', 'docs/51_thesis_metrics_and_guard_protocol.md']
HISTORY = ['frozen_comparison_v1.json', 'frozen_connectivity_v2.json',
           'frozen_reward_comparison_v15.json', 'frozen_service_reward_v21.json']


def configure(label):
    global BASE, FREEZE, SCENARIOS
    if label:
        if not re.fullmatch(r'[A-Za-z0-9_]+', label):
            raise ValueError('Use letters, digits and underscores for the reproduction label.')
        BASE = ROOT/f'results/thesis_metrics_{label}'
        FREEZE = ROOT/f'configs/frozen_thesis_metrics_{label}.json'
        SCENARIOS = ROOT/f'configs/thesis_metrics_scenarios_{label}.json'
    return BASE, FREEZE, SCENARIOS


def sha(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False)+'\n', encoding='utf-8')


def verify_history():
    for name in HISTORY:
        d = json.loads((ROOT/'configs'/name).read_text())
        for p, h in d['source_hashes'].items():
            assert sha(ROOT/p) == h, p
        for p, h in d.get('reused_checkpoint_hashes', {}).items():
            assert sha(ROOT/p) == h, p


def checkpoint(arm, seed):
    if arm in ('full', 'guard'):
        return ROOT/f'results/connectivity_experiment/confirmatory_v2/full_seed_{seed}/checkpoint.pt'
    if arm == 'original':
        return ROOT/f'results/reward_comparison/confirmatory_v15/original_seed_{seed}/checkpoint.pt'
    if arm == 'service':
        return ROOT/f'results/service_reward_v21/confirmatory/service_seed_{seed}/checkpoint.pt'
    return None


def load_policy(arm, seed):
    d = torch.load(checkpoint(arm, seed), map_location='cpu', weights_only=False)
    policy = HybridPolicy(d['obs_dim'], d['hidden'])
    policy.load_state_dict(d['policy']); policy.eval()
    return policy


def evaluate(arm, seed, radio, routes, horizon=None):
    policy = load_policy(arm, seed) if seed is not None else None
    if arm == 'original':
        env = RewardComparisonBatch(radio, len(routes), routes, reward='original', config=ConnectivityConfig())
    elif arm == 'service':
        env = ServiceRewardBatch(radio, len(routes), routes, config=ServiceRewardConfig())
    else:
        env = ConnectivityBatch(radio, len(routes), routes, config=ConnectivityConfig())
    metrics = ThesisMetrics(env); records = []
    obs, mask = env.observe(); start = time.perf_counter()
    for _ in range(env.cfg.horizon):
        active = ~env.done.copy()
        if policy is None:
            motion, choice = env.controller(arm)
        else:
            with torch.no_grad():
                latent, network, _, _ = policy.action(torch.from_numpy(obs), torch.from_numpy(mask), True)
            motion, choice = env.decode_residual(torch.tanh(latent).numpy()), network.numpy()
            if arm == 'guard':
                motion, choice = guarded_action(env, motion, horizon)
        obs, mask, _, _, completed = env.step(motion, choice)
        metrics.record(active, completed); records.extend(completed)
        if env.done.all():
            break
    records.sort(key=lambda r: r['lane'])
    assert len(records) == len(routes)
    arrays = {**metrics.samples, 'counts': metrics.counts}
    return records, arrays, time.perf_counter()-start


def snapshot(folder):
    hashes = {p: sha(ROOT/p) for p in SOURCES}
    save(folder/'source_hashes.json', hashes)
    for p in SOURCES:
        target = folder/'source_snapshot'/p
        target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes((ROOT/p).read_bytes())
    return hashes


def write_run(prefix, records, arrays, seconds, arm, seed, horizon):
    if prefix.with_suffix('.json').exists():
        raise FileExistsError(prefix)
    save(prefix.with_suffix('.json'), {'arm': arm, 'seed': seed, 'guard_horizon': horizon,
        'runtime_seconds': seconds, 'episodes': records, 'summary': summarize(records)})
    np.savez_compressed(prefix.with_suffix('.npz'), **arrays)
    print(json.dumps({'run': prefix.relative_to(BASE).as_posix(), 'seconds': round(seconds, 2),
                      'success': sum(r['success'] for r in records), 'episodes': len(records)}), flush=True)


def development(radio):
    folder = BASE/'development'
    if folder.exists():
        raise FileExistsError(folder)
    snapshot(folder)
    routes = json.loads((ROOT/'configs/connectivity_scenarios_v2.json').read_text())
    data = {}; settings = [('full', 2101, None), ('straight_radio', None, None)]
    settings += [('guard', 2101, h) for h in (3, 5, 8)]
    for arm, seed, horizon in settings:
        name = f'guard_{horizon}' if horizon else arm
        data[name] = {}
        for split in ('validation', 'validation_longer'):
            records, arrays, seconds = evaluate(arm, seed, radio, routes[split], horizon)
            write_run(folder/name/split, records, arrays, seconds, arm, seed, horizon)
            data[name][split] = records
    counts = {a: sum(r['success'] for rows in v.values() for r in rows) for a, v in data.items()}
    reports = {}; eligible = []
    for horizon in (3, 5, 8):
        name = f'guard_{horizon}'; delays = {}; common_rows = []
        for split, rows in data[name].items():
            pairs = [(a, b) for a, b in zip(rows, data['full'][split]) if a['success'] and b['success']]
            delays[split] = float(np.mean([a['delay_proxy_mean_s']-b['delay_proxy_mean_s'] for a, b in pairs])) if pairs else None
            common_rows.extend(a for a, b in pairs)
        gate = counts[name] >= counts['full'] and all(v is not None and v <= 0 for v in delays.values())
        reports[name] = {'successes': counts[name], 'matched_delay_difference': delays, 'gate': gate}
        if gate:
            eligible.append((-counts[name], np.mean([r['delay_proxy_mean_s'] for r in common_rows]),
                             np.mean([r['handovers'] for r in common_rows]), horizon))
    selected = int(min(eligible)[-1]) if eligible else None
    result = {'completed_utc': datetime.now(timezone.utc).isoformat(), 'selected_horizon': selected,
              'reference_successes': {a: counts[a] for a in ('full', 'straight_radio')}, 'candidates': reports}
    save(folder/'selection.json', result); print(json.dumps(result, indent=2), flush=True)


def freeze():
    if FREEZE.exists() or SCENARIOS.exists():
        raise FileExistsError('Existing freeze or scenarios')
    selection = json.loads((BASE/'development/selection.json').read_text())
    routes = {'test': make_scenarios(500, 55012), 'longer_test': make_scenarios(500, 55013, 1000, 1800)}
    seen = set()
    for name in ['controlled_scenarios.json', 'connectivity_scenarios_v2.json',
                 'reward_comparison_scenarios_v15.json', 'service_reward_scenarios_v21.json']:
        prior = json.loads((ROOT/'configs'/name).read_text())
        seen.update(tuple(r['start']+r['goal']) for values in prior.values() for r in values)
    for pool in routes.values():
        for r in pool:
            key = tuple(r['start']+r['goal']); assert key not in seen; seen.add(key)
    save(SCENARIOS, routes)
    save(FREEZE, {'frozen_utc': datetime.now(timezone.utc).isoformat(), 'study': 'thesis_metrics_v22',
        'selected_horizon': selection['selected_horizon'], 'seeds': SEEDS,
        'source_hashes': {p: sha(ROOT/p) for p in SOURCES}, 'scenarios_sha256': sha(SCENARIOS),
        'selection_sha256': sha(BASE/'development/selection.json'),
        'dataset_sha256': sha(ROOT/'dataset/Barcelona_dataset_January.h5'),
        'reused_checkpoint_hashes': {checkpoint(a, s).relative_to(ROOT).as_posix(): sha(checkpoint(a, s))
                                    for a in ('original', 'full', 'service') for s in SEEDS},
        'primary_contrast': 'guard_minus_full_test', 'bootstrap_seed': 65000, 'bootstrap_draws': 5000})


def verify_new():
    d = json.loads(FREEZE.read_text())
    for key in ('source_hashes', 'reused_checkpoint_hashes'):
        for p, h in d[key].items():
            assert sha(ROOT/p) == h, p
    assert sha(SCENARIOS) == d['scenarios_sha256']
    assert sha(BASE/'development/selection.json') == d['selection_sha256']
    return d


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--phase', required=True, choices=['development', 'freeze', 'evaluate', 'replay'])
    parser.add_argument('--label')
    args = parser.parse_args(); configure(args.label); verify_history(); torch.set_num_threads(2)
    if args.phase == 'freeze':
        freeze(); return
    frozen = None if args.phase == 'development' else verify_new()
    expected = json.loads((ROOT/'configs/frozen_comparison_v1.json').read_text())['dataset_sha256']
    assert sha(ROOT/'dataset/Barcelona_dataset_January.h5') == expected
    print('Loading the unchanged native map.', flush=True)
    radio = RadioMap(ROOT/'dataset/Barcelona_dataset_January.h5')
    metadata = {'minimum_stored_rss': int(radio.rss.min()), 'maximum_stored_rss': int(radio.rss.max()),
                'maximum_eq8_snr_db': float(radio.rss.max()) + 103.41,
                'dataset_sha256': expected, 'map_is_same_as_original_thesis': True}
    if args.phase == 'development':
        development(radio); save(BASE/'map_metric_bounds.json', metadata); return
    routes = json.loads(SCENARIOS.read_text()); horizon = frozen['selected_horizon']
    arms = ['original', 'full', 'service'] + (['guard'] if horizon is not None else [])
    settings = [(a, s) for a in arms for s in SEEDS]
    settings += [(a, None) for a in ('straight_radio', 'joint_mpc', 'joint_lookahead')]
    checks = []; replay = args.phase == 'replay'
    if not replay:
        if (BASE/'confirmatory').exists():
            raise FileExistsError(BASE/'confirmatory')
        snapshot(BASE/'confirmatory')
    for arm, seed in settings:
        for split in routes:
            prefix = BASE/'confirmatory'/(f'{arm}_seed_{seed}' if seed else arm)/split
            records, arrays, seconds = evaluate(arm, seed, radio, routes[split], horizon if arm == 'guard' else None)
            if replay:
                assert records == json.loads(prefix.with_suffix('.json').read_text())['episodes'], str(prefix)
                with np.load(prefix.with_suffix('.npz')) as saved:
                    assert set(saved.files) == set(arrays)
                    for key, value in arrays.items():
                        np.testing.assert_array_equal(value, saved[key])
                checks.append({'run': prefix.relative_to(BASE).as_posix(), 'episodes': len(records),
                               'record_sha256': sha(prefix.with_suffix('.json')), 'samples_sha256': sha(prefix.with_suffix('.npz'))})
                print(json.dumps({'replay': checks[-1]['run'], 'matches': len(records)}), flush=True)
            else:
                write_run(prefix, records, arrays, seconds, arm, seed, horizon if arm == 'guard' else None)
    if replay:
        save(BASE/'replay_audit.json', {'exact_episode_and_metric_matches': sum(r['episodes'] for r in checks),
                                      'all_sample_arrays_exact': True, 'runs': checks})


if __name__ == '__main__':
    main()
