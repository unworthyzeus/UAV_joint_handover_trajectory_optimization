"""V2.1 reward candidates on the unchanged frozen V2 transition system.

This adapter changes training rewards only. The V2 radio cost remains the
reporting metric and the score used by the shared prospective safety filter.
"""
from dataclasses import dataclass

import numpy as np

from .connectivity_env import ConnectivityBatch as FrozenBatch, ConnectivityConfig


@dataclass(frozen=True)
class ServiceRewardConfig(ConnectivityConfig):
    service_delay_weight: float = .10
    service_queue_weight: float = .20
    service_handover_weight: float = .03
    service_interference_weight: float = .30
    service_rss_weight: float = 0.
    service_failure_penalty: float = 20.
    delay_scale_s: float = 1.
    rss_reference_dbm: float = -80.
    rss_scale_db: float = 10.


def service_cost(delay, buffer_fraction, handover, interference, rss, config):
    """One second is a normalization scale, not a packet deadline.

The RSS reference shapes the reward and never changes the -96 dBm constraint.
The logarithm retains delay sensitivity beyond the saturated V2 transform.
"""
    c = config
    power = c.interference_beta * interference
    return (c.service_delay_weight * np.log1p(delay / c.delay_scale_s)
            + c.service_queue_weight * buffer_fraction ** 2
            + c.service_handover_weight * handover
            + c.service_interference_weight * power / (1 + power)
            + c.service_rss_weight * np.logaddexp(0., (c.rss_reference_dbm - rss) / c.rss_scale_db))


class ServiceRewardBatch(FrozenBatch):
    """Use identical V2 transitions, observations, mask, filter and metrics."""

    def __init__(self, radio, n, scenarios, reward="service", config=ServiceRewardConfig()):
        if reward not in {"service", "full", "arrival"}:
            raise ValueError(reward)
        self.use_service_reward = reward == "service"
        super().__init__(radio, n, scenarios, "full" if self.use_service_reward else reward, config)

    def step(self, motion, network):
        if not self.use_service_reward:
            return super().step(motion, network)
        active = ~self.done
        phi0 = self.potential().copy()
        prior_return = self.return_sum.copy()
        prior_handovers = self.handovers.copy()
        obs, mask, _, done, completed = super().step(motion, network)
        rss, interference, _, rate = self.radio_state()
        delay = np.minimum(self.cfg.horizon * self.cfg.dt_s,
                           self.buffer / np.maximum(rate, 1.))
        success = np.zeros(self.n, dtype=bool)
        for row in completed:
            success[row["lane"]] = row["success"]
        failure = done & ~success
        phi1 = np.where(done, 0., self.potential())
        costs = service_cost(delay, self.buffer / self.cfg.buffer_bits,
                             self.handovers - prior_handovers, interference,
                             rss[self.rows, self.serving], self.cfg)
        reward = (self.cfg.gamma * phi1 - phi0 - self.cfg.time_cost - costs
                  + self.cfg.success_reward * success
                  - self.cfg.service_failure_penalty * failure) * active
        self.return_sum[:] = prior_return + reward
        for row in completed:
            row["raw_return"] = float(self.return_sum[row["lane"]])
        return obs, mask, reward.astype(np.float32), done, completed
