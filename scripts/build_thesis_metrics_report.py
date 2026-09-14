"""Generate metric recovery notes, current README fragments and paper results."""
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT/'results/thesis_metrics_v22'
NAMES = {'original': 'V1.5 original reward', 'full': 'Full V2', 'service': 'V2.1 service',
         'guard': 'V2.2 guarded V2', 'straight_radio': 'Goal radio',
         'joint_mpc': 'Joint one step', 'joint_lookahead': 'Joint three step'}
METRICS = [('SNR (dB), higher is better', 'snr_mean_db', 1),
           ('All neighbor RSS power (µW), lower is better', 'neighbor_rss_power_mean_uw', 1),
           ('Remaining energy (kJ), higher is better', 'remaining_energy_kj', 1),
           ('Executed handovers, lower is better while preserving service', 'handovers', 1),
           ('Delay proxy (s), lower is better', 'delay_proxy_mean_s', 1),
           ('Flight time (s), lower is better', 'time_s', 1),
           ('SINR (dB), higher is better', 'sinr_mean_db', 1),
           ('Cochannel downlink interference (µW), lower is better', 'interference_mean_w', 1e6),
           ('Consumed energy (kJ), lower is better', 'energy_proxy_j', .001),
           ('Handovers per second, lower is better while preserving service', 'handovers_per_second', 1)]


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip()+'\n', encoding='utf-8')


def read_runs(arm, split, folder='confirmatory'):
    return [json.loads((BASE/folder/f'{arm}_seed_{seed}'/(split+'.json')).read_text())['episodes']
            for seed in range(2101, 2106)]


def interval_text(values, scale=1):
    return '['+', '.join(f'{v*scale:.3f}' for v in values)+']'


def interpretation(s):
    """Explicit interpretation of this completed study, guarded by its results."""
    cs = [s['contrasts']['guard_minus_full_'+sp] for sp in ('test', 'longer_test')]
    os = [s['contrasts']['guard_minus_original_'+sp] for sp in ('test', 'longer_test')]
    assert all(c['success_difference_ci95_pp'][0] > 0 for c in cs+os)
    assert all(c['delay_proxy_mean_s']['difference_ci95'][1] < 0 for c in cs+os)
    assert all(c['handovers']['difference_ci95'][0] > 0 for c in cs)
    assert all(c['energy_proxy_j']['difference_ci95'][0] > 0 for c in os)
    assert all(c[k]['difference_ci95'][0] <= 0 <= c[k]['difference_ci95'][1]
               for c in cs for k in ('energy_proxy_j', 'time_s'))
    delay_reduction = [100*(1-c['delay_proxy_mean_s']['left_mean']/c['delay_proxy_mean_s']['right_mean']) for c in cs]
    return [
        'For the declared completion first, then service priority, V2.2 is the preferred controller among the '
        'tested V2 variants in this simulator. It passes the primary completion criterion and reduces delay. '
        'This conclusion is about the complete supervised controller, including its extra lookahead computation.',
        f"Delay falls by {delay_reduction[0]:.1f}% on standard and {delay_reduction[1]:.1f}% on longer common successes. "
        f"SNR improves by {cs[0]['snr_mean_db']['difference']:.3f} and {cs[1]['snr_mean_db']['difference']:.3f} dB; "
        'SINR also improves, and both all neighbor power and cochannel interference decrease. SNR measures signal '
        'relative to noise alone; SINR also accounts for interfering transmitters. The neighbor sum is a map based '
        'equation proxy, not measured physical uplink interference.',
        f"The cost is more handovers than full V2: {cs[0]['handovers']['right_mean']:.3f} to {cs[0]['handovers']['left_mean']:.3f} "
        f"per standard flight and {cs[1]['handovers']['right_mean']:.3f} to {cs[1]['handovers']['left_mean']:.3f} per longer flight. "
        'These are executed station switches and therefore extra control overhead. Flight time and energy '
        'differences versus full V2 have intervals containing zero; we do not claim an energy saving.',
        f"Against the V1.5 original reward control on these same fresh routes, completion improves by "
        f"{os[0]['success_difference_pp']:.3f} points {interval_text(os[0]['success_difference_ci95_pp'])} standard and "
        f"{os[1]['success_difference_pp']:.3f} {interval_text(os[1]['success_difference_ci95_pp'])} longer. "
        'Delay, flight time, signal quality and handover count also improve on their common successes, but V2.2 '
        f"consumes {os[0]['energy_proxy_j']['difference']/1000:.3f} and {os[1]['energy_proxy_j']['difference']/1000:.3f} kJ more. "
        'It does not improve every objective. These secondary comparisons have unadjusted intervals, and V1.5 '
        'is our original reward control on V2, not the unavailable original thesis agent.']


