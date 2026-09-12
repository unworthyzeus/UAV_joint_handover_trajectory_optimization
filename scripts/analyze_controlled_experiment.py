"""Validate the frozen experiment and produce source backed tables and figures."""
import csv
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from uav_joint_optimization.experiment_ppo import summarize

ARMS = ["legacy", "terminal_only", "reward_only", "fixed"]
LABELS = {"legacy": "Legacy reward", "terminal_only": "Termination only",
          "reward_only": "Reward only", "fixed": "Reward + termination", "pd": "Deterministic reference"}
COLORS = {"legacy": "#B44435", "terminal_only": "#D89032", "reward_only": "#4A8395", "fixed": "#1B634B", "pd": "#3D3D3D"}
SEEDS = [1101, 1102, 1103, 1104, 1105]
RUNS = ROOT / "results" / "controlled_experiment" / "confirmatory_v1"
OUT = ROOT / "results" / "controlled_experiment" / "analysis_v1"


def paired_interval(difference, seed=73021, draws=10000):
    rng = np.random.default_rng(seed)
    ns, nr = difference.shape
    si = rng.integers(0, ns, (draws, ns))
    ri = rng.integers(0, nr, (draws, nr))
    samples = difference[si[:, :, None], ri[:, None, :]].mean(axis=(1, 2))
    return {"mean": float(difference.mean()), "lower": float(np.quantile(samples, .025)),
            "upper": float(np.quantile(samples, .975)), "draws": draws,
            "bootstrap_seed": seed, "seed_means": difference.mean(axis=1).tolist()}


