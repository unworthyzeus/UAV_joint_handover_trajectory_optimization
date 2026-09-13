"""Original written reward on the unchanged V2 transition and control system.

TFM printed p. 12, Eqs. (13)-(14) and energy override; p. 15, Table 3.
This is a reward intervention, not a reproduction of the original simulator.
"""
import numpy as np

from .connectivity_env import ConnectivityBatch, ConnectivityConfig


def original_reward(distance_before, distance_after, delay, interference,
                    handover, rss, speed, boundary, energy_failure):
    """Retain the source's equal weights, coefficients and reward thresholds.

The written speed threshold is 100 m/s, unreachable under V2's 25 m/s cap.
The source reward penalizes RSS equality although the joint constraint allows it.
No new arrival, timeout or overflow reward term is added to the original arm.
"""
    value = (.35 / (1 + 10 * delay) + .30 / (1 + 1e5 * interference)
             + .35 / (1 + 100 * handover) + 12. * (distance_after < distance_before)
             - 10. * boundary - 10. * (rss <= -96.) - 10. * (speed >= 100.))
    return np.where(energy_failure, -10., value)


class RewardComparisonBatch(ConnectivityBatch):
    """Delegate all state transitions, observations and termination to V2."""

    def __init__(self, radio, n, scenarios, reward="full", config=ConnectivityConfig()):
        if reward not in {"original", "full", "arrival"}:
            raise ValueError(reward)
        self.use_original_reward = reward == "original"
        super().__init__(radio, n, scenarios, "full" if self.use_original_reward else reward, config)

    def step(self, motion, network):
        if not self.use_original_reward:
            return super().step(motion, network)
        active = ~self.done
        distance_before = self.geometry()[0].copy()
        handovers_before, return_before = self.handovers.copy(), self.return_sum.copy()
        obs, mask, _, done, completed = super().step(motion, network)
        distance, _, _, speed = self.geometry()
        rss, interference, _, rate = self.radio_state()
        delay = np.minimum(self.cfg.horizon * self.cfg.dt_s, self.buffer / np.maximum(rate, 1.))
        # Boundary has first priority in the unchanged V2 failure record.
        boundary = np.zeros(self.n, dtype=bool)
        for row in completed:
            boundary[row["lane"]] = row["outcome"] == "boundary"
        reward = original_reward(distance_before, distance, delay, interference,
                                 self.handovers - handovers_before, rss[self.rows, self.serving],
                                 speed, boundary, self.energy >= self.cfg.battery_j) * active
        self.return_sum[:] = return_before + reward
        for row in completed:
            row["raw_return"] = float(self.return_sum[row["lane"]])
        return obs, mask, reward.astype(np.float32), done, completed
