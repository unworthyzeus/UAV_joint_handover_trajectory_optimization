"""Recover a matched SNR CDF comparison from existing V2.2 sample arrays."""
import hashlib
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT/'results/thesis_metrics_v22'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def recover():
    statistics_path = BASE/'analysis/statistics.json'
    statistics = json.loads(statistics_path.read_text())
    result = {'scope': 'Reporting only: existing 55012/55013 flights, common successful full V2/V2.2 pairs.',
              'statistics_sha256': sha(statistics_path), 'source_hashes': {}, 'splits': {}}
    for split in ('test', 'longer_test'):
        pooled = {'full': [], 'guard': []}; means = {'full': [], 'guard': []}; pairs = 0
        for seed in range(2101, 2106):
            rows = {}; prefixes = {}
            for arm in ('full', 'guard'):
                prefix = BASE/'confirmatory'/f'{arm}_seed_{seed}'/split
                prefixes[arm] = prefix
                rows[arm] = json.loads(prefix.with_suffix('.json').read_text())['episodes']
                for suffix in ('.json', '.npz'):
                    path = prefix.with_suffix(suffix)
                    result['source_hashes'][path.relative_to(ROOT).as_posix()] = sha(path)
            assert [r['scenario_id'] for r in rows['full']] == [r['scenario_id'] for r in rows['guard']]
            keep = np.array([a['success'] and b['success'] for a, b in zip(rows['full'], rows['guard'])])
            pairs += int(keep.sum())
            for arm in ('full', 'guard'):
                with np.load(prefixes[arm].with_suffix('.npz')) as samples:
                    values = samples['snr_db'][keep]
                pooled[arm].extend(values[np.isfinite(values)].tolist())
                means[arm].extend(r['snr_mean_db'] for r, use in zip(rows[arm], keep) if use)
        contrast = statistics['contrasts']['guard_minus_full_'+split]
        assert pairs == contrast['paired_success_count']
        row = {'common_success_pairs': pairs}
        for arm, side in (('full', 'right'), ('guard', 'left')):
            mean = float(np.mean(means[arm]))
            assert abs(mean-contrast['snr_mean_db'][side+'_mean']) < 1e-12
            row[arm] = {'mean_flight_snr_db': mean, 'pooled_sample_median_db': float(np.median(pooled[arm])),
                        'executed_sample_count': len(pooled[arm])}
        row['mean_difference_db'] = contrast['snr_mean_db']['difference']
        row['mean_difference_ci95_db'] = contrast['snr_mean_db']['difference_ci95']
        result['splits'][split] = row
    return result


def write_report():
    result = recover()
    (BASE/'analysis/snr_comparison.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    lines = ['### SNR Comparison for the Current Controller', '',
        '**V2.2 already improves valid SNR.** The older source comparison below shows V1.5 and full V2 on '
        '53012/53013 routes; those 63.410 values are not V2.2 results. This table uses the same fresh '
        '55012/55013 routes for full V2 and V2.2, with identical units and aggregation within each row.', '',
        '| SNR statistic and preferred direction | Full V2 (dB) | V2.2 (dB) | Difference (dB) | Original thesis comparison |',
        '| --- | ---: | ---: | --- | --- |']
    for split, name in (('test', 'Standard'), ('longer_test', 'Longer')):
        d = result['splits'][split]
        ci = '['+', '.join(f'{v:.3f}' for v in d['mean_difference_ci95_db'])+']'
        lines += [f"| {name} mean flight SNR: higher is better | {d['full']['mean_flight_snr_db']:.3f} | "
                  f"{d['guard']['mean_flight_snr_db']:.3f} | {d['mean_difference_db']:+.3f}; 95% interval {ci} | "
                  'Verified source mean NR [printed p. 10, Eq. (8); pp. 18, 20, Figs. 6/8]. |',
                  f"| {name} pooled sample CDF median: higher is better | {d['full']['pooled_sample_median_db']:.3f} | "
                  f"{d['guard']['pooled_sample_median_db']:.3f} | "
                  f"{d['guard']['pooled_sample_median_db']-d['full']['pooled_sample_median_db']:+.3f}; descriptive | "
                  'Source plotted medians remain unverified; no numerical improvement over that scale is claimed [pp. 18, 20]. |']
    lines += ['', 'The comparisons use 2,331 standard and 2,225 longer common successful pairs. A mean flight '
        'SNR gives each flight equal weight; the pooled sample median gives each executed one second sample '
        'equal weight, so longer flights contribute more samples. Median differences are descriptive, not new '
        'confidence intervals or new independent trials.', '',
        '**Why 122–127 dB is not an optimization target:** using the thesis formula and settings, '
        '`SNR = RSS + 112.41 − 9`. The maximum RSS in the same Operator 1 map is −25 dBm, giving '
        '`−25 + 112.41 − 9 = 78.41 dB`. The original plotted values exceed that bound. Their source inputs '
        'or implementation need clarification [printed p. 10, Eq. (8); p. 15, Table 3; pp. 18, 20, Figs. 6/8]. '
        'The 78.41 dB bound is the best value anywhere on the map, not an attainable average along every mission.', '',
        'Further SNR gains must preserve completion and communication service. SNR alone excludes interference; '
        'the SINR, delay, handover and failure rows above remain necessary. '
        '[Reporting clarification and sample counts](docs/56_snr_comparison_clarification.md).', '']
    (BASE/'analysis/snr_readme_fragment.md').write_text('\n'.join(lines), encoding='utf-8')
    return result


if __name__ == '__main__':
    print(json.dumps(write_report()['splits'], indent=2))
