"""Mission success first evaluation for UAV control episodes."""

from __future__ import annotations

from dataclasses import dataclass
from math import hypot, isfinite
from statistics import fmean
from typing import Iterable, Sequence

from .rewards import StepSignals


Point2D = tuple[float, float]


@dataclass(frozen=True)
class EpisodeMetrics:
    """Episode outcome with mission completion before secondary metrics."""

    episode_name: str
    reward_name: str
    mission_success: bool
    recorded_feasible_success: bool
    outcome_class: str
    termination_reason: str
    arrival_step: int | None
    arrival_time_s: float | None
    steps: int
    total_duration_s: float
    final_distance_m: float
    undiscounted_return: float
    discounted_return: float
    path_length_m: float
    straight_line_distance_m: float
    excess_path_length_m: float | None
    path_efficiency: float | None
    total_delay_s: float
    mean_delay_s: float
    total_interference_cost: float
    mean_interference_cost: float
    total_energy_used_j: float
    mean_energy_used_j: float
    total_outage_s: float
    outage_fraction: float
    handover_count: int
    recorded_constraint_violations: int


@dataclass(frozen=True)
class AggregateMetrics:
    """Aggregate metrics with success rate as the primary result."""

    episode_count: int
    mission_success_count: int
    mission_failure_count: int
    mission_success_rate: float
    recorded_feasible_success_count: int
    recorded_feasible_success_rate: float
    mean_steps_to_success: float | None
    mean_time_to_success_s: float | None
    mean_path_efficiency_recorded_feasible_successes: float | None
    mean_final_distance_failures_m: float | None
    mean_undiscounted_return: float
    mean_delay_s_recorded_feasible_successes: float | None
    mean_interference_cost_recorded_feasible_successes: float | None
    mean_total_energy_used_j_recorded_feasible_successes: float | None
    mean_outage_fraction_recorded_feasible_successes: float | None
    mean_handovers_recorded_feasible_successes: float | None


def discounted_return(rewards: Iterable[float], gamma: float = 0.99) -> float:
    """Compute a forward discounted episode return."""

    if not isfinite(gamma) or not 0.0 <= gamma <= 1.0:
        raise ValueError("gamma must be finite and in [0, 1]")
    total = 0.0
    discount = 1.0
    for reward in rewards:
        if not isfinite(reward):
            raise ValueError("rewards must be finite")
        total += discount * reward
        discount *= gamma
    return total


def _validate_point(point: Point2D) -> None:
    if len(point) != 2 or any(not isfinite(value) for value in point):
        raise ValueError("trajectory points must be finite two dimensional coordinates")


def summarize_episode(
    *,
    episode_name: str,
    reward_name: str,
    trajectory: Sequence[Point2D],
    signals: Sequence[StepSignals],
    rewards: Sequence[float],
    gamma: float = 0.99,
) -> EpisodeMetrics:
    """Compute outcome and secondary metrics for one complete episode.

    The trajectory contains the initial point followed by one point per
    transition.  A success may occur before the final transition so this
    evaluator can audit Marina's nonterminating arrival behavior.  Explicit
    failures must be final.  The corrected environment should truncate the
    trace at its first successful transition.
    """

    if not episode_name.strip():
        raise ValueError("episode_name must be nonempty")
    if not reward_name.strip():
        raise ValueError("reward_name must be nonempty")
    if not signals:
        raise ValueError("signals must contain at least one transition")
    if len(trajectory) != len(signals) + 1:
        raise ValueError("trajectory must contain one more point than signals")
    if len(rewards) != len(signals):
        raise ValueError("rewards and signals must have equal length")
    for point in trajectory:
        _validate_point(point)
    initial_distance = signals[0].initial_distance_m
    if any(
        abs(signal.initial_distance_m - initial_distance) > 1.0e-9
        for signal in signals
    ):
        raise ValueError("initial_distance_m must be constant through an episode")

    success_indices = [
        index
        for index, signal in enumerate(signals)
        if signal.mission_success
    ]
    failure_indices = [
        index
        for index, signal in enumerate(signals)
        if signal.mission_failure or signal.energy_depleted
    ]
    if len(success_indices) > 1:
        raise ValueError("an episode may record goal arrival only once")
    if failure_indices and failure_indices[-1] != len(signals) - 1:
        raise ValueError("explicit failure must occur on the final transition")
    if len(failure_indices) > 1:
        raise ValueError("an episode may contain only one explicit failure")
    if success_indices and failure_indices:
        raise ValueError("an episode cannot contain both success and failure")

    mission_success = bool(success_indices)
    if mission_success:
        arrival_step = success_indices[0] + 1
        arrival_time = sum(
            signal.step_duration_s for signal in signals[:arrival_step]
        )
        termination_reason = (
            "goal_reached"
            if arrival_step == len(signals)
            else "goal_reached_then_horizon"
        )
    elif signals[-1].energy_depleted:
        termination_reason = signals[-1].failure_reason or "energy_depleted"
        arrival_step = None
        arrival_time = None
    elif signals[-1].mission_failure:
        termination_reason = signals[-1].failure_reason or "mission_failure"
        arrival_step = None
        arrival_time = None
    else:
        termination_reason = "horizon_exhausted"
        arrival_step = None
        arrival_time = None

    path_end = arrival_step + 1 if arrival_step is not None else len(trajectory)
    mission_trajectory = trajectory[:path_end]
    path_length = sum(
        hypot(end[0] - start[0], end[1] - start[1])
        for start, end in zip(
            mission_trajectory[:-1], mission_trajectory[1:], strict=True
        )
    )
    if mission_success:
        excess_path_length = max(0.0, path_length - initial_distance)
        path_efficiency = (
            min(1.0, initial_distance / path_length) if path_length > 0.0 else 1.0
        )
    else:
        excess_path_length = None
        path_efficiency = None

    total_delay = sum(signal.delay_s for signal in signals)
    total_interference = sum(signal.interference_cost for signal in signals)
    total_energy = sum(signal.energy_used_j for signal in signals)
    total_outage = sum(signal.outage_s for signal in signals)
    total_duration = sum(signal.step_duration_s for signal in signals)
    handovers = sum(signal.handover_count for signal in signals)
    recorded_constraint_violations = sum(
        int(signal.out_of_bounds)
        + int(signal.rss_below_minimum)
        + int(signal.overspeed)
        for signal in signals
    )
    recorded_feasible_success = (
        mission_success and recorded_constraint_violations == 0
    )
    if recorded_feasible_success:
        outcome_class = "recorded_feasible_success"
    elif mission_success:
        outcome_class = "arrival_with_recorded_violation"
    else:
        outcome_class = "mission_failure"

    return EpisodeMetrics(
        episode_name=episode_name,
        reward_name=reward_name,
        mission_success=mission_success,
        recorded_feasible_success=recorded_feasible_success,
        outcome_class=outcome_class,
        termination_reason=termination_reason,
        arrival_step=arrival_step,
        arrival_time_s=arrival_time,
        steps=len(signals),
        total_duration_s=total_duration,
        final_distance_m=signals[-1].distance_m,
        undiscounted_return=sum(rewards),
        discounted_return=discounted_return(rewards, gamma),
        path_length_m=path_length,
        straight_line_distance_m=initial_distance,
        excess_path_length_m=excess_path_length,
        path_efficiency=path_efficiency,
        total_delay_s=total_delay,
        mean_delay_s=total_delay / len(signals),
        total_interference_cost=total_interference,
        mean_interference_cost=total_interference / len(signals),
        total_energy_used_j=total_energy,
        mean_energy_used_j=total_energy / len(signals),
        total_outage_s=total_outage,
        outage_fraction=total_outage / total_duration,
        handover_count=handovers,
        recorded_constraint_violations=recorded_constraint_violations,
    )


