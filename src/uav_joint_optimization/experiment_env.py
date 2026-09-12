"""Vectorized, explicitly reimplemented UAV benchmark on the received RSS map.

This is not Marina's simulator. See docs/18_experiment_protocol.md for every
assumption. All reward treatments share these dynamics and observations.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

import h5py
import numpy as np


@dataclass(frozen=True)
class EnvironmentConfig:
    dt_s: float = 1.0
    horizon: int = 200
    max_acceleration: float = 5.0
    max_speed: float = 25.0
    goal_radius: float = 10.0
    stop_speed: float = 2.0
    network_interval: int = 5
    a3_db: float = 3.0
    rss_min_dbm: float = -96.0
    max_consecutive_outage: int = 5
    bandwidth_hz: float = 1_440_000.0
    noise_dbm: float = -103.41
    offered_bps: float = 200_000.0
    buffer_bits: float = 1_280_000.0
    battery_j: float = 100_000.0
    gamma: float = 0.99
    success_reward: float = 20.0
    failure_penalty: float = 20.0
    time_cost: float = 0.05
    potential_scale_m: float = 100.0
    radio_cost_weight: float = 0.05


class RadioMap:
    """Load operator 1 at native resolution, preserving integer source values."""
    def __init__(self, path: str | Path, stride: int = 1):
        self.path = str(Path(path).resolve())
        self.stride = stride
        with h5py.File(path, "r") as f:
            ids = np.flatnonzero(f["BS/operator_map"][0] == 1)
            self.station_ids = f["BS/id"][...][ids].astype(int)
            self.positions = f["BS/position"][...][:2, ids].T.astype(np.float32)
            self.x = f["grid/x"][...].ravel()[::stride]
            self.y = f["grid/y"][...].ravel()[::stride]
            self.rss = np.empty((len(ids), len(self.x), len(self.y)), dtype=np.int8)
            for i, station in enumerate(ids):
                self.rss[i] = f["measurements/rss_dBm"][int(station)][::stride, ::stride]
        self.limits = np.array([5000., 3500.], dtype=np.float32)

    def query(self, positions: np.ndarray) -> np.ndarray:
        # The stored coordinate vectors have slightly more than 1 m spacing.
        ix = np.rint(positions[:, 0] / (self.x[1] - self.x[0])).astype(int)
        iy = np.rint(positions[:, 1] / (self.y[1] - self.y[0])).astype(int)
        ix = np.clip(ix, 0, len(self.x) - 1)
        iy = np.clip(iy, 0, len(self.y) - 1)
        return self.rss[:, ix, iy].T.astype(np.float32)


def make_scenarios(count: int, seed: int, low: float = 200., high: float = 1000.) -> list[dict]:
    rng = np.random.default_rng(seed)
    result = []
    while len(result) < count:
        start = rng.uniform([250., 250.], [4750., 3250.])
        angle, distance = rng.uniform(-np.pi, np.pi), rng.uniform(low, high)
        goal = start + distance * np.array([np.cos(angle), np.sin(angle)])
        if np.all(goal >= [150., 150.]) and np.all(goal <= [4850., 3350.]):
            result.append({"id": f"{seed}_{len(result):04d}", "start": start.tolist(),
                           "goal": goal.tolist(), "load_phase": int(rng.integers(12))})
    return result


class UAVBatch:
    """Independent episodes, explicit resets, and a common evaluation endpoint."""
    def __init__(self, radio: RadioMap, n: int, scenarios: list[dict],
                 reward: str = "legacy", terminate_success: bool = False,
                 config: EnvironmentConfig = EnvironmentConfig(), evaluation: bool = False):
        if reward not in {"legacy", "fixed"}:
            raise ValueError("Unknown reward treatment")
        self.radio, self.n, self.scenarios, self.cfg = radio, n, scenarios, config
        self.reward_kind, self.terminate_success, self.evaluation = reward, terminate_success, evaluation
        self.rows = np.arange(n)
        self.episode_number = np.full(n, -1, dtype=int)
        self.pos = np.zeros((n, 2), dtype=np.float32)
        self.vel = self.pos.copy()
        self.goal = self.pos.copy()
        self.start = self.pos.copy()
        self.t = np.zeros(n, dtype=int)
        self.serving = np.zeros(n, dtype=int)
        self.rbg = np.zeros(n, dtype=int)
        self.phase = np.zeros(n, dtype=int)
        self.scenario_index = np.zeros(n, dtype=int)
        self.ever_success = np.zeros(n, dtype=bool)
        self.done = np.zeros(n, dtype=bool)
        self.consecutive_outage = np.zeros(n, dtype=int)
        self.buffer = np.zeros(n, dtype=np.float32)
        self.energy = np.zeros(n, dtype=np.float32)
        self.path = np.zeros(n, dtype=np.float32)
        self.handovers = np.zeros(n, dtype=int)
        self.outage_steps = np.zeros(n, dtype=int)
        self.drop_bits = np.zeros(n, dtype=np.float64)
        self.delay_sum = np.zeros(n, dtype=np.float64)
        self.interference_sum = np.zeros(n, dtype=np.float64)
        self.return_sum = np.zeros(n, dtype=np.float64)
        self.sinr_history = np.zeros((n, config.horizon), dtype=np.float32)
        self.rss_history = self.sinr_history.copy()
        self.reset(np.ones(n, dtype=bool))

    def reset(self, mask: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        ids = np.flatnonzero(mask)
        self.episode_number[ids] += 1
        self.scenario_index[ids] = (ids + self.episode_number[ids] * self.n) % len(self.scenarios)
        for i in ids:
            route = self.scenarios[self.scenario_index[i]]
            self.pos[i], self.start[i], self.goal[i] = route["start"], route["start"], route["goal"]
            self.phase[i] = route["load_phase"]
        self.vel[ids] = 0
        for name in ("t", "consecutive_outage", "buffer", "energy", "path", "handovers",
                     "outage_steps", "drop_bits", "delay_sum", "interference_sum", "return_sum"):
            getattr(self, name)[ids] = 0
        self.ever_success[ids] = self.done[ids] = False
        self.sinr_history[ids] = self.rss_history[ids] = 0
        rss = self.radio.query(self.pos[ids])
        self.serving[ids] = rss.argmax(axis=1)
        # Half the 12 groups are occupied by background traffic at each station.
        self.rbg[ids] = (7 * self.serving[ids] + self.phase[ids] + 6) % 12
        return self.observe()

    def geometry(self):
        delta = self.goal - self.pos
        distance = np.linalg.norm(delta, axis=1)
        radial = delta / np.maximum(distance[:, None], 1e-6)
        radial[distance < 1e-6] = [1., 0.]
        lateral = np.stack([-radial[:, 1], radial[:, 0]], axis=1)
        speed = np.linalg.norm(self.vel, axis=1)
        return distance, radial, lateral, speed

    def potential(self):
        distance, _, _, speed = self.geometry()
        return -(distance + speed ** 2 / (2 * self.cfg.max_acceleration)) / self.cfg.potential_scale_m

    def radio_state(self):
        rss = self.radio.query(self.pos)
        # Treat -128 as no usable path in this declared reimplementation.
        watts = np.where(rss > -128, 10. ** ((rss - 30.) / 10.), 0.)
        occupied = ((self.rbg[:, None] - (7 * np.arange(rss.shape[1])[None, :]
                     + self.phase[:, None])) % 12) < 6
        occupied[self.rows, self.serving] = False
        interference = (watts * occupied).sum(axis=1)
        signal = watts[self.rows, self.serving]
        sinr = signal / (interference + 10. ** ((self.cfg.noise_dbm - 30.) / 10.))
        sinr_db = 10 * np.log10(np.maximum(sinr, 1e-15))
        rate = self.cfg.bandwidth_hz * np.log2(1 + sinr)
        return rss, interference, sinr_db, rate

    def observe(self):
        d, radial, lateral, speed = self.geometry()
        rss, interference, sinr, rate = self.radio_state()
        order = np.argsort(-rss, axis=1, kind="stable")[:, :4]
        self.candidates = np.column_stack([self.serving, order])
        crss = np.take_along_axis(rss, self.candidates, axis=1)
        mask = (crss > rss[self.rows, self.serving, None] + self.cfg.a3_db)
        mask &= crss > self.cfg.rss_min_dbm
        mask &= self.candidates != self.serving[:, None]
        network_tick = (self.t % self.cfg.network_interval == 0) | (rss[self.rows, self.serving] <= self.cfg.rss_min_dbm)
        mask &= network_tick[:, None]
        mask[:, 0] = True
        self.action_mask = mask
        cpos = (self.radio.positions[self.candidates] - self.pos[:, None, :]) / 5000.
        nav = np.column_stack([
            self.pos / self.radio.limits, radial, d / 1000.,
            (self.vel * radial).sum(axis=1) / self.cfg.max_speed,
            (self.vel * lateral).sum(axis=1) / self.cfg.max_speed,
            speed / self.cfg.max_speed, self.t / self.cfg.horizon,
            self.buffer / self.cfg.buffer_bits, self.energy / self.cfg.battery_j,
            self.ever_success, self.phase / 11., self.rbg / 11.,
            (self.t % self.cfg.network_interval) / self.cfg.network_interval,
            sinr / 30., self.consecutive_outage / self.cfg.max_consecutive_outage,
        ])
        obs = np.column_stack([nav, (crss + 70.) / 60., cpos.reshape(self.n, -1),
                               self.candidates / (rss.shape[1] - 1), mask])
        return obs.astype(np.float32), mask.copy()

    def step(self, motion: np.ndarray, network: np.ndarray):
        c = self.cfg
        active = ~self.done
        d0, radial, lateral, _ = self.geometry()
        phi0 = self.potential()
        valid = self.action_mask[self.rows, network] & active
        requested = self.candidates[self.rows, network]
        handover = valid & (requested != self.serving)
        self.serving[handover] = requested[handover]
        self.rbg[handover] = (7 * self.serving[handover] + self.phase[handover] + 6) % 12
        controls = np.clip(motion, -1., 1.)
        controls /= np.maximum(np.linalg.norm(controls, axis=1, keepdims=True), 1.)
        acceleration = c.max_acceleration * (controls[:, :1] * radial + controls[:, 1:] * lateral)
        new_vel = self.vel + acceleration * c.dt_s
        new_vel *= np.minimum(1., c.max_speed / np.maximum(np.linalg.norm(new_vel, axis=1, keepdims=True), 1e-8))
        new_pos = self.pos + .5 * (self.vel + new_vel) * c.dt_s
        boundary = np.any((new_pos < 0) | (new_pos > self.radio.limits), axis=1) & active
        new_pos = np.clip(new_pos, 0, self.radio.limits)
        self.path += np.linalg.norm(new_pos - self.pos, axis=1) * active
        self.pos[active], self.vel[active] = new_pos[active], new_vel[active]
        self.t += active
        d1, _, _, speed = self.geometry()
        rss, interference, sinr, rate = self.radio_state()
        outage = (rss[self.rows, self.serving] <= c.rss_min_dbm) & active
        self.consecutive_outage = np.where(active, np.where(outage, self.consecutive_outage + 1, 0), self.consecutive_outage)
        bits = self.buffer + c.offered_bps * c.dt_s + handover * 4800
        after_service = np.maximum(0., bits - rate * c.dt_s)
        dropped = np.maximum(0., after_service - c.buffer_bits)
        self.buffer[active] = np.minimum(after_service, c.buffer_bits)[active]
        # A zero service rate has unbounded instantaneous backlog/service delay.
        # Censor this proxy at the mission deadline and report it as such.
        delay = np.minimum(c.horizon * c.dt_s, self.buffer / np.maximum(rate, 1.))
        # Engineering propulsion proxy, not a calibrated rotorcraft model.
        self.energy += (100. + .4 * speed ** 2) * c.dt_s * active
        physical_failure = boundary | ((self.energy >= c.battery_j) & active)
        physical_failure |= (self.consecutive_outage >= c.max_consecutive_outage) & active
        arrival = (d1 <= c.goal_radius) & (speed <= c.stop_speed) & ~physical_failure & active
        new_success = arrival & ~self.ever_success
        self.ever_success |= new_success
        timeout = (self.t >= c.horizon) & active
        ends = physical_failure | timeout
        if self.terminate_success or self.evaluation:
            ends |= arrival
        failure = ends & ~self.ever_success
        if self.reward_kind == "legacy":
            reward = (.35 / (1 + 10 * delay) + .30 / (1 + 1e5 * interference)
                      + .35 / (1 + 100 * handover) + 12. * (d1 < d0)
                      - 10. * outage - 10. * boundary)
            reward = np.where(self.energy >= c.battery_j, -10., reward)
        else:
            phi1 = np.where(ends, 0., self.potential())
            shaping = c.gamma * phi1 - phi0
            radio_cost = np.clip(delay, 0, 1) + outage + handover
            reward = (shaping - c.time_cost - c.radio_cost_weight * radio_cost
                      + c.success_reward * new_success - c.failure_penalty * failure)
        reward = reward * active
        self.handovers += handover
        self.outage_steps += outage
        self.drop_bits += dropped * active
        self.delay_sum += delay * active
        self.interference_sum += interference * active
        self.return_sum += reward
        index = np.clip(self.t - 1, 0, c.horizon - 1)
        ai = self.rows[active]
        self.sinr_history[ai, index[active]] = sinr[active]
        self.rss_history[ai, index[active]] = rss[ai, self.serving[active]]
        completed = []
        for i in np.flatnonzero(ends & active):
            steps = int(self.t[i])
            success = bool(self.ever_success[i])
            feasible = success and self.outage_steps[i] / steps <= .05 and self.drop_bits[i] == 0
            reason = "success" if success else ("boundary" if boundary[i] else "energy" if self.energy[i] >= c.battery_j
                       else "connectivity" if physical_failure[i] else "timeout")
            completed.append({"lane": int(i), "scenario_id": self.scenarios[self.scenario_index[i]]["id"],
                "success": success, "recorded_feasible_success": bool(feasible), "outcome": reason,
                "time_s": steps * c.dt_s, "final_distance_m": float(d1[i]), "final_speed_mps": float(speed[i]),
                "path_m": float(self.path[i]), "straight_distance_m": float(np.linalg.norm(self.goal[i]-self.start[i])),
                "energy_proxy_j": float(self.energy[i]), "handovers": int(self.handovers[i]),
                "outage_s": float(self.outage_steps[i] * c.dt_s), "dropped_bits": float(self.drop_bits[i]),
                "delay_proxy_mean_s": float(self.delay_sum[i] / steps),
                "interference_mean_w": float(self.interference_sum[i] / steps),
                "sinr_mean_db": float(self.sinr_history[i, :steps].mean()),
                "sinr_p05_db": float(np.percentile(self.sinr_history[i, :steps], 5)),
                "rss_mean_dbm": float(self.rss_history[i, :steps].mean()), "raw_return": float(self.return_sum[i])})
        self.done |= ends
        obs, mask = self.observe()
        return obs, mask, reward.astype(np.float32), ends & active, completed

    def pd_action(self):
        d, radial, lateral, _ = self.geometry()
        desired_speed = np.minimum(self.cfg.max_speed, .7 * np.sqrt(2 * self.cfg.max_acceleration * np.maximum(d-4, 0)))
        acceleration = (desired_speed[:, None] * radial - self.vel) / self.cfg.dt_s
        motion = np.column_stack([(acceleration * radial).sum(axis=1), (acceleration * lateral).sum(axis=1)]) / self.cfg.max_acceleration
        # Highest RSS admissible request; index 1 is the strongest candidate.
        network = np.where(self.action_mask[:, 1], 1, 0)
        return motion, network
