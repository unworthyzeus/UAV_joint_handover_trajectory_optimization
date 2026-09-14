"""Integrate the current metric recovery and fresh controller results."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT/'results/thesis_metrics_v22'


def main():
    p = ROOT/'README.md'; text = p.read_text(encoding='utf-8')
    initial = json.loads((BASE/'analysis/initial_recovered_metrics.json').read_text())
    fragment = (BASE/'analysis/readme_fragment.md').read_text(encoding='utf-8')
    heading = '## Recovered Thesis Metrics and V2.2 Controller Test'
    if heading in text:
        start = text.index(heading); end = text.index('\n## ', start+len(heading))
        text = text[:start]+fragment+'\n'+text[end+1:]
    else:
        text = text.replace('## Initial V1.5 Versus V2 Conclusion', fragment+'\n## Initial V1.5 Versus V2 Conclusion', 1)
    text = text.replace('**V2 and its V1.5 original reward control, with a completed V2.1 service reward followup.**',
        '**V2 with its original reward control, the V2.1 reward study, and the V2.2 controller and thesis metric study.**')
    text = text.replace('[results and every seed](docs/37_v15_reward_results.md),',
        '[new controller results and every seed](docs/53_v22_guard_results.md),\n'
        '[initial reward comparison](docs/37_v15_reward_results.md),')
    start = text.index('| Outcome, unit and preferred direction |'); end = text.index('\n\n', start)
    table = text[start:end].splitlines(); revised = []
    added_names = ('| Mean SNR ', '| All neighbor RSS power ', '| Remaining energy under V2 ', '| Handover frequency ')
    def pair(key, split):
        d = initial[split]['metrics'][key]
        return f"{d['original_mean']:.3f} / {d['full_mean']:.3f}"
    for line in table:
        if line.startswith(added_names):
            continue
        if line.startswith('| Source SNR ') or line.startswith('| SNR sample CDF '):
            cells = line.split('|')
            cells[1] = ' SNR sample CDF median (dB): higher is better '
            for ix, split in [(4, 'test'), (5, 'longer_test')]:
                d = initial[split]['step_cdf_medians']
                cells[ix] = f" Pooled sample median {d['original']['snr_db']:.3f} / {d['full']['snr_db']:.3f} "
            cells[6] = (' Eq. (8) is now evaluated on our unchanged flights. Its maximum possible value on this map is '
                        '78.41 dB, below the source plotted medians. Source inputs or implementation are inconsistent; '
                        'its CDF aggregation is also unspecified [pp. 10, 15, 18, 20]. ')
            line = '|'.join(cells)
            revised.append(line)
            revised.append('| Mean SNR (dB): higher is better | NR as a per flight mean | NR as a per flight mean | '+
                pair('snr_mean_db', 'test')+' | '+pair('snr_mean_db', 'longer_test')+
                ' | Signal relative to noise alone, averaged per flight. This is distinct from a sample CDF median and from SINR. Same written Eq. (8), with the source figure inconsistency explained above. |')
            continue
        revised.append(line)
        if line.startswith('| Downlink interference (µW):'):
            revised.append('| All neighbor RSS power (µW): lower is better | NR as a verified linear sum | NR as a verified linear sum | '+
                pair('neighbor_rss_power_mean_uw', 'test')+' | '+pair('neighbor_rss_power_mean_uw', 'longer_test')+
                ' | Added linear power interpretation of source Eq. (9), including every nonserving Operator 1 station. Source conversion and aggregation are unverified. This proxy is not calibrated physical uplink. |')
        if line.startswith('| Consumed energy proxy (kJ):'):
            revised.append('| Remaining energy under V2 (kJ): higher is better | NR under this energy model | NR under this energy model | '+
                pair('remaining_energy_kj', 'test')+' | '+pair('remaining_energy_kj', 'longer_test')+
                ' | Added energy remaining from the shared 100 kJ budget. It is the complement of our consumed energy, not a conversion of the source energy display. |')
        if line.startswith('| Executed handovers '):
            revised.append('| Handover frequency (switches/s): lower is better while preserving service | NR with this denominator | NR with this denominator | '+
                pair('handovers_per_second', 'test')+' | '+pair('handovers_per_second', 'longer_test')+
                ' | Added executed handovers divided by actual flight duration, then averaged over common successes. Source normalization is unknown, so its fractional axis is not substituted here. |')
    text = text[:start]+'\n'.join(revised)+text[end:]
    text = text.replace('They have\nseparate rows: our uplink result is not evaluated and the source downlink\nresult is not reported.',
        'They have\nseparate rows: physical uplink remains unevaluated, while the explicit Eq. (9)\nlinear power proxy is now reported in its own row. The source cochannel\ndownlink result is not reported.')
    if 'For V2.2, use the existing full V2 weights' not in text:
        text = text.replace('## Exact Mission Definition and Source Pages',
            'For V2.2, use the existing full V2 weights through the new supervisor evaluator.\n'
            '**No additional model download or training is needed.**\n\n'
            '```powershell\n'
            'python scripts/evaluate_thesis_metrics_controller.py --controller guard --seed 2101 --split test --output outputs/v22_check\n'
            'python scripts/evaluate_thesis_metrics_controller.py --controller guard --seed 2101 --start 1000 1000 --goal 1800 1300 --output outputs/v22_custom\n'
            '```\n\n'
            'The [V2.2 reproduction guide](docs/54_thesis_metrics_reproduction.md) covers all controllers,\n'
            'custom coordinates, dataset placement, metric sample arrays and fresh output labels.\n\n'
            '## Exact Mission Definition and Source Pages', 1)
    if '| V2.2 controller evaluation |' not in text:
        row = '| Exact replay | 7,600 episodes | Every new record compared exactly | Exact replay count and record hashes NR [pp. 16-20, Secs. 6.3-7.2]. |'
        text = text.replace(row, row+'\n'
            '| V2.2 controller evaluation | 23,000 episodes | Separate 500 standard + 500 longer routes, seeds 55012/55013; four learned arms × five fixed seeds and three deterministic references; all exactly replayed | Original joint success and independently specified test split NR [pp. 15-20]. |\n'
            '| Initial metric recovery | 4,000 unchanged episodes | Added metrics on the original 53012/53013 V1.5/full V2 flights; no new independent observations | Source SNR and interference equations p. 10; plotted metrics pp. 18/20. |')
    p.write_text(text, encoding='utf-8')


if __name__ == '__main__':
    main()
