"""Run the declared V2.3 development, freeze and paired final replay."""
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import time

import numpy as np
import torch

import run_thesis_metrics_study as old

ROOT = old.ROOT
BASE = ROOT/'results/signal_guard_v23'
FREEZE = ROOT/'configs/frozen_signal_guard_v23.json'
DEV_ROUTES = ROOT/'configs/signal_guard_development_v23.json'
TEST_ROUTES = ROOT/'configs/signal_guard_scenarios_v23.json'
sys.path.insert(0, str(ROOT/'src'))
from uav_joint_optimization.signal_guard import signal_guard_action

SOURCES = ['src/uav_joint_optimization/signal_guard.py', 'scripts/run_signal_guard_study.py',
           'scripts/analyze_signal_guard_study.py', 'tests/test_signal_guard.py', 'docs/58_signal_guard_protocol.md']
RADIO = None


def verify_history():
    old.verify_history(); old.verify_new()


def hashes():
    return {p: old.sha(ROOT/p) for p in SOURCES}


def snapshot(folder):
    old.save(folder/'source_hashes.json', hashes())
    for p in SOURCES:
        q = folder/'source_snapshot'/p
        q.parent.mkdir(parents=True, exist_ok=True); q.write_bytes((ROOT/p).read_bytes())


def verify_snapshot(folder):
    assert json.loads((folder/'source_hashes.json').read_text()) == hashes()


def prior_pairs():
    seen = set()
    for p in (ROOT/'configs').glob('*.json'):
        if p == TEST_ROUTES:
            continue
        data = json.loads(p.read_text())
        if not isinstance(data, dict):
            continue
        for value in data.values():
            if isinstance(value, list):
                for row in value:
                    if isinstance(row, dict) and 'start' in row and 'goal' in row:
                        seen.add(tuple(row['start']+row['goal']))
    return seen


def create_routes(path, count, longer_count, seed, longer_seed):
    if path.exists():
        raise FileExistsError(path)
    seen = prior_pairs()
    result = {'test': old.make_scenarios(count, seed),
              'longer_test': old.make_scenarios(longer_count, longer_seed, 1000, 1800)}
    for values in result.values():
        for row in values:
            key = tuple(row['start']+row['goal'])
            assert key not in seen; seen.add(key)
    old.save(path, result)


def initialize():
    global RADIO
    torch.set_num_threads(1)
    RADIO = old.RadioMap(ROOT/'dataset/Barcelona_dataset_January.h5')


def evaluate(seed, routes, allowance):
    policy = old.load_policy('full', seed)
    env = old.ConnectivityBatch(RADIO, len(routes), routes, config=old.ConnectivityConfig())
    metrics = old.ThesisMetrics(env); obs, mask = env.observe(); rows = []
    changed = np.zeros(env.n, dtype=int)
    start = time.perf_counter()
    for _ in range(env.cfg.horizon):
        active = ~env.done.copy()
        with torch.no_grad():
            latent, _, _, _ = policy.action(torch.from_numpy(obs), torch.from_numpy(mask), True)
        proposal = env.decode_residual(torch.tanh(latent).numpy())
        if allowance is None:
            motion, network = old.guarded_action(env, proposal, 5)
        else:
            motion, network, details = signal_guard_action(env, proposal, allowance, diagnostics=True)
            changed += active & (details['selected'] != details['baseline'])
        obs, mask, _, _, completed = env.step(motion, network)
        metrics.record(active, completed)
        for row in completed:
            row['signal_selection_steps'] = int(changed[row['lane']])
        rows.extend(completed)
        if env.done.all():
            break
    rows.sort(key=lambda r: r['lane']); assert len(rows) == len(routes)
    return rows, {**metrics.samples, 'counts': metrics.counts}, time.perf_counter()-start


def run_job(job):
    phase, arm, seed, split, routes, allowance = job
    prefix = BASE/phase/f'{arm}_seed_{seed}'/split
    if prefix.with_suffix('.json').exists():
        saved = json.loads(prefix.with_suffix('.json').read_text())
        assert saved['seed'] == seed and saved['allowance_m'] == allowance
        assert saved['scenario_ids'] == [r['id'] for r in routes]
        if phase == 'development':
            return {'run': prefix.relative_to(BASE).as_posix(), 'episodes': len(saved['episodes']), 'reused': True}
    else:
        records, arrays, seconds = evaluate(seed, routes, allowance)
        old.save(prefix.with_suffix('.json'), {'arm': arm, 'seed': seed, 'allowance_m': allowance,
            'scenario_ids': [r['id'] for r in routes], 'runtime_seconds': seconds,
            'episodes': records, 'summary': old.summarize(records)})
        np.savez_compressed(prefix.with_suffix('.npz'), **arrays)
        print(json.dumps({'completed': prefix.relative_to(BASE).as_posix(),
            'successes': sum(r['success'] for r in records), 'episodes': len(records),
            'seconds': round(seconds, 2)}), flush=True)
    if phase == 'confirmatory':
        records, arrays, _ = evaluate(seed, routes, allowance)
        assert records == json.loads(prefix.with_suffix('.json').read_text())['episodes']
        with np.load(prefix.with_suffix('.npz')) as saved_arrays:
            assert set(saved_arrays.files) == set(arrays)
            for key, value in arrays.items():
                np.testing.assert_array_equal(value, saved_arrays[key])
    return {'run': prefix.relative_to(BASE).as_posix(), 'episodes': len(routes),
        'record_sha256': old.sha(prefix.with_suffix('.json')),
        'samples_sha256': old.sha(prefix.with_suffix('.npz')), 'exact_replay': phase == 'confirmatory'}


