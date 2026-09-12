"""Generate IEEE tables, macros and publication figures from verified results."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results/connectivity_experiment/analysis_v2"
PAPER = ROOT / "paper"


def main():
    d = json.loads((OUT / "report_statistics.json").read_text())
    audit = json.loads((ROOT / "results/connectivity_experiment/replay_v2/audit.json").read_text())
    assert audit["exact_episode_matches"] == d["total_evaluated_episodes"]
    g, contrasts = d["groups"], d["contrasts"]
    macros = {}
    for split, suffix in (("test", "Std"), ("longer_test", "Long")):
        p = contrasts[f"full_minus_arrival_{split}"]
        macros.update({f"Full{suffix}": 100*g[f"full_{split}"]["success_rate"],
                       f"Arrival{suffix}": 100*g[f"arrival_{split}"]["success_rate"],
                       f"SuccessDelta{suffix}": p["success_difference_pp"],
                       f"SuccessLow{suffix}": p["success_difference_ci95_pp"][0],
                       f"SuccessHigh{suffix}": p["success_difference_ci95_pp"][1],
                       f"CostChange{suffix}": p["radio_cost_sum"]["relative_difference_pct"],
                       f"DelayChange{suffix}": p["delay_proxy_mean_s"]["relative_difference_pct"],
                       f"HandoverChange{suffix}": p["handovers"]["relative_difference_pct"],
                       f"FullFailures{suffix}": sum(g[f"full_{split}"]["failure_counts"].values()),
                       f"Common{suffix}": p["paired_success_count"]})
    integers = [k for k in macros if k.startswith(("FullFailures", "Common"))]
    lines = ["% Generated from frozen connectivity statistics. Do not edit numbers manually."]
    for key, value in macros.items():
        number = str(int(value)) if key in integers else f"{value:.1f}"
        lines.append("\\newcommand{\\"+key+"}{"+number+"}")
    (PAPER / "connectivity_macros.tex").write_text("\n".join(lines)+"\n", encoding="utf-8")
    arms = ["arrival", "full", "straight_rss", "straight_radio", "joint_mpc", "joint_lookahead"]
    labels = ["PPO arrival", "PPO full", "Goal RSS", "Goal radio", "Joint one step", "Joint three steps"]
    table = [r"\begin{table}[!t]\centering", r"\caption{Joint success and successful standard mission cost. Learned rows aggregate five seeds on 200 routes; references use 200 routes.}",
             r"\label{tab:jointresults}", r"\begin{tabular}{lrrr}\toprule", r"Controller & Standard (\%) & Longer (\%) & $\sum C_t$\\\midrule"]
    for arm, label in zip(arms, labels):
        table.append(f"{label} & {100*g[arm+'_test']['success_rate']:.1f} & {100*g[arm+'_longer_test']['success_rate']:.1f} & {g[arm+'_test']['successful_radio_cost_sum']:.2f}"+r"\\")
    table.extend([r"\bottomrule\end{tabular}", r"\end{table}"])
    (PAPER / "connectivity_results_table.tex").write_text("\n".join(table)+"\n", encoding="utf-8")
    paired = [r"\begin{table*}[!t]\centering", r"\caption{Full minus arrival on paired successful missions. Differences and 95\% crossed bootstrap intervals. Negative cost, time, delay, interference and handover changes favor full.}",
              r"\label{tab:pairedradio}", r"\begin{tabular}{lrr}\toprule", r"Metric & Standard difference [95\% interval] & Longer difference [95\% interval]\\\midrule"]
    for key, label, scale in [("radio_cost_sum", r"Accumulated radio cost", 1), ("radio_cost_mean", r"Mean radio cost", 1),
                              ("time_s", r"Arrival time (s)", 1), ("delay_proxy_mean_s", r"Delay proxy (s)", 1),
                              ("interference_mean_w", r"Interference ($\mu$W)", 1e6), ("handovers", r"Handovers", 1),
                              ("sinr_mean_db", r"Mean SINR (dB)", 1)]:
        cells = []
        for split in ("test", "longer_test"):
            x = contrasts[f"full_minus_arrival_{split}"][key]
            low, high = x["difference_ci95"]
            cells.append(f"${scale*x['paired_mean_difference']:.3f}$ [$ {scale*low:.3f}, {scale*high:.3f} $]")
        paired.append(label + " & " + " & ".join(cells) + r"\\")
    paired.extend([r"\bottomrule\end{tabular}", r"\end{table*}"])
    (PAPER / "connectivity_paired_table.tex").write_text("\n".join(paired)+"\n", encoding="utf-8")
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "pdf.fonttype": 42, "ps.fonttype": 42,
                         "axes.spines.top": False, "axes.spines.right": False})
    colors = ["#7D8795", "#136F63", "#B7C2CC", "#4C78A8", "#D78B2E", "#8B5A91"]
    fig, axes = plt.subplots(1, 2, figsize=(7.1, 2.0), constrained_layout=True)
    short = ["PPO\narrival", "PPO\nfull", "Goal\nRSS", "Goal\nradio", "Joint\n1 step", "Joint\n3 steps"]
    for ax, split, title in zip(axes, ("test", "longer_test"), ("Standard routes: 200–1000 m", "Longer routes: 1000–1800 m")):
        values = [100*g[f"{a}_{split}"]["success_rate"] for a in arms]
        ax.bar(np.arange(6), values, color=colors, width=.7)
        for i, arm in enumerate(arms[:2]):
            seeds = g[f"{arm}_{split}"]["per_seed_success_rates"]
            ax.scatter(i+np.linspace(-.18,.18,len(seeds)), np.array(seeds)*100, s=13, color="#17212B", zorder=3)
        ax.set_xticks(np.arange(6), short, fontsize=8)
        ax.set_ylim(0, 106)
        ax.set_yticks([0, 25, 50, 75, 100])
        ax.set_title(title, fontsize=10)
        ax.set_ylabel("Joint mission success (%)")
        ax.grid(axis="y", alpha=.18)
        ax.set_axisbelow(True)
    for extension in ("pdf", "png"):
        fig.savefig(OUT / f"connectivity_success.{extension}", dpi=190)
    plt.close(fig)
    traces = ROOT / "results/connectivity_experiment/replay_v2"
    selected = [("full_seed_2101_test", "PPO full, seed 2101", colors[1]),
                ("straight_radio_test", "Goal radio", colors[3]), ("joint_lookahead_test", "Joint three steps", colors[5])]
    fig, axes = plt.subplots(1, 2, figsize=(7.1, 2.2), constrained_layout=True)
    for name, label, color in selected:
        raw = json.loads((traces / f"{name}.json").read_text())
        xy = np.array(raw["traces"][0])
        axes[0].plot(xy[:,1], xy[:,2], label=label, color=color, lw=1.7)
        axes[1].plot(xy[:,0], xy[:,6], label=label, color=color, lw=1.2, marker=".", markersize=2)
    route = raw["scenarios"][0]
    axes[0].scatter(*route["start"], color="black", marker="o", s=25, zorder=4)
    axes[0].scatter(*route["goal"], color="black", marker="*", s=70, zorder=4)
    axes[0].set(xlabel="x (m)", ylabel="y (m)", title="First standard route")
    axes[0].set_aspect("equal", adjustable="datalim")
    axes[0].legend(fontsize=7, loc="best")
    axes[1].axhline(-96, color="#B44343", linestyle="--", lw=1, label="RSS minimum")
    axes[1].set(xlabel="Elapsed time (s)", ylabel="Serving RSS (dBm)", title="Connection along the flight")
    axes[1].legend(fontsize=7, loc="best")
    for ax in axes:
        ax.grid(alpha=.18)
    for extension in ("pdf", "png"):
        fig.savefig(OUT / f"connectivity_example.{extension}", dpi=190)
    plt.close(fig)
    (OUT / "paper_inputs.json").write_text(json.dumps({"macros": macros, "exact_replayed_episodes": audit["exact_episode_matches"]}, indent=2)+"\n", encoding="utf-8")
    print("Generated paper macros, two tables, and two figures from verified frozen results.")


if __name__ == "__main__":
    main()
