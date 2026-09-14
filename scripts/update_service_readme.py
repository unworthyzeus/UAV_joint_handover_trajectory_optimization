"""Integrate the completed V2.1 followup without changing initial result tables."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def main():
    s=json.loads((ROOT/'results/service_reward_v21/analysis/statistics.json').read_text())
    p=ROOT/'README.md';text=p.read_text(encoding='utf-8')
    a=s['contrasts']['service_minus_full_test'];b=s['contrasts']['service_minus_full_longer_test']
    interval=lambda x:'['+', '.join(f'{v:.3f}' for v in x)+']'
    verdict=('The fresh standard comparison supports improved completion over full V2.' if s['primary_completion_improvement'] else
             'The fresh standard comparison supports lower completion than full V2.'
             if a['success_difference_ci95_pp'][1] < 0 else
             'The fresh standard comparison does not establish improved completion over full V2.')
    block=['## V2.1 Followup on Fresh Routes','',
        '**A new candidate was trained and tested with completion first, then service as the priority.** '
        'Three declared candidates and a fresh V2 pilot control were evaluated on validation routes. '
        'The service candidate completed 91/96 versus 90/96 for control; the stronger failure penalty candidates '
        'completed 87/96 and 89/96. The selected reward uses logarithmic delay cost, a queue fraction penalty and a '
        'smaller handover payment. Physical transitions, the safety filter and all mission requirements stay V2.', '',
        'The following results use **new seeds 54012 and 54013: 500 standard and 500 longer routes**, '
        'five training seeds per learned arm and 18,000 final episodes including references. '
        'They are separate from the 53012/53013 tables below; results from different test sets are not pooled.', '',
        '| Controller | New standard success | New longer success | Episodes per split | Original thesis comparison |',
        '| --- | ---: | ---: | ---: | --- |']
    names={'service':'V2.1 service','full':'Full V2','original':'Original reward V1.5',
           'straight_radio':'Goal radio','joint_mpc':'Joint one step','joint_lookahead':'Joint three step'}
    for arm,name in names.items():
        x=s['groups'][arm+'_test'];y=s['groups'][arm+'_longer_test']
        block.append(f"| {name} | {100*x['success_rate']:.2f}% | {100*y['success_rate']:.2f}% | {x['episodes']:,} | Comparable original joint success NR [printed pp. 16-20, Sec. 7/Figs. 5-8]; V1.5 is our reward control, not the source agent. |")
    block+=['',f"**{verdict}** "+('The candidate meets the declared completion and delay reporting gate. ' if s['primary_completion_and_delay_gate'] else
        'The candidate fails the declared completion first gate and is not promoted as the main model. ')+
        f"The primary V2.1 minus full V2 difference is {a['success_difference_pp']:+.3f} "
        f"percentage points, 95% interval {interval(a['success_difference_ci95_pp'])}. The longer difference is "
        f"{b['success_difference_pp']:+.3f} points {interval(b['success_difference_ci95_pp'])}. "
        +('The longer interval supports worse completion. ' if b['success_difference_ci95_pp'][1]<0 else '')+
        'An interval containing zero does not prove equivalence. The paired bootstrap uses 5,000 crossed seed/route draws.', '',
        '| Metric and preferred direction | New standard: full V2 / V2.1 | Paired difference, 95% interval | New longer: full V2 / V2.1 | Paired difference, 95% interval | Original thesis comparison |',
        '| --- | --- | --- | --- | --- | --- |']
    metrics=[('Flight time (s), lower','time_s',1,'Comparable mean arrival time NR; source continues after arrival [p. 12, Sec. 5.2].'),
             ('Delay proxy (s), lower','delay_proxy_mean_s',1,'Queue/rate defined [p. 9, Eq. (4)]; numerical delay results NR in Figs. 6 and 8 [pp. 18, 20].'),
             ('Handovers, lower with service','handovers',1,'CDF raw scale is not a mean executed count per successful flight [pp. 18, 20, Figs. 6, 8].'),
             ('Consumed energy (kJ), lower','energy_proxy_j',.001,'Source remaining energy bars labeled kW use a different model [p. 10, Eq. (10); pp. 18, 20].'),
             ('SINR (dB), higher','sinr_mean_db',1,'Source SNR and its CDF medians are not this metric [p. 10, Eq. (8); pp. 18, 20].')]
    for label,metric,scale,original in metrics:
        cells=[]
        for c in [a,b]:
            m=c[metric]
            cells += [f"{m['right_mean_on_common_success']*scale:.3f} / {m['left_mean_on_common_success']*scale:.3f}",
                      f"{m['paired_mean_difference']*scale:+.3f} {interval([v*scale for v in m['difference_ci95']])}"]
        block.append('| '+label+' | '+' | '.join(cells)+' | '+original+' |')
    block+=['',f"These service means use **{a['paired_success_count']} standard and {b['paired_success_count']} longer "
        'common successful pairs**. All failed flights still count in completion rates. Secondary intervals are descriptive '
        'and are not adjusted for multiple comparisons. Smaller delay does not imply fewer handovers, and a new '
        'reward is not an overall better controller unless the relevant metrics support that conclusion.', '',
        '[Every new result, failure count and seed](docs/48_service_reward_results.md), '
        '[all pilot outcomes](docs/47_service_reward_development.md), '
        '[frozen protocol](docs/46_service_reward_development_protocol.md) and '
        '[V2.1 model usage](docs/49_service_reward_models_and_reproduction.md) are retained. '
        'All 18,000 fresh evaluations replayed exactly. The implementation suite passed 88 tests. '
        'No additional candidate or training change followed these test outcomes.', '',
        '### What the New Reward Means','',
        'This followup tests a reward package with the same neural architecture and control system. '
        'It does not isolate each reward term, improve the propagation model, reproduce the source simulator '
        'or demonstrate performance in another city. The next research decision must follow the measured completion '
        'and service tradeoffs, not a requirement to produce a favorable conclusion.', '']
    if '## V2.1 Followup on Fresh Routes' in text:
        start=text.index('## V2.1 Followup on Fresh Routes');end=text.index('## Main Differences from the Thesis',start)
        text=text[:start]+'\n'.join(block)+'\n'+text[end:]
    else:
        text=text.replace('## Main Differences from the Thesis','\n'.join(block)+'\n## Main Differences from the Thesis',1)
    text=text.replace('## Current Conclusion','## Initial V1.5 Versus V2 Conclusion',1)
    text=text.replace('All current results use **fresh test seeds 53012 and 53013**',
                      'Results in this initial comparison use **test seeds 53012 and 53013**',1)
    text=text.replace('## Conclusions and Revised Diagnosis\n\n',
        '## Conclusions and Revised Diagnosis\n\nThe following conclusions concern the initial 53012/53013 comparison. '
        'The V2.1 followup above has its own fresh results and interpretation.\n\n',1)
    text=text.replace('**Current study: V2, with V1.5 as the original reward control on the same system.**',
        '**V2 and its V1.5 original reward control, with a completed V2.1 service reward followup.**',1)
    old='A clone includes source, configuration, results and **all 15 final checkpoints**:\nfive original reward V1.5, five full V2 and five arrival V2. Total size is about\n2.05 MB.'
    new='A clone includes source, configuration, results and **all 20 final checkpoints**:\nfive original reward V1.5, five full V2, five arrival V2 and five service V2.1.\nTheir combined size is about **2.74 MB**. The initial fifteen remain in their\noriginal manifest; [the V2.1 manifest](models/service_reward_manifest.json) adds\nfive final policies and their hashes.'
    assert old in text
    text=text.replace(old,new,1)
    text=text.replace('lists every path, size and SHA256. Checkpoints contain policy tensors',
        'lists the initial fifteen paths, sizes and SHA256 values; the V2.1 manifest\nlists the additional five. Checkpoints contain policy tensors',1)
    marker='The [complete guide](docs/35_dataset_and_model_setup.md) covers absolute paths,\nchecksum verification, splits, environment installation and troubleshooting.\n'
    addition='''
For a V2.1 checkpoint, use its dedicated evaluator and a fresh output prefix:

```powershell
python scripts/evaluate_service_reward_controller.py --checkpoint results/service_reward_v21/confirmatory/service_seed_2101/checkpoint.pt --split validation --output outputs/service_validation_01
```

The [V2.1 guide](docs/49_service_reward_models_and_reproduction.md) explains its
500 route test splits, custom flights and complete reproduction under a new label.
'''
    assert marker in text
    text=text.replace(marker,marker+addition,1)
    text=text.replace('All three learned arms have the same 156 inputs; indices are zero based.',
        'V1.5, full V2, arrival V2 and V2.1 all have the same 156 inputs; indices are zero based.',1)
    oldrow='| `models/checkpoint_manifest.json` | All 15 published paths, sizes and SHA256 values |'
    text=text.replace(oldrow,'| `models/checkpoint_manifest.json` | The initial 15 published paths, sizes and SHA256 values |',1)
    row='| `models/service_reward_manifest.json` | Five additional V2.1 final weights, sizes and hashes | Our followup models; no original thesis weights are available [source PPO: p. 13, Sec. 5.3]. |\n'
    text=text.replace('| `src/uav_joint_optimization/` |',row+'| `src/uav_joint_optimization/` |',1)
    p.write_text(text,encoding='utf-8',newline='\n')
    print('Integrated the completed V2.1 comparison; initial numerical results retained.')


if __name__=='__main__':main()
