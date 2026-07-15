#!/usr/bin/env python3
"""Run a handcrafted reward formulation diagnostic.

This script compares two fixed trajectories.  It does not train or evaluate a
policy, so every artifact is explicitly labelled as engineering diagnostic
output rather than trained performance.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import asdict
from math import hypot
from pathlib import Path
from typing import Callable, Sequence


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from uav_joint_optimization import (  # noqa: E402
    MIXED_ACTION_SPEC,
    RAW_JOINT_ACTION_COUNT,
    LegacyRewardConfig,
    MissionFirstRewardConfig,
    StepSignals,
    legacy_reward,
    mission_first_reward,
    summarize_episode,
)


ARTIFACT_TYPE = "engineering diagnostic"
DISCLAIMER = "Handcrafted trajectories only. This is not trained performance."
GAMMA = 0.99
Point2D = tuple[float, float]


def _signals_for_path(
    trajectory: Sequence[Point2D],
    *,
    goal: Point2D,
    success_step: int | None,
) -> list[StepSignals]:
    initial_distance = hypot(
        trajectory[0][0] - goal[0], trajectory[0][1] - goal[1]
    )
    signals: list[StepSignals] = []
    for step_index, (start, end) in enumerate(
        zip(trajectory[:-1], trajectory[1:], strict=True), start=1
    ):
        final_transition = step_index == len(trajectory) - 1
        signals.append(
            StepSignals(
                delay_s=0.005,
                interference_cost=1.0e-7,
                handover_count=0,
                previous_distance_m=hypot(start[0] - goal[0], start[1] - goal[1]),
                distance_m=hypot(end[0] - goal[0], end[1] - goal[1]),
                initial_distance_m=initial_distance,
                step_duration_s=0.1,
                mission_success=step_index == success_step,
                mission_failure=success_step is None and final_transition,
                failure_reason=(
                    "time_limit"
                    if success_step is None and final_transition
                    else None
                ),
            )
        )
    return signals


def _diagnostic_inputs() -> dict[str, tuple[list[Point2D], list[StepSignals]]]:
    goal = (5.0, 0.0)
    direct = [(float(x), 0.0) for x in range(6)] + [(5.0, 0.0)] * 7
    oscillating = [(0.0, 0.0)] + [
        ((1.0, 0.0) if step % 2 else (0.0, 0.0)) for step in range(1, 13)
    ]
    return {
        "direct_arrival": (
            direct,
            _signals_for_path(direct, goal=goal, success_step=5),
        ),
        "never_arrive_oscillation": (
            oscillating,
            _signals_for_path(oscillating, goal=goal, success_step=None),
        ),
    }


def build_diagnostic() -> tuple[list[dict[str, object]], dict[str, object]]:
    """Build table rows and a JSON ready diagnostic record."""

    legacy_config = LegacyRewardConfig()
    corrected_config = MissionFirstRewardConfig()
    reward_functions: tuple[
        tuple[str, Callable[[StepSignals], float]], ...
    ] = (
        ("legacy_equations_13_14", lambda signal: legacy_reward(signal, legacy_config)),
        (
            "mission_first_corrected",
            lambda signal: mission_first_reward(signal, corrected_config),
        ),
    )

    table_rows: list[dict[str, object]] = []
    metrics_lookup: dict[tuple[str, str], dict[str, object]] = {}
    trajectories = _diagnostic_inputs()
    for reward_name, reward_function in reward_functions:
        for episode_name, (trajectory, signals) in trajectories.items():
            if reward_name == "mission_first_corrected":
                success_index = next(
                    (
                        index
                        for index, signal in enumerate(signals)
                        if signal.mission_success
                    ),
                    None,
                )
                if success_index is not None:
                    trajectory = trajectory[: success_index + 2]
                    signals = signals[: success_index + 1]
            rewards = [reward_function(signal) for signal in signals]
            metrics = summarize_episode(
                episode_name=episode_name,
                reward_name=reward_name,
                trajectory=trajectory,
                signals=signals,
                rewards=rewards,
                gamma=GAMMA,
            )
            row: dict[str, object] = {
                "artifact_type": ARTIFACT_TYPE,
                "trained_performance": False,
                **asdict(metrics),
            }
            table_rows.append(row)
            metrics_lookup[(reward_name, episode_name)] = asdict(metrics)

    legacy_direct = metrics_lookup[("legacy_equations_13_14", "direct_arrival")]
    legacy_oscillation = metrics_lookup[
        ("legacy_equations_13_14", "never_arrive_oscillation")
    ]
    corrected_direct = metrics_lookup[("mission_first_corrected", "direct_arrival")]
    corrected_oscillation = metrics_lookup[
        ("mission_first_corrected", "never_arrive_oscillation")
    ]
    assertions = {
        "legacy_never_arrive_outscores_direct_undiscounted": (
            legacy_oscillation["undiscounted_return"]
            > legacy_direct["undiscounted_return"]
        ),
        "legacy_never_arrive_outscores_direct_discounted_gamma_0_99": (
            legacy_oscillation["discounted_return"]
            > legacy_direct["discounted_return"]
        ),
        "corrected_direct_outscores_never_arrive_undiscounted": (
            corrected_direct["undiscounted_return"]
            > corrected_oscillation["undiscounted_return"]
        ),
        "corrected_direct_outscores_never_arrive_discounted_gamma_0_99": (
            corrected_direct["discounted_return"]
            > corrected_oscillation["discounted_return"]
        ),
    }
    if not all(assertions.values()):
        raise AssertionError(f"diagnostic ordering failed: {assertions}")

    json_record: dict[str, object] = {
        "artifact_type": ARTIFACT_TYPE,
        "trained_performance": False,
        "disclaimer": DISCLAIMER,
        "diagnostic_question": (
            "Can a handcrafted path that never arrives score above direct arrival?"
        ),
        "trace_protocol": {
            "legacy": (
                "Both paths use the same 12 step horizon. Direct arrival occurs "
                "at step 5 and then holds at the goal because the thesis does not "
                "terminate on arrival."
            ),
            "corrected": (
                "The successful path terminates at first safe arrival; the "
                "never arrive path ends with a time limit failure."
            ),
        },
        "source_formulation": {
            "equation_13": (
                "R_D=1/(1+beta_1 D), R_I=1/(1+beta_2 I), "
                "R_h=1/(1+beta_3 h)"
            ),
            "equation_14": (
                "weighted positive terms plus constraint penalties and a binary "
                "closer bonus; energy depletion substitutes P4"
            ),
            "arrival_terminal_reward": False,
            "arrival_termination_in_thesis": False,
        },
        "action_space_audit": {
            "legacy_raw_joint_action_count": RAW_JOINT_ACTION_COUNT,
            "factorization": "5 acceleration x 8 heading x 87 BS x 12 RBG",
            "mixed_action_interface": MIXED_ACTION_SPEC.interface,
        },
        "legacy_reward_config": asdict(legacy_config),
        "corrected_reward_config": asdict(corrected_config),
        "discount_factor": GAMMA,
        "assertions": assertions,
        "episodes": table_rows,
    }
    return table_rows, json_record


def _write_csv(path: Path, rows: Sequence[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _write_png(path: Path, rows: Sequence[dict[str, object]]) -> None:
    import matplotlib

    matplotlib.use("Agg")
    from matplotlib import pyplot as plt

    lookup = {
        (str(row["reward_name"]), str(row["episode_name"])): float(
            row["discounted_return"]
        )
        for row in rows
    }
    trajectories = _diagnostic_inputs()

    figure, (path_axis, return_axis) = plt.subplots(1, 2, figsize=(11.5, 4.6))
    for name, (_, signals) in trajectories.items():
        distances = [signals[0].previous_distance_m] + [
            signal.distance_m for signal in signals
        ]
        label = (
            "Direct arrival, then hold"
            if name == "direct_arrival"
            else "Never arrives"
        )
        path_axis.plot(range(len(distances)), distances, marker="o", label=label)
    path_axis.set_title("Handcrafted distance to goal")
    path_axis.set_xlabel("Step")
    path_axis.set_ylabel("Distance to goal (m)")
    path_axis.grid(alpha=0.25)
    path_axis.legend()

    x_positions = [0.0, 0.8, 2.0, 2.8]
    values = [
        lookup[("legacy_equations_13_14", "direct_arrival")],
        lookup[("legacy_equations_13_14", "never_arrive_oscillation")],
        lookup[("mission_first_corrected", "direct_arrival")],
        lookup[("mission_first_corrected", "never_arrive_oscillation")],
    ]
    colors = ["#2A6FBB", "#E07A3F", "#2A6FBB", "#E07A3F"]
    bars = return_axis.bar(x_positions, values, width=0.62, color=colors)
    return_axis.axhline(0.0, color="black", linewidth=0.8)
    return_axis.set_xticks([0.4, 2.4], ["Legacy Eq. 13-14", "Mission first"])
    return_axis.set_ylabel("Discounted return (gamma = 0.99)")
    return_axis.set_title("Reward ordering reversal")
    return_axis.grid(axis="y", alpha=0.25)
    for bar, value in zip(bars, values, strict=True):
        vertical_alignment = "bottom" if value >= 0.0 else "top"
        offset = 1.0 if value >= 0.0 else -1.0
        return_axis.text(
            bar.get_x() + bar.get_width() / 2.0,
            value + offset,
            f"{value:.2f}",
            ha="center",
            va=vertical_alignment,
            fontsize=9,
        )

    figure.suptitle(
        "Engineering diagnostic only: handcrafted paths, not trained performance",
        fontweight="bold",
    )
    figure.tight_layout()
    figure.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(figure)


def run(output_dir: Path) -> tuple[Path, Path, Path]:
    """Run the diagnostic and write CSV, JSON, and PNG artifacts."""

    table_dir = output_dir / "tables"
    figure_dir = output_dir / "figures"
    table_dir.mkdir(parents=True, exist_ok=True)
    figure_dir.mkdir(parents=True, exist_ok=True)

    rows, json_record = build_diagnostic()
    csv_path = table_dir / "reward_alignment_diagnostic.csv"
    json_path = table_dir / "reward_alignment_diagnostic.json"
    png_path = figure_dir / "reward_alignment_diagnostic.png"
    _write_csv(csv_path, rows)
    with json_path.open("w", encoding="utf-8") as handle:
        json.dump(json_record, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    _write_png(png_path, rows)
    return csv_path, json_path, png_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "results",
        help="Result root. Defaults to the project's results directory.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    csv_path, json_path, png_path = run(args.output_dir.resolve())
    print(DISCLAIMER)
    print(f"CSV: {csv_path}")
    print(f"JSON: {json_path}")
    print(f"PNG: {png_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
