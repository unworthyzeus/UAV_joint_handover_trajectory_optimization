"""Render station context and communication diagnostics from verified saved traces."""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from matplotlib.ticker import MaxNLocator
import numpy as np

from run_reward_comparison import ROOT, digest

OUT = ROOT / "results/reward_comparison/analysis_v15"
STYLES = {
    "original": ("Original reward (V1.5)", "#987044", "-"),
    "full": ("Full reward (V2)", "#236da0", "--"),
    "straight_radio": ("Goal radio", "#2a8879", ":"),
}


def build_long_route_figures():
    record = json.loads((OUT / "long_route_illustration.json").read_text())
    assert record["selection_sha256"] == digest(ROOT / "configs/long_route_illustration_v15.json")
    assert record["statistics_sha256"] == digest(OUT / "statistics.json")
    assert record["exact_episode_matches"] == 600
    for row in record["arms"].values():
        assert row["record_sha256"] == digest(ROOT / row["record_path"])
        if row["checkpoint_path"]:
            assert row["checkpoint_sha256"] == digest(ROOT / row["checkpoint_path"])
    plt.rcParams.update({"font.size": 10, "pdf.fonttype": 42, "ps.fonttype": 42,
                         "axes.spines.top": False, "axes.spines.right": False})
    series = {arm: dict(zip(record["columns"], np.asarray(row["trace"]).T))
              for arm, row in record["arms"].items()}
    stations = np.asarray(record["station_positions_m"])
    start, goal = np.array(record["scenario"]["start"]), np.array(record["scenario"]["goal"])
    all_xy = np.concatenate([np.column_stack((d["x_m"], d["y_m"])) for d in series.values()] + [start[None], goal[None]])
    lower = np.maximum(all_xy.min(axis=0) - 180, 0)
    upper = np.minimum(all_xy.max(axis=0) + 180, [5000, 3500])
    # Equal physical scale on both axes; the zoom does not exaggerate lateral motion.
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.9), gridspec_kw={"width_ratios": [1.05, 1]})
    for ax in axes:
        ax.scatter(*stations.T, color="0.73", marker="^", s=25, zorder=1)
        for arm, d in series.items():
            _, color, linestyle = STYLES[arm]
            ax.plot(d["x_m"], d["y_m"], color=color, linestyle=linestyle, lw=1.8, zorder=3)
            changes = np.flatnonzero(np.diff(d["station_id"])) + 1
            ax.scatter(d["x_m"][changes], d["y_m"][changes], s=48, facecolors="none",
                       edgecolors=color, linewidths=1.3, zorder=4)
        ax.scatter(*start, color="black", marker="o", s=28, zorder=6)
        ax.scatter(*goal, color="black", marker="*", s=90, zorder=6)
        ax.set(xlabel="Local x (m)", ylabel="Local y (m)")
        ax.grid(alpha=.18)
        ax.set_aspect("equal", adjustable="box")
    axes[0].set(xlim=(0, 5000), ylim=(0, 3500), title="(a) Full map and 87 base stations")
    axes[0].add_patch(Rectangle(lower, *(upper-lower), fill=False, edgecolor="0.4", linestyle=":"))
    axes[1].set(xlim=(lower[0], upper[0]), ylim=(lower[1], upper[1]), title="(b) Route detail and handover locations")
    axes[1].text(.5, -.43, "Paths largely overlap; circles mark association changes.\n"
                 "Axis scales are equal in both map panels.", transform=axes[1].transAxes,
                 ha="center", va="top", fontsize=9, color="0.3")
    handles = [Line2D([], [], color=color, linestyle=ls, lw=2, label=label)
               for label, color, ls in STYLES.values()]
    symbols = [Line2D([], [], color="0.73", marker="^", linestyle="none", label="Base station"),
               Line2D([], [], color="black", marker="o", linestyle="none", label="Start"),
               Line2D([], [], color="black", marker="*", linestyle="none", markersize=10, label="Goal"),
               Line2D([], [], color="0.25", marker="o", markerfacecolor="none", linestyle="none", label="Handover")]
    fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(.5, .085), ncol=3, frameon=False, fontsize=9)
    fig.legend(handles=symbols, loc="lower center", bbox_to_anchor=(.5, .015), ncol=4, frameon=False, fontsize=9)
    fig.suptitle("Longest declared test route: 1,784.7 m | Same start, goal and traffic", fontsize=12)
    fig.tight_layout(rect=(0, .20, 1, .96))
    for extension in ("pdf", "png"):
        fig.savefig(OUT / f"reward_comparison_example.{extension}", dpi=200)
    plt.close(fig)

    cfg = record["environment"]
    panels = [
        ("rss_dbm", "Serving RSS (dBm)", 1., cfg["rss_min_dbm"], "Minimum RSS", "line"),
        ("sinr_db", "SINR (dB)", 1., None, None, "line"),
        ("queue_bits", "Queue (kbit)", .001, cfg["buffer_bits"] * .001, "Buffer limit", "line"),
        ("capacity_bps", "Service capacity (Mbit/s)", 1e-6, cfg["offered_bps"] * 1e-6, "Offered traffic", "line"),
        ("handovers", "Cumulative handovers", 1., None, None, "step"),
        ("delay_proxy_s", "Delay proxy (s)", 1., None, None, "line"),
        ("energy_proxy_j", "Consumed energy proxy (kJ)", .001, None, None, "line"),
        ("interference_w", r"Interference ($\mu$W)", 1e6, None, None, "line"),
    ]
    fig, axes = plt.subplots(4, 2, figsize=(9, 9), sharex=True)
    max_time = max(d["time_s"][-1] for d in series.values())
    for letter, ax, (field, label, scale, reference, reference_label, kind) in zip("abcdefgh", axes.flat, panels):
        for arm, d in series.items():
            _, color, linestyle = STYLES[arm]
            kwargs = {"color": color, "linestyle": linestyle, "lw": 1.35}
            if kind == "step":
                ax.step(d["time_s"], d[field] * scale, where="post", **kwargs)
            else:
                ax.plot(d["time_s"], d[field] * scale, **kwargs)
            ax.plot(d["time_s"][-1], d[field][-1] * scale, marker="o", markersize=3, color=color)
        if reference is not None:
            ax.axhline(reference, color="0.3", linestyle=":", lw=1)
            ax.text(.99, reference, reference_label, transform=ax.get_yaxis_transform(),
                    ha="right", va="bottom", fontsize=8, color="0.25")
        ax.set_title(f"({letter}) {label}", loc="left", fontsize=10)
        ax.set_xlim(0, max_time + 2)
        ax.grid(alpha=.18)
        if field not in ("rss_dbm", "sinr_db"):
            ax.set_ylim(bottom=0)
        if field == "rss_dbm":
            ax.set_ylim(bottom=cfg["rss_min_dbm"] - 4)
        if field == "handovers":
            ax.yaxis.set_major_locator(MaxNLocator(integer=True))
            for arm, d in series.items():
                ax.annotate(f"{int(d[field][-1])}", (d["time_s"][-1], d[field][-1]),
                            xytext=(3, 3 if arm != "full" else -8), textcoords="offset points",
                            color=STYLES[arm][1], fontsize=8)
    for ax in axes[-1]:
        ax.set_xlabel("Time (s)")
    fig.legend(handles=handles, loc="upper center", bbox_to_anchor=(.5, .957), ncol=3, frameon=False, fontsize=9)
    fig.suptitle("Communication and energy along the same 1,784.7 m route", fontsize=12)
    fig.text(.5, .01, "Initial and executed samples at 1 s intervals; each curve stops at its episode endpoint.",
             ha="center", fontsize=9)
    fig.tight_layout(rect=(0, .025, 1, .91), h_pad=1.1)
    for extension in ("pdf", "png"):
        fig.savefig(OUT / f"reward_comparison_diagnostics.{extension}", dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    build_long_route_figures()