def main():
    frozen = json.loads((ROOT / "configs/frozen_comparison_v1.json").read_text())
    for name, expected in frozen["source_hashes"].items():
        actual = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
        if actual != expected:
            raise AssertionError(f"Frozen source changed: {name}")
    OUT.mkdir(parents=True, exist_ok=True)
    episodes, seed_rows, validation = {}, [], []
    reference_ids = {}
    for arm in ARMS:
        for seed in SEEDS:
            folder = RUNS / f"{arm}_seed_{seed}"
            cfg = json.loads((folder / "config.json").read_text())
            assert cfg["ppo"] == frozen["ppo"] and cfg["environment"] == frozen["environment"]
            assert cfg["seed"] == seed and cfg["map_stride"] == 1
            assert cfg["reward"] == ("legacy" if arm in ["legacy", "terminal_only"] else "fixed")
            assert cfg["terminate_success"] == (arm in ["fixed", "terminal_only"])
            summary = json.loads((folder / "summary.json").read_text())
            assert summary["steps"] == frozen["ppo"]["steps"]
            validation.append({"arm": arm, "seed": seed, **summary})
            for split in ["test", "longer_test"]:
                rows = json.loads((folder / f"{split}.json").read_text())["episodes"]
                ids = [r["scenario_id"] for r in rows]
                assert len(ids) == len(set(ids)) == 200
                if split not in reference_ids:
                    reference_ids[split] = ids
                assert ids == reference_ids[split]
                assert all(r["time_s"] <= frozen["environment"]["horizon"] for r in rows)
                assert all(not r["success"] or (r["final_distance_m"] <= 10 and r["final_speed_mps"] <= 2) for r in rows)
                episodes[arm, seed, split] = rows
                seed_rows.append({"arm": arm, "seed": seed, "split": split, **summarize(rows)})
    statistics = {"scope": "Validated reimplementation, not original thesis replication", "arms": {}, "contrasts": {},
                  "seeds": SEEDS, "routes_per_split": 200, "frozen_source_hashes_verified": True,
                  "total_training_interactions": len(ARMS)*len(SEEDS)*frozen["ppo"]["steps"]}
    for split in ["test", "longer_test"]:
        matrices = {}
        for arm in ARMS:
            matrices[arm] = np.array([[r["success"] for r in episodes[arm, seed, split]] for seed in SEEDS], dtype=float)
            rates = matrices[arm].mean(axis=1)
            pooled = [r for seed in SEEDS for r in episodes[arm, seed, split]]
            feasible = np.array([[r["recorded_feasible_success"] for r in episodes[arm, seed, split]] for seed in SEEDS], dtype=float)
            statistics["arms"][f"{arm}_{split}"] = {**summarize(pooled), "seed_success_rates": rates.tolist(),
                "seed_success_std": float(rates.std(ddof=1)), "seed_feasible_rates": feasible.mean(axis=1).tolist(),
                "seed_feasible_std": float(feasible.mean(axis=1).std(ddof=1)),
                "successful_episodes": int(matrices[arm].sum()), "outcomes": dict(Counter(r["outcome"] for r in pooled)),
                "all_route_final_distance_median_m": float(np.median([r["final_distance_m"] for r in pooled]))}
        for name, a, b in [("fixed_minus_legacy", "fixed", "legacy"),
                            ("reward_only_minus_legacy", "reward_only", "legacy"),
                            ("terminal_only_minus_legacy", "terminal_only", "legacy"),
                            ("fixed_minus_reward_only", "fixed", "reward_only")]:
            statistics["contrasts"][f"{name}_{split}"] = paired_interval(matrices[a]-matrices[b])
        statistics["contrasts"][f"factorial_interaction_{split}"] = paired_interval(
            matrices["fixed"]-matrices["reward_only"]-matrices["terminal_only"]+matrices["legacy"])
        pd_rows = json.loads((RUNS / f"pd_{split}.json").read_text())["episodes"]
        assert [r["scenario_id"] for r in pd_rows] == reference_ids[split]
        statistics["arms"][f"pd_{split}"] = summarize(pd_rows)
        # Matched successful routes, avoiding claims from unlike successful subsets.
        differences = []
        for seed in SEEDS:
            for learned, reference in zip(episodes["fixed", seed, split], pd_rows, strict=True):
                if learned["success"] and reference["success"]:
                    differences.append({m: learned[m]-reference[m] for m in ["time_s", "energy_proxy_j", "handovers", "sinr_mean_db"]})
        statistics[f"fixed_minus_pd_matched_success_{split}"] = {"paired_episodes": len(differences),
            **{m: float(np.mean([r[m] for r in differences])) for m in differences[0]}}
    gate = frozen["positive_gate"]
    fixed = statistics["arms"]["fixed_test"]
    statistics["positive_gate_passed"] = bool(fixed["success_rate"] >= gate["standard_success_min"]
        and fixed["feasible_success_rate"] >= gate["standard_feasible_success_min"]
        and statistics["contrasts"]["fixed_minus_legacy_test"]["lower"] > 0)
    statistics["training_wall_seconds"] = sum(x["wall_seconds"] for x in validation)
    (OUT / "statistics.json").write_text(json.dumps(statistics, indent=2)+"\n", encoding="utf-8")
    with (OUT / "per_seed_summary.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(seed_rows[0])); writer.writeheader(); writer.writerows(seed_rows)
    plot_results(statistics)
    write_markdown(statistics, seed_rows)
    print(json.dumps(statistics, indent=2))


def plot_results(stats):
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "axes.spines.top": False,
                         "axes.spines.right": False, "pdf.fonttype": 42, "ps.fonttype": 42})
    fig, axes = plt.subplots(1, 2, figsize=(7.1, 2.8), sharey=True)
    for ax, split, title in zip(axes, ["test", "longer_test"], ["200–1000 m routes", "1000–1800 m routes"]):
        for i, arm in enumerate(ARMS):
            v = np.array(stats["arms"][f"{arm}_{split}"]["seed_success_rates"])*100
            ax.bar(i, v.mean(), color=COLORS[arm], alpha=.8, width=.65)
            ax.scatter(i+np.linspace(-.17,.17,5), v, s=17, edgecolor="white", linewidth=.5, color=COLORS[arm], zorder=4)
            ax.errorbar(i,v.mean(),yerr=v.std(ddof=1),color="black",capsize=3,lw=.8)
        ax.axhline(100*stats["arms"][f"pd_{split}"]["success_rate"], color=COLORS["pd"], ls=":", lw=1)
        ax.set_xticks(range(4), ["Legacy", "Termination\nonly", "Reward\nonly", "Both"])
        ax.set_title(title); ax.set_ylim(0,110); ax.grid(axis="y", alpha=.2); ax.set_axisbelow(True)
    axes[0].set_ylabel("Mission success (%)")
    fig.tight_layout()
    for ext in ["pdf", "png"]: fig.savefig(OUT / f"success_comparison.{ext}", dpi=200, bbox_inches="tight")
    plt.close(fig)
    fig, axes = plt.subplots(1, 2, figsize=(7.1, 2.7))
    for arm in ["legacy", "terminal_only", "reward_only", "fixed", "pd"]:
        p = RUNS / ("pd_test.json" if arm == "pd" else f"{arm}_seed_1101/test.json")
        record = json.loads(p.read_text()); trace = np.array(record["traces"][0]); scenario=record["scenarios"][0]
        axes[0].plot(trace[:,0],trace[:,1], color=COLORS[arm],label=LABELS[arm],lw=1.2)
        distances=np.linalg.norm(trace[:,:2]-scenario["goal"],axis=1)
        axes[1].plot(np.arange(len(trace)),distances,color=COLORS[arm],lw=1.2)
    start=np.array(scenario["start"]); goal=np.array(scenario["goal"])
    axes[0].scatter(*start, marker="o", color="black",s=18,zorder=8)
    axes[0].scatter(*goal, marker="*", color="black",s=55,zorder=8)
    axes[0].set_xlabel("x (m)"); axes[0].set_ylabel("y (m)"); axes[0].set_aspect("equal", adjustable="datalim")
    axes[1].set_xlabel("Time (s)"); axes[1].set_ylabel("Distance to destination (m)")
    axes[1].axhline(10,color="black",ls=":",lw=.6)
    for ax in axes: ax.grid(alpha=.2)
    fig.legend(*axes[0].get_legend_handles_labels(),loc="upper center",ncol=3,bbox_to_anchor=(.5,1.12),frameon=False)
    fig.tight_layout()
    for ext in ["pdf", "png"]: fig.savefig(OUT / f"example_trajectory.{ext}",dpi=200,bbox_inches="tight")
    plt.close(fig)
    fig,ax=plt.subplots(figsize=(3.45,2.4))
    for arm in ARMS:
        p=ROOT / "results/controlled_experiment/pilot_v2" / f"{arm}_seed_42/training_log.json"
        log=[r for r in json.loads(p.read_text()) if "validation_success" in r]
        ax.plot([r["steps"] / 1000 for r in log],[100*r["validation_success"] for r in log],
                marker="o",ms=3,label=LABELS[arm],color=COLORS[arm])
    ax.set(xlabel="Training interactions (thousands)",ylabel="Validation success (%)",ylim=(-3,103))
    ax.grid(alpha=.2); ax.legend(fontsize=6.5,frameon=False,loc="center right")
    fig.tight_layout()
    for ext in ["pdf","png"]: fig.savefig(OUT/f"pilot_learning.{ext}",dpi=200,bbox_inches="tight")
    plt.close(fig)