def aggregate_episode_metrics(
    episodes: Sequence[EpisodeMetrics],
) -> AggregateMetrics:
    """Aggregate episodes without allowing return to hide mission failures."""

    if not episodes:
        raise ValueError("episodes must be nonempty")
    successes = [episode for episode in episodes if episode.mission_success]
    recorded_feasible_successes = [
        episode for episode in successes if episode.recorded_feasible_success
    ]
    failures = [episode for episode in episodes if not episode.mission_success]

    return AggregateMetrics(
        episode_count=len(episodes),
        mission_success_count=len(successes),
        mission_failure_count=len(failures),
        mission_success_rate=len(successes) / len(episodes),
        recorded_feasible_success_count=len(recorded_feasible_successes),
        recorded_feasible_success_rate=(
            len(recorded_feasible_successes) / len(episodes)
        ),
        mean_steps_to_success=(
            fmean(
                episode.arrival_step
                for episode in successes
                if episode.arrival_step is not None
            )
            if successes
            else None
        ),
        mean_time_to_success_s=(
            fmean(
                episode.arrival_time_s
                for episode in successes
                if episode.arrival_time_s is not None
            )
            if successes
            else None
        ),
        mean_path_efficiency_recorded_feasible_successes=(
            fmean(
                episode.path_efficiency
                for episode in recorded_feasible_successes
                if episode.path_efficiency is not None
            )
            if recorded_feasible_successes
            else None
        ),
        mean_final_distance_failures_m=(
            fmean(episode.final_distance_m for episode in failures)
            if failures
            else None
        ),
        mean_undiscounted_return=fmean(
            episode.undiscounted_return for episode in episodes
        ),
        mean_delay_s_recorded_feasible_successes=(
            fmean(
                episode.mean_delay_s for episode in recorded_feasible_successes
            )
            if recorded_feasible_successes
            else None
        ),
        mean_interference_cost_recorded_feasible_successes=(
            fmean(
                episode.mean_interference_cost
                for episode in recorded_feasible_successes
            )
            if recorded_feasible_successes
            else None
        ),
        mean_total_energy_used_j_recorded_feasible_successes=(
            fmean(
                episode.total_energy_used_j
                for episode in recorded_feasible_successes
            )
            if recorded_feasible_successes
            else None
        ),
        mean_outage_fraction_recorded_feasible_successes=(
            fmean(
                episode.outage_fraction
                for episode in recorded_feasible_successes
            )
            if recorded_feasible_successes
            else None
        ),
        mean_handovers_recorded_feasible_successes=(
            fmean(
                episode.handover_count for episode in recorded_feasible_successes
            )
            if recorded_feasible_successes
            else None
        ),
    )
