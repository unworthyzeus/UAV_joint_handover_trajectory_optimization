"""Verify the V2.2 archive, metric recovery, README and current paper."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote

import numpy as np

from audit_service_delivery import tables
from build_thesis_metrics_report import METRICS, NAMES, interval_text
from report_snr_comparison import recover as recover_snr
from recover_source_snr import recover as recover_source_snr

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT/'results/thesis_metrics_v22'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load(p):
    return json.loads(p.read_text(encoding='utf-8'))


def check_samples(p):
    rows = load(p)['episodes']
    with np.load(p.with_suffix('.npz')) as archive:
        samples = {key: archive[key] for key in archive.files}
        assert np.array_equal(samples['counts'], [r['metric_samples'] for r in rows])
        for i, row in enumerate(rows):
            n = row['metric_samples']
            assert n == row['time_s']
            for name in samples:
                if name != 'counts':
                    assert np.isnan(samples[name][i, n:]).all()
            signal = samples['snr_db'][i, :n]
            rss = samples['rss_dbm'][i, :n]
            assert row['missing_signal_samples'] == int(np.isnan(signal).sum())
            np.testing.assert_allclose(signal[rss > -128], rss[rss > -128]+103.41, atol=1e-12)
            assert np.nanmax(signal) <= 78.41+1e-12
            if np.isfinite(signal).any():
                assert row['snr_mean_db'] == float(np.nanmean(signal))
            assert row['neighbor_rss_power_mean_uw'] == float(samples['neighbor_rss_power_uw'][i, :n].mean())
            assert row['remaining_energy_kj'] == samples['remaining_energy_kj'][i, n-1]
            # Match V2's recorded float32 arithmetic order, rather than a
            # differently rounded float64 rearrangement of the same formula.
            expected_energy = float((np.float32(100000)-np.float32(row['energy_proxy_j']))/np.float32(1000))
            assert row['remaining_energy_kj'] == expected_energy
            assert row['literal_energy_score'] == samples['literal_energy_score'][i, n-1]
            assert np.all(np.diff(np.r_[1000., samples['literal_energy_score'][i, :n]]) > 0)
            assert row['handovers_per_second'] == row['handovers']/row['time_s']
            if row['success']:
                assert row['outage_s'] == row['dropped_bits'] == 0
                assert row['minimum_rss_dbm'] >= -96
                assert row['final_distance_m'] <= 10 and row['final_speed_mps'] <= 2
    return len(rows)


def main():
    frozen = {}
    for name in ('comparison_v1', 'connectivity_v2', 'reward_comparison_v15', 'service_reward_v21', 'thesis_metrics_v22'):
        d = load(ROOT/'configs'/('frozen_'+name+'.json'))
        frozen.update(d['source_hashes'])
        for p, h in d.get('reused_checkpoint_hashes', {}).items():
            assert sha(ROOT/p) == h, p
    assert len(frozen) == 33
    for p, h in frozen.items():
        assert sha(ROOT/p) == h, p
    models = []
    for name in ('checkpoint_manifest.json', 'service_reward_manifest.json'):
        models += load(ROOT/'models'/name)['checkpoints']
    assert len(models) == 20
    for r in models:
        assert sha(ROOT/r['path']) == r['sha256'], r['path']
    replay = load(BASE/'replay_audit.json')
    assert replay['exact_episode_and_metric_matches'] == 23000 and replay['all_sample_arrays_exact']
    assert replay['orchestration_sha256'] == sha(ROOT/'scripts/finish_thesis_metrics_parallel.py')
    checked = 0
    for r in replay['runs']:
        p = BASE/(r['run']+'.json')
        assert sha(p) == r['record_sha256']
        assert sha(p.with_suffix('.npz')) == r['samples_sha256']
        checked += check_samples(p)
    assert checked == 23000
    initial = load(BASE/'initial_replay/audit.json')
    assert initial['exact_core_episode_matches'] == 4000
    assert initial['script_sha256'] == sha(ROOT/'scripts/recover_initial_thesis_metrics.py')
    initial_checked = 0
    for r in initial['runs']:
        a, b = ROOT/r['source'], ROOT/r['recovered']
        assert sha(a) == r['source_sha256'] and sha(b) == r['recovered_sha256']
        old, new = load(a)['episodes'], load(b)['episodes']
        assert len(old) == len(new) == 200
        for x, y in zip(old, new):
            assert all(x[k] == y[k] for k in x)
        initial_checked += check_samples(b)
    assert initial_checked == 4000
    s = load(BASE/'analysis/statistics.json')
    assert s['total_evaluated_episodes'] == checked
    readme = (ROOT/'README.md').read_text(encoding='utf-8')
    ts = tables(readme)
    assert all(any('original' in c.lower() for c in t[0]) for t in ts)
    completion = next(t for t in ts if t[0][1] == 'Standard success (%), higher is better')
    for row, arm in zip(completion[2:], NAMES):
        for ix, split in ((1, 'test'), (2, 'longer_test')):
            assert row[ix] == f"{100*s['groups'][arm+'_'+split]['success_rate']:.2f}"
    paired = next(t for t in ts if t[0][0] == 'Recovered or service metric')
    assert len(paired[2:]) == len(METRICS)
    for row, (label, key, scale) in zip(paired[2:], METRICS):
        assert row[0] == label and re.search(r'(higher|lower) is better', label)
        for ix, split in ((1, 'test'), (3, 'longer_test')):
            d = s['contrasts']['guard_minus_full_'+split][key]
            assert row[ix] == f"{d['right_mean']*scale:.3f} / {d['left_mean']*scale:.3f}"
            assert row[ix+1] == f"{d['difference']*scale:+.3f} {interval_text(d['difference_ci95'], scale)}"
    recovered = load(BASE/'analysis/initial_recovered_metrics.json')
    source = next(t for t in ts if t[0][0] == 'Outcome, unit and preferred direction')
    for label, key in [('Mean SNR', 'snr_mean_db'), ('All neighbor RSS power', 'neighbor_rss_power_mean_uw'),
                       ('Remaining energy under V2', 'remaining_energy_kj'), ('Handover frequency', 'handovers_per_second')]:
        row = next(r for r in source[2:] if r[0].startswith(label+' '))
        for ix, split in ((3, 'test'), (4, 'longer_test')):
            d = recovered[split]['metrics'][key]
            assert row[ix] == f"{d['original_mean']:.3f} / {d['full_mean']:.3f}"
    cdf = next(r for r in source[2:] if r[0].startswith('SNR sample CDF'))
    assert cdf[1:3] == ['NR as a verified Eq. (8) result']*2
    source_snr = next(r for r in source[2:] if r[0].startswith('Source plotted SNR'))
    assert source_snr[3:5] == ['NC: unverified source scale']*2
    assert '≈124 / ≈127' in source_snr[1] and '≈123 / ≈122 / ≈123' in source_snr[2]
    for ix, split in ((3, 'test'), (4, 'longer_test')):
        d = recovered[split]['step_cdf_medians']
        assert cdf[ix] == f"Pooled sample median {d['original']['snr_db']:.3f} / {d['full']['snr_db']:.3f}"
    snr = load(BASE/'analysis/snr_comparison.json')
    assert snr == recover_snr()
    snr_table = next(t for t in ts if t[0][0] == 'SNR statistic and preferred direction')
    assert len(snr_table) == 6
    for offset, split in ((2, 'test'), (4, 'longer_test')):
        d = snr['splits'][split]
        for ix, metric in ((offset, 'mean_flight_snr_db'), (offset+1, 'pooled_sample_median_db')):
            assert 'higher is better' in snr_table[ix][0]
            assert snr_table[ix][1:3] == [f"{d[arm][metric]:.3f}" for arm in ('full', 'guard')]
        assert snr_table[offset][3] == f"{d['mean_difference_db']:+.3f}; 95% interval {interval_text(d['mean_difference_ci95_db'])}"
        delta = d['guard']['pooled_sample_median_db']-d['full']['pooled_sample_median_db']
        assert snr_table[offset+1][3] == f"{delta:+.3f}; descriptive"
    assert '78.41' in readme and 'same Barcelona ray tracing dataset' in readme
    source_recovery = load(BASE/'analysis/source_snr_recovery.json')
    assert source_recovery == recover_source_snr()
    assert not source_recovery['correction_confirmed']
    conditional = next(t for t in ts if t[0][0].startswith('Original thesis policy (SNR:'))
    recovered_policies = [r for f in source_recovery['figures'] for r in f['policies']]
    assert len(conditional[2:]) == len(recovered_policies) == 5
    for row, recorded in zip(conditional[2:], recovered_policies):
        assert row[0] == recorded['policy']
        assert row[1] == f"≈{recorded['reported_plot_median_db']:.0f}"
        assert row[2] == f"≈{recorded['conditional_corrected_median_db']:.1f}"
    assert 'Conditional corrected' in conditional[0][2]
    assert 'not recovered actual measurements' in readme
    paper_source = (ROOT/'paper/v22_followup.tex').read_text()
    assert 'conditional hypothesis, not a recovered actual result' in paper_source
    assert '62.4/65.4' in paper_source and '61.4/60.4/61.4' in paper_source
    paths = ['README.md', 'docs/README.md', 'docs/12_task_status.md', 'paper/README.md']
    paths += [p.relative_to(ROOT).as_posix() for p in (ROOT/'docs').glob('5[1-7]_*.md')]
    links = 0
    for name in paths:
        p = ROOT/name; text = p.read_text(encoding='utf-8'); tables(text)
        assert text.count('```') % 2 == 0
        for line in text.splitlines():
            if line.startswith('|'):
                assert not ('uplink' in line.lower() and 'downlink' in line.lower()), (name, line)
        for u in re.findall(r'\[[^\]]*\]\(([^)]+)\)', text):
            if '://' in u:
                continue
            target = unquote(u).split('#')[0]
            q = (p.parent/target).resolve() if target else p
            # The delivery note links to this audit's own output, written below.
            assert q.exists() or q == BASE/'analysis/delivery_validation.json', (name, u)
            links += 1
    paper = load(ROOT/'results/reward_comparison/analysis_v15/paper_audit.json')
    assert sha(ROOT/'paper/UAV_joint_reward_connectivity_IEEE.pdf') == paper['pdf_sha256']
    assert paper['visual_review'].startswith('Passed')
    for p, h in paper['source_hashes'].items():
        assert sha(ROOT/p) == h
    tests = BASE/'analysis/implementation_tests.txt'
    assert '94 passed' in tests.read_text()
    assert not subprocess.check_output(['git', 'ls-files', '*.h5', '*.hdf5'], cwd=ROOT).strip()
    for name in ('statistics.json', 'reward_comparison_example.pdf', 'reward_comparison_diagnostics.pdf', 'reward_comparison_success.pdf'):
        path = 'results/reward_comparison/analysis_v15/'+name
        assert (ROOT/path).read_bytes() == subprocess.check_output(['git', 'show', 'd53b293:'+path], cwd=ROOT)
    report = dict(scope='Current README, recovered source metrics, separate V2.2 supervisor study and unified paper.',
        frozen_source_protocol_files_verified=33, checkpoints=20, checkpoint_bytes=sum(r['bytes'] for r in models),
        new_weights=0, new_ppo_training=False, exact_final_replays=checked, exact_initial_recoveries=initial_checked,
        sample_metrics_independently_checked=checked+initial_checked, implementation_tests_passed=94,
        test_log_sha256=sha(tests), readme_tables_with_original_comparisons=len(ts),
        new_success_values_checked=14, new_service_means_checked=40, new_service_intervals_checked=20,
        initial_recovered_means_checked=16, initial_cdf_medians_checked=4, local_links_checked=links,
        current_snr_means_checked=4, current_snr_medians_checked=4, current_snr_source_files_checked=40,
        unverified_source_snr_scale_separated=True,
        source_plot_medians_digitized=5, conditional_source_estimates_checked=5,
        source_correction_confirmed=False,
        paper_pages=paper['pages'], paper_sha256=paper['pdf_sha256'], paper_visual_review=paper['visual_review'],
        primary_completion_improvement=s['primary_completion_improvement'],
        primary_delay_no_regression=s['primary_delay_no_regression'],
        source_eq8_max_snr_db=78.41, physical_uplink_evaluated=False,
        initial_statistics_and_figures_unchanged=True, private_hdf5_untracked=True)
    (BASE/'analysis/delivery_validation.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