def write_markdown(stats, seed_rows):
    text=["# Confirmed Reward Experiment Results", "", "Date: 12 September 2026.", "",
        "## What Was Done and Why", "", "Completed the frozen four treatment, five seed experiment and verified source hashes, configurations, complete route pairing, and every successful episode's position and speed criteria. The purpose is to isolate reward and termination effects within the declared reimplementation.", "",
        "## Main Results", "", "| Arm | Standard success, mean ± seed SD | Longer success, mean ± seed SD | Standard recorded feasible success |", "| --- | --- | --- | --- |"]
    for arm in ARMS:
        a=stats["arms"][f"{arm}_test"]; b=stats["arms"][f"{arm}_longer_test"]
        text.append(f"| {LABELS[arm]} | {100*a['success_rate']:.1f}% ± {100*a['seed_success_std']:.1f} | {100*b['success_rate']:.1f}% ± {100*b['seed_success_std']:.1f} | {100*a['feasible_success_rate']:.1f}% |")
    p=stats["contrasts"]["fixed_minus_legacy_test"]
    text += ["",f"Primary paired difference: {100*p['mean']:.1f} percentage points, 95% crossed seed and route bootstrap interval [{100*p['lower']:.1f}, {100*p['upper']:.1f}]. There are five independent training seeds and 200 shared routes per split, not 1000 independent training runs.","",
        f"Prespecified practical positive gate passed: **{stats['positive_gate_passed']}**.","",
        "## Deterministic Reference and Limits", ""]
    for split in ["test","longer_test"]:
        pd=stats["arms"][f"pd_{split}"]; paired=stats[f"fixed_minus_pd_matched_success_{split}"]
        text.append(f"For {split}, the deterministic reference achieved {100*pd['success_rate']:.1f}% mission success. Across {paired['paired_episodes']} matched successful learned/reference episodes, the fixed policy used {paired['time_s']:.2f} s more time, {paired['energy_proxy_j']:.1f} J more proxy energy, and {paired['handovers']:.2f} more handovers on average. These signed differences are learned minus reference. They do not establish superiority to classical control.")
    text += ["", "Success conditional metrics for all methods and every training seed are in `per_seed_summary.csv`. Comparing secondary averages across different successful subsets is subject to selection bias. Detailed failure counts, downlink SINR, censored delay, energy proxy, interference, handovers, and bootstrap contrasts are in `statistics.json`.", "",
        "## Every Seed", "", "| Split | Arm | Seed | Mission success | Recorded feasible success |", "| --- | --- | --- | --- | --- |"]
    for r in seed_rows:
        text.append(f"| {r['split']} | {r['arm']} | {r['seed']} | {100*r['success_rate']:.1f}% | {100*r['feasible_success_rate']:.1f}% |")
    text += ["", "## Risks and Remaining Work", "", "The source simulator remains unavailable. These results use shared full observations, continuous motion, candidate masking, emergency handovers, deterministic traffic, a downlink interference proxy, and uncalibrated energy. They cannot be reported as reproducing or beating Marina's trained baseline. A single city and five seeds limit generalization and uncertainty estimates. No field or obstacle safety validation was performed.", "",
        "## Manuscript and Next Decision", "", "The positive result is documented in the IEEE research draft under `paper/`; see note 23 for its final audit. It includes the deterministic reference, all ablations, the private dataset dependency, and the distinction from original baseline reproduction. The raw shaping identity precedes PPO reward normalization and clipping; the experiment does not isolate those interactions. Next research should recover the original environment and test independent traffic and maps before claiming a broadly useful new control method.", ""]
    (ROOT/"docs/21_confirmed_results.md").write_text("\n".join(text),encoding="utf-8")


if __name__ == "__main__":
    main()
