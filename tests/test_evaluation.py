"""Tests for mission success first episode metrics."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from uav_joint_optimization import (
    StepSignals,
    aggregate_episode_metrics,
    discounted_return,
    summarize_episode,
)
from scripts.run_reward_diagnostic import build_diagnostic, run


def signal(
    previous_distance: float,
    distance: float,
    *,
    success: bool = False,
    failure: bool = False,
    delay: float = 0.1,
    interference: float = 0.2,
    handovers: int = 0,
    step_duration: float = 1.0,
    energy_used: float = 0.0,
    outage: float = 0.0,
    overspeed: bool = False,
) -> StepSignals:
    return StepSignals(
        delay_s=delay,
        interference_cost=interference,
        handover_count=handovers,
        previous_distance_m=previous_distance,
        distance_m=distance,
        initial_distance_m=2.0,
        step_duration_s=step_duration,
        energy_used_j=energy_used,
        outage_s=outage,
        overspeed=overspeed,
        mission_success=success,
        mission_failure=failure,
        failure_reason="time_limit" if failure else None,
    )


def test_successful_episode_metrics_include_arrival_and_path_efficiency() -> None:
    metrics = summarize_episode(
        episode_name="direct",
        reward_name="test_reward",
        trajectory=[(0.0, 0.0), (1.0, 0.0), (2.0, 0.0)],
        signals=[
            signal(2.0, 1.0, step_duration=0.5, energy_used=2.0),
            signal(
                1.0,
                0.0,
                success=True,
                handovers=1,
                step_duration=0.5,
                energy_used=3.0,
                outage=0.1,
            ),
        ],
        rewards=[1.0, 2.0],
        gamma=0.5,
    )

    assert metrics.mission_success is True
    assert metrics.recorded_feasible_success is True
    assert metrics.outcome_class == "recorded_feasible_success"
    assert metrics.termination_reason == "goal_reached"
    assert metrics.arrival_step == 2
    assert metrics.steps == 2
    assert metrics.total_duration_s == 1.0
    assert metrics.arrival_time_s == 1.0
    assert metrics.final_distance_m == 0.0
    assert metrics.undiscounted_return == 3.0
    assert metrics.discounted_return == 2.0
    assert metrics.path_length_m == 2.0
    assert metrics.straight_line_distance_m == 2.0
    assert metrics.excess_path_length_m == 0.0
    assert metrics.path_efficiency == 1.0
    assert metrics.total_energy_used_j == 5.0
    assert metrics.total_outage_s == 0.1
    assert metrics.outage_fraction == 0.1
    assert metrics.handover_count == 1


def test_return_does_not_replace_explicit_mission_outcome() -> None:
    success = summarize_episode(
        episode_name="success",
        reward_name="test_reward",
        trajectory=[(0.0, 0.0), (1.0, 0.0), (2.0, 0.0)],
        signals=[signal(2.0, 1.0), signal(1.0, 0.0, success=True)],
        rewards=[-5.0, -5.0],
    )
    failure = summarize_episode(
        episode_name="failure",
        reward_name="test_reward",
        trajectory=[(0.0, 0.0), (1.0, 0.0), (1.0, 0.0)],
        signals=[signal(2.0, 1.0), signal(1.0, 1.0, failure=True)],
        rewards=[100.0, 100.0],
    )

    assert failure.undiscounted_return > success.undiscounted_return
    assert success.outcome_class == "recorded_feasible_success"
    assert failure.outcome_class == "mission_failure"
    assert failure.path_efficiency is None
    assert failure.excess_path_length_m is None
    assert failure.termination_reason == "time_limit"


def test_arrival_with_recorded_violation_is_separately_classified() -> None:
    feasible = summarize_episode(
        episode_name="feasible",
        reward_name="test_reward",
        trajectory=[(0.0, 0.0), (2.0, 0.0)],
        signals=[signal(2.0, 0.0, success=True)],
        rewards=[0.0],
    )
    infeasible = summarize_episode(
        episode_name="infeasible",
        reward_name="test_reward",
        trajectory=[(0.0, 0.0), (2.0, 0.0)],
        signals=[signal(2.0, 0.0, success=True, overspeed=True)],
        rewards=[100.0],
    )

    assert feasible.recorded_feasible_success is True
    assert infeasible.recorded_feasible_success is False
    assert feasible.outcome_class == "recorded_feasible_success"
    assert infeasible.outcome_class == "arrival_with_recorded_violation"


def test_legacy_trace_can_record_arrival_before_equal_horizon_ends() -> None:
    metrics = summarize_episode(
        episode_name="legacy_hold",
        reward_name="legacy",
        trajectory=[(0.0, 0.0), (1.0, 0.0), (2.0, 0.0), (2.0, 0.0)],
        signals=[
            signal(2.0, 1.0),
            signal(1.0, 0.0, success=True),
            signal(0.0, 0.0),
        ],
        rewards=[1.0, 1.0, 1.0],
    )

    assert metrics.mission_success is True
    assert metrics.arrival_step == 2
    assert metrics.steps == 3
    assert metrics.arrival_time_s == 2.0
    assert metrics.total_duration_s == 3.0
    assert metrics.termination_reason == "goal_reached_then_horizon"


def test_aggregate_reports_success_rate_before_conditional_metrics() -> None:
    success = summarize_episode(
        episode_name="success",
        reward_name="test_reward",
        trajectory=[(0.0, 0.0), (1.0, 0.0), (2.0, 0.0)],
        signals=[signal(2.0, 1.0), signal(1.0, 0.0, success=True)],
        rewards=[1.0, 2.0],
    )
    failure = summarize_episode(
        episode_name="failure",
        reward_name="test_reward",
        trajectory=[(0.0, 0.0), (1.0, 0.0), (1.0, 0.0)],
        signals=[signal(2.0, 1.0), signal(1.0, 1.0, failure=True)],
        rewards=[4.0, 5.0],
    )

    aggregate = aggregate_episode_metrics([success, failure])

    assert aggregate.episode_count == 2
    assert aggregate.mission_success_count == 1
    assert aggregate.mission_failure_count == 1
    assert aggregate.mission_success_rate == 0.5
    assert aggregate.recorded_feasible_success_count == 1
    assert aggregate.recorded_feasible_success_rate == 0.5
    assert aggregate.mean_steps_to_success == 2.0
    assert aggregate.mean_time_to_success_s == 2.0
    assert aggregate.mean_path_efficiency_recorded_feasible_successes == 1.0
    assert aggregate.mean_final_distance_failures_m == 1.0
    assert aggregate.mean_undiscounted_return == 6.0
    assert aggregate.mean_delay_s_recorded_feasible_successes == pytest.approx(0.1)
    assert aggregate.mean_handovers_recorded_feasible_successes == 0.0


def test_discounted_return_and_episode_shapes_are_validated() -> None:
    with pytest.raises(ValueError, match="gamma"):
        discounted_return([1.0], gamma=1.01)
    with pytest.raises(ValueError, match="one more point"):
        summarize_episode(
            episode_name="bad",
            reward_name="test_reward",
            trajectory=[(0.0, 0.0)],
            signals=[signal(2.0, 1.0)],
            rewards=[1.0],
        )


def test_reward_alignment_script_writes_stably_named_labelled_artifacts(
    tmp_path: Path,
) -> None:
    csv_path, json_path, png_path = run(tmp_path)

    assert csv_path.name == "reward_alignment_diagnostic.csv"
    assert json_path.name == "reward_alignment_diagnostic.json"
    assert png_path.name == "reward_alignment_diagnostic.png"
    record = json.loads(json_path.read_text(encoding="utf-8"))
    assert record["artifact_type"] == "engineering diagnostic"
    assert record["trained_performance"] is False
    assert all(record["assertions"].values())
    assert png_path.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")


def test_checked_in_diagnostic_json_matches_current_formulation() -> None:
    project_root = Path(__file__).resolve().parents[1]
    checked_in = json.loads(
        (
            project_root
            / "results"
            / "tables"
            / "reward_alignment_diagnostic.json"
        ).read_text(encoding="utf-8")
    )
    _, expected = build_diagnostic()
    expected_json = json.loads(json.dumps(expected))

    assert checked_in == expected_json
