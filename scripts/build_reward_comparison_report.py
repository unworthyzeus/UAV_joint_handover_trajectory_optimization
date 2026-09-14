"""Generate current paper tables, figures and the Markdown result from saved data."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from run_reward_comparison import ROOT, SEEDS, ARMS, CONTROLLERS, digest
from build_long_route_figures import build_long_route_figures

OUT = ROOT / "results/reward_comparison/analysis_v15"
BASE = ROOT / "results/reward_comparison/confirmatory_v15"
PAPER = ROOT / "paper"
NAMES = {"original": "PPO original (V1.5)", "full": "PPO full (V2)", "arrival": "PPO arrival (V2)",
         "straight_rss": "Goal RSS", "straight_radio": "Goal radio", "joint_mpc": "Joint one step",
         "joint_lookahead": "Joint three steps"}


def ci(values, decimals=1):
    return "[" + ", ".join(f"{x:.{decimals}f}" for x in values) + "]"


def table(filename, caption, label, columns, header, rows, wide=False):
    kind = "table*" if wide else "table"
    placement = "!t" if wide else "t"
    text = [f"\\begin{{{kind}}}[{placement}]", f"\\caption{{{caption}}}", f"\\label{{{label}}}\\centering\\small",
            f"\\begin{{tabular}}{{{columns}}}\\toprule", " & ".join(header) + r"\\\midrule"]
    text += [" & ".join(map(str, row)) + r"\\" for row in rows]
    text += [r"\bottomrule\end{tabular}", f"\\end{{{kind}}}"]
    (PAPER / filename).write_text("\n".join(text)+"\n", encoding="utf-8")


def main():
    s = json.loads((OUT / "statistics.json").read_text())
    g,c = s["groups"],s["contrasts"]
    primary,longer = c["full_minus_original_test"],c["full_minus_original_longer_test"]
    positive = primary["success_difference_ci95_pp"][0] > 0
    negative = primary["success_difference_ci95_pp"][1] < 0
    conclusion = ("Full reward improves primary completion under this design." if positive else
                  "Full reward reduces primary completion under this design." if negative else
                  "The primary comparison does not establish improved completion from reward replacement.")
    macros = {"PrimaryDiff": f"{primary['success_difference_pp']:+.1f}", "PrimaryCI": "$"+ci(primary["success_difference_ci95_pp"])+"$",
              "LongDiff": f"{longer['success_difference_pp']:+.1f}", "LongCI": "$"+ci(longer["success_difference_ci95_pp"])+"$",
              "PairStd": str(primary["paired_success_count"]), "PairLong": str(longer["paired_success_count"]),
              "TestCount": "73", "ReplayCount": "7,600", "PrimaryAbstract": conclusion,
              "PrimaryInterpretation": conclusion + " An interval containing zero is not proof of equivalence.",
              "LongInterpretation": "The longer route interval also includes zero; its observed difference does not establish improvement.",
              "ConclusionResult": conclusion + " The full reward trades fewer handovers and shorter flights for higher delay, slightly higher proxy energy and lower SINR on common successful routes.",
              "ReferenceInterpretation": "Joint search has the highest observed longer completion on this route set, while Goal radio has the highest standard completion. These observed rankings are not a demonstrated overall superiority claim."}
    for arm,prefix in (("original","Original"),("full","Full"),("arrival","Arrival"),("straight_radio","Radio")):
        for split,suffix in (("test","Std"),("longer_test","Long")):
            macros[prefix+suffix] = f"{100*g[arm+'_'+split]['success_rate']:.1f}"
    for split,suffix in (("test","Std"),("longer_test","Long")):
        comparison=c['full_minus_arrival_'+split]
        macros['ArrivalDiff'+suffix]=f"{comparison['success_difference_pp']:+.1f}"
        macros['ArrivalCI'+suffix]="$"+ci(comparison['success_difference_ci95_pp'])+"$"
    macros["RadioInterpretation"] = (
        f"On standard common successes, accumulated radio cost changes by {primary['radio_cost_sum']['relative_difference_pct']:.1f}\\%, "
        f"while delay changes from {primary['delay_proxy_mean_s']['right_mean_on_common_success']:.2f} to {primary['delay_proxy_mean_s']['left_mean_on_common_success']:.2f} s. "
        f"Flight time changes by {primary['time_s']['paired_mean_difference']:.2f} s and handovers by {primary['handovers']['paired_mean_difference']:.2f}. "
        f"On longer common successes, delay changes from {longer['delay_proxy_mean_s']['right_mean_on_common_success']:.2f} to {longer['delay_proxy_mean_s']['left_mean_on_common_success']:.2f} s. "
        "Interference differences remain inconclusive on both splits.")
    (PAPER / "v15_macros.tex").write_text("\n".join(f"\\newcommand{{\\{k}}}{{{v}}}" for k,v in macros.items())+"\n",encoding="utf-8")
    arms=ARMS+CONTROLLERS
    rows=[[NAMES[a], f"{100*g[a+'_test']['success_rate']:.1f}",f"{100*g[a+'_longer_test']['success_rate']:.1f}","1,000" if a in ARMS else "200"] for a in arms]
    table("v15_results_table.tex", "Strict joint success on the new shared routes (percent).", "tab:jointresults", "lrrr",["Controller","Standard","Longer","Per split"],rows)
    failures=[]
    for arm in arms:
        cells=[]
        for split in ("test","longer_test"):
            f=g[arm+'_'+split]['failure_counts']
            assert f['energy']==f['boundary']==0
            cells.append(" / ".join(str(f[k]) for k in ("connectivity","buffer","timeout")))
        failures.append([NAMES[arm],*cells])
    table("v15_failure_table.tex", "First failures: RSS / buffer / timeout counts. No energy or boundary failures occurred.","tab:failures","lrr",["Controller","Standard","Longer"],failures)
    metrics=[("time_s","Flight time (s)",1), ("radio_cost_sum","Accumulated radio cost",1),
             ("delay_proxy_mean_s","Delay proxy (s)",1),("handovers","Handovers",1),
             ("interference_mean_w",r"Interference ($\mu$W)",1e6), ("energy_proxy_j","Energy proxy (kJ)",.001),
             ("sinr_mean_db","SINR (dB)",1),("path_m","Path length (m)",1),
             ("network_interventions","Network overrides",1),("motion_interventions","Motion overrides",1)]
    paired_rows=[]
    for split,comparison in (("Standard",primary),("Longer",longer)):
        for key,label,scale in metrics:
            v=comparison[key]
            paired_rows.append([split,label,f"{scale*v['right_mean_on_common_success']:.3f}",f"{scale*v['left_mean_on_common_success']:.3f}",
                                f"{scale*v['paired_mean_difference']:+.3f}","$"+ci([x*scale for x in v['difference_ci95']],3)+"$"])
    table("v15_paired_table.tex", f"Full minus original on {primary['paired_success_count']} standard and {longer['paired_success_count']} longer common successful pairs. Secondary intervals are descriptive and unadjusted.",
          "tab:paired","llrrrr",["Split","Metric","Original","Full","Difference","95\\% interval"],paired_rows,wide=True)
    seed_rows=[]
    for arm in ARMS:
        for i,seed in enumerate(SEEDS):
            seed_rows.append([NAMES[arm],seed,f"{100*g[arm+'_test']['per_seed_success_rates'][i]:.1f}",f"{100*g[arm+'_longer_test']['per_seed_success_rates'][i]:.1f}"])
    table("v15_seed_table.tex","Every learned seed on initial 53012/53013 routes: joint success percentages.","tab:seeds","lrrr",["Arm","Seed","Standard","Longer"],seed_rows)
    seed_file = PAPER / "v15_seed_table.tex"
    seed_file.write_text(seed_file.read_text().replace(r"\begin{table}[t]", r"\par\noindent\begin{minipage}{\columnwidth}").replace(r"\caption{", r"\captionof{table}{").replace(r"\end{table}", r"\end{minipage}\par"), encoding="utf-8")
    plt.rcParams.update({'font.size':10,'pdf.fonttype':42,'ps.fonttype':42,'axes.spines.top':False,'axes.spines.right':False})
    fig,axs=plt.subplots(1,2,figsize=(11,3.7),sharey=True)
    labels=['Original\nV1.5','Full\nV2','Arrival\nV2','Goal\nRSS','Goal\nradio','Joint\n1 step','Joint\n3 steps']
    colors=['#987044','#236da0','#88959f','#798674','#2a8879','#695d96','#b27b9d']
    for ax,split,title in zip(axs,['test','longer_test'],['Standard routes','Longer routes']):
        ax.bar(range(7),[100*g[a+'_'+split]['success_rate'] for a in arms],color=colors,width=.7)
        for j,arm in enumerate(ARMS):
            ax.scatter(j+np.linspace(-.18,.18,5),np.array(g[arm+'_'+split]['per_seed_success_rates'])*100,color='black',s=13,zorder=3)
        ax.set_xticks(range(7),labels); ax.set_ylim(0,102); ax.set_title(title); ax.grid(axis='y',alpha=.18); ax.set_axisbelow(True)
    axs[0].set_ylabel('Strict joint success (%)')
    fig.tight_layout(); fig.savefig(OUT/'reward_comparison_success.pdf'); fig.savefig(OUT/'reward_comparison_success.png',dpi=180); plt.close(fig)
    build_long_route_figures()
    lines=['# V1.5 Original Reward on V2: Results','', 'Date: 13 September 2026. All results below use the new route seeds 53012 and 53013.', '',
           '## Outcome','',conclusion,'',
           f"Standard full minus original completion: **{primary['success_difference_pp']:+.1f} percentage points**, 95% interval **{ci(primary['success_difference_ci95_pp'])}**. "
           f"Longer completion: **{longer['success_difference_pp']:+.1f} points {ci(longer['success_difference_ci95_pp'])}**. "
           'Neither interval establishes improved completion; this is not evidence of equivalence.','',
           'The full reward produces fewer handovers and faster completion on paired successful routes, but higher delay, slightly higher proxy energy and lower SINR. '
           'The original reward is not an ineffective navigation controller when it shares the V2 prior and filter. No overall learned superiority claim is supported.','',
           '## Joint Success','', '| Controller | Standard | Longer | Episodes per split |','| --- | ---: | ---: | ---: |']
    lines += ['| '+' | '.join(map(str,row))+' |' for row in rows]
    lines += ['', '## First Failure Counts','', '| Controller | Standard RSS / buffer / timeout | Longer RSS / buffer / timeout |','| --- | ---: | ---: |']
    lines += ['| '+' | '.join(row)+' |' for row in failures]
    lines += ['', 'No energy or boundary failures occurred. All reported successes satisfy sampled RSS, queue, time, position and speed criteria.', '',
              '## Matched Successful Flights','',f"The comparison uses {primary['paired_success_count']} standard and {longer['paired_success_count']} longer successful seed/route pairs. Failure rates remain unconditional above.", '',
              '| Split | Metric | Original | Full | Full minus original | 95% interval |','| --- | --- | ---: | ---: | ---: | --- |']
    lines += ['| '+' | '.join(str(x).replace('$','').replace('\\mu','micro') for x in row)+' |' for row in paired_rows]
    lines += ['', '## All Seeds','', '| Arm | Seed | Standard (%) | Longer (%) |','| --- | ---: | ---: | ---: |']
    lines += ['| '+' | '.join(map(str,row))+' |' for row in seed_rows]
    lines += ['', '## What Changed and Why','',
              'The user requested the original written reward with every other V2 component unchanged. Five new policies were trained with seeds 2101-2105 and 524,288 interactions each. '
              'All ten original final V2 weights were reused without selection and fixed by hash before the new run. The new 400 test routes are disjoint from prior saved routes; training and validation routes remain exactly V2.', '',
              'The wrapper changes only reward and accumulated raw return. The original formula retains the source equal weights, approach bonus, penalties and energy override [TFM, printed p. 12, Eqs. (13)-(14), Sec. 5.2; p. 15, Table 3]. '
              'Its 100 m/s reward threshold cannot activate under the shared 25 m/s cap; its RSS equality penalty is retained. Arrival termination, constraints and controller remain V2.', '',
              'The source freeze and analysis were declared in [note 36](36_v15_reward_comparison_protocol.md). The primary standard contrast uses 5,000 crossed seed/route bootstrap draws, seed 63000. Longer and other contrasts are secondary. '
              'Intervals are not adjusted for multiple secondary comparisons. Five training seeds limit uncertainty inference.', '',
              '## Verification, Limits and Next Decision','',
              'The implementation passed 73 tests, including transition identity and exact small PPO training equivalence. The final delivery audit records the exact replay and published checkpoint manifest. '
              'No implementation or hyperparameter was retuned after these results. Software checks do not validate the physical assumptions.', '',
              'The navigation prior and prospective filter are shared aids; the contrast does not isolate their effects or explain the original simulator. One map, static load, sampled connectivity, proxy service and energy remain limitations. '
              'Outstanding queue at arrival is allowed. A lower radio aggregate is not uniformly better service.', '',
              'The result closes the requested comparison, including its null primary finding. The next research decision is independent evaluation and separately frozen component ablations, not rewriting the reward until the present test looks favorable. '
              'See the [setup guide](35_dataset_and_model_setup.md) for released checkpoints and commands.']
    (ROOT/'docs/37_v15_reward_results.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps({'statistics_sha256':digest(OUT/'statistics.json'),'primary_positive':positive,'figures':3,'tables':4}))


if __name__ == '__main__':
    main()
