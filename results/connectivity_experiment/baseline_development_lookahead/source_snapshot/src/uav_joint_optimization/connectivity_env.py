"""Thesis communication constraints in a separately versioned surrogate.

Preserves the v1 map, motion, traffic, energy and SINR capacity assumptions.
Adds strict sampled RSS and buffer feasibility, restores all three radio costs,
and exposes available RBG choices. This is not the original thesis simulator.
"""
from dataclasses import dataclass

import numpy as np

from .experiment_env import EnvironmentConfig, UAVBatch


@dataclass(frozen=True)
class ConnectivityConfig(EnvironmentConfig):
    network_interval: int = 1
    radio_cost_weight: float = 1.0
    delay_weight: float = .35
    interference_weight: float = .30
    handover_weight: float = .35
    delay_beta: float = 10.0
    interference_beta: float = 1e5
    handover_beta: float = 100.0
    safety_filter: bool = True


class ConnectivityBatch(UAVBatch):
    """61 network actions: stay, then five candidate slots by twelve RBGs."""

    def __init__(self, radio, n, scenarios, reward="full", config=ConnectivityConfig()):
        self.objective = reward
        if reward not in {"arrival", "full"}:
            raise ValueError(reward)
        self.resource_changes = np.zeros(n, dtype=int)
        self.radio_cost_sum = np.zeros(n)
        self.arrived = np.zeros(n, dtype=bool)
        self.bad_rss_ever = np.zeros(n, dtype=bool)
        self.bad_buffer_ever = np.zeros(n, dtype=bool)
        self.network_interventions = np.zeros(n, dtype=int)
        self.motion_interventions = np.zeros(n, dtype=int)
        super().__init__(radio, n, scenarios, "fixed", True, config, evaluation=True)

    def reset(self, mask):
        for name in ("resource_changes", "radio_cost_sum", "arrived", "bad_rss_ever", "bad_buffer_ever",
                     "network_interventions", "motion_interventions"):
            getattr(self, name)[mask] = 0
        result = super().reset(mask)
        rss = self.radio.query(self.pos)
        self.bad_rss_ever[mask] = (rss[self.rows, self.serving] < self.cfg.rss_min_dbm)[mask]
        return result

    def free_groups(self, stations):
        return ((np.arange(12) - (7 * stations[..., None] + self.phase[:, None, None])) % 12) >= 6

    def options_at(self, positions):
        """Return signal and cochannel interference for the current action map."""
        rss = self.radio.query(positions)
        watts = np.where(rss > -128, 10. ** ((rss - 30.) / 10.), 0.)
        occupied = ((np.arange(12)[None, None, :] - (7 * np.arange(rss.shape[1])[None, :, None]
                     + self.phase[:, None, None])) % 12) < 6
        totals = np.einsum("nk,nkg->ng", watts, occupied)
        signal = np.take_along_axis(watts, self.option_station, axis=1)
        serving_occupied = ((self.option_rbg - (7 * self.option_station + self.phase[:, None])) % 12) < 6
        interference = np.take_along_axis(totals, self.option_rbg, axis=1) - signal * serving_occupied
        interference = np.maximum(interference, 0.)
        sinr = signal / (interference + 10. ** ((self.cfg.noise_dbm - 30.) / 10.))
        rate = self.cfg.bandwidth_hz * np.log2(1 + sinr)
        crss = np.take_along_axis(rss, self.option_station, axis=1)
        return crss, interference, rate

    def observe(self):
        d, radial, lateral, speed = self.geometry()
        rss, _, sinr, _ = self.radio_state()
        order = np.argsort(-rss, axis=1, kind="stable")[:, :4]
        self.candidates = np.column_stack([self.serving, order])
        crss = np.take_along_axis(rss, self.candidates, axis=1)
        same = self.candidates == self.serving[:, None]
        station_valid = same | ((crss > rss[self.rows, self.serving, None] + self.cfg.a3_db)
                               & (crss >= self.cfg.rss_min_dbm))
        # Candidate zero already represents every RBG at the serving cell.
        station_valid[:, 1:] &= ~same[:, 1:]
        self.option_station = np.column_stack([self.serving, np.repeat(self.candidates, 12, axis=1)])
        self.option_rbg = np.column_stack([self.rbg, np.tile(np.arange(12), (self.n, 5))])
        valid = (station_valid[..., None] & self.free_groups(self.candidates)).reshape(self.n, -1)
        self.action_mask = np.column_stack([np.ones(self.n, dtype=bool), valid])
        _, _, rate = self.options_at(self.pos)
        nav = np.column_stack([
            self.pos / self.radio.limits, radial, d / 1000.,
            (self.vel * radial).sum(axis=1) / self.cfg.max_speed,
            (self.vel * lateral).sum(axis=1) / self.cfg.max_speed,
            speed / self.cfg.max_speed, self.t / self.cfg.horizon,
            self.buffer / self.cfg.buffer_bits, self.energy / self.cfg.battery_j,
            self.phase / 11., self.rbg / 11., sinr / 30.,
        ])
        cpos = (self.radio.positions[self.candidates] - self.pos[:, None, :]) / 5000.
        obs = np.column_stack([nav, (crss + 70.) / 60., cpos.reshape(self.n, -1),
                               self.candidates / (rss.shape[1] - 1),
                               np.log1p(rate / max(self.cfg.offered_bps, 1.)), self.action_mask])
        return obs.astype(np.float32), self.action_mask.copy()

    def predict_motion(self, motion):
        _, radial, lateral, _ = self.geometry()
        controls = np.clip(motion, -1., 1.)
        controls /= np.maximum(np.linalg.norm(controls, axis=1, keepdims=True), 1.)
        acc = self.cfg.max_acceleration * (controls[:, :1] * radial + controls[:, 1:] * lateral)
        vel = self.vel + acc * self.cfg.dt_s
        vel *= np.minimum(1., self.cfg.max_speed / np.maximum(np.linalg.norm(vel, axis=1, keepdims=True), 1e-8))
        pos = self.pos + .5 * (self.vel + vel) * self.cfg.dt_s
        return pos.astype(np.float32), vel.astype(np.float32)

    def communication_cost(self, delay, interference, handover):
        c = self.cfg
        # One minus the original reciprocal utility. Avoid its positive alive bonus.
        d = c.delay_beta * delay
        i = c.interference_beta * interference
        h = c.handover_beta * handover
        return c.delay_weight * d / (1 + d) + c.interference_weight * i / (1 + i) + c.handover_weight * h / (1 + h)

    def step(self, motion, network):
        c = self.cfg
        active = ~self.done
        if c.safety_filter:
            motion, network = self.filter_action(motion, network)
        phi0 = self.potential()
        valid = self.action_mask[self.rows, network] & active
        station = self.option_station[self.rows, network]
        group = self.option_rbg[self.rows, network]
        handover = valid & (station != self.serving)
        changed = valid & ((station != self.serving) | (group != self.rbg))
        self.serving[valid], self.rbg[valid] = station[valid], group[valid]
        pos, vel = self.predict_motion(motion)
        boundary = np.any((pos < 0) | (pos > self.radio.limits), axis=1) & active
        pos = np.clip(pos, 0, self.radio.limits)
        self.path += np.linalg.norm(pos - self.pos, axis=1) * active
        self.pos[active], self.vel[active] = pos[active], vel[active]
        self.t += active
        distance, _, _, speed = self.geometry()
        rss, interference, sinr, rate = self.radio_state()
        # The written C2 allows equality. Do not silently substitute <= here.
        outage = ((rss[self.rows, self.serving] < c.rss_min_dbm) | self.bad_rss_ever) & active
        bits = self.buffer + c.offered_bps * c.dt_s + handover * 4800
        after = np.maximum(0., bits - rate * c.dt_s)
        dropped = np.maximum(0., after - c.buffer_bits)
        overflow = (dropped > 0) & active
        self.buffer[active] = np.minimum(after, c.buffer_bits)[active]
        delay = np.minimum(c.horizon * c.dt_s, self.buffer / np.maximum(rate, 1.))
        self.energy += (100. + .4 * speed ** 2) * c.dt_s * active
        energy_failure = (self.energy >= c.battery_j) & active
        arrival = (distance <= c.goal_radius) & (speed <= c.stop_speed) & active
        self.arrived |= arrival
        self.bad_rss_ever |= outage
        self.bad_buffer_ever |= overflow
        violation = boundary | energy_failure | outage | overflow
        success = arrival & ~violation
        timeout = (self.t >= c.horizon) & active
        ends = violation | success | timeout
        failure = ends & ~success
        self.ever_success |= success
        phi1 = np.where(ends, 0., self.potential())
        costs = self.communication_cost(delay, interference, handover)
        reward = (c.gamma * phi1 - phi0 - c.time_cost
                  - (c.radio_cost_weight * costs if self.objective == "full" else 0.)
                  + c.success_reward * success - c.failure_penalty * failure) * active
        self.handovers += handover
        self.resource_changes += changed
        self.outage_steps += outage
        self.drop_bits += dropped * active
        self.delay_sum += delay * active
        self.interference_sum += interference * active
        self.radio_cost_sum += costs * active
        self.return_sum += reward
        index = np.clip(self.t - 1, 0, c.horizon - 1)
        ai = self.rows[active]
        self.sinr_history[ai, index[active]] = sinr[active]
        self.rss_history[ai, index[active]] = rss[ai, self.serving[active]]
        completed = []
        for i in np.flatnonzero(ends & active):
            steps = int(self.t[i])
            reason = ("boundary" if boundary[i] else "energy" if energy_failure[i] else
                      "connectivity" if outage[i] else "buffer" if overflow[i] else
                      "success" if success[i] else "timeout")
            completed.append({"lane": int(i), "scenario_id": self.scenarios[self.scenario_index[i]]["id"],
                "success": bool(success[i]), "arrival_at_endpoint": bool(self.arrived[i]), "outcome": reason,
                "time_s": steps * c.dt_s, "final_distance_m": float(distance[i]), "final_speed_mps": float(speed[i]),
                "path_m": float(self.path[i]), "straight_distance_m": float(np.linalg.norm(self.goal[i] - self.start[i])),
                "energy_proxy_j": float(self.energy[i]), "handovers": int(self.handovers[i]),
                "resource_changes": int(self.resource_changes[i]), "outage_s": float(self.outage_steps[i] * c.dt_s),
                "network_interventions": int(self.network_interventions[i]),
                "motion_interventions": int(self.motion_interventions[i]),
                "dropped_bits": float(self.drop_bits[i]), "final_buffer_bits": float(self.buffer[i]),
                "delay_proxy_mean_s": float(self.delay_sum[i] / steps),
                "interference_mean_w": float(self.interference_sum[i] / steps),
                "radio_cost_sum": float(self.radio_cost_sum[i]), "radio_cost_mean": float(self.radio_cost_sum[i] / steps),
                "sinr_mean_db": float(self.sinr_history[i, :steps].mean()),
                "sinr_p05_db": float(np.percentile(self.sinr_history[i, :steps], 5)),
                "minimum_rss_dbm": float(self.rss_history[i, :steps].min()), "raw_return": float(self.return_sum[i])})
        self.done |= ends
        obs, mask = self.observe()
        return obs, mask, reward.astype(np.float32), ends & active, completed

    def filter_action(self, motion, network):
        """Reject predicted sampled RSS/queue violations when a safe option exists.

Uses the same known map and dynamics as the model based references. It is a
separate control component, not a learned guarantee. An empty feasible set can
still end in failure; no violation is relabeled successful.
"""
        original_motion, original_network = motion.copy(), network.copy()
        pos, _ = self.predict_motion(motion)
        rss, _, rate = self.options_at(pos)
        ho = self.option_station != self.serving[:, None]
        after = np.maximum(0., self.buffer[:, None] + self.cfg.offered_bps * self.cfg.dt_s + ho * 4800 - rate * self.cfg.dt_s)
        feasible = self.action_mask & (rss >= self.cfg.rss_min_dbm) & (after <= self.cfg.buffer_bits)
        inside = ~np.any((pos < 0) | (pos > self.radio.limits), axis=1)
        safe = feasible[self.rows, network] & inside
        need = ~safe & ~self.done
        if not need.any():
            return motion, network
        alternative, score = self.greedy_network(motion)
        repair_network = need & (score < 1e4) & inside
        network = np.where(repair_network, alternative, network)
        unresolved = need & ~repair_network
        if unresolved.any():
            fallback_motion, fallback_network = self.controller("joint_mpc")
            motion = np.where(unresolved[:, None], fallback_motion, motion)
            network = np.where(unresolved, fallback_network, network)
        self.network_interventions += need & (network != original_network)
        self.motion_interventions += unresolved & np.any(motion != original_motion, axis=1)
        return motion, network

    def reference_motion(self, angle=0., speed_scale=1.):
        d, radial, lateral, _ = self.geometry()
        direction = np.cos(angle) * radial + np.sin(angle) * lateral
        desired = speed_scale * np.minimum(self.cfg.max_speed, .7 * np.sqrt(2 * self.cfg.max_acceleration * np.maximum(d - 4, 0)))
        acc = (desired[:, None] * direction - self.vel) / self.cfg.dt_s
        return np.column_stack([(acc * radial).sum(axis=1), (acc * lateral).sum(axis=1)]) / self.cfg.max_acceleration

    def greedy_network(self, motion, prospective=True):
        """Model based association and RBG choice for a specified motion."""
        pos, _ = self.predict_motion(motion)
        crss, interference, rate = self.options_at(pos if prospective else self.pos)
        handover = self.option_station != self.serving[:, None]
        after = np.maximum(0., self.buffer[:, None] + self.cfg.offered_bps * self.cfg.dt_s + handover * 4800 - rate * self.cfg.dt_s)
        delay = np.minimum(self.cfg.horizon * self.cfg.dt_s, after / np.maximum(rate, 1.))
        cost = self.communication_cost(delay, interference, handover)
        bad = (crss < self.cfg.rss_min_dbm) | (after > self.cfg.buffer_bits)
        score = cost + 1e4 * bad
        score[~self.action_mask] = 1e9
        choice = score.argmin(axis=1)
        return choice, score[self.rows, choice]

    def controller(self, kind):
        if kind == "joint_lookahead":
            from .connectivity_planner import lookahead_action
            return lookahead_action(self)
        motion = self.reference_motion()
        if kind == "straight_rss":
            # Original v1 reference rule, now evaluated against strict constraints.
            best = self.candidates[:, 1]
            group = (7 * best + self.phase + 6) % 12
            option = 1 + 12 + group
            choice = np.where(self.action_mask[self.rows, option], option, 0)
            return motion, choice
        if kind == "straight_radio":
            choice, _ = self.greedy_network(motion)
            return motion, choice
        if kind != "joint_mpc":
            raise ValueError(kind)
        best_score = np.full(self.n, np.inf)
        best_motion, best_choice = motion.copy(), np.zeros(self.n, dtype=int)
        distance0 = self.geometry()[0]
        # A small, declared set of dynamically feasible local motion alternatives.
        for scale, angle in [(1., 0.), (.6, 0.), (0., 0.)] + [(1., a) for a in (-.6, -.3, .3, .6, -1.2, 1.2)]:
            candidate = self.reference_motion(angle, scale)
            choice, radio_score = self.greedy_network(candidate)
            pos, vel = self.predict_motion(candidate)
            distance = np.linalg.norm(self.goal - pos, axis=1)
            boundary = np.any((pos < 0) | (pos > self.radio.limits), axis=1)
            # Progress in units of 100 m, plus original normalized radio cost.
            score = radio_score + (distance - distance0) / self.cfg.potential_scale_m + 1e5 * boundary
            # Feasibility takes priority, then avoid a stationary low cost trap.
            # If every progressing candidate is unsafe, a safe braking candidate
            # may still be selected; no global reachability guarantee is implied.
            score += 1e3 * ((distance0 > 30.) & (distance >= distance0 - .1))
            # Prevent near goal loitering for a radio improvement after safe arrival.
            score -= 20 * ((distance <= self.cfg.goal_radius) & (np.linalg.norm(vel, axis=1) <= self.cfg.stop_speed))
            improve = score < best_score
            best_score[improve] = score[improve]
            best_motion[improve], best_choice[improve] = candidate[improve], choice[improve]
        return best_motion, best_choice
