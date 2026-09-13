"""Prespecified paired analysis for original reward versus full reward on V2."""
import argparse
import csv
import json
from pathlib import Path

import numpy as np

from run_reward_comparison import ROOT, SEEDS, ARMS, CONTROLLERS, verify, summarize, save
from analyze_connectivity_experiment import interval

METRICS = ["radio_cost_sum", "radio_cost_mean", "time_s", "delay_proxy_mean_s",
           "interference_mean_w", "handovers", "energy_proxy_j", "sinr_mean_db",
           "path_m", "network_interventions", "motion_interventions"]


def paired(left, right):
    assert len(left) == len(right)
    for a, b in zip(left, right):
        assert [r["scenario_id"] for r in a] == [r["scenario_id"] for r in b]
    ls = np.array([[r["success"] for r in run] for run in left])
    rs = np.array([[r["success"] for r in run] for run in right])
    common = ls & rs
    difference = ls.astype(float) - rs.astype(float)
    result = {"success_difference_pp": float(100 * difference.mean()),
              "success_difference_ci95_pp": [100*x for x in interval(difference, seed=63000)],
              "paired_success_count": int(common.sum()), "paired_evaluations": int(common.size)}
    for metric in METRICS:
        a = np.array([[r[metric] for r in run] for run in left])
        b = np.array([[r[metric] for r in run] for run in right])
        result[metric] = {"left_mean_on_common_success": float(a[common].mean()) if common.any() else None,
                          "right_mean_on_common_success": float(b[common].mean()) if common.any() else None,
                          "paired_mean_difference": float((a-b)[common].mean()) if common.any() else None,
                          "difference_ci95": interval(a-b, common, seed=63000),
                          "relative_difference_pct": float(100*(a[common].sum()/b[common].sum()-1))
                          if metric != "sinr_mean_db" and common.any() and b[common].sum() != 0 else None}
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--label", default="v15")
    args = parser.parse_args()
    frozen = verify()
    base = ROOT / "results/reward_comparison" / f"confirmatory_{args.label}"
    out = ROOT / "results/reward_comparison" / f"analysis_{args.label}"
    groups, per_seed, data = {}, [], {}
    for split in ("test", "longer_test"):
        data[split] = {}
        for arm in ARMS + CONTROLLERS:
            runs = []
            for seed in SEEDS if arm in ARMS else [None]:
                relative = f"{arm}_seed_{seed}/{split}.json" if seed else f"{arm}_{split}.json"
                rows = json.loads((base / relative).read_text())["episodes"]
                assert len(rows) == 200
                for row in rows:
                    if row["success"]:
                        assert row["minimum_rss_dbm"] >= -96 and row["outage_s"] == 0
                        assert row["dropped_bits"] == 0 and row["time_s"] <= 200
                        assert row["final_distance_m"] <= 10 and row["final_speed_mps"] <= 2
                runs.append(rows)
                per_seed.append({"arm": arm, "seed": seed, "split": split, **summarize(rows)})
            data[split][arm] = runs
            flat = [row for run in runs for row in run]
            summary = summarize(flat)
            summary["per_seed_success_rates"] = [summarize(run)["success_rate"] for run in runs]
            ratios = [r["path_m"]/r["straight_distance_m"] for r in flat if r["success"]]
            summary["successful_path_ratio_mean"] = float(np.mean(ratios)) if ratios else None
            for metric in ("network_interventions", "motion_interventions"):
                good = [r[metric] for r in flat if r["success"]]
                summary["successful_"+metric] = float(np.mean(good)) if good else None
            groups[f"{arm}_{split}"] = summary
    contrasts = {}
    for split in data:
        for left, right in (("full", "original"), ("full", "arrival"),
                            ("straight_radio", "straight_rss"), ("joint_mpc", "straight_radio"),
                            ("joint_lookahead", "straight_radio")):
            contrasts[f"{left}_minus_{right}_{split}"] = paired(data[split][left], data[split][right])
    primary = contrasts["full_minus_original_test"]
    report = {"scope": "Fresh tests of V1.5 original reward and V2 controls on the identical V2 system",
              "groups": groups, "contrasts": contrasts, "seeds": SEEDS,
              "primary_contrast": frozen["primary_contrast"],
              "primary_positive_completion_evidence": primary["success_difference_ci95_pp"][0] > 0,
              "bootstrap_draws": 5000, "bootstrap_seed": 63000,
              "total_evaluated_episodes": sum(g["episodes"] for g in groups.values()),
              "all_reported_successes_meet_sampled_constraints": True}
    assert report["total_evaluated_episodes"] == 7600
    save(out / "statistics.json", report)
    with (out / "per_seed_summary.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(per_seed[0]))
        writer.writeheader(); writer.writerows(per_seed)
    print(json.dumps({"groups": {k: {"success": v["success_rate"], "failures": v["failure_counts"]}
                                for k,v in groups.items()},
                      "primary_contrast": primary,
                      "longer_contrast": contrasts["full_minus_original_longer_test"]}, indent=2))


if __name__ == "__main__":
    main()
