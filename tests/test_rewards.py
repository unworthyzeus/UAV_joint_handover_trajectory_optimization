"""Tests for the legacy and mission first reward formulations."""

from __future__ import annotations

import json
from dataclasses import asdict
from math import pi
from pathlib import Path

import pytest

from uav_joint_optimization import (
    MIXED_ACTION_SPEC,
    RAW_JOINT_ACTION_COUNT,
    LegacyRewardConfig,
    MissionFirstRewardConfig,
    MixedAction,
    StepSignals,
    decode_legacy_joint_action,
    discounted_return,
    encode_legacy_joint_action,
    legacy_equation_13_components,
    legacy_equation_14_components,
    legacy_reward,
    mission_first_reward,
    mission_first_reward_components,
)


def make_signal(**overrides: object) -> StepSignals:
    values: dict[str, object] = {
        "delay_s": 0.01,
        "interference_cost": 1.0e-7,
        "handover_count": 0,
        "previous_distance_m": 5.0,
        "distance_m": 4.0,
        "initial_distance_m": 5.0,
    }
    values.update(overrides)
    return StepSignals(**values)  # type: ignore[arg-type]


def test_equation_13_reciprocal_terms_are_structurally_reproduced() -> None:
    config = LegacyRewardConfig(
        beta_delay=2.0,
        beta_interference=4.0,
        beta_handover=3.0,
    )
    signal = make_signal(
        delay_s=0.5,
        interference_cost=0.25,
        handover_count=1,
    )

    components = legacy_equation_13_components(signal, config)

    assert components == pytest.approx(
        {
            "delay_reward": 0.5,
            "interference_reward": 0.5,
            "handover_reward": 0.25,
        }
    )


def test_equation_14_adds_weighted_terms_penalties_and_binary_bonus() -> None:
    signal = make_signal(
        delay_s=0.1,
        interference_cost=1.0e-5,
        handover_count=1,
        out_of_bounds=True,
    )

    components = legacy_equation_14_components(signal)
    expected = 0.35 * 0.5 + 0.30 * 0.5 + 0.35 / 101.0 - 10.0 + 12.0

    assert components["closer_term"] == 12.0
    assert components["boundary_term"] == -10.0
    assert components["total"] == pytest.approx(expected)
    assert legacy_reward(signal) == pytest.approx(expected)


def test_legacy_energy_depletion_substitutes_p4_for_the_whole_reward() -> None:
    signal = make_signal(
        energy_depleted=True,
        mission_failure=True,
        failure_reason="energy_depleted",
        out_of_bounds=True,
    )

    components = legacy_equation_14_components(signal)

    assert components["critical_failure_term"] == -10.0
    assert components["total"] == -10.0
    assert sum(
        components[name]
        for name in (
            "delay_term",
            "interference_term",
            "handover_term",
            "boundary_term",
            "rss_term",
            "speed_term",
            "closer_term",
        )
    ) == 0.0


def test_mission_first_reward_has_terminal_step_progress_and_normalized_costs() -> None:
    signal = make_signal(
        delay_s=0.2,
        interference_cost=2.0e-5,
        handover_count=2,
        energy_used_j=200.0,
        outage_s=0.5,
        mission_success=True,
        overspeed=True,
    )

    components = mission_first_reward_components(signal)

    assert components["delay_normalized"] == 1.0
    assert components["interference_normalized"] == 1.0
    assert components["handover_normalized"] == 1.0
    assert components["energy_normalized"] == 1.0
    assert components["outage_normalized"] == 1.0
    assert components["success_term"] == 20.0
    assert components["step_term"] == -0.10
    assert components["progress_term"] == pytest.approx(0.4)
    assert components["constraint_term"] == -1.0
    assert components["energy_term"] == -0.2
    assert components["outage_term"] == -0.2
    assert components["total"] == pytest.approx(18.3)


def _signals_from_distances(
    distances: list[float], *, success_step: int | None
) -> list[StepSignals]:
    signals: list[StepSignals] = []
    for index, (previous, current) in enumerate(
        zip(distances[:-1], distances[1:], strict=True), start=1
    ):
        final = index == len(distances) - 1
        signals.append(
            make_signal(
                previous_distance_m=previous,
                distance_m=current,
                initial_distance_m=distances[0],
                mission_success=index == success_step,
                mission_failure=success_step is None and final,
                failure_reason=(
                    "time_limit" if success_step is None and final else None
                ),
            )
        )
    return signals


def test_handcrafted_oscillation_exposes_legacy_reward_hacking() -> None:
    direct = _signals_from_distances(
        [5.0, 4.0, 3.0, 2.0, 1.0, 0.0] + [0.0] * 7,
        success_step=5,
    )
    oscillating = _signals_from_distances(
        [5.0] + [4.0 if step % 2 else 5.0 for step in range(1, 13)],
        success_step=None,
    )

    legacy_direct = [legacy_reward(signal) for signal in direct]
    legacy_oscillating = [legacy_reward(signal) for signal in oscillating]
    corrected_direct = [mission_first_reward(signal) for signal in direct[:5]]
    corrected_oscillating = [
        mission_first_reward(signal) for signal in oscillating
    ]

    assert sum(legacy_oscillating) > sum(legacy_direct)
    assert discounted_return(legacy_oscillating) > discounted_return(legacy_direct)
    assert sum(corrected_direct) > sum(corrected_oscillating)
    assert discounted_return(corrected_direct) > discounted_return(
        corrected_oscillating
    )


def test_raw_joint_count_and_mixed_action_interface_are_exposed() -> None:
    assert RAW_JOINT_ACTION_COUNT == 41_760
    assert encode_legacy_joint_action(4, 7, 86, 11) == 41_759
    assert decode_legacy_joint_action(41_759) == (4, 7, 86, 11)
    assert decode_legacy_joint_action(encode_legacy_joint_action(2, 3, 40, 6)) == (
        2,
        3,
        40,
        6,
    )

    action = MixedAction(
        acceleration_mps2=1.25,
        heading_rad=pi / 3.0,
        base_station=10,
        rbg=4,
    )
    assert MIXED_ACTION_SPEC.validate(action) is action
    assert MIXED_ACTION_SPEC.interface["movement"]["type"] == "Box"  # type: ignore[index]
    assert (
        MIXED_ACTION_SPEC.interface["communication"]["type"]  # type: ignore[index]
        == "MultiDiscrete"
    )


def test_corrected_terminal_parameters_must_dominate_one_step_shaping() -> None:
    with pytest.raises(ValueError, match="success_bonus"):
        MissionFirstRewardConfig(success_bonus=1.0, progress_weight=2.0)


def test_step_signal_validates_duration_and_outage_units() -> None:
    with pytest.raises(ValueError, match="step_duration_s"):
        make_signal(step_duration_s=0.0)
    with pytest.raises(ValueError, match="outage_s cannot exceed"):
        make_signal(step_duration_s=0.1, outage_s=0.2)


def test_versioned_reward_config_matches_executable_defaults() -> None:
    project_root = Path(__file__).resolve().parents[1]
    config = json.loads(
        (project_root / "configs" / "mission_first_v0.json").read_text(
            encoding="utf-8"
        )
    )

    assert config["reward"] == asdict(MissionFirstRewardConfig())
