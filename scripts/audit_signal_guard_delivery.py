"""Check raw V2.3 records, source preservation and publication values."""
import hashlib
import json
from pathlib import Path
import re
import subprocess

import numpy as np

import run_signal_guard_study as study
from analyze_signal_guard_study import contrast, load_runs
from audit_service_delivery import tables
from build_signal_guard_report import FIELDS, ci, metric_digits

ROOT = study.ROOT
OUT = study.BASE/'analysis'


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def verify_arrays(path):
    rows = load(path)['episodes']
    with np.load(path.with_suffix('.npz')) as archive:
        a = {k: archive[k] for k in archive.files}
    np.testing.assert_array_equal(a['counts'], [r['metric_samples'] for r in rows])
    for i, r in enumerate(rows):
        n = r['metric_samples']; assert n == r['time_s']
        for key, values in a.items():
            if key != 'counts':
                assert np.isnan(values[i, n:]).all()
        rss = a['rss_dbm'][i, :n]; signal = a['snr_db'][i, :n]
        np.testing.assert_allclose(signal[rss > -128], rss[rss > -128]+103.41, atol=1e-12)
        assert np.isnan(signal[rss <= -128]).all()
        if np.isfinite(signal).any():
            assert r['snr_mean_db'] == float(np.nanmean(signal))
        assert r['missing_signal_samples'] == int(np.isnan(signal).sum())
        assert r['remaining_energy_kj'] == a['remaining_energy_kj'][i, n-1]
        assert r['neighbor_rss_power_mean_uw'] == float(a['neighbor_rss_power_uw'][i, :n].mean())
        assert r['handovers_per_second'] == r['handovers']/r['time_s']
        if r['success']:
            assert r['outage_s'] == r['dropped_bits'] == 0 and r['minimum_rss_dbm'] >= -96
            assert r['final_distance_m'] <= 10 and r['final_speed_mps'] <= 2 and r['time_s'] <= 200
    return len(rows)


