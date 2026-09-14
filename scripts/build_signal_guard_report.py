"""Publish complete V2.3 outcomes without changing its frozen analysis."""
from collections import Counter
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42
import matplotlib.pyplot as plt
import numpy as np

import run_signal_guard_study as study
from analyze_signal_guard_study import load_runs

ROOT = study.ROOT
OUT = study.BASE/'analysis'
FIELDS = [
    ('Mean flight SNR (dB), higher is better', 'snr_mean_db', 1, 'Source Eq. (8), p. 10; plotted scale remains unverified.'),
    ('Mean SINR (dB), higher is better', 'sinr_mean_db', 1, 'SINR NR; source reports SNR, p. 10, Eq. (8).'),
    ('Delay proxy (s), lower is better', 'delay_proxy_mean_s', 1, 'Queue/rate definition p. 9, Eq. (4); comparable result NR.'),
    ('Handovers per flight, lower is better while preserving service', 'handovers', 1, 'Source count normalization unknown, pp. 18/20, Figs. 6/8.'),
    ('Flight time (s), lower is better', 'time_s', 1, 'Matched arrival time NR; source arrival does not terminate, p. 12, Sec. 5.2.'),
    ('Consumed energy (kJ), lower is better', 'energy_proxy_j', .001, 'Different energy model; source remaining display is not kJ, pp. 10/15, Eq. (10)/Table 3.'),
    ('Remaining energy (kJ), higher is better', 'remaining_energy_kj', 1, 'Verified source kJ result NR, pp. 10/15.'),
    ('Cochannel downlink interference (µW), lower is better', 'interference_mean_w', 1e6, 'Comparable source result NR, p. 10, Eq. (9).'),
    ('All neighbor RSS power (µW), lower is better', 'neighbor_rss_power_mean_uw', 1, 'Our linear interpretation of Eq. (9), p. 10; source aggregation unverified.'),
    ('Handovers per second, lower is better while preserving service', 'handovers_per_second', 1, 'Comparable source denominator NR, pp. 18/20.'),
    ('Path length (m), lower is better while preserving service', 'path_m', 1, 'Source trajectory illustrations, pp. 17/19; aggregate length NR.'),
    ('Accumulated V2 radio cost, lower is better while preserving service', 'radio_cost_sum', 1, 'Our transformed reporting cost; source returns not comparable, pp. 10/12, Eqs. (11)–(14).'),
]


def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip()+'\n', encoding='utf-8')


def ci(values, scale=1, digits=3):
    return '['+', '.join(f'{v*scale:.{digits}f}' for v in values)+']'


def metric_digits(key):
    return 6 if key in ('interference_mean_w', 'neighbor_rss_power_mean_uw') else 3


def recover_samples():
    output = {}; source_hashes = {}
    for split in ('test', 'longer_test'):
        pooled = {'v22': [], 'signal': []}; counts = {'v22': 0, 'signal': 0}
        for seed in study.old.SEEDS:
            rows = {}; arrays = {}
            for arm in pooled:
                prefix = study.BASE/'confirmatory'/f'{arm}_seed_{seed}'/split
                rows[arm] = json.loads(prefix.with_suffix('.json').read_text())['episodes']
                with np.load(prefix.with_suffix('.npz')) as archive:
                    arrays[arm] = archive['snr_db'].copy()
                for suffix in ('.json', '.npz'):
                    p = prefix.with_suffix(suffix)
                    source_hashes[p.relative_to(ROOT).as_posix()] = study.old.sha(p)
            assert [r['scenario_id'] for r in rows['v22']] == [r['scenario_id'] for r in rows['signal']]
            keep = np.array([a['success'] and b['success'] for a, b in zip(rows['v22'], rows['signal'])])
            for arm in pooled:
                v = arrays[arm][keep]; valid = v[np.isfinite(v)]
                pooled[arm].extend(valid.tolist()); counts[arm] += len(valid)
        output[split] = {arm: {'pooled_sample_snr_median_db': float(np.median(pooled[arm])),
                              'executed_sample_count': counts[arm]} for arm in pooled}
    result = {'scope': 'Executed samples from common successful V2.2/V2.3 pairs only.',
              'source_hashes': source_hashes, 'splits': output}
    write(OUT/'sample_summary.json', json.dumps(result, indent=2))
    return output


