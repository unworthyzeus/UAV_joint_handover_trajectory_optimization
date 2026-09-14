"""Declared selection and honest paired analysis for the signal path study."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import json

import numpy as np

import run_signal_guard_study as study
from analyze_connectivity_experiment import interval

METRICS = ['snr_mean_db', 'sinr_mean_db', 'delay_proxy_mean_s', 'handovers', 'time_s',
           'energy_proxy_j', 'remaining_energy_kj', 'interference_mean_w', 'neighbor_rss_power_mean_uw',
           'handovers_per_second', 'path_m', 'radio_cost_sum']


def load_runs(phase, arm, split, seeds):
    return [json.loads((study.BASE/phase/f'{arm}_seed_{seed}'/(split+'.json')).read_text())['episodes'] for seed in seeds]


def contrast(a, b, bootstrap=False):
    for x, y in zip(a, b):
        assert [r['scenario_id'] for r in x] == [r['scenario_id'] for r in y]
    success_a = np.array([[r['success'] for r in run] for run in a])
    success_b = np.array([[r['success'] for r in run] for run in b])
    common = success_a & success_b; delta = success_a.astype(float)-success_b
    result = {'candidate_successes': int(success_a.sum()), 'baseline_successes': int(success_b.sum()),
        'episodes_per_arm': int(success_a.size), 'common_successes': int(common.sum()),
        'success_difference_pp': float(100*delta.mean()), 'metrics': {}}
    if bootstrap:
        result['success_ci95_pp'] = [100*v for v in interval(delta, seed=66000)]
    for key in METRICS:
        x = np.array([[r[key] for r in run] for run in a], dtype=float)
        y = np.array([[r[key] for r in run] for run in b], dtype=float)
        assert np.isfinite(x[common]).all() and np.isfinite(y[common]).all()
        m = {'candidate_mean': float(x[common].mean()), 'baseline_mean': float(y[common].mean()),
             'difference': float((x-y)[common].mean())}
        if bootstrap:
            m['ci95'] = interval(x-y, common, seed=66000)
            if key in ('time_s', 'energy_proxy_j'):
                # Test the ratio margin through the paired mean contrast X - 1.02 Y.
                m['two_percent_margin_ci95'] = interval(x-1.02*y, common, seed=66000)
        result['metrics'][key] = m
    return result


def development():
    study.verify_snapshot(study.BASE/'development')
    path = study.BASE/'development/selection.json'
    if path.exists():
        raise FileExistsError('Selection is already recorded.')
    baseline = {sp: load_runs('development', 'v22', sp, [2101, 2102]) for sp in ('test', 'longer_test')}
    reports = {}; eligible = []
    for allowance in (1, 3, 6):
        arm = f'signal_{allowance}'; splits = {}; gates = []
        for sp in baseline:
            d = contrast(load_runs('development', arm, sp, [2101, 2102]), baseline[sp])
            m = d['metrics']
            gate = (d['candidate_successes'] >= d['baseline_successes']
                and m['snr_mean_db']['difference'] > (0.1 if sp == 'test' else 0.)
                and m['delay_proxy_mean_s']['difference'] <= 0
                and m['handovers']['difference'] <= 0
                and all(m[k]['candidate_mean'] <= 1.02*m[k]['baseline_mean'] for k in ('time_s', 'energy_proxy_j')))
            d['selection_gate'] = bool(gate); gates.append(gate); splits[sp] = d
        reports[arm] = splits
        if all(gates):
            eligible.append((-sum(d['candidate_successes'] for d in splits.values()),
                -min(d['metrics']['snr_mean_db']['difference'] for d in splits.values()),
                sum(d['metrics']['delay_proxy_mean_s']['difference'] for d in splits.values()), allowance))
    result = {'completed_utc': datetime.now(timezone.utc).isoformat(),
        'selected_allowance_m': min(eligible)[-1] if eligible else None, 'candidates': reports,
        'final_test_opened': False, 'development_only': True}
    study.old.save(path, result)
    print(json.dumps(result, indent=2))


def final_analysis():
    frozen = study.verify_frozen(); results = {}; groups = {}
    audit = json.loads((study.BASE/'confirmatory/run_audit.json').read_text())
    assert audit['episodes'] == 10000 and audit['all_exactly_replayed']
    for sp in ('test', 'longer_test'):
        by_arm = {}
        for arm in ('v22', 'signal'):
            runs = load_runs('confirmatory', arm, sp, study.old.SEEDS); by_arm[arm] = runs
            flat = [r for run in runs for r in run]; successful = [r for r in flat if r['success']]
            for row in successful:
                assert row['minimum_rss_dbm'] >= -96 and row['outage_s'] == row['dropped_bits'] == 0
                assert row['time_s'] <= 200 and row['final_distance_m'] <= 10 and row['final_speed_mps'] <= 2
            groups[arm+'_'+sp] = {'episodes': len(flat), 'successes': len(successful),
                'outcomes': dict(Counter(r['outcome'] for r in flat)),
                'per_seed_successes': [sum(r['success'] for r in run) for run in runs],
                'all_flight_mean_outage_s': float(np.mean([r['outage_s'] for r in flat])),
                'successful_means': {key: float(np.mean([r[key] for r in successful])) for key in METRICS}}
        d = contrast(by_arm['signal'], by_arm['v22'], bootstrap=True); m = d['metrics']
        d['gates'] = {'completion': d['success_difference_pp'] >= 0 and d['success_ci95_pp'][0] > -1,
            'delay': m['delay_proxy_mean_s']['difference'] <= 0 and m['delay_proxy_mean_s']['ci95'][1] < .05,
            'handovers': m['handovers']['difference'] <= 0 and m['handovers']['ci95'][1] < .25,
            'time': m['time_s']['two_percent_margin_ci95'][1] < 0,
            'energy': m['energy_proxy_j']['two_percent_margin_ci95'][1] < 0,
            'snr': m['snr_mean_db']['ci95'][0] > (.1 if sp == 'test' else 0)}
        results[sp] = d
    output = {'scope': 'Fresh 56012/56013 paired V2.3 versus V2.2; fixed weights and unchanged mission.',
        'selected_allowance_m': frozen['selected_allowance_m'], 'groups': groups, 'contrasts': results,
        'combined_improvement_gate': all(all(d['gates'].values()) for d in results.values()),
        'bootstrap_seed': 66000, 'bootstrap_draws': 5000, 'new_training': False, 'new_weights': 0}
    study.old.save(study.BASE/'analysis/statistics.json', output)
    print(json.dumps(output, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--phase', choices=['development', 'confirmatory'], required=True)
    args = parser.parse_args(); study.verify_history()
    development() if args.phase == 'development' else final_analysis()
