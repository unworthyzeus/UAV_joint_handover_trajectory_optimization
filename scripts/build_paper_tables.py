"""Populate the IEEE manuscript only from the validated positive experiment."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
s=json.loads((ROOT/"results/controlled_experiment/analysis_v1/statistics.json").read_text())
assert s["positive_gate_passed"], "The prespecified positive gate did not pass."
a=s["arms"]; c=s["contrasts"]["fixed_minus_legacy_test"]
macros={
    "LegacySuccess":100*a["legacy_test"]["success_rate"],
    "RewardOnlySuccess":100*a["reward_only_test"]["success_rate"],
    "FixedSuccess":100*a["fixed_test"]["success_rate"],
    "TerminationSuccess":100*a["terminal_only_test"]["success_rate"],
    "PrimaryGain":100*c["mean"], "CILower":100*c["lower"],"CIUpper":100*c["upper"],
    "RewardOnlyLongSuccess":100*a["reward_only_longer_test"]["success_rate"],
    "FixedLongSuccess":100*a["fixed_longer_test"]["success_rate"],
    "FixedLongSD":100*a["fixed_longer_test"]["seed_success_std"],
    "FixedFeasible":100*a["fixed_test"]["feasible_success_rate"],
    "PDSuccess":100*a["pd_test"]["success_rate"], "PDLongSuccess":100*a["pd_longer_test"]["success_rate"],
    "LegacyTime":a["legacy_test"]["successful_time_s"],
    "RewardOnlyTime":a["reward_only_test"]["successful_time_s"],
    "FixedTime":a["fixed_test"]["successful_time_s"],"PDTime":a["pd_test"]["successful_time_s"],
    "FixedMinusPDTime":s["fixed_minus_pd_matched_success_test"]["time_s"],
    "TrainingMinutes":s["training_wall_seconds"]/60,
}
(ROOT/"paper/results_macros.tex").write_text("% Generated from validated statistics; do not edit numbers manually.\n"+
    "\n".join(f"\\newcommand{{\\{k}}}{{{v:.1f}}}" for k,v in macros.items())+"\n",encoding="utf-8")
arms=[("legacy","Legacy"),("terminal_only","Termination only"),("reward_only","Reward only"),("fixed","Both")]
rows=[]
for arm,label in arms:
    x=a[f"{arm}_test"]; y=a[f"{arm}_longer_test"]
    rows.append(f"{label} & ${100*x['success_rate']:.1f}\\pm{100*x['seed_success_std']:.1f}$ & "
                f"${100*y['success_rate']:.1f}\\pm{100*y['seed_success_std']:.1f}$ & "
                f"${100*x['feasible_success_rate']:.1f}\\pm{100*x['seed_feasible_std']:.1f}$ & "
                f"${100*y['feasible_success_rate']:.1f}\\pm{100*y['seed_feasible_std']:.1f}$ & "
                f"{x['successful_episodes']}/1000 & {y['successful_episodes']}/1000 \\\\")
rows.append(f"Deterministic reference & {100*a['pd_test']['success_rate']:.1f} & {100*a['pd_longer_test']['success_rate']:.1f} & "
            f"{100*a['pd_test']['feasible_success_rate']:.1f} & {100*a['pd_longer_test']['feasible_success_rate']:.1f} & 200/200 & 200/200 \\\\")
table=r"""\begin{table*}[t]
\caption{Frozen results: percentages are mean $\pm$ standard deviation over five training seeds. Standard routes are 200--1000 m; longer routes are 1000--1800 m. Each learned policy evaluates 200 routes per split.}
\label{tab:results}\centering\footnotesize
\begin{tabular}{lcccccc}\toprule
 & \multicolumn{2}{c}{Mission success (\%)} & \multicolumn{2}{c}{Recorded feasible success (\%)} & \multicolumn{2}{c}{Successful episodes}\\
Treatment & Standard & Longer & Standard & Longer & Standard & Longer\\\midrule
"""+"\n".join(rows)+r"""
\bottomrule\end{tabular}
\end{table*}
"""
(ROOT/"paper/results_table.tex").write_text(table,encoding="utf-8")
rows=[]
for arm,label in arms+[("pd","Deterministic reference")]:
    r=a[f"{arm}_test"]; n=r.get("successful_episodes",200)
    vals=[]
    for key,scale in [("successful_time_s",1),("successful_energy_proxy_j",.001),("successful_handovers",1),
                      ("successful_sinr_mean_db",1),("successful_delay_proxy_mean_s",1),("successful_outage_s",1),
                      ("successful_interference_mean_w",1e6)]:
        v=r[key]; vals.append("n/a" if v is None else f"{v*scale:.2f}")
    rows.append(f"{label} & {n} & "+" & ".join(vals)+" \\\\")
table=r"""\begin{table*}[t]
\caption{Standard route metrics conditional on mission success, pooled across the five seeds. The deterministic reference has one run on 200 routes. Different successful subsets prevent unqualified secondary dominance claims. Energy, delay, and interference are the declared proxies.}
\label{tab:metrics}\centering\footnotesize
\begin{tabular}{lrrrrrrrr}\toprule
Treatment & $n$ & Time (s) & Energy (kJ) & Handovers & SINR (dB) & Delay (s) & Outage (s) & Interf. ($\mu$W)\\\midrule
"""+"\n".join(rows)+r"""
\bottomrule\end{tabular}
\end{table*}
"""
(ROOT/"paper/metrics_table.tex").write_text(table,encoding="utf-8")
print("Manuscript numbers generated from the validated positive result.")