def plots():
    fig, axes = plt.subplots(2, 2, figsize=(9, 6), constrained_layout=True)
    for i, split in enumerate(('test', 'longer_test')):
        a = load_runs('confirmatory', 'v22', split, study.old.SEEDS)
        b = load_runs('confirmatory', 'signal', split, study.old.SEEDS)
        pairs = [(x, y) for ar, br in zip(a, b) for x, y in zip(ar, br) if x['success'] and y['success']]
        for j, (key, label) in enumerate((('snr_mean_db', 'Mean flight SNR (dB)\nHigher is better'),
                                         ('delay_proxy_mean_s', 'Mean flight delay proxy (s)\nLower is better'))):
            ax = axes[i, j]
            for index, name, color in ((0, 'V2.2', '#335c9b'), (1, 'V2.3', '#16836b')):
                values = np.sort([pair[index][key] for pair in pairs])
                ax.step(values, np.arange(1, len(values)+1)/len(values), where='post', label=name, color=color)
            ax.set_title(('Standard' if i == 0 else 'Longer')+f': {len(pairs)} common successes')
            ax.set_xlabel(label); ax.set_ylabel('Empirical CDF'); ax.set_ylim(0, 1)
            ax.grid(alpha=.25); ax.legend()
    fig.suptitle('Separate fresh 56012/56013 comparison; five fixed policies\nFailures remain in the completion tables')
    fig.savefig(OUT/'signal_service_cdfs.png', dpi=170)
    fig.savefig(OUT/'signal_service_cdfs.pdf')
    plt.close(fig)


