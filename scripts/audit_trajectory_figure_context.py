"""Inspect saved example routes and add station context without rerunning policies."""
import json
from pathlib import Path

import h5py
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "results/reward_comparison/confirmatory_v15"
OUT = ROOT / "results/reward_comparison/analysis_v15"


def main():
    arms = [("original", "Original reward (V1.5)", "#987044", "-"),
            ("full", "Full reward (V2)", "#236da0", "--"),
            ("straight_radio", "Goal radio", "#2a8879", ":")]
    report = {"scope": "Saved first example only; no new policy evaluation", "arms": {}}
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.7))
    with h5py.File(ROOT / "dataset/Barcelona_dataset_January.h5", "r") as f:
        indices = np.flatnonzero(f["BS/operator_map"][0] == 1)
        positions = f["BS/position"][...][:2, indices].T
        identifiers = f["BS/id"][...][indices].astype(int)
        dx = float(np.diff(f["grid/x"][...].ravel()[:2])[0])
        dy = float(np.diff(f["grid/y"][...].ravel()[:2])[0])
        report["operator_1_station_count"] = len(indices)
        report["map_extent_m"] = [5000, 3500]
        for ax in axes:
            ax.scatter(*positions.T, marker="^", color="0.72", s=28,
                       label="Operator 1 base stations", zorder=1)
        serving = set()
        common_route = None
        for arm, label, color, linestyle in arms:
            relative = f"{arm}_seed_2101/test.json" if arm != "straight_radio" else f"{arm}_test.json"
            saved = json.loads((BASE / relative).read_text())
            trace = np.asarray(saved["traces"][0])
            route, episode = saved["scenarios"][0], saved["episodes"][0]
            if common_route is not None:
                assert route == common_route
            common_route = route
            station = trace[:, 3].astype(int)
            serving.update(station.tolist())
            rss = [float(f["measurements/rss_dBm"][int(indices[k]),
                         int(np.clip(np.rint(row[0] / dx), 0, 4999)),
                         int(np.clip(np.rint(row[1] / dy), 0, 3499))])
                   for row, k in zip(trace, station)]
            assert min(rss) >= -96 and episode["outcome"] == "success"
            report["arms"][arm] = {
                "source": str((BASE / relative).relative_to(ROOT)).replace("\\", "/"),
                "global_station_ids": np.unique(identifiers[station]).tolist(),
                "rss_min_including_initial_dbm": min(rss), "rss_max_dbm": max(rss),
                "handovers": episode["handovers"], "time_s": episode["time_s"],
                "outcome": episode["outcome"], "final_buffer_bits": episode["final_buffer_bits"]}
            for ax in axes:
                ax.plot(trace[:, 0], trace[:, 1], color=color, linestyle=linestyle,
                        linewidth=2.1, label=label, zorder=3)
        report["scenario"] = common_route
        report["straight_distance_m"] = float(np.linalg.norm(
            np.array(common_route["goal"]) - common_route["start"]))
        for ax in axes:
            ax.scatter(*positions[sorted(serving)].T, marker="^", color="#af532d",
                       s=75, label="Serving station (ID 29)", zorder=4)
            ax.scatter(*common_route["start"], color="black", s=25, marker="o", label="Start", zorder=5)
            ax.scatter(*common_route["goal"], color="black", s=85, marker="*", label="Goal", zorder=5)
            ax.set(xlabel="Local x (m)", ylabel="Local y (m)")
            ax.set_aspect("equal", adjustable="box")
            ax.grid(alpha=.15)
        assert np.array_equal(identifiers[sorted(serving)], [29])
        axes[0].set(xlim=(0, 5000), ylim=(0, 3500), title="All 87 selected base stations")
        axes[0].add_patch(Rectangle((4250, 1750), 750, 750, fill=False, edgecolor="0.35", linestyle=":"))
        axes[1].set(xlim=(4250, 5000), ylim=(1750, 2500), title="Example route and surrounding stations")
    handles, labels = axes[1].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=4, fontsize=8.5, frameon=False)
    fig.suptitle("First declared test route: 222 m; no handovers for these three controllers", fontsize=12)
    fig.tight_layout(rect=(0, .14, 1, .96))
    fig.savefig(OUT / "trajectory_station_context.png", dpi=180)
    plt.close(fig)
    (OUT / "figure_context_audit.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
