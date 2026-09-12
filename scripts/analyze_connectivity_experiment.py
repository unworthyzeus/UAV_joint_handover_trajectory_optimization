"""Paired analysis of the frozen connectivity experiment, including failures."""
import csv
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from uav_joint_optimization.connectivity_ppo import summarize

BASE = ROOT / "results/connectivity_experiment/confirmatory_v2"
OUT = ROOT / "results/connectivity_experiment/analysis_v2"


def interval(values, mask=None, seed=62000, draws=5000):
    """Crossed seed and route bootstrap; one seed row for deterministic pairs."""
    values = np.asarray(values, dtype=float)
    if mask is None:
        mask = np.ones_like(values, dtype=bool)
    rng = np.random.default_rng(seed)
    samples = []
    for _ in range(draws):
        si = rng.integers(values.shape[0], size=values.shape[0])
        ri = rng.integers(values.shape[1], size=values.shape[1])
        v, m = values[np.ix_(si, ri)], mask[np.ix_(si, ri)]
        if m.any():
            samples.append(float(v[m].mean()))
    return np.percentile(samples, [2.5, 97.5]).tolist() if samples else [None, None]


def contrast(left, right):
    assert len(left) == len(right)
    for a, b in zip(left, right):
        assert [r["scenario_id"] for r in a] == [r["scenario_id"] for r in b]
    ls = np.array([[r["success"] for r in run] for run in left])
    rs = np.array([[r["success"] for r in run] for run in right])
    common = ls & rs
    difference = ls.astype(float) - rs.astype(float)
    result = {"success_difference_pp": float(100 * difference.mean()),
              "success_difference_ci95_pp": [100 * x for x in interval(difference)],
              "paired_success_count": int(common.sum()), "paired_evaluations": int(common.size)}
    for metric in ("radio_cost_sum", "radio_cost_mean", "time_s", "delay_proxy_mean_s",
                   "interference_mean_w", "handovers", "energy_proxy_j", "sinr_mean_db", "path_m"):
        a = np.array([[r[metric] for r in run] for run in left])
        b = np.array([[r[metric] for r in run] for run in right])
        result[metric] = {"left_mean_on_common_success": float(a[common].mean()) if common.any() else None,
                          "right_mean_on_common_success": float(b[common].mean()) if common.any() else None,
                          "paired_mean_difference": float((a - b)[common].mean()) if common.any() else None,
                          "difference_ci95": interval(a - b, common),
                          "relative_difference_pct": float(100 * (a[common].sum() / b[common].sum() - 1))
                          if common.any() and b[common].sum() != 0 else None}
    return result


def main():
    frozen = json.loads((ROOT / "configs/frozen_connectivity_v2.json").read_text())
    for manifest in (frozen, json.loads((ROOT / "configs/frozen_comparison_v1.json").read_text())):
        for n, expected in manifest["source_hashes"].items():
            assert hashlib.sha256((ROOT / n).read_bytes()).hexdigest() == expected, n
    OUT.mkdir(parents=True, exist_ok=True)
    groups, per_run, data = {}, [], {}
    for split in ("test", "longer_test"):
        data[split] = {}
        for arm in frozen["arms"] + frozen["controllers"]:
            runs = []
            seeds = frozen["seeds"] if arm in frozen["arms"] else [None]
            for seed in seeds:
                p = BASE / (f"{arm}_seed_{seed}/{split}.json" if seed is not None else f"{arm}_{split}.json")
                rows = json.loads(p.read_text())["episodes"]
                assert len(rows) == 200
                for row in rows:
                    if row["success"]:
                        assert row["minimum_rss_dbm"] >= -96 and row["dropped_bits"] == 0
                        assert row["final_distance_m"] <= 10 and row["final_speed_mps"] <= 2
                        assert row["outage_s"] == 0
                runs.append(rows)
                per_run.append({"arm": arm, "seed": seed, "split": split, **summarize(rows)})
            data[split][arm] = runs
            flat = [row for run in runs for row in run]
            summary = summarize(flat)
            success = [r for r in flat if r["success"]]
            summary["successful_path_ratio_mean"] = float(np.mean([r["path_m"] / r["straight_distance_m"] for r in success])) if success else None
            for key in ("network_interventions", "motion_interventions"):
                summary["successful_" + key] = float(np.mean([r[key] for r in success])) if success else None
            summary["per_seed_success_rates"] = [summarize(run)["success_rate"] for run in runs]
            groups[f"{arm}_{split}"] = summary
    contrasts = {}
    for split in data:
        for left, right in (("full", "arrival"), ("joint_mpc", "straight_radio"),
                            ("joint_lookahead", "straight_radio"), ("straight_radio", "straight_rss")):
            contrasts[f"{left}_minus_{right}_{split}"] = contrast(data[split][left], data[split][right])
    report = {"scope": "Frozen v2 results; communication metrics condition on successful paired missions",
              "groups": groups, "contrasts": contrasts, "bootstrap_draws": 5000, "bootstrap_seed": 62000,
              "frozen_v1_and_v2_hashes_verified": True, "seeds": frozen["seeds"],
              "total_evaluated_episodes": sum(g["episodes"] for g in groups.values()),
              "all_reported_successes_meet_sampled_constraints": True}
    (OUT / "statistics.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    with (OUT / "per_seed_summary.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(per_run[0]))
        writer.writeheader()
        writer.writerows(per_run)
    print(json.dumps({"groups": {k: {"success": v["success_rate"], "failures": v["failure_counts"]} for k, v in groups.items()},
                      "learned_contrasts": {k: {"success_difference_pp": v["success_difference_pp"],
                       "success_ci95_pp": v["success_difference_ci95_pp"],
                       "radio_cost_sum": v["radio_cost_sum"]} for k, v in contrasts.items() if k.startswith("full_")}}, indent=2))


if __name__ == "__main__":
    main()