def main():
    study.verify_frozen()
    selection = json.loads((study.BASE/'development/selection.json').read_text())
    s = json.loads((OUT/'statistics.json').read_text()); ds = s['contrasts']; passed = s['combined_improvement_gate']
    samples = recover_samples(); plots()
    verdict = ('V2.3 passes the declared combined improvement gate.' if passed else
               'V2.3 does not pass the declared combined improvement gate; V2.2 remains the default.')
    final = ['## V2.3 Signal Aware Path Selection', '', '**'+verdict+'**', '',
        'This is a new fixed weight controller comparison on the same Barcelona ray tracing dataset as the original thesis. '
        'It allows up to 1 m less predicted goal progress within the existing five step rollout score when a path predicts '
        'stronger SNR with no extra delay or handovers. This is not a 1 m total detour limit. '
        'The original mission, RSS, buffer, A3 masks and executed safety filter remain unchanged.', '',
        'Development tested 1, 3 and 6 m allowances on 192 new routes with two saved policies (1,536 episodes). '
        'Only 1 m qualified. The other candidates improved SNR more but lost standard completions. '
        'The selected version was frozen before 500 fresh standard and 500 fresh longer routes, seeds 56012/56013, '
        'were generated. Both controllers used all five full V2 policies: 10,000 final episodes, all exactly replayed. '
        'These results are separate from every earlier test set.', '',
        '| Fresh split; completion: higher is better | V2.2 success | V2.3 success | Difference (pp), 95% interval | Original thesis comparison |',
        '| --- | ---: | ---: | --- | --- |']
    for split, name in (('test', 'Standard'), ('longer_test', 'Longer')):
        d = ds[split]; n = d['episodes_per_arm']
        final.append(f"| {name} | {100*d['baseline_successes']/n:.2f}% ({d['baseline_successes']}/{n}) | "
                     f"{100*d['candidate_successes']/n:.2f}% ({d['candidate_successes']}/{n}) | "
                     f"{d['success_difference_pp']:+.3f} {ci(d['success_ci95_pp'])} | Comparable joint success NR [printed pp. 16–20]. |")
    final += ['', '| Metric and preferred direction | Standard V2.2 / V2.3 | Difference, 95% interval | Longer V2.2 / V2.3 | Difference, 95% interval | Original thesis definition / comparability |',
              '| --- | --- | --- | --- | --- | --- |']
    for label, key, scale, source in FIELDS:
        cells = []
        digits = metric_digits(key)
        for split in ('test', 'longer_test'):
            m = ds[split]['metrics'][key]
            cells += [f"{m['baseline_mean']*scale:.{digits}f} / {m['candidate_mean']*scale:.{digits}f}",
                      f"{m['difference']*scale:+.{digits}f} {ci(m['ci95'], scale, digits)}"]
        final.append('| '+label+' | '+' | '.join(cells)+' | '+source+' |')
    cells = []
    for split in ('test', 'longer_test'):
        a, b = (samples[split][arm]['pooled_sample_snr_median_db'] for arm in ('v22', 'signal'))
        cells += [f'{a:.3f} / {b:.3f}', f'{b-a:+.3f}; descriptive']
    final += ['| Pooled sample SNR median (dB), higher is better | '+' | '.join(cells)+' | Source aggregation and scale unverified, pp. 18/20; note 57 gives a separate conditional correction. |', '',
        f"Service means use {ds['test']['common_successes']:,} standard and {ds['longer_test']['common_successes']:,} longer common successful pairs. "
        'Every failure remains in completion denominators. Mean flight SNR weights flights equally; the pooled sample median '
        'weights every executed second equally. A better median alone is not the declared improvement test.', '',
        '**How to read the result:** positive SNR or SINR differences favor V2.3; negative delay and handover differences favor V2.3. '
        'Positive time and consumed energy differences are costs. Completion is checked first: its point difference '
        'must be nonnegative and its interval must exclude a loss of 1 percentage point. This does not establish identical reliability. '
        'Delay, handover, time and energy margins are study choices, not thesis requirements. '
        'Secondary metric intervals are descriptive and unadjusted.', '']
    improvements = []
    completion_notes = []
    for split, name in (('test', 'Standard'), ('longer_test', 'Longer')):
        d = ds[split]; m = d['metrics']; failures = [k for k, v in d['gates'].items() if not v]
        improvements.append(f"{name}: SNR {m['snr_mean_db']['difference']:+.3f} dB; delay "
            f"{100*m['delay_proxy_mean_s']['difference']/m['delay_proxy_mean_s']['baseline_mean']:+.1f}%; "
            f"handovers {100*m['handovers']['difference']/m['handovers']['baseline_mean']:+.1f}%; "
            f"flight time {100*m['time_s']['difference']/m['time_s']['baseline_mean']:+.2f}%; "
            f"consumed energy {100*m['energy_proxy_j']['difference']/m['energy_proxy_j']['baseline_mean']:+.2f}%. "
            f"Failed gates: {', '.join(failures) if failures else 'none'}.")
        if d['success_difference_pp'] < 0 and d['success_ci95_pp'][0] > -1:
            completion_notes.append(f"{name} completion misses the gate's nonnegative point requirement, "
                'although its interval excludes a loss of 1 percentage point. '
                +('The interval includes zero, so the observed decrease is not statistically resolved.'
                  if d['success_ci95_pp'][0] <= 0 <= d['success_ci95_pp'][1] else
                  'Its interval does not include zero.'))
    final += improvements+['']+completion_notes+['',
        '| Controller / split | RSS / buffer / timeout / boundary / energy failures (counts), lower is better | Mean sampled outage (s), lower is better | Original thesis comparison |',
        '| --- | --- | ---: | --- |']
    for arm, label in [('v22', 'V2.2'), ('signal', 'V2.3')]:
        for split, name in [('test', 'standard'), ('longer_test', 'longer')]:
            group = s['groups'][arm+'_'+split]
            failures = ' / '.join(str(group['outcomes'].get(k, 0)) for k in ('connectivity', 'buffer', 'timeout', 'boundary', 'energy'))
            final.append(f"| {label} {name} | {failures} | {group['all_flight_mean_outage_s']:.4f} | Source first failure counts NR; outage bars pp. 18/20 do not use our strict termination. |")
    final += ['', 'Sampled outage stops at the first violation, so its mean is censored by termination. '
        'Zero outage on successful flights is a requirement, not independent proof of better connectivity.', '',
        'No new weights or PPO training were added. '
        'The source thesis agent remains unavailable; neither its conditional SNR correction nor its plotted outcomes '
        'are matched numerical baselines for this study.', '',
        '![V2.3 signal and service distributions](results/signal_guard_v23/analysis/signal_service_cdfs.png)', '',
        '[Declared protocol](docs/58_signal_guard_protocol.md), '
        '[complete results, failed candidates, all seeds and reproduction](docs/59_signal_guard_results.md), '
        '[numerical analysis](results/signal_guard_v23/analysis/statistics.json).', '',
        'Try one saved route or your own coordinates with the existing weights and '
        '`dataset/Barcelona_dataset_January.h5`:', '',
        '```powershell',
        'python scripts/evaluate_signal_guard_controller.py --controller signal --seed 2101 --split test --scenario-index 0 --output outputs/v23_example',
        'python scripts/evaluate_signal_guard_controller.py --controller signal --seed 2101 --start 1000 1000 --goal 1800 1300 --output outputs/v23_custom',
        '```', '',
        'These commands save one route and all metric samples. Use `--controller v22` for the baseline. '
        'Use a new output prefix for each run; the full study runner is required for exact batch replay.', '']
    fragment = '\n'.join(final)
    write(OUT/'readme_fragment.md', fragment)
    p = ROOT/'README.md'; readme = p.read_text(encoding='utf-8')
    heading = '## V2.3 Signal Aware Path Selection'
    if heading in readme:
        start = readme.index(heading); end = readme.index('\n## ', start+len(heading))
        readme = readme[:start]+fragment+'\n'+readme[end+1:]
    else:
        readme = readme.replace('## Recovered Thesis Metrics and V2.2 Controller Test', fragment+'\n## Recovered Thesis Metrics and V2.2 Controller Test', 1)
    readme = readme.replace('**V2 with its original reward control, the V2.1 reward study, and the V2.2 controller and thesis metric study.**',
        '**V2 with its original reward control, separate V2.1 and V2.2 studies, and the V2.3 signal path comparison.**')
    readme = readme.replace('[new controller results and every seed](docs/53_v22_guard_results.md)',
        '[latest signal path results](docs/59_signal_guard_results.md),\n[V2.2 controller results and every seed](docs/53_v22_guard_results.md)')
    if '| V2.3 path selection |' not in readme:
        revised = []
        for line in readme.splitlines():
            revised.append(line)
            if line.startswith('| V2.2 supervisor |'):
                revised.append('| V2.3 path selection | Same V2.2 rollouts and network choice; beyond 50 m, '
                    'prefer higher predicted SNR within 1 m of the best rollout progress and no predicted '
                    'delay or handover increase. Selected from 1/3/6 m on new development routes. '
                    '[Full definition](docs/58_signal_guard_protocol.md). | No corresponding lookahead signal '
                    'selection is defined in the original PPO method [pp. 12–13, Secs. 5.2–5.3]. No new training, '
                    'weights or changed mission constraints. |')
            if line.startswith('| V2.2 controller evaluation |'):
                revised.append('| V2.3 development | 1,536 episodes | 128 standard + 64 longer routes '
                    '(56001/56002), two fixed policies, V2.2 and three candidates; all outcomes retained | '
                    'Corresponding original validation split and candidate records NR [pp. 15–16]. |')
                revised.append('| V2.3 final evaluation | 10,000 episodes | 500 standard + 500 longer fresh '
                    'routes (56012/56013), five fixed policies, V2.2 versus selected V2.3; all exactly replayed | '
                    'Corresponding original independent split and exact replay NR [pp. 15–20]. |')
        readme = '\n'.join(revised)
    write(p, readme)
    note = ['# V2.3 Signal Path Results and Reproduction', '', 'Date: 14 September 2026.', '',
        '## What Changed and Why', '',
        'The user asked to improve signal quality further. A separately versioned controller considers predicted SNR '
        'when choosing among near equal progress paths. It retains the V2.2 rollout machinery, network choice and '
        'all physical and mission requirements. The frozen protocol is note 58.', '',
        '## Development: Every Candidate', '',
        'These are selection data, not final improvement evidence. Each row uses its own common successful pairs. '
        'Differences are candidate minus V2.2. All development seeds and sample arrays are preserved.', '',
        '| Allowance / split | Successes V2.2 / candidate (higher is better) | SNR difference (dB, higher is better) | Delay difference (s, lower is better) | Handovers difference (lower is better) | Selection gate |',
        '| --- | --- | ---: | ---: | ---: | --- |']
    for arm, splits in selection['candidates'].items():
        for split, d in splits.items():
            m = d['metrics']
            note.append(f"| {arm.replace('signal_', '')} m / {split} | {d['baseline_successes']} / {d['candidate_successes']} of {d['episodes_per_arm']} | "
                f"{m['snr_mean_db']['difference']:+.3f} | {m['delay_proxy_mean_s']['difference']:+.3f} | "
                f"{m['handovers']['difference']:+.3f} | {'Pass' if d['selection_gate'] else 'Fail'} |")
    note += ['', f"Selected allowance: {selection['selected_allowance_m']} m. Larger allowances failed the completion first selection. "
        'The 3 m and 6 m standard time increases also exceed the declared 2% limit.', '',
        '## Final Result', '', verdict, '', *improvements, '', *completion_notes, '',
        '| Split / gate | Passed | Interpretation |', '| --- | --- | --- |']
    explanations = {'completion': 'Nonnegative point difference and interval lower bound above −1 pp.',
        'delay': 'Nonpositive point difference and upper bound below +0.05 s.',
        'handovers': 'Nonpositive point difference and upper bound below +0.25 switches per flight.',
        'time': 'Upper bound for candidate time minus 1.02 × baseline time below zero.',
        'energy': 'Upper bound for candidate energy minus 1.02 × baseline energy below zero.',
        'snr': 'SNR lower bound above 0.1 dB standard or zero longer.'}
    for split, d in ds.items():
        for gate, value in d['gates'].items():
            note.append(f'| {split} / {gate} | {value} | {explanations[gate]} |')
    note += ['', '## Every Policy Seed and Failure', '',
        '| Seed | Standard V2.2 / V2.3 successes, higher is better | Longer V2.2 / V2.3 successes, higher is better |',
        '| --- | --- | --- |']
    for i, seed in enumerate(study.old.SEEDS):
        cells = [' / '.join(str(s['groups'][a+'_'+sp]['per_seed_successes'][i]) for a in ('v22', 'signal'))+' of 500' for sp in ('test', 'longer_test')]
        note.append(f'| {seed} | '+' | '.join(cells)+' |')
    note += ['', '| Controller / split | All outcomes, lower failure counts are better | Mean sampled outage (s), lower is better |', '| --- | --- | --- |']
    for key, g in s['groups'].items():
        note.append(f"| {key} | "+'; '.join(f'{k}: {v}' for k, v in sorted(g['outcomes'].items()))+f" | {g['all_flight_mean_outage_s']:.4f} |")
    note += ['', 'Outage ends at the first failed sample and is censored, so it is not complete outage duration '
        'under continued operation. Success still requires zero sampled outage and no overflow.', '',
        '## Recorded Evaluation Runtime', '',
        '| Controller / split | Mean wall time per 500 route evaluation (s), lower is better under matched conditions |',
        '| --- | ---: |']
    for arm in ('v22', 'signal'):
        for split in ('test', 'longer_test'):
            times = [json.loads((study.BASE/'confirmatory'/f'{arm}_seed_{seed}'/(split+'.json')).read_text())['runtime_seconds'] for seed in study.old.SEEDS]
            note.append(f'| {arm} / {split} | {np.mean(times):.2f} |')
    note += ['', 'These times exclude model/map loading and the separate replay. Jobs ran concurrently on the '
        'same workstation; three early V2.2 records used three workers and the remaining jobs used six. '
        'CPU contention and scheduling differ, so these are workload records, not a controlled speed comparison '
        'or onboard latency estimate. The restart retained every completed record and reran its exact replay. '
        'The orchestration note and runtime package versions are saved in the analysis folder.', '',
        '## Complete Means and Sample Aggregates', '',
        'The following copy preserves the same numerical table as the README. All service rows are conditional on common success.', '']
    start = final.index('| Metric and preferred direction | Standard V2.2 / V2.3 | Difference, 95% interval | Longer V2.2 / V2.3 | Difference, 95% interval | Original thesis definition / comparability |')
    end = next(i for i in range(start+1, len(final)) if final[i] == '')
    note += final[start:end]
    note += ['', '## Reproduction and Existing Models', '',
        'Place the private unchanged map at `dataset/Barcelona_dataset_January.h5`. Its expected SHA256 is '
        '`d4630dd3a6c45419e12d0b60dd08473c4ffa4062ca4fab1decabecf2b992ea0d`. '
        'Use the five already committed full V2 checkpoints in '
        '`results/connectivity_experiment/confirmatory_v2/full_seed_2101/checkpoint.pt` through seed 2105. '
        'No extra model download or training is needed.', '',
        '```powershell',
        'python -m pytest -q',
        'python scripts/run_signal_guard_study.py --phase confirmatory --workers 3',
        'python scripts/analyze_signal_guard_study.py --phase confirmatory',
        'python scripts/build_signal_guard_report.py',
        'python scripts/audit_signal_guard_delivery.py',
        '```', '',
        'For a single route demonstration with the same controller and weights:', '',
        '```powershell',
        'python scripts/evaluate_signal_guard_controller.py --controller signal --seed 2101 --start 1000 1000 --goal 1800 1300 --output outputs/v23_custom',
        '```', '',
        'The command saves JSON episode metrics and NPZ sample arrays. It reports failure normally when a '
        'custom route fails the mission. A one route inference batch is a demonstration; the complete frozen '
        'runner above is used for exact original batch replay.', '',
        'The evaluator verifies existing records by replay and refuses to overwrite conflicting results. '
        'Development selection and freeze are already complete; do not rerun those phases to pick a new candidate. '
        'The frozen runner, analysis and protocol are archived under both source snapshot folders. '
        'A new experiment needs a new name, protocol and routes.', '',
        'For custom integration, load the ordinary full V2 `HybridPolicy`, decode its deterministic residual with '
        '`env.decode_residual`, and call `signal_guard_action(env, proposal, 1)` from '
        '`uav_joint_optimization.signal_guard`. Pass the returned motion and network action to the unchanged '
        '`ConnectivityBatch.step`. Observations and the action mask must come from that same environment state. '
        'The full executable loop is in `scripts/run_signal_guard_study.py`.', '',
        '## Limitations and Next Decision', '',
        'This is not an independent map test or newly trained network. Five fixed policies reuse the same route pools, '
        'so uncertainty resamples both policies and routes. Finite planning, static occupancy, sampled connectivity, '
        'ideal handovers and proxy energy still limit claims. Gains are conditional on common successes and additional '
        'map access. No inference about an actual correction to the original thesis or global SNR optimality follows.', '',
        'All 10,000 final episode records and all saved sample arrays matched exact replay. The complete implementation '
        'suite passed 100 tests. Runtime is measured with concurrent workstation batches, not as onboard latency. '
        'The next experiment should use independent maps or a declared controller component ablation, not retuning '
        'against these final routes.', '']
    # Relativize links in the copied metric table only when actual links are added.
    write(ROOT/'docs/59_signal_guard_results.md', '\n'.join(note))
    build_tex(s, selection)
    summary = verdict+' '+' '.join(improvements)
    path = ROOT/'docs/12_task_status.md'; text = path.read_text(encoding='utf-8')
    text = text.replace('Updated 14 September 2026 after the thesis metric recovery and V2.2 controller study.',
        'Updated 14 September 2026 after the separate V2.3 signal path study.')
    marker = '## Latest Signal Path Study'
    if marker in text:
        start = text.index(marker); end = text.index('\n## Earlier Study Status', start)
        text = text[:start]+marker+'\n\n'+summary+'\n\n[Complete results and reproduction](59_signal_guard_results.md).\n'+text[end:]
    else:
        index = text.index('\n\n', text.index('Updated '))+2
        text = text[:index]+marker+'\n\n'+summary+'\n\n[Complete results and reproduction](59_signal_guard_results.md).\n\n## Earlier Study Status\n\n'+text[index:]
    write(path, text)
    log = ROOT/'docs/13_logbook.md'; text = log.read_text(encoding='utf-8')
    heading = '## 2026-09-14: Further Signal Path Selection'
    if heading not in text:
        entry = ('\n\n'+heading+'\n\n'
            'Declared and tested 1, 3 and 6 m rollout progress allowances with the unchanged V2.2 system. '
            'All 1,536 development episodes were retained. Only 1 m qualified; larger candidates gained more '
            'SNR but lost standard completions. Source, selection and weights were frozen before the '
            '56012/56013 route set was generated. Both controllers then used five fixed full V2 policies '
            'on 500 standard and 500 longer routes, with all 10,000 final episodes and metric arrays exactly replayed.\n\n'
            +summary+'\n\n'
            'The implementation suite passes 100 tests. A single route command was checked on a custom '
            '854 m mission; that demonstration is not added to the final evidence. The same private '
            'dataset and all twenty released checkpoints remain unchanged. Notes 58–59 give the protocol, '
            'complete results, gates, failures and reproduction. No further tuning uses these final routes.\n')
        write(log, text+entry)