def freeze():
    if FREEZE.exists() or TEST_ROUTES.exists():
        raise FileExistsError('This study already has frozen final data.')
    verify_snapshot(BASE/'development')
    selection = json.loads((BASE/'development/selection.json').read_text())
    assert selection['selected_allowance_m'] is not None, 'No eligible candidate; final test stays unopened.'
    create_routes(TEST_ROUTES, 500, 500, 56012, 56013)
    old.save(FREEZE, {'frozen_utc': datetime.now(timezone.utc).isoformat(),
        'study': 'signal_guard_v23', 'selected_allowance_m': selection['selected_allowance_m'],
        'source_hashes': hashes(), 'scenarios_sha256': old.sha(TEST_ROUTES),
        'development_scenarios_sha256': old.sha(DEV_ROUTES),
        'selection_sha256': old.sha(BASE/'development/selection.json'),
        'dataset_sha256': old.sha(ROOT/'dataset/Barcelona_dataset_January.h5'),
        'historical_manifest_hashes': {p.name: old.sha(p) for p in (ROOT/'configs').glob('frozen_*.json')},
        'reused_checkpoint_hashes': {old.checkpoint('full', s).relative_to(ROOT).as_posix(): old.sha(old.checkpoint('full', s)) for s in old.SEEDS},
        'seeds': old.SEEDS, 'bootstrap_seed': 66000, 'bootstrap_draws': 5000})
    snapshot(BASE/'confirmatory')


def verify_frozen():
    d = json.loads(FREEZE.read_text())
    assert d['source_hashes'] == hashes()
    assert d['scenarios_sha256'] == old.sha(TEST_ROUTES)
    assert d['development_scenarios_sha256'] == old.sha(DEV_ROUTES)
    assert d['selection_sha256'] == old.sha(BASE/'development/selection.json')
    for p, h in d['reused_checkpoint_hashes'].items():
        assert old.sha(ROOT/p) == h
    for p, h in d['historical_manifest_hashes'].items():
        assert old.sha(ROOT/'configs'/p) == h
    return d


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--phase', required=True, choices=['development', 'freeze', 'confirmatory'])
    parser.add_argument('--workers', type=int, default=3)
    args = parser.parse_args(); verify_history()
    if args.phase == 'freeze':
        freeze(); return
    dataset_hash = json.loads((ROOT/'configs/frozen_comparison_v1.json').read_text())['dataset_sha256']
    assert old.sha(ROOT/'dataset/Barcelona_dataset_January.h5') == dataset_hash
    if args.phase == 'development':
        if not (BASE/'development').exists():
            create_routes(DEV_ROUTES, 128, 64, 56001, 56002); snapshot(BASE/'development')
            old.save(BASE/'development/provenance.json', {'started_utc': datetime.now(timezone.utc).isoformat(),
                'dataset_sha256': dataset_hash, 'scenarios_sha256': old.sha(DEV_ROUTES),
                'reused_checkpoint_hashes': {old.checkpoint('full', s).relative_to(ROOT).as_posix(): old.sha(old.checkpoint('full', s)) for s in [2101, 2102]},
                'historical_manifest_hashes': {p.name: old.sha(p) for p in (ROOT/'configs').glob('frozen_*.json')}})
        verify_snapshot(BASE/'development')
        provenance = json.loads((BASE/'development/provenance.json').read_text())
        assert provenance['scenarios_sha256'] == old.sha(DEV_ROUTES)
        assert provenance['dataset_sha256'] == dataset_hash
        for p, h in provenance['reused_checkpoint_hashes'].items():
            assert old.sha(ROOT/p) == h
        routes = json.loads(DEV_ROUTES.read_text()); seeds = [2101, 2102]
        arms = [('v22', None), ('signal_1', 1), ('signal_3', 3), ('signal_6', 6)]
    else:
        frozen = verify_frozen(); routes = json.loads(TEST_ROUTES.read_text()); seeds = old.SEEDS
        arms = [('v22', None), ('signal', frozen['selected_allowance_m'])]
    jobs = [(args.phase, arm, seed, split, values, allowance)
            for arm, allowance in arms for seed in seeds for split, values in routes.items()]
    checks = []
    with ProcessPoolExecutor(max_workers=args.workers, initializer=initialize) as pool:
        for future in as_completed([pool.submit(run_job, job) for job in jobs]):
            r = future.result(); checks.append(r)
            print(json.dumps({'verified': r['run'], 'episodes': r['episodes']}), flush=True)
    old.save(BASE/args.phase/'run_audit.json', {'runs': sorted(checks, key=lambda r: r['run']),
        'episodes': sum(r['episodes'] for r in checks), 'workers': args.workers,
        'all_exactly_replayed': args.phase == 'confirmatory', 'source_hashes': hashes()})


if __name__ == '__main__':
    main()