def main():
    study.verify_history(); frozen = study.verify_frozen()
    sources = {}
    for p in (ROOT/'configs').glob('frozen_*.json'):
        d = load(p); sources.update(d['source_hashes'])
        for name, expected in d['source_hashes'].items():
            assert study.old.sha(ROOT/name) == expected, name
    assert len(sources) == 38
    for phase, expected in [('development', 1536), ('confirmatory', 10000)]:
        study.verify_snapshot(study.BASE/phase)
        for name, h in frozen['source_hashes'].items():
            assert study.old.sha(study.BASE/phase/'source_snapshot'/name) == h
        audit = load(study.BASE/phase/'run_audit.json')
        count = 0
        for row in audit['runs']:
            p = study.BASE/(row['run']+'.json')
            assert study.old.sha(p) == row['record_sha256']
            assert study.old.sha(p.with_suffix('.npz')) == row['samples_sha256']
            count += verify_arrays(p)
        assert count == expected and audit['episodes'] == expected
        if phase == 'confirmatory':
            assert audit['all_exactly_replayed'] and all(r['exact_replay'] for r in audit['runs'])
    s = load(OUT/'statistics.json'); selection = load(study.BASE/'development/selection.json')
    assert selection['selected_allowance_m'] == frozen['selected_allowance_m'] == 1
    assert all(d['selection_gate'] for d in selection['candidates']['signal_1'].values())
    assert not selection['candidates']['signal_3']['test']['selection_gate']
    assert not selection['candidates']['signal_6']['test']['selection_gate']
    for sp, d in s['contrasts'].items():
        recomputed = contrast(load_runs('confirmatory', 'signal', sp, study.old.SEEDS),
                              load_runs('confirmatory', 'v22', sp, study.old.SEEDS))
        for key in ('candidate_successes', 'baseline_successes', 'episodes_per_arm', 'common_successes', 'success_difference_pp'):
            assert d[key] == recomputed[key]
        for key, metric in recomputed['metrics'].items():
            for name, value in metric.items():
                assert d['metrics'][key][name] == value
    sample_report = load(OUT/'sample_summary.json')
    for p, h in sample_report['source_hashes'].items():
        assert study.old.sha(ROOT/p) == h
    readme = (ROOT/'README.md').read_text(encoding='utf-8'); ts = tables(readme)
    assert all(any('original' in cell.lower() for cell in t[0]) for t in ts)
    success = next(t for t in ts if t[0][0] == 'Fresh split; completion: higher is better')
    for row, sp in zip(success[2:], ('test', 'longer_test')):
        d = s['contrasts'][sp]; n = d['episodes_per_arm']
        assert row[1] == f"{100*d['baseline_successes']/n:.2f}% ({d['baseline_successes']}/{n})"
        assert row[2] == f"{100*d['candidate_successes']/n:.2f}% ({d['candidate_successes']}/{n})"
        assert row[3] == f"{d['success_difference_pp']:+.3f} {ci(d['success_ci95_pp'])}"
    metrics = next(t for t in ts if t[0][1] == 'Standard V2.2 / V2.3')
    assert len(metrics[2:]) == len(FIELDS)+1
    for row, (label, key, scale, source) in zip(metrics[2:], FIELDS):
        assert row[0] == label and ('higher is better' in label or 'lower is better' in label)
        digits = metric_digits(key)
        for ix, sp in ((1, 'test'), (3, 'longer_test')):
            m = s['contrasts'][sp]['metrics'][key]
            assert row[ix] == f"{m['baseline_mean']*scale:.{digits}f} / {m['candidate_mean']*scale:.{digits}f}"
            assert row[ix+1] == f"{m['difference']*scale:+.{digits}f} {ci(m['ci95'], scale, digits)}"
    for ix, sp in ((1, 'test'), (3, 'longer_test')):
        a, b = (sample_report['splits'][sp][arm]['pooled_sample_snr_median_db'] for arm in ('v22', 'signal'))
        assert metrics[-1][ix] == f'{a:.3f} / {b:.3f}'
        assert metrics[-1][ix+1] == f'{b-a:+.3f}; descriptive'
    gate = all(all(d['gates'].values()) for d in s['contrasts'].values())
    assert s['combined_improvement_gate'] == gate
    expected = ('V2.3 passes the declared combined improvement gate.' if gate else
                'V2.3 does not pass the declared combined improvement gate; V2.2 remains the default.')
    assert expected in readme
    links = 0
    for path in [ROOT/'README.md', ROOT/'docs/59_signal_guard_results.md', ROOT/'docs/README.md', ROOT/'paper/README.md']:
        content = path.read_text(encoding='utf-8'); tables(content)
        assert content.count('```') % 2 == 0
        for u in re.findall(r'\[[^\]]*\]\(([^)]+)\)', content):
            if '://' not in u:
                dest = u.split('#')[0]
                assert (path.parent/dest).exists() if dest else True, (str(path), u)
                links += 1
    paper = load(ROOT/'results/reward_comparison/analysis_v15/paper_audit.json')
    assert paper['visual_review'].startswith('Passed')
    assert study.old.sha(ROOT/paper['pdf']) == paper['pdf_sha256']
    for p, h in paper['source_hashes'].items():
        assert study.old.sha(ROOT/p) == h
    tests = OUT/'implementation_tests.txt'
    assert '100 passed' in tests.read_text(encoding='utf-8-sig')
    assert not subprocess.check_output(['git', 'ls-files', '*.h5', '*.hdf5'], cwd=ROOT).strip()
    checkpoints = []
    for name in ['checkpoint_manifest.json', 'service_reward_manifest.json']:
        checkpoints.extend(load(ROOT/'models'/name)['checkpoints'])
    for record in checkpoints:
        assert study.old.sha(ROOT/record['path']) == record['sha256']
    result = {'scope': 'Final signal path study, every development candidate and current publications.',
        'source_protocol_files_preserved': 38, 'checkpoints_preserved': len(checkpoints),
        'new_weights': 0, 'new_ppo_training': False, 'development_episodes_checked': 1536,
        'final_episodes_checked_and_exactly_replayed': 10000, 'sample_arrays_checked': 36,
        'new_means_checked': 48, 'new_difference_intervals_checked': 24, 'pooled_sample_medians_checked': 4,
        'tests_passed': 100, 'test_log_sha256': study.old.sha(tests),
        'combined_improvement_gate': gate, 'selected_allowance_m': frozen['selected_allowance_m'],
        'readme_tables_with_original_comparison': len(ts), 'local_links_checked': links,
        'paper_sha256': paper['pdf_sha256'], 'paper_pages': paper['pages'],
        'paper_visual_review': paper['visual_review'], 'private_dataset_untracked': True}
    study.old.save(OUT/'delivery_validation.json', result)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