def initial_metrics():
    result = {}
    for split in ('test', 'longer_test'):
        a = read_runs('original', split, 'initial_replay'); b = read_runs('full', split, 'initial_replay')
        common = [(x, y) for ar, br in zip(a, b) for x, y in zip(ar, br) if x['success'] and y['success']]
        assert len(common) == (925 if split == 'test' else 781)
        result[split] = {'common_success_pairs': len(common), 'metrics': {}}
        for key in ['snr_mean_db', 'neighbor_rss_power_mean_uw', 'remaining_energy_kj',
                    'literal_energy_score', 'literal_rss_sum_mean', 'handovers_per_second']:
            result[split]['metrics'][key] = {'original_mean': float(np.mean([x[key] for x, y in common])),
                                           'full_mean': float(np.mean([y[key] for x, y in common]))}
        result[split]['step_cdf_medians'] = {}
        for arm, runs in [('original', a), ('full', b)]:
            samples = {k: [] for k in ['snr_db', 'neighbor_rss_power_uw']}
            for i, (ar, br) in enumerate(zip(a, b)):
                keep = np.array([x['success'] and y['success'] for x, y in zip(ar, br)])
                with np.load(BASE/'initial_replay'/f'{arm}_seed_{2101+i}'/(split+'.npz')) as arrays:
                    for k in samples:
                        v = arrays[k][keep]; samples[k].extend(v[np.isfinite(v)].tolist())
            result[split]['step_cdf_medians'][arm] = {k: float(np.median(v)) for k, v in samples.items()}
    write(BASE/'analysis/initial_recovered_metrics.json', json.dumps(result, indent=2))
    return result


def plot_results(s):
    for split in ('test', 'longer_test'):
        full = read_runs('full', split); guard = read_runs('guard', split)
        pairs = [(a, b) for ar, br in zip(full, guard) for a, b in zip(ar, br) if a['success'] and b['success']]
        fig, axes = plt.subplots(2, 3, figsize=(10, 6.7), constrained_layout=True)
        colors = ['#335c9b', '#16836b']; names = ['Full V2', 'V2.2 guarded V2']
        fields = [('snr_mean_db', 'Flight mean SNR (dB)\nHigher is better'),
                  ('neighbor_rss_power_mean_uw', 'Flight mean neighbor RSS power (µW)\nLower is better'),
                  ('handovers', 'Handovers per flight\nLower is better with service'),
                  ('remaining_energy_kj', 'Remaining energy (kJ)\nHigher is better')]
        for ax, (key, label) in zip(axes.flat, fields):
            for index in range(2):
                values = np.sort([pair[index][key] for pair in pairs])
                ax.step(values, np.arange(1, len(values)+1)/len(values), where='post', color=colors[index], label=names[index])
            ax.set_xlabel(label, fontsize=10); ax.set_ylabel('Empirical CDF'); ax.set_ylim(0, 1)
            ax.grid(alpha=.25); ax.legend(fontsize=9)
        for ax, metric, label, scale in [(axes.flat[4], 'all_flight_mean_outage_s', 'Mean sampled outage, all flights (s)\nLower is better', 1),
                                        (axes.flat[5], 'success_rate', 'Joint mission success (%)\nHigher is better', 100)]:
            values = [s['groups'][arm+'_'+split][metric]*scale for arm in ('full', 'guard')]
            ax.bar(names, values, color=colors, width=.55)
            for i, value in enumerate(values):
                ax.text(i, value, f'{value:.3f}' if scale == 1 else f'{value:.2f}', ha='center', va='bottom', fontsize=9)
            ax.set_ylabel(label, fontsize=10); ax.grid(axis='y', alpha=.25)
            ax.set_ylim(0, 100 if scale == 100 else max(values)*1.25+.002)
        fig.suptitle(('Standard' if split == 'test' else 'Longer')+' fresh routes: 500 routes × 5 fixed policy seeds\n'
                     f'CDFs use {len(pairs)} common successful pairs; bars include all 2,500 flights per controller', fontsize=12)
        fig.savefig(BASE/'analysis'/f'metric_comparison_{split}.png', dpi=180)
        fig.savefig(BASE/'analysis'/f'metric_comparison_{split}.pdf', metadata={'CreationDate': None, 'ModDate': None})
        plt.close(fig)


