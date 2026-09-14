"""Declared finite lookahead supervisor around a fixed V2 PPO proposal."""
from copy import copy
from dataclasses import replace

import numpy as np


def strongest_feasible_network(env, motion):
    position, _ = env.predict_motion(motion)
    rss, _, rate = env.options_at(position)
    handover = env.option_station != env.serving[:, None]
    after = np.maximum(0., env.buffer[:, None] + env.cfg.offered_bps * env.cfg.dt_s
                       + 4800 * handover - rate * env.cfg.dt_s)
    bad = (rss < env.cfg.rss_min_dbm) | (after > env.cfg.buffer_bits)
    # The bounded tie breaker cannot overturn a one dB RSS difference.
    tie = .001 * rate / (rate + 1e6)
    score = 1e6 * bad - rss - tie
    score[~env.action_mask] = np.inf
    return score.argmin(axis=1)


def guarded_action(env, proposal, horizon):
    if horizon not in (3, 5, 8):
        raise ValueError('The declared horizons are 3, 5 and 8.')
    distance0 = env.geometry()[0]
    primitives = [proposal] + [env.reference_motion(angle, scale) for scale, angle in
        [(1., 0.), (.6, 0.), (0., 0.)] + [(1., a) for a in (-.6, -.3, .3, .6, -1.2, 1.2)]]
    best_score = np.full(env.n, np.inf)
    best_motion = proposal.copy(); best_network = np.zeros(env.n, dtype=int)
    for first_motion in primitives:
        trial = copy(env)
        trial.__dict__ = {k: v.copy() if isinstance(v, np.ndarray) else v for k, v in env.__dict__.items()}
        trial.cfg = replace(env.cfg, safety_filter=False)
        failed = np.zeros(env.n, dtype=bool)
        survival = np.full(env.n, horizon, dtype=int)
        first_pos, _ = env.predict_motion(first_motion)
        first_distance = np.linalg.norm(env.goal - first_pos, axis=1)
        first_network = None
        for step in range(horizon):
            motion = first_motion if step == 0 else trial.reference_motion()
            network = strongest_feasible_network(trial, motion)
            if step == 0:
                first_network = network.copy()
            _, _, _, _, completed = trial.step(motion, network)
            for row in completed:
                if not row['success']:
                    failed[row['lane']] = True
                    survival[row['lane']] = step + 1
            if trial.done.all():
                break
        distance = trial.geometry()[0]
        score = (1e6 * failed + 1e4 * (horizon - survival) + distance
                 - 1e5 * trial.ever_success
                 + 1e3 * ((distance0 > 30.) & (first_distance >= distance0 - .1)))
        better = score < best_score
        best_score[better] = score[better]
        best_motion[better] = first_motion[better]
        best_network[better] = first_network[better]
    return best_motion, best_network
