"""Build V2.1 Markdown and paper tables from the frozen fresh analysis."""
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'results/service_reward_v21'
METRICS=[('Flight time (s), lower','time_s',1),
         ('Delay proxy (s), lower','delay_proxy_mean_s',1),
         ('Handovers, lower with service','handovers',1),
         ('Consumed energy (kJ), lower','energy_proxy_j',.001),
         ('SINR (dB), higher','sinr_mean_db',1),
         ('Interference (µW), lower','interference_mean_w',1e6),
         ('Fixed V2 radio cost, lower','radio_cost_sum',1),
         ('Path length (m)','path_m',1),
         ('Queue at arrival (kbit), lower','final_buffer_bits',.001),
         ('Network filter interventions','network_interventions',1),
         ('Motion filter interventions','motion_interventions',1)]
NAMES={'service':'V2.1 service','full':'Full V2','original':'Original reward V1.5',
       'straight_radio':'Goal radio','joint_mpc':'Joint one step','joint_lookahead':'Joint three step'}


def write(path,text):
    path.write_text(text.strip()+'\n',encoding='utf-8',newline='\n')


def ci(values,scale=1,tex=False):
    if any(v is None for v in values): return 'not estimable'
    return '['+', '.join(f'{v*scale:.3f}' for v in values)+']'