def main():
    initial = initial_metrics()
    s = json.loads((BASE/'analysis/statistics.json').read_text())
    selection = json.loads((BASE/'development/selection.json').read_text())
    bounds = json.loads((BASE/'map_metric_bounds.json').read_text())
    primary = s['contrasts'].get('guard_minus_full_test')
    longer = s['contrasts'].get('guard_minus_full_longer_test')
    explanations = interpretation(s)
    verdict = ('The primary fresh comparison supports improved standard mission completion.'
               if s['primary_completion_improvement'] else
               'The primary fresh comparison does not establish improved standard mission completion.')
    recovery = ['# Recovered Thesis Metrics and Source Consistency Audit', '', 'Date: 14 September 2026.', '',
        'The README is the main result entry point. These measurements add to the unchanged initial '
        '53012/53013 flights. All 4,000 underlying V1.5/full V2 episodes replayed exactly before metrics were added; '
        'this is not new independent performance evidence.', '',
        '## Same Formula, Unresolved Source Figures', '',
        f"The native Operator 1 map has maximum RSS {bounds['maximum_stored_rss']} dBm. Source Eq. (8), "
        f"RSS + 112.41 - 9, therefore cannot exceed {bounds['maximum_eq8_snr_db']:.2f} dB anywhere in this map. "
        'Source Fig. 6/8 medians around 122-127 dB cannot follow from that equation, Table 3 noise values and this '
        'same dataset. This identifies an unresolved source inconsistency, not its coding cause '
        '[TFM, printed p. 10, Eq. (8); p. 15, Table 3; pp. 18, 20, Figs. 6, 8].', '',
        'The new all neighbor RSS power is a linear power interpretation of Eq. (9). It excludes the serving '
        'station and includes all other Operator 1 stations regardless of cochannel occupancy. The thesis labels '
        'the quantity uplink but does not specify how RSS powers are summed. Our metric is a source equation '
        'proxy, not a physical uplink estimate. The literal raw integer sum, including sentinel entries, is kept '
        'only as an arithmetic diagnostic. Missing serving paths (-128) produce no valid SNR sample; their '
        'sample count is recorded instead of interpreting the sentinel as signal power.', '',
        'Remaining energy is now reported in kJ under our V2 accounting. The literal source Eq. (10) score is '
        'also retained separately, initialized to 1000 with the printed plus electronics term and no timestep. '
        'It increases for every speed allowed by V2, including when stationary. It has no validated physical '
        'unit or meaningful better direction; it must not be compared with source remaining energy bars as '
        'a successful energy improvement [printed pp. 10, 15].', '',
        '## Added Initial Comparison Metrics', '',
        '| Metric and preferred direction | Standard V1.5 / full V2 | Longer V1.5 / full V2 | Original thesis definition |',
        '| --- | --- | --- | --- |']
    locators = {'snr_mean_db': 'SNR, printed p. 10, Eq. (8); noise values, p. 15, Table 3.',
                'neighbor_rss_power_mean_uw': 'Linear power interpretation of printed p. 10, Eq. (9); physical link direction remains uncalibrated.',
                'remaining_energy_kj': 'Our V2 energy accounting; source Eq. (10), p. 10, and Table 3, p. 15, do not define this physical metric.',
                'handovers_per_second': 'Explicit switches per second; source Figs. 6/8, pp. 18/20, have unspecified normalization.'}
    for label, key, scale in METRICS[:3]+[METRICS[-1]]:
        cells = [' / '.join(f"{initial[sp]['metrics'][key][arm+'_mean']*scale:.3f}" for arm in ('original', 'full'))
                 for sp in ('test', 'longer_test')]
        recovery.append('| '+label+' | '+' | '.join(cells)+' | '+locators[key]+' |')
    recovery += ['', 'These means use the original 925 standard and 781 longer common successful pairs. '
        'The raw archive also stores pooled step CDF medians separately in `analysis/initial_recovered_metrics.json`. '
        'Neither a per flight mean nor our declared pooled sample median silently reproduces unspecified source CDF aggregation.', '',
        '## What Was Done, Verified and Remains', '',
        'Added source SNR, all neighbor RSS power, remaining energy, explicit handover frequency and complete sample arrays. '
        'Preserved all original episode fields and source files. The missing physical uplink model and original handover '
        'normalization remain unresolved. A direct source agent comparison needs its implementation or validated raw records. '
        'The separately declared guard improvement is evaluated in note 53; it does not resolve those source ambiguities.']
    write(ROOT/'docs/52_recovered_thesis_metrics.md', '\n'.join(recovery))
    lines = ['# V2.2 Guard Results and Recovered Metrics', '', 'Date: 14 September 2026.', '', verdict, '',
        'The supervisor uses the existing full V2 weights, without new training or a changed reward. It changes '
        'action selection through finite lookahead. Development evaluated horizons 3, 5 and 8 on the same 96 '
        'validation routes with seed 2101. Full V2 completed 91/96; Goal radio 92/96. Guard totals were 90/96, '
        '92/96 and 92/96. The declared delay tie breaker selected horizon 5.', '',
        'Fresh tests use 500 standard and 500 longer routes, seeds 55012/55013, and five fixed policy seeds '
        'per learned arm. All mission and connectivity requirements remain V2. Results are separate from '
        '53012/53013 and 54012/54013. No controller change followed the fresh tests.', '',
        '| Controller | Standard success (%), higher is better | Longer success (%), higher is better | Episodes per split | Original thesis comparison |',
        '| --- | ---: | ---: | ---: | --- |']
    for arm, name in NAMES.items():
        if arm+'_test' in s['groups']:
            lines.append(f"| {name} | {100*s['groups'][arm+'_test']['success_rate']:.2f} | {100*s['groups'][arm+'_longer_test']['success_rate']:.2f} | {s['groups'][arm+'_test']['episodes']} | Comparable original joint success NR [printed pp. 16-20]. |")
    lines += ['', '## Matched Completion Contrasts', '',
        '| V2.2 minus reference: higher is better for V2.2 | Standard difference (pp), 95% interval | Longer difference (pp), 95% interval |',
        '| --- | --- | --- |']
    for arm in ('full', 'original', 'service', 'straight_radio', 'joint_mpc', 'joint_lookahead'):
        if primary:
            cs = [s['contrasts']['guard_minus_'+arm+'_'+sp] for sp in ('test', 'longer_test')]
            lines.append('| '+NAMES[arm]+' | '+' | '.join(f"{c['success_difference_pp']:+.3f} {interval_text(c['success_difference_ci95_pp'])}" for c in cs)+' |')
    lines += ['', 'The primary contrast is guarded versus full V2 standard completion. Intervals use 5,000 crossed '
        'seed/route bootstrap draws, seed 65000. Other contrasts are secondary and unadjusted for multiplicity. '
        'The five seeds represent reused learned policies, not five new supervisor training runs.', '',
        '## Service on Common Successful Pairs', '']
    if primary:
        for reference in ('full', 'original'):
            lines += ['### V2.2 versus '+NAMES[reference], '',
                '| Metric and preferred direction | Standard reference / V2.2 | Difference, 95% interval | Longer reference / V2.2 | Difference, 95% interval |',
                '| --- | --- | --- | --- | --- |']
            cs = [s['contrasts']['guard_minus_'+reference+'_'+sp] for sp in ('test', 'longer_test')]
            for label, key, scale in METRICS:
                cells = []
                for c in cs:
                    d = c[key]
                    cells += [f"{d['right_mean']*scale:.3f} / {d['left_mean']*scale:.3f}",
                              f"{d['difference']*scale:+.3f} {interval_text(d['difference_ci95'], scale)}"]
                lines.append('| '+label+' | '+' | '.join(cells)+' |')
            lines += ['', f"Common successes: {cs[0]['paired_success_count']} standard and {cs[1]['paired_success_count']} longer. "
                'All failures remain in the completion denominator. Different references have different common success subsets.', '']
    lines += ['## Failures and All Flight Outage', '',
        '| Controller / split | RSS failures, lower is better | Buffer failures, lower is better | Timeouts, lower is better | Other failures, lower is better | Mean sampled outage (s), lower is better |',
        '| --- | ---: | ---: | ---: | ---: | ---: |']
    for arm, name in NAMES.items():
        for sp in ('test', 'longer_test'):
            if arm+'_'+sp not in s['groups']: continue
            g = s['groups'][arm+'_'+sp]; f = g['failure_counts']
            lines.append(f"| {name} / {sp} | {f['connectivity']} | {f['buffer']} | {f['timeout']} | {f['energy']+f['boundary']} | {g['all_flight_mean_outage_s']:.4f} |")
    lines += ['', 'Lower counts and shorter outage are preferable, but the simulator terminates at the first violation. '
        'Outage duration is therefore censored and cannot reproduce a continuing source episode.', '',
        '## Every Fixed Policy Seed', '',
        '| Seed | V1.5 success standard / longer (%), higher is better | Full V2 success standard / longer (%), higher is better | V2.1 success standard / longer (%), higher is better | V2.2 success standard / longer (%), higher is better |',
        '| --- | --- | --- | --- | --- |']
    if primary:
        for i, seed in enumerate(range(2101, 2106)):
            cells = [' / '.join(f"{100*s['groups'][arm+'_'+sp]['per_seed_success_rates'][i]:.2f}" for sp in ('test', 'longer_test'))
                     for arm in ('original', 'full', 'service', 'guard')]
            lines.append(f'| {seed} | '+' | '.join(cells)+' |')
    lines += ['', 'Higher success is better in every seed column. The supervisor retains the same five full V2 weights.', '',
        '## Conclusions and Limits', '', verdict, '', *sum(([p, ''] for p in explanations), []),
        'SNR, remaining energy, all neighbor RSS power, handover distributions and all flight outage are now recorded. '
        'Source SNR figures exceed the maximum implied by its stated equation and this dataset; source energy and '
        'handover scaling remain unresolved. The all neighbor metric is an Eq. (9) proxy, not calibrated physical uplink. '
        'Any improvement here concerns the specified shared simulator and compared controllers, not a validated repair '
        'of the original agent. See note 52 for the source consistency audit.', '',
        'The next decision must follow the completion and service intervals, including regressions. Further tuning '
        'requires another declared protocol and untouched evaluation routes. No such extra tuning is included here.']
    write(ROOT/'docs/53_v22_guard_results.md', '\n'.join(lines))
    if primary:
        plot_results(s)
    # The README fragment is generated from the same verified values as the note.
    readme = ['## Recovered Thesis Metrics and V2.2 Controller Test', '',
        '**We now report SNR, remaining energy, all neighbor RSS power, handover distributions and all flight outage.** '
        'The all neighbor power is a declared linear interpretation of the thesis Eq. (9), not a calibrated physical '
        'uplink measurement. The original 4,000 V1.5/full V2 flights were replayed without changing any prior result; '
        'the source comparison further below now includes the recoverable metrics.', '',
        '**New controller test:** a five-step lookahead supervisor uses the existing full V2 policy weights. '
        'It changes motion/network action selection; there is no new PPO training or isolated reward change. '
        'Three declared horizons were tested on validation before selecting five steps. It retains the thesis RSS '
        'and buffer requirements through the unchanged V2 system. These results use '
        '**fresh 55012/55013 routes**, separate from the earlier tables.', '']
    start = lines.index('| Controller | Standard success (%), higher is better | Longer success (%), higher is better | Episodes per split | Original thesis comparison |')
    readme += lines[start:start+2+len(NAMES)] + ['', '**'+verdict+'**']
    if primary:
        readme += [f"V2.2 minus full V2 completion is {primary['success_difference_pp']:+.3f} percentage points "
            f"{interval_text(primary['success_difference_ci95_pp'])} on standard routes and "
            f"{longer['success_difference_pp']:+.3f} {interval_text(longer['success_difference_ci95_pp'])} on longer routes (95% intervals).", '',
            '| Recovered or service metric | Standard full V2 / V2.2 | Difference, 95% interval | Longer full V2 / V2.2 | Difference, 95% interval | Original thesis definition / comparability |',
            '| --- | --- | --- | --- | --- | --- |']
        locations = ['Eq. (8), printed p. 10. The source plotted SNR cannot follow from its stated inputs; see the bound below.',
            'Linear interpretation of Eq. (9), printed p. 10; source conversion/aggregation unverified. No physical uplink comparison.',
            'Our remaining energy under V2 accounting. Source Eq. (10), printed p. 10, has unresolved arithmetic and units.',
            'Source Figs. 6/8, printed pp. 18/20, have unknown count normalization; no numerical source comparison.',
            'Queue/rate in Eq. (4), printed p. 9; source numerical delay NR.',
            'Matched arrival time NR; source continues after arrival [printed p. 12, Sec. 5.2].',
            'Corresponding SINR NR; source reports SNR [printed p. 10, Eq. (8)].',
            'Corresponding cochannel downlink result NR [printed p. 10, Eq. (9)].',
            'V2 energy accounting. Source Eq. (10), printed p. 10, cannot be converted into this consumed energy metric.',
            'Explicit switches/flight duration. Source Figs. 6/8, printed pp. 18/20, do not specify this denominator.']
        for (label, key, scale), location in zip(METRICS, locations):
            cells = []
            for c in (primary, longer):
                d = c[key]; cells += [f"{d['right_mean']*scale:.3f} / {d['left_mean']*scale:.3f}",
                                     f"{d['difference']*scale:+.3f} {interval_text(d['difference_ci95'], scale)}"]
            readme.append('| '+label+' | '+' | '.join(cells)+' | '+location+' |')
        readme += ['', f"Service means use {primary['paired_success_count']} standard and {longer['paired_success_count']} longer common successful pairs. "
            'All failures count in mission success. Secondary intervals are descriptive and unadjusted for multiple comparisons.', '',
            '**Interpretation:**', '', *sum(([p, ''] for p in explanations), []),
            '| Controller | Standard RSS / buffer / timeout failures, lower is better | Longer RSS / buffer / timeout failures, lower is better | All flight mean outage standard / longer (s), lower is better | Original thesis comparison |',
            '| --- | --- | --- | --- | --- |']
        for arm, name in NAMES.items():
            gs = [s['groups'][arm+'_'+sp] for sp in ('test', 'longer_test')]
            fails = [' / '.join(str(g['failure_counts'][key]) for key in ('connectivity', 'buffer', 'timeout')) for g in gs]
            outages = ' / '.join(f"{g['all_flight_mean_outage_s']:.4f}" for g in gs)
            readme.append('| '+name+' | '+' | '.join(fails)+' | '+outages+' | Source outage bars are approximate; first failure counts NR [printed pp. 18, 20, Figs. 6/8]. |')
        readme += ['', 'These failure counts use 2,500 flights per learned arm and 500 per deterministic reference in each split. '
            'Energy and boundary failures are zero. Mean outage includes successful and failed flights, but is censored by '
            'termination at the first violation. It is not a full continuing episode outage duration.', '',
            '![New standard route metric comparisons](results/thesis_metrics_v22/analysis/metric_comparison_test.png)', '',
            '![New longer route metric comparisons](results/thesis_metrics_v22/analysis/metric_comparison_longer_test.png)', '']
    readme += ['**Source consistency finding:** the same dataset has maximum Operator 1 RSS of -25 dBm. '
        'With the thesis Eq. (8) and Table 3 noise settings, SNR cannot exceed **78.41 dB**. Its plotted medians '
        'around 122-127 dB therefore cannot be reproduced from the stated inputs. This is an unresolved source '
        'inconsistency, not evidence that our controller should aim for those numbers.', '',
        '[Recovered metrics and source audit](docs/52_recovered_thesis_metrics.md), '
        '[all new results, failures and policy seeds](docs/53_v22_guard_results.md), '
        '[declared protocol](docs/51_thesis_metrics_and_guard_protocol.md) and '
        '[model usage and reproduction](docs/54_thesis_metrics_reproduction.md).', '']
    write(BASE/'analysis/readme_fragment.md', '\n'.join(readme))
    if primary:
        build_tex(s, primary, longer, verdict, initial)


