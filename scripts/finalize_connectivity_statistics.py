"""Reporting correction without changing the frozen estimator or its output.

Relative percentages of dB values are not physically interpretable. Preserve
the frozen raw output, remove that unused generic field in the reporting copy,
and evaluate the prespecified joint claim rule. No estimate or interval changes.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results/connectivity_experiment/analysis_v2"


def main():
    source = OUT / "statistics.json"
    report = json.loads(source.read_text())
    for item in report["contrasts"].values():
        item["sinr_mean_db"]["relative_difference_pct"] = None
    report["reporting_adjustments"] = {
        "frozen_statistics_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "description": "Set relative percentage fields for logarithmic SINR values to null. Absolute dB differences and all other estimates/intervals are unchanged.",
    }
    report["strong_learned_joint_improvement_claim"] = {
        split: (report["contrasts"][f"full_minus_arrival_{split}"]["success_difference_ci95_pp"][0] > 0
                and report["contrasts"][f"full_minus_arrival_{split}"]["radio_cost_sum"]["difference_ci95"][1] < 0)
        for split in ("test", "longer_test")}
    (OUT / "report_statistics.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report["strong_learned_joint_improvement_claim"]))


if __name__ == "__main__":
    main()