def main():
    selection=json.loads((BASE/'development/selection.json').read_text())
    s=json.loads((BASE/'analysis/statistics.json').read_text())
    replay=json.loads((BASE/'replay/audit.json').read_text())
    assert replay['exact_episode_matches']==18000
    assert s['selected']=='service', 'Review the narrative if a different declared candidate is selected.'
    primary=s['contrasts']['service_minus_full_test']
    longer=s['contrasts']['service_minus_full_longer_test']
    improved=s['primary_completion_improvement']
    verdict=('The fresh standard comparison supports improved completion over full V2.' if improved else
             'The fresh standard comparison supports lower completion than full V2.'
             if primary['success_difference_ci95_pp'][1] < 0 else
             'The fresh standard comparison does not establish improved completion over full V2.')
    delay=primary['delay_proxy_mean_s']['paired_mean_difference']
    ho=primary['handovers']['paired_mean_difference']
    tradeoff=f"The standard paired delay difference is {delay:+.3f} s and the handover difference is {ho:+.3f}, conditional on common successes."
    long_verdict=('The longer route interval supports lower completion than full V2.'
                  if longer['success_difference_ci95_pp'][1] < 0 else
                  'The longer route completion contrast remains a secondary result.')
    development=['# V2.1 Development Results','Date: 14 September 2026.',
        'The four declared pilot policies were trained before any 54012/54013 evaluation. '
        'Each used seed 2199, 524,288 interactions, the same training pool and identical PPO settings. '
        'Selection used 64 standard and 32 longer validation routes. These are development results, not a final superiority test.',
        '| Candidate | Standard successes / 64 | Longer successes / 32 | Total / 96 | Matched delay difference versus control, standard / longer (s) |',
        '| --- | ---: | ---: | ---: | --- |']
    for name,d in selection['candidates'].items():
        a=d['summaries']['validation']; b=d['summaries']['validation_longer']; ds=d['matched_delay_differences']
        development.append(f"| {name} | {round(a['success_rate']*64)} | {round(b['success_rate']*32)} | {d['successes']} | {ds['validation']:+.3f} / {ds['validation_longer']:+.3f} |")
    development+=['',f"The selected candidate was **{selection['selected']}**, following the declared completion first rule. "
        'It achieved 91/96 successes versus 90/96 for control and reduced matched delay in both splits. '
        'The stronger failure penalty candidates achieved 87/96 and 89/96, so neither was advanced.',
        'The selected cost uses logarithmic delay weight 0.10, queue fraction squared weight 0.20, '
        'handover weight 0.03, the unchanged interference transform with weight 0.30, and failure penalty 20. '
        'No RSS shaping term was selected. It preserves every physical transition, action mask, filter and metric.',
        'All four pilot result folders, source snapshots, logs and checkpoint hashes are retained. Pilot weights remain local '
        'development artifacts and can be regenerated; the five final V2.1 checkpoints are published separately. '
        'After pilot completion, the runner gained a reproduction label option and a standalone inference CLI was included '
        'in the final source freeze. These packaging changes did not alter candidate rewards, training or selection. '
        'The original pilot source snapshot preserves the version actually used.',
        'The full implementation suite passed 88 tests, including 15 new reward adapter checks. '
        'The estimator is identical to V2 apart from the adapter import. All historical freezes were verified. '
        'A small validation gain is not evidence of a reliable population improvement; the next decision was the frozen fresh test.',
        'See note 46 for the prespecified gate and note 48 for the independent evaluation. '
        'The original thesis supplies no comparable joint success rate [printed pp. 16-20, Sec. 7/Figs. 5-8].']
    write(ROOT/'docs/47_service_reward_development.md','\n\n'.join(development[:3])+'\n\n'+'\n'.join(development[3:]))

    result=['# V2.1 Fresh Evaluation Results','Date: 14 September 2026.',verdict,tradeoff,
        'These results use **500 new standard and 500 new longer routes**, seeds 54012 and 54013. '
        'They are separate from every 53012/53013 result in the original reward comparison. '
        'Five V2.1 models were trained from scratch with seeds 2101-2105 and 524,288 interactions each. '
        'The ten V1.5 and full V2 controls were reused with their original hashes, the same training pool and per policy budget.',
        '| Controller | Standard success | Longer success | Evaluations per split | Original thesis comparison |',
        '| --- | ---: | ---: | ---: | --- |']
    for arm,name in NAMES.items():
        a=s['groups'][arm+'_test'];b=s['groups'][arm+'_longer_test']
        result.append(f"| {name} | {100*a['success_rate']:.2f}% | {100*b['success_rate']:.2f}% | {a['episodes']:,} | Comparable original joint success NR [printed pp. 16-20, Sec. 7]. |")
    result+=['','## Completion and Failure Counts','',
        '| Contrast: V2.1 minus reference | Standard difference (pp), 95% interval | Longer difference (pp), 95% interval |',
        '| --- | --- | --- |']
    for arm in ['full','original','straight_radio','joint_mpc','joint_lookahead']:
        a=s['contrasts']['service_minus_'+arm+'_test'];b=s['contrasts']['service_minus_'+arm+'_longer_test']
        result.append(f"| {NAMES[arm]} | {a['success_difference_pp']:+.3f} {ci(a['success_difference_ci95_pp'])} | {b['success_difference_pp']:+.3f} {ci(b['success_difference_ci95_pp'])} |")
    result+=['','Primary: V2.1 minus full V2 on standard routes. Crossed seed/route bootstrap uses 5,000 draws and seed 64000. '
        'Other contrasts and metric intervals are secondary and unadjusted for multiplicity. '
        'The deterministic comparator record is paired with each learned seed without counting those reused pairings as additional evaluations.',
        '', '| Arm / split | RSS failures | Buffer failures | Energy | Boundary | Timeout | Total failures |',
        '| --- | ---: | ---: | ---: | ---: | ---: | ---: |']
    for arm in NAMES:
        for split in ['test','longer_test']:
            f=s['groups'][arm+'_'+split]['failure_counts']
            result.append('| '+NAMES[arm]+' / '+split+' | '+' | '.join(str(f[k]) for k in ['connectivity','buffer','energy','boundary','timeout'])+f" | {sum(f.values())} |")
    for arm in ['full','original']:
        result+=['',f'## Conditional Service: V2.1 versus {NAMES[arm]}','',
            'Values below are means on common successful seed/route pairs. Each contrast has its own intersection; '
            'do not compare a reference mean from one intersection with a V2.1 mean from another.', '',
            '| Metric | Standard reference | Standard V2.1 | Difference, 95% interval | Longer reference | Longer V2.1 | Difference, 95% interval |',
            '| --- | ---: | ---: | --- | ---: | ---: | --- |']
        a=s['contrasts']['service_minus_'+arm+'_test'];b=s['contrasts']['service_minus_'+arm+'_longer_test']
        for label,metric,scale in METRICS:
            cells=[]
            for c in [a,b]:
                m=c[metric];cells += [f"{m['right_mean_on_common_success']*scale:.3f}",f"{m['left_mean_on_common_success']*scale:.3f}",
                                      f"{m['paired_mean_difference']*scale:+.3f} {ci(m['difference_ci95'],scale)}"]
            result.append('| '+label+' | '+' | '.join(cells)+' |')
        result+=['',f"Common successes: {a['paired_success_count']} standard and {b['paired_success_count']} longer pairs. "
            'Higher SINR is preferable; no SINR percentage change is computed. '
            'A shorter path or fewer interventions is not intrinsically better if it compromises service or mission success.']
    result+=['','## Every Training Seed','',
        '| Seed | V1.5 standard / longer | Full V2 standard / longer | V2.1 standard / longer |',
        '| --- | --- | --- | --- |']
    for i,seed in enumerate([2101,2102,2103,2104,2105]):
        vals=[]
        for arm in ['original','full','service']:
            vals.append(' / '.join(f"{100*s['groups'][arm+'_'+sp]['per_seed_success_rates'][i]:.2f}%" for sp in ['test','longer_test']))
        result.append(f"| {seed} | "+' | '.join(vals)+' |')
    result+=['','## Conclusion, Validation and Remaining Work','',verdict,long_verdict,tradeoff,
        'The failure breakdown explains why fewer overflows did not improve completion: standard RSS failures '
        'increase from 71 to 111 while buffer failures decrease from 6 to 2; longer RSS failures increase '
        'from 160 to 276 while buffer failures decrease from 39 to 4. Timeout counts stay unchanged. '
        'This identifies the recorded failure category, not the isolated causal contribution of switching or motion.',
        'V2.1 remains an evaluated research candidate. It is not promoted as a replacement for full V2 unless the '
        'declared completion and delay reporting gate is met. Lower delay alone does not satisfy the user\'s completion first priority.',
        f"The prespecified joint completion and delay reporting gate is **{'met' if s['primary_completion_and_delay_gate'] else 'not met'}**. "
        'A null completion result is not equivalence. Any service improvement is conditional on the declared common successes; '
        'it does not prove a better controller on every objective or improvement over the unavailable thesis simulator.',
        'All 18,000 final episodes replayed exactly. The five V2.1 checkpoint hashes were fixed before testing; '
        'the ten reused control checkpoint hashes and all historical freezes still match. '
        'No retraining, new candidate, checkpoint selection or test route selection followed test outcomes. '
        'The 88 implementation tests assess software behavior, not physical calibration.',
        'The next decision must respect completion first: retain unfavorable outcomes, investigate the shared control limits '
        'with a separately declared study, and reserve new evaluation data for any further tuning. '
        'The same map, static traffic, energy proxy, ideal switching and sampled connectivity limits remain. '
        'The original thesis results are still limited to its reported figures and definitions [printed pp. 16-21, Secs. 7-8].']
    write(ROOT/'docs/48_service_reward_results.md','\n\n'.join(result[:5])+'\n\n'+'\n'.join(result[5:]))

    tex=[r'\section{Completion First Service Reward Followup}',r'\label{sec:v21}',
        'After the initial comparison, we declared a separate V2.1 study to prioritize completion, then service. '
        'The full V2 delay cost is 0.318 at 1 s, 0.344 at 6 s and 0.347 at 10 s; '
        'a handover costs about 0.347. This saturation motivates a different reward, not a conclusion about trained performance.',
        r'\subsection{Development and Frozen Protocol}',
        'Four pilots used seed 2199 and 524,288 interactions each, with the same 64 standard and 32 longer validation routes. '
        'Full V2 completed 90/96 missions, the service candidate 91/96, and two candidates with stronger RSS, queue and '
        'failure penalties 87/96 and 89/96. The declared rule selected by completion first, then matched delay and handovers; '
        'advancement required no larger matched delay in either split. All candidates were retained.',
        'The selected service cost is',r'\begin{align}',
        r'C^{\mathrm{svc}}_t={}&0.10\log(1+D_t/(1\,\mathrm{s}))+0.20(q_t/Q)^2\nonumber\\',
        r'&+0.03H_t+0.30\frac{10^5I_t}{1+10^5I_t}.',r'\end{align}',
        'It replaces only the training radio cost; V2 potential shaping, time cost and terminal payments remain. '
        'One second is a normalization scale, not a packet deadline. The selected candidate has no RSS shaping term. '
        'Transitions, observations, actions, navigation aid, filter, PPO and mission requirements remain identical. '
        'The filter and all reported fixed radio costs continue to use the original V2 cost, preventing a hidden controller change.',
        'After selection, the source and coefficients were frozen. Five new policies used seeds 2101--2105 '
        'and 524,288 interactions each. They were compared with the five fixed V1.5 and five full V2 checkpoints '
        'on 500 new standard and 500 new longer routes, seeds 54012/54013. '
        'Goal radio and both joint search references were also evaluated. All 18,000 episodes replayed exactly. '
        'These routes are disjoint from prior saved routes but remain on the same map and within training distances.',
        r'The primary contrast is V2.1 minus full V2 standard success. A 95\% crossed seed/route interval '
        'uses 5,000 draws and seed 64000. A favorable completion claim requires its lower bound above zero; '
        'a claim of completion improvement without a delay regression additionally requires the paired delay '
        'interval upper bound at most zero. Other intervals are descriptive. No tuning followed the fresh tests.',
        r'\subsection{Fresh Results and Tradeoffs}',
        r'\begin{table}[t]\centering\small',
        r'\caption{V2.1 followup joint success on new 54012/54013 routes. Learned arms use 2,500 episodes per split; references use 500. Higher is preferable.}',
        r'\label{tab:v21success}',r'\begin{tabular}{lrr}\toprule Controller & Standard (\%) & Longer (\%)\\\midrule']
    for arm,name in NAMES.items():
        tex.append(f"{name} & {100*s['groups'][arm+'_test']['success_rate']:.2f} & {100*s['groups'][arm+'_longer_test']['success_rate']:.2f}\\\\")
    tex += [r'\bottomrule\end{tabular}\end{table}',
        f"Standard V2.1 minus full V2 is {primary['success_difference_pp']:+.3f} percentage points, interval "
        f"{ci(primary['success_difference_ci95_pp'])}. {verdict} On longer routes the difference is "
        f"{longer['success_difference_pp']:+.3f} points, interval {ci(longer['success_difference_ci95_pp'])}. {long_verdict}",
        r'\begin{table*}[!t]\centering\small',
        r'\caption{V2.1 minus full V2 on common successful fresh pairs. Values are means; intervals describe paired differences. Lower time, delay, handovers and consumed energy and higher SINR are preferable.}',
        r'\label{tab:v21paired}',
        r'\begin{tabular}{lrrlrrl}\toprule & \multicolumn{3}{c}{Standard} & \multicolumn{3}{c}{Longer}\\',
        r'Metric & Full V2 & V2.1 & 95\% difference interval & Full V2 & V2.1 & 95\% difference interval\\\midrule']
    for label,metric,scale in METRICS[:7]:
        lab=label.split(',')[0].replace('µW',r'$\mu$W')
        cells=[]
        for c in [primary,longer]:
            m=c[metric];cells += [f"{m['right_mean_on_common_success']*scale:.3f}",f"{m['left_mean_on_common_success']*scale:.3f}",ci(m['difference_ci95'],scale)]
        tex.append(lab+' & '+' & '.join(cells)+r'\\')
    tex += [r'\bottomrule\end{tabular}\end{table*}',
        f"The paired service comparison contains {primary['paired_success_count']} standard and "
        f"{longer['paired_success_count']} longer common successes. {tradeoff} "
        'A service improvement does not establish improved completion or simultaneous improvement in every radio metric. '
        'All failures remain in the success denominators.',
        'For standard V2.1 / full V2, first RSS failures are '+
        ' / '.join(str(s['groups'][a+'_test']['failure_counts']['connectivity']) for a in ['service','full'])+
        ' and first buffer failures are '+
        ' / '.join(str(s['groups'][a+'_test']['failure_counts']['buffer']) for a in ['service','full'])+
        '; for longer routes they are '+
        ' / '.join(str(s['groups'][a+'_longer_test']['failure_counts']['connectivity']) for a in ['service','full'])+
        ' and '+ ' / '.join(str(s['groups'][a+'_longer_test']['failure_counts']['buffer']) for a in ['service','full'])+
        ', respectively. Other failure types and every seed are retained in note 48.',
        'Against V1.5, standard completion differs by '+f"{s['contrasts']['service_minus_original_test']['success_difference_pp']:+.3f}"+
        ' points, interval '+ci(s['contrasts']['service_minus_original_test']['success_difference_ci95_pp'])+
        '. This is a comparison with the written original reward on V2, not the original thesis agent. '
        'Selection from a small validation set and only five final training seeds limit inference.']
    # Declare the wide result table early enough to share a page with the
    # followup text instead of being flushed onto an otherwise empty page.
    wide_start=tex.index(r'\begin{table*}[!t]\centering\small')
    wide_end=next(i for i in range(wide_start,len(tex)) if tex[i]==r'\bottomrule\end{tabular}\end{table*}')+1
    wide=tex[wide_start:wide_end]
    del tex[wide_start:wide_end]
    tex[2:2]=wide
    tex_source='\n\n'.join(tex)
    tex_source=re.sub(r'(\\begin\{(tabular|align)\}.*?\\end\{\2\})',
                      lambda m:m[0].replace('\n\n','\n'),tex_source,flags=re.S)
    write(ROOT/'paper/v21_followup.tex',tex_source)
    write(ROOT/'paper/v21_conclusion.tex',verdict+' '+long_verdict+' '+tradeoff)
    abstract=('A subsequent validation selected logarithmic delay reward was tested on 1,000 new shared routes with five seeds. '
              f"Its standard completion difference versus full V2 is {primary['success_difference_pp']:+.3f} points "
              f"{ci(primary['success_difference_ci95_pp'])}. "+verdict)
    write(ROOT/'paper/v21_abstract.tex',abstract)
    seed_tex=[r'\par\noindent\begin{minipage}{\columnwidth}',
        r'\captionof{table}{Every learned seed on fresh 54012/54013 routes. Entries are standard / longer joint success percentages.}',
        r'\label{tab:v21seeds}\centering\small',
        r'\begin{tabular}{rccc}\toprule Seed & V1.5 & Full V2 & V2.1\\\midrule']
    for i,seed in enumerate([2101,2102,2103,2104,2105]):
        cells=[' / '.join(f"{100*s['groups'][arm+'_'+sp]['per_seed_success_rates'][i]:.1f}"
                         for sp in ['test','longer_test']) for arm in ['original','full','service']]
        seed_tex.append(str(seed)+' & '+' & '.join(cells)+r'\\')
    seed_tex += [r'\bottomrule\end{tabular}',r'\end{minipage}\par\medskip']
    write(ROOT/'paper/v21_seed_table.tex','\n'.join(seed_tex))
    print(json.dumps({'primary_verdict':verdict,'primary_gate':s['primary_completion_and_delay_gate'],
                      'markdown':['docs/47_service_reward_development.md','docs/48_service_reward_results.md'],
                      'paper_inputs':['v21_followup.tex','v21_conclusion.tex','v21_abstract.tex','v21_seed_table.tex']}))


if __name__=='__main__': main()