def build_tex(s, primary, longer, verdict, initial):
    tex = [r'\section{Thesis Metric Recovery and Guarded Control}',
        'We added passive SNR, all neighbor RSS power, remaining energy and handover frequency measurements. '
        'All 4,000 initial V1.5/full V2 episodes replayed with unchanged original fields. These added measurements '
        'are not independent new flights.',
        r'Source Eq.~(8) gives $\mathrm{SNR}=\mathrm{RSS}+112.41-9$ dB '
        r'\cite[p.~10, Eq.~(8); p.~15, Table~3]{thesis}. The same map has maximum Operator 1 RSS of '
        r'$-25$ dBm, so this expression cannot exceed 78.41 dB. The source plotted medians near 122--127 dB '
        r'\cite[pp.~18, 20, Figs.~6, 8]{thesis} cannot follow from these stated inputs. We do not infer the coding cause.',
        r'The source explicitly converts an initial noise value of $-174$ to $-112.41$ dBm '
        r'\cite[p.~14, Sec.~6.1; p.~15, Table~3]{thesis}. If that conversion were omitted in the plotted calculation, '
        r'subtracting 61.59 dB would give approximate median SNRs of 62.4/65.4 dB for equal PPO/greedy and '
        r'61.4/60.4/61.4 dB for delay/interference/handover policies. Note 57 records native image digitization '
        r'and a conservative $\pm1$ dB reading allowance. This is a conditional hypothesis, not a recovered '
        r'actual result: source code and raw figure data remain unavailable. Neither this correction nor '
        r'superiority over the source policies is established.',
        r'For Eq.~(9), we explicitly sum the linear RSS powers of all nonserving stations, without cochannel masking '
        r'\cite[p.~10, Eq.~(9)]{thesis}. This is a source equation proxy; it is not calibrated physical uplink. '
        r'We retain cochannel downlink interference separately. Remaining energy is $100-E_{\mathrm{used}}/1000$ kJ '
        r'under V2 accounting. The source recurrence adds electronics consumption, omits time, and labels capacity in kW '
        r'\cite[p.~10, Eq.~(10); p.~15, Table~3]{thesis}. Its literal score increases under the V2 speed cap and has '
        'no validated energy interpretation. Handovers use explicit counts and frequencies; source axis normalization remains unknown.',
        r'\subsection{Declared Supervisor and Fresh Tests}',
        'A new supervisor considers the existing full V2 PPO motion and nine shared motion primitives. It simulates '
        'each followed by goal/braking guidance, chooses admissible network options by feasibility then RSS and capacity, '
        'and ranks rollouts by failure avoidance, arrival and remaining distance. The shared A3 rule and executed '
        'filter remain active. It adds computation and known map access, not a reward intervention or new training.',
        'Guard horizons 3, 5 and 8 completed 90, 92 and 92 of 96 validation missions with policy seed 2101; '
        'full V2 completed 91. The declared completion and delay rule selected horizon 5. Source and parameters '
        'were then frozen before generating 500 new standard and 500 new longer routes with seeds 55012/55013. '
        'The five full V2 policies were reused under the supervisor; V1.5, V2.1 and deterministic references were '
        'also evaluated. No tuning followed the fresh tests.',
        r'\begin{table}[!t]\centering\small',
        r'\caption{Fresh 55012/55013 joint success (\%). Higher is better. Learned arms use 2,500 flights per split; references use 500.}',
        r'\begin{tabular}{lrr}\toprule Controller & Standard & Longer\\\midrule']
    for arm, name in NAMES.items():
        tex.append(f"{name} & {100*s['groups'][arm+'_test']['success_rate']:.2f} & {100*s['groups'][arm+'_longer_test']['success_rate']:.2f}"+r'\\')
    tex += [r'\bottomrule\end{tabular}\end{table}',
        verdict+f" V2.2 minus full V2 is {primary['success_difference_pp']:+.3f} percentage points, 95 percent interval "
        f"{interval_text(primary['success_difference_ci95_pp'])}, standard; longer is {longer['success_difference_pp']:+.3f} "
        f"{interval_text(longer['success_difference_ci95_pp'])}. Intervals use 5,000 crossed seed/route bootstrap draws, "
        'seed 65000; secondary intervals are descriptive and unadjusted. Five reused policy seeds are not five new supervisor training runs.',
        r'\begin{table*}[!t]\centering\small',
        r'\caption{Full V2 / V2.2 means on common successful fresh pairs. Brackets give 95\% intervals for V2.2 minus full V2.}',
        r'\begin{tabular}{lrrrr}\toprule Metric and preferred direction & Standard means & Difference interval & Longer means & Difference interval\\\midrule']
    for label, key, scale in METRICS[:8]:
        lab = label.replace('µW', r'$\mu$W').replace(', higher is better', r' $\uparrow$').replace(', lower is better while preserving service', r' $\downarrow$').replace(', lower is better', r' $\downarrow$')
        if key == 'neighbor_rss_power_mean_uw': lab = r'All neighbor RSS power ($\mu$W) $\downarrow$'
        if key == 'interference_mean_w': lab = r'Cochannel interference ($\mu$W) $\downarrow$'
        cells = []
        for c in (primary, longer):
            d = c[key]; cells += [f"{d['right_mean']*scale:.3f} / {d['left_mean']*scale:.3f}", interval_text(d['difference_ci95'], scale)]
        tex.append(lab+' & '+' & '.join(cells)+r'\\')
    tex += [r'\bottomrule\end{tabular}\end{table*}',
        f"Service comparisons contain {primary['paired_success_count']} standard and {longer['paired_success_count']} longer common successful pairs. "
        'Every failed mission remains in completion denominators. Higher SNR and remaining energy and lower delay, '
        'interference and flight time are preferable; fewer handovers must preserve service. Notes 52--54 retain '
        'all source diagnostics, seed outcomes, failure reasons and reproduction commands.',
        r'\begin{figure*}[!t]\centering\includegraphics[width=.97\textwidth]{../results/thesis_metrics_v22/analysis/metric_comparison_longer_test.pdf}',
        r'\caption{Longer fresh route metrics. CDFs compare per flight values on common successes; bars include all flights. '
        'SNR is a per flight mean, all neighbor power is the explicit source equation proxy, and remaining energy uses V2 accounting. '
        'Sampled outage ends at the first violation and is censored. These are not reconstructed source figure distributions.}',
        r'\end{figure*}']
    write(ROOT/'paper/v22_followup.tex', '\n'.join(tex))
    # Keep the outcome interpretation with the result section, before its figure.
    summary = (f"Delay decreases by {100*(1-primary['delay_proxy_mean_s']['left_mean']/primary['delay_proxy_mean_s']['right_mean']):.1f} percent "
        f"and {100*(1-longer['delay_proxy_mean_s']['left_mean']/longer['delay_proxy_mean_s']['right_mean']):.1f} percent on standard and longer common successes. "
        'SNR and SINR increase and both interference proxies decrease. Executed handovers increase, while energy and flight time '
        'differences versus full V2 have intervals containing zero. The guard meets the declared completion first and service '
        'priority in this simulator, at additional control and computation cost. Against the V1.5 control, it also improves '
        'completion and delay, but consumes more energy; complete secondary intervals are in note 53.')
    path = ROOT/'paper/v22_followup.tex'
    source = path.read_text(encoding='utf-8')
    source = source.replace(r'\begin{figure*}', summary+'\n'+r'\begin{figure*}', 1)
    write(path, source)
    write(ROOT/'paper/v22_conclusion.tex', 'The separate V2.2 supervisor study supports improved standard mission completion. '
          'It improves delay and signal quality at the cost of more handovers than full V2. '
          'The additional metrics expose unresolved source arithmetic and aggregation; '
          'they do not establish physical uplink performance or a reproduced repair of the original agent.')
    write(ROOT/'paper/v22_abstract.tex', f"A separate fixed weight lookahead supervisor has a fresh standard completion difference of "
          f"{primary['success_difference_pp']:+.3f} points {interval_text(primary['success_difference_ci95_pp'])} versus full V2. "+verdict)
    seeds = [r'\par\noindent\begin{minipage}{\columnwidth}',
             r'\captionof{table}{Every fixed policy seed on fresh 55012/55013 routes. Entries are standard / longer success percentages; higher is better. V2.2 reuses full V2 weights.}',
             r'\label{tab:v22seeds}\centering\footnotesize',
             r'\setlength{\tabcolsep}{3pt}',
             r'\begin{tabular}{rcccc}\toprule Seed & V1.5 & Full V2 & V2.1 & V2.2\\\midrule']
    for i, seed in enumerate(range(2101, 2106)):
        cells = [' / '.join(f"{100*s['groups'][arm+'_'+sp]['per_seed_success_rates'][i]:.1f}"
                           for sp in ('test', 'longer_test')) for arm in ('original', 'full', 'service', 'guard')]
        seeds.append(str(seed)+' & '+' & '.join(cells)+r'\\')
    seeds += [r'\bottomrule\end{tabular}', r'\end{minipage}\par\medskip']
    write(ROOT/'paper/v22_seed_table.tex', '\n'.join(seeds))


if __name__ == '__main__':
    main()