def build_tex(s, selection):
    ds = s['contrasts']; passed = s['combined_improvement_gate']
    tex = [r'\section{Signal Aware Path Selection}',
        r'We next tested a separately declared path selection rule, V2.3, retaining V2.2\textquotesingle s '
        r'five step rollouts, ten motion candidates, feasible strongest signal association and executed filter. '
        r'Outside 50 m of the goal, it chooses a higher predicted mean SNR path only within a fixed rollout '
        r'progress allowance and with no predicted increase in delay or handovers. No weights, reward, '
        r'RSS requirement or buffer limit change. SNR still follows the source Eq.~(8) '
        r'\cite[p.~10, Eq.~(8); p.~15, Table~3]{thesis}.',
        r'Development used 128 standard and 64 longer new routes (56001/56002), with fixed policies 2101 and 2102. '
        r'Allowances 1, 3 and 6 m were tested, totaling 1536 episodes including V2.2. Only 1 m qualified. '
        r'It preserved 252/256 standard and 122/128 longer completions while increasing matched mean SNR by '
        r'0.421/0.297 dB and reducing delay and handovers. Both larger allowances lost standard completions '
        r'and exceeded the 2\% standard time allowance; all candidates remain in note 59.',
        r'After freezing source and selection, we generated 500 standard and 500 longer routes (56012/56013). '
        r'Both controllers used all five unchanged full V2 policies, for 10000 final episodes. Every episode '
        r'and sample array replayed exactly. No tuning followed the final tests. The 1 m allowance applies to '
        r'predicted terminal progress within the same safety class, not total mission detour distance.']
    for split, label in (('test', 'Standard'), ('longer_test', 'Longer')):
        d = ds[split]; n = d['episodes_per_arm']
        tex.append(f"{label} completion is {100*d['baseline_successes']/n:.2f}\\% / "
            f"{100*d['candidate_successes']/n:.2f}\\% for V2.2/V2.3, difference "
            f"{d['success_difference_pp']:+.3f} percentage points, 95\\% interval {ci(d['success_ci95_pp'])}.")
    tex += [r'The combined claim requires nonnegative completion differences with interval lower bounds above '
        r'$-1$ percentage point in both splits; nonpositive delay and handover differences with upper bounds '
        r'below 0.05 s and 0.25 switches; and time and energy increases below 2\%. Subject to these gates, '
        r'the SNR lower bound must exceed 0.1 dB standard and zero longer. These are declared study margins, '
        r'not source requirements or proof of equal reliability. Intervals use 5000 crossed policy/route '
        r'bootstrap draws, seed 66000. Other metrics are descriptive and unadjusted.',
        r'\begin{table*}[!t]\centering\footnotesize',
        r'\caption{Fresh V2.2 / V2.3 means on common successful pairs. Brackets give 95\% intervals for V2.3 minus V2.2. Higher SNR and lower other quantities are preferable.}',
        r'\label{tab:v23metrics}', r'\begin{tabular}{lrrrr}\toprule',
        r'Metric & Standard & Difference interval & Longer & Difference interval\\\midrule']
    for label, key, scale in [('SNR (dB)', 'snr_mean_db', 1), ('Delay (s)', 'delay_proxy_mean_s', 1),
                             ('Handovers', 'handovers', 1), ('Flight time (s)', 'time_s', 1), ('Consumed energy (kJ)', 'energy_proxy_j', .001)]:
        cells = []
        for split in ('test', 'longer_test'):
            m = ds[split]['metrics'][key]
            cells += [f"{m['baseline_mean']*scale:.3f} / {m['candidate_mean']*scale:.3f}", ci(m['ci95'], scale)]
        tex.append(label+' & '+' & '.join(cells)+r'\\')
    tex += [r'\bottomrule\end{tabular}\end{table*}',
        f"There are {ds['test']['common_successes']} standard and {ds['longer_test']['common_successes']} longer common successful pairs. "
        r'Every failure remains in completion denominators. Note 59 reports SINR, interference, all failures, '
        r'sample medians and every policy seed.']
    verdict = ('V2.3 passes the combined gate, supporting an SNR improvement within the declared completion, service, time and energy margins.'
        if passed else 'V2.3 fails the combined gate and is not promoted over V2.2.')
    failed = [f"{sp.replace('_', ' ')} {gate}" for sp, d in ds.items() for gate, value in d['gates'].items() if not value]
    if failed:
        verdict += ' Failed gates: '+', '.join(failed)+'.'
    if (not passed and all(d['success_difference_pp'] < 0 and d['success_ci95_pp'][0] > -1
                          and d['success_ci95_pp'][0] <= 0 <= d['success_ci95_pp'][1] for d in ds.values())):
        verdict += (' Both completion intervals include zero and exclude a loss of one percentage point. '
                    'The conservative nonnegative point requirement fails; a completion decrease is not statistically resolved.')
    tex.append(verdict)
    # Keep the wide results table with its section after the preceding float flush.
    table_start = tex.index(r'\begin{table*}[!t]\centering\footnotesize')
    table_end = tex.index(r'\bottomrule\end{tabular}\end{table*}')
    table = tex[table_start + 1:table_end]
    table[0] = table[0].replace(r'\caption{', r'\captionof{table}{', 1)
    tex = ([r'\twocolumn[{', tex[0],
            r'\noindent\begin{minipage}{\textwidth}\centering\footnotesize']
           + table + [r'\bottomrule\end{tabular}\end{minipage}\vspace{1em}}]']
           + tex[1:table_start] + tex[table_end + 1:])
    write(ROOT/'paper/v23_followup.tex', '\n'.join(tex))
    concise = (f"The further signal path rule has mean SNR differences of "
        f"{ds['test']['metrics']['snr_mean_db']['difference']:+.3f}/{ds['longer_test']['metrics']['snr_mean_db']['difference']:+.3f} dB "
        f"versus V2.2 on 10000 fresh episodes, and {'passes' if passed else 'misses'} its declared combined gate.")
    write(ROOT/'paper/v23_conclusion.tex', concise+' This result does not establish dominance on every metric or superiority over the unavailable thesis agent.')
    write(ROOT/'paper/v23_abstract.tex', concise)
    seeds = [r'\par\noindent\begin{minipage}{\columnwidth}',
        r'\captionof{table}{Every fixed policy seed on fresh 56012/56013 routes. Entries are successful flights of 500; higher is better.}',
        r'\label{tab:v23seeds}\centering\footnotesize',
        r'\begin{tabular}{rcc}\toprule Seed & Standard V2.2 / V2.3 & Longer V2.2 / V2.3\\\midrule']
    for i, seed in enumerate(study.old.SEEDS):
        cells = [' / '.join(str(s['groups'][arm+'_'+split]['per_seed_successes'][i]) for arm in ('v22', 'signal')) for split in ('test', 'longer_test')]
        seeds.append(str(seed)+' & '+' & '.join(cells)+r'\\')
    seeds += [r'\bottomrule\end{tabular}', r'\end{minipage}\par\medskip']
    write(ROOT/'paper/v23_seed_table.tex', '\n'.join(seeds))


if __name__ == '__main__':
    main()
