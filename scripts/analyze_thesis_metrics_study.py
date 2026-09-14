"""Declared fresh comparisons and additional thesis motivated metrics."""
import argparse
import json

import numpy as np

import run_thesis_metrics_study as study
from analyze_connectivity_experiment import interval

METRICS = ['time_s', 'delay_proxy_mean_s', 'handovers', 'energy_proxy_j', 'remaining_energy_kj',
           'sinr_mean_db', 'snr_mean_db', 'neighbor_rss_power_mean_uw', 'interference_mean_w',
           'radio_cost_sum', 'handovers_per_second', 'literal_energy_score', 'literal_rss_sum_mean']


def contrast(left, right):
    if len(right) == 1 and len(left) > 1:
        right = right * len(left)
    assert len(left) == len(right)
    for a, b in zip(left, right):
        assert [r['scenario_id'] for r in a] == [r['scenario_id'] for r in b]
    a = np.array([[r['success'] for r in run] for run in left])
    b = np.array([[r['success'] for r in run] for run in right])
    delta = a.astype(float)-b.astype(float); common = a & b
    result = {'success_difference_pp': float(100 * delta.mean()),
              'success_difference_ci95_pp': [100*x for x in interval(delta, seed=65000, draws=5000)],
              'paired_success_count': int(common.sum()), 'paired_evaluations': int(common.size)}
    for metric in METRICS:
        x = np.array([[r[metric] for r in run] for run in left], dtype=float)
        y = np.array([[r[metric] for r in run] for run in right], dtype=float)
        assert np.isfinite(x[common]).all() and np.isfinite(y[common]).all(), metric
        result[metric] = {'left_mean': float(x[common].mean()) if common.any() else None,
                          'right_mean': float(y[common].mean()) if common.any() else None,
                          'difference': float((x-y)[common].mean()) if common.any() else None,
                          'difference_ci95': interval(x-y, common, seed=65000, draws=5000)}
    return result


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--label'); args = parser.parse_args()
    base, _, _ = study.configure(args.label)
    study.verify_history(); frozen = study.verify_new()
    learned = ['original', 'full', 'service'] + (['guard'] if frozen['selected_horizon'] is not None else [])
    arms = learned + ['straight_radio', 'joint_mpc', 'joint_lookahead']
    data = {}; groups = {}
    for split in ('test', 'longer_test'):
        data[split] = {}
        for arm in arms:
            runs = []; pooled = {k: [] for k in ('snr_db', 'neighbor_rss_power_uw', 'rss_dbm')}
            seconds = []
            for seed in study.SEEDS if arm in learned else [None]:
                prefix = base/'confirmatory'/(f'{arm}_seed_{seed}' if seed else arm)/split
                content = json.loads(prefix.with_suffix('.json').read_text())
                rows = content['episodes']; assert len(rows) == 500
                success = np.array([r['success'] for r in rows])
                with np.load(prefix.with_suffix('.npz')) as samples:
                    assert np.array_equal(samples['counts'], [r['metric_samples'] for r in rows])
                    for key in pooled:
                        values = samples[key][success]
                        pooled[key].extend(values[np.isfinite(values)].tolist())
                for row in rows:
                    if row['success']:
                        assert row['minimum_rss_dbm'] >= -96 and row['outage_s'] == 0 and row['dropped_bits'] == 0
                        assert row['time_s'] <= 200 and row['final_distance_m'] <= 10 and row['final_speed_mps'] <= 2
                runs.append(rows); seconds.append(content['runtime_seconds'])
            data[split][arm] = runs; flat = [r for run in runs for r in run]
            success_rows = [r for r in flat if r['success']]
            group = study.summarize(flat)
            group.update(per_seed_success_rates=[float(np.mean([r['success'] for r in run])) for run in runs],
                runtime_seconds=float(sum(seconds)), all_flight_mean_outage_s=float(np.mean([r['outage_s'] for r in flat])),
                all_flight_mean_literal_energy_score=float(np.mean([r['literal_energy_score'] for r in flat])),
                missing_signal_samples=sum(r['missing_signal_samples'] for r in flat),
                successful_flight_means={k: float(np.mean([r[k] for r in success_rows])) if success_rows else None for k in METRICS},
                successful_flight_handover_median=float(np.median([r['handovers'] for r in success_rows])) if success_rows else None,
                successful_step_cdf_medians={k: float(np.median(v)) if v else None for k, v in pooled.items()},
                successful_step_samples={k: len(v) for k, v in pooled.items()})
            groups[arm+'_'+split] = group
    contrasts = {}
    if 'guard' in learned:
        for split in data:
            for right in ['full', 'original', 'service', 'straight_radio', 'joint_mpc', 'joint_lookahead']:
                contrasts['guard_minus_'+right+'_'+split] = contrast(data[split]['guard'], data[split][right])
    primary = contrasts.get('guard_minus_full_test')
    result = {'scope': 'Fresh 55012/55013 routes; source motivated metric recovery and a fixed weight controller supervisor.',
              'selected_horizon': frozen['selected_horizon'], 'groups': groups, 'contrasts': contrasts,
              'total_evaluated_episodes': sum(g['episodes'] for g in groups.values()),
              'primary_completion_improvement': bool(primary and primary['success_difference_ci95_pp'][0] > 0),
              'primary_delay_no_regression': bool(primary and primary['delay_proxy_mean_s']['difference_ci95'][1] <= 0),
              'bootstrap_seed': 65000, 'bootstrap_draws': 5000,
              'new_ppo_training': False, 'physical_uplink_evaluated': False,
              'source_eq9_linear_power_interpretation': True, 'source_energy_score_has_physical_units': False}
    study.save(base/'analysis/statistics.json', result)
    print(json.dumps({'success': {k: v['success_rate'] for k, v in groups.items()},
                      'primary': primary, 'total': result['total_evaluated_episodes']}, indent=2))


if __name__ == '__main__':
    main()
