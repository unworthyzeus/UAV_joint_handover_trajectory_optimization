"""Reward formulations for the joint UAV control audit.

The legacy functions below deliberately mirror Equations 13 and 14 of Marina
Bermúdez Granados' thesis.  They are an executable formulation audit, not a
reimplementation of a trained policy or evidence of trained performance.

The corrected formulation makes mission completion the primary objective.  It
adds explicit terminal outcomes, charges every step, normalizes communication
costs, and uses bounded distance progress as shaping.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class StepSignals:
    """Signals needed by both reward formulations for one transition.

    ``interference_cost`` is a nonnegative engineering cost.  A simulator that
    stores interference as received power in dBm or watts must convert it to a
    monotone nonnegative cost before constructing this record.
    """

    delay_s: float
    interference_cost: float
    handover_count: int
    previous_distance_m: float
    distance_m: float
    initial_distance_m: float
    step_duration_s: float = 1.0
    energy_used_j: float = 0.0
    outage_s: float = 0.0
    out_of_bounds: bool = False
    rss_below_minimum: bool = False
    overspeed: bool = False
    energy_depleted: bool = False
    mission_success: bool = False
    mission_failure: bool = False
    failure_reason: str | None = None

    def __post_init__(self) -> None:
        numeric_values = {
            "delay_s": self.delay_s,
            "interference_cost": self.interference_cost,
            "previous_distance_m": self.previous_distance_m,
            "distance_m": self.distance_m,
            "initial_distance_m": self.initial_distance_m,
            "step_duration_s": self.step_duration_s,
            "energy_used_j": self.energy_used_j,
            "outage_s": self.outage_s,
        }
        for name, value in numeric_values.items():
            if not isfinite(value):
                raise ValueError(f"{name} must be finite")
        for name in (
            "delay_s",
            "interference_cost",
            "previous_distance_m",
            "distance_m",
            "energy_used_j",
            "outage_s",
        ):
            if getattr(self, name) < 0.0:
                raise ValueError(f"{name} must be nonnegative")
        if self.initial_distance_m <= 0.0:
            raise ValueError("initial_distance_m must be positive")
        if self.step_duration_s <= 0.0:
            raise ValueError("step_duration_s must be positive")
        if self.outage_s > self.step_duration_s:
            raise ValueError("outage_s cannot exceed step_duration_s")
        if isinstance(self.handover_count, bool) or not isinstance(
            self.handover_count, int
        ):
            raise TypeError("handover_count must be an integer")
        if self.handover_count < 0:
            raise ValueError("handover_count must be nonnegative")
        if self.mission_success and self.mission_failure:
            raise ValueError("a transition cannot be both success and failure")
        if self.mission_success and self.energy_depleted:
            raise ValueError("a successful transition cannot deplete all energy")


@dataclass(frozen=True)
class LegacyRewardConfig:
    """Parameters in thesis Equations 13 and 14 and Table 3.

    The defaults use the equal policy from Table 3.  Penalties are signed so
    that the Equation 14 additions can be reproduced literally.
    """

    beta_delay: float = 10.0
    beta_interference: float = 100_000.0
    beta_handover: float = 100.0
    weight_delay: float = 0.35
    weight_interference: float = 0.30
    weight_handover: float = 0.35
    boundary_penalty: float = -10.0
    rss_penalty: float = -10.0
    speed_penalty: float = -10.0
    critical_failure_penalty: float = -10.0
    closer_bonus: float = 12.0

    def __post_init__(self) -> None:
        for name in ("beta_delay", "beta_interference", "beta_handover"):
            value = getattr(self, name)
            if not isfinite(value) or value < 0.0:
                raise ValueError(f"{name} must be finite and nonnegative")
        for name in ("weight_delay", "weight_interference", "weight_handover"):
            value = getattr(self, name)
            if not isfinite(value) or value < 0.0:
                raise ValueError(f"{name} must be finite and nonnegative")
        for name in (
            "boundary_penalty",
            "rss_penalty",
            "speed_penalty",
            "critical_failure_penalty",
        ):
            value = getattr(self, name)
            if not isfinite(value) or value > 0.0:
                raise ValueError(f"{name} must be finite and nonpositive")
        if not isfinite(self.closer_bonus) or self.closer_bonus < 0.0:
            raise ValueError("closer_bonus must be finite and nonnegative")


def legacy_equation_13_components(
    signals: StepSignals, config: LegacyRewardConfig = LegacyRewardConfig()
) -> dict[str, float]:
    """Return Equation 13's three reciprocal reward terms.

    ``R_D = 1 / (1 + beta_1 D(t))`` and likewise for interference
    and handover events.
    """

    return {
        "delay_reward": 1.0 / (1.0 + config.beta_delay * signals.delay_s),
        "interference_reward": 1.0
        / (1.0 + config.beta_interference * signals.interference_cost),
        "handover_reward": 1.0
        / (1.0 + config.beta_handover * signals.handover_count),
    }


def legacy_equation_14_components(
    signals: StepSignals, config: LegacyRewardConfig = LegacyRewardConfig()
) -> dict[str, float]:
    """Return the signed Equation 14 contributions for one transition.

    The thesis replaces the whole reward by ``P4`` only when the UAV exhausts
    its energy.  Arrival itself has neither a terminal reward nor a termination
    in the original formulation, so ``mission_success`` is intentionally not
    used here.
    """

    if signals.energy_depleted:
        return {
            "delay_term": 0.0,
            "interference_term": 0.0,
            "handover_term": 0.0,
            "boundary_term": 0.0,
            "rss_term": 0.0,
            "speed_term": 0.0,
            "closer_term": 0.0,
            "critical_failure_term": config.critical_failure_penalty,
            "total": config.critical_failure_penalty,
        }

    equation_13 = legacy_equation_13_components(signals, config)
    components = {
        "delay_term": config.weight_delay * equation_13["delay_reward"],
        "interference_term": config.weight_interference
        * equation_13["interference_reward"],
        "handover_term": config.weight_handover
        * equation_13["handover_reward"],
        "boundary_term": config.boundary_penalty if signals.out_of_bounds else 0.0,
        "rss_term": config.rss_penalty if signals.rss_below_minimum else 0.0,
        "speed_term": config.speed_penalty if signals.overspeed else 0.0,
        "closer_term": (
            config.closer_bonus
            if signals.previous_distance_m > signals.distance_m
            else 0.0
        ),
        "critical_failure_term": 0.0,
    }
    components["total"] = sum(components.values())
    return components


def legacy_reward(
    signals: StepSignals, config: LegacyRewardConfig = LegacyRewardConfig()
) -> float:
    """Evaluate the thesis Equation 13 and 14 reward."""

    return legacy_equation_14_components(signals, config)["total"]


@dataclass(frozen=True)
class MissionFirstRewardConfig:
    """Mission first reward with bounded, normalized secondary objectives."""

    success_bonus: float = 20.0
    failure_penalty: float = 20.0
    step_cost_per_s: float = 0.10
    progress_weight: float = 2.0
    delay_weight: float = 0.25
    interference_weight: float = 0.25
    handover_weight: float = 0.10
    energy_weight: float = 0.20
    outage_weight: float = 0.20
    delay_reference_s: float = 0.10
    interference_reference: float = 1.0e-5
    handover_reference: float = 1.0
    energy_reference_j: float = 100.0
    outage_reference_s: float = 0.10
    constraint_violation_penalty: float = 1.0

    def __post_init__(self) -> None:
        nonnegative = (
            "success_bonus",
            "failure_penalty",
            "step_cost_per_s",
            "progress_weight",
            "delay_weight",
            "interference_weight",
            "handover_weight",
            "energy_weight",
            "outage_weight",
            "constraint_violation_penalty",
        )
        for name in nonnegative:
            value = getattr(self, name)
            if not isfinite(value) or value < 0.0:
                raise ValueError(f"{name} must be finite and nonnegative")
        for name in (
            "delay_reference_s",
            "interference_reference",
            "handover_reference",
            "energy_reference_j",
            "outage_reference_s",
        ):
            value = getattr(self, name)
            if not isfinite(value) or value <= 0.0:
                raise ValueError(f"{name} must be finite and positive")
        maximum_nonterminal_gain = self.progress_weight
        if self.success_bonus <= maximum_nonterminal_gain:
            raise ValueError(
                "success_bonus must exceed the largest one step progress shaping gain"
            )
        if self.failure_penalty <= maximum_nonterminal_gain:
            raise ValueError(
                "failure_penalty must exceed the largest one step progress shaping gain"
            )


def _unit_clip(value: float) -> float:
    return min(1.0, max(0.0, value))


def mission_first_reward_components(
    signals: StepSignals,
    config: MissionFirstRewardConfig = MissionFirstRewardConfig(),
) -> dict[str, float]:
    """Return the corrected reward decomposition.

    Secondary metrics are first divided by fixed engineering references and
    clipped to ``[0, 1]``.  The progress term is normalized by initial mission
    distance and clipped to ``[-1, 1]`` per transition.  Timeout, depleted
    energy, and other explicit failures receive the same terminal penalty.
    """

    delay_normalized = _unit_clip(signals.delay_s / config.delay_reference_s)
    interference_normalized = _unit_clip(
        signals.interference_cost / config.interference_reference
    )
    handover_normalized = _unit_clip(
        signals.handover_count / config.handover_reference
    )
    energy_normalized = _unit_clip(signals.energy_used_j / config.energy_reference_j)
    outage_normalized = _unit_clip(signals.outage_s / config.outage_reference_s)
    raw_progress = (
        signals.previous_distance_m - signals.distance_m
    ) / signals.initial_distance_m
    bounded_progress = min(1.0, max(-1.0, raw_progress))
    violation_count = sum(
        (signals.out_of_bounds, signals.rss_below_minimum, signals.overspeed)
    )
    terminal_failure = signals.mission_failure or signals.energy_depleted

    components = {
        "success_term": config.success_bonus if signals.mission_success else 0.0,
        "failure_term": -config.failure_penalty if terminal_failure else 0.0,
        "step_term": -config.step_cost_per_s * signals.step_duration_s,
        "progress_term": config.progress_weight * bounded_progress,
        "delay_term": -config.delay_weight * delay_normalized,
        "interference_term": -config.interference_weight
        * interference_normalized,
        "handover_term": -config.handover_weight * handover_normalized,
        "energy_term": -config.energy_weight * energy_normalized,
        "outage_term": -config.outage_weight * outage_normalized,
        "constraint_term": -config.constraint_violation_penalty * violation_count,
        "delay_normalized": delay_normalized,
        "interference_normalized": interference_normalized,
        "handover_normalized": handover_normalized,
        "energy_normalized": energy_normalized,
        "outage_normalized": outage_normalized,
    }
    components["total"] = sum(
        value
        for name, value in components.items()
        if name
        not in {
            "delay_normalized",
            "interference_normalized",
            "handover_normalized",
            "energy_normalized",
            "outage_normalized",
        }
    )
    return components


def mission_first_reward(
    signals: StepSignals,
    config: MissionFirstRewardConfig = MissionFirstRewardConfig(),
) -> float:
    """Evaluate the corrected mission first reward."""

    return mission_first_reward_components(signals, config)["total"]
