"""Executable definitions for the legacy and corrected control formulations."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, pi
from typing import Iterable


THESIS_ACCELERATION_BINS_MPS2 = (-5.0, -2.5, 0.0, 2.5, 5.0)
THESIS_HEADING_BINS_RAD = tuple(index * pi / 4.0 for index in range(8))
THESIS_BASE_STATION_COUNT = 87
THESIS_RBG_COUNT = 12

RAW_JOINT_ACTION_COUNT = (
    len(THESIS_ACCELERATION_BINS_MPS2)
    * len(THESIS_HEADING_BINS_RAD)
    * THESIS_BASE_STATION_COUNT
    * THESIS_RBG_COUNT
)

if RAW_JOINT_ACTION_COUNT != 41_760:
    raise RuntimeError("the thesis action cardinalities must produce 41,760 actions")


@dataclass(frozen=True)
class LegacyObjectiveWeights:
    """Weights in the thesis Equation 11 cost per timestep."""

    delay: float = 0.35
    interference: float = 0.30
    handover: float = 0.35

    def __post_init__(self) -> None:
        for name in ("delay", "interference", "handover"):
            value = getattr(self, name)
            if not isfinite(value) or value < 0.0:
                raise ValueError(f"{name} weight must be finite and nonnegative")


def legacy_step_objective(
    delay: float,
    interference: float,
    handover: int,
    weights: LegacyObjectiveWeights = LegacyObjectiveWeights(),
) -> float:
    """Evaluate the thesis Equation 11 step cost ``omega_t``."""

    values = (delay, interference, handover)
    if any(not isfinite(float(value)) for value in values):
        raise ValueError("objective inputs must be finite")
    if any(value < 0 for value in values):
        raise ValueError("objective inputs must be nonnegative costs")
    return (
        weights.delay * delay
        + weights.interference * interference
        + weights.handover * handover
    )


def legacy_episode_objective(step_costs: Iterable[float]) -> float:
    """Evaluate the thesis Equation 12 sum over the mission horizon."""

    total = 0.0
    for cost in step_costs:
        if not isfinite(cost) or cost < 0.0:
            raise ValueError("step costs must be finite and nonnegative")
        total += cost
    return total


@dataclass(frozen=True)
class MixedAction:
    """One action with continuous movement and discrete radio requests.

    This interface avoids a 41,760 class categorical policy.  A policy can use
    a two value continuous movement head and two categorical communication
    heads while the environment still receives a single typed action.
    """

    acceleration_mps2: float
    heading_rad: float
    base_station: int
    rbg: int


@dataclass(frozen=True)
class MixedActionSpec:
    """Dependency free description and validation of the mixed action space."""

    acceleration_min_mps2: float = -5.0
    acceleration_max_mps2: float = 5.0
    heading_min_rad: float = 0.0
    heading_max_rad: float = 2.0 * pi
    base_station_count: int = THESIS_BASE_STATION_COUNT
    rbg_count: int = THESIS_RBG_COUNT

    @property
    def interface(self) -> dict[str, object]:
        """Return a Gym compatible conceptual specification without Gym."""

        return {
            "movement": {
                "type": "Box",
                "fields": ("acceleration_mps2", "heading_rad"),
                "low": (self.acceleration_min_mps2, self.heading_min_rad),
                "high": (self.acceleration_max_mps2, self.heading_max_rad),
            },
            "communication": {
                "type": "MultiDiscrete",
                "fields": ("base_station", "rbg"),
                "cardinalities": (self.base_station_count, self.rbg_count),
            },
        }

    def validate(self, action: MixedAction) -> MixedAction:
        """Return ``action`` when valid, otherwise raise a useful exception."""

        if not isinstance(action, MixedAction):
            raise TypeError("action must be a MixedAction")
        if not isfinite(action.acceleration_mps2):
            raise ValueError("acceleration_mps2 must be finite")
        if not self.acceleration_min_mps2 <= action.acceleration_mps2 <= self.acceleration_max_mps2:
            raise ValueError("acceleration_mps2 is outside its bounds")
        if not isfinite(action.heading_rad):
            raise ValueError("heading_rad must be finite")
        if not self.heading_min_rad <= action.heading_rad < self.heading_max_rad:
            raise ValueError("heading_rad must be in [0, 2 pi)")
        if isinstance(action.base_station, bool) or not isinstance(action.base_station, int):
            raise TypeError("base_station must be an integer")
        if isinstance(action.rbg, bool) or not isinstance(action.rbg, int):
            raise TypeError("rbg must be an integer")
        if not 0 <= action.base_station < self.base_station_count:
            raise ValueError("base_station is outside its bounds")
        if not 0 <= action.rbg < self.rbg_count:
            raise ValueError("rbg is outside its bounds")
        return action


MIXED_ACTION_SPEC = MixedActionSpec()


def encode_legacy_joint_action(
    acceleration_bin: int, heading_bin: int, base_station: int, rbg: int
) -> int:
    """Encode four zero based thesis decisions into one categorical index."""

    cardinalities = (
        len(THESIS_ACCELERATION_BINS_MPS2),
        len(THESIS_HEADING_BINS_RAD),
        THESIS_BASE_STATION_COUNT,
        THESIS_RBG_COUNT,
    )
    indices = (acceleration_bin, heading_bin, base_station, rbg)
    for name, index, cardinality in zip(
        ("acceleration_bin", "heading_bin", "base_station", "rbg"),
        indices,
        cardinalities,
        strict=True,
    ):
        if isinstance(index, bool) or not isinstance(index, int):
            raise TypeError(f"{name} must be an integer")
        if not 0 <= index < cardinality:
            raise ValueError(f"{name} is outside its bounds")

    encoded = acceleration_bin
    encoded = encoded * cardinalities[1] + heading_bin
    encoded = encoded * cardinalities[2] + base_station
    return encoded * cardinalities[3] + rbg


def decode_legacy_joint_action(index: int) -> tuple[int, int, int, int]:
    """Decode one categorical index into the four thesis decisions."""

    if isinstance(index, bool) or not isinstance(index, int):
        raise TypeError("index must be an integer")
    if not 0 <= index < RAW_JOINT_ACTION_COUNT:
        raise ValueError("index is outside the 41,760 action space")
    remainder, rbg = divmod(index, THESIS_RBG_COUNT)
    remainder, base_station = divmod(remainder, THESIS_BASE_STATION_COUNT)
    acceleration_bin, heading_bin = divmod(
        remainder, len(THESIS_HEADING_BINS_RAD)
    )
    return acceleration_bin, heading_bin, base_station, rbg


MISSION_FIRST_OBJECTIVE_ORDER = (
    "maximize mission success rate",
    "satisfy safety, energy, buffer, and connectivity constraints",
    "minimize time, energy, delay, interference, outage, and handovers among successful missions",
    "maximize mean and fifth percentile SINR among successful missions",
)
