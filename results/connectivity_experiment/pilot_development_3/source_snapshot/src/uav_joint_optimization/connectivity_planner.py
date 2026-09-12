"""Three step model based reference, evaluated separately from learned policies."""
from copy import copy
from dataclasses import replace

import numpy as np


def lookahead_action(env, horizon=3):
    distance0 = env.geometry()[0]
    best_score = np.full(env.n, np.inf)
    best_motion = env.reference_motion()
    best_choice = np.zeros(env.n, dtype=int)
    primitives = [(1., 0.), (.6, 0.), (0., 0.)] + [(1., a) for a in (-.6, -.3, .3, .6, -1.2, 1.2)]
    for scale, angle in primitives:
        trial = copy(env)
        trial.__dict__ = {key: value.copy() if isinstance(value, np.ndarray) else value
                          for key, value in env.__dict__.items()}
        trial.cfg = replace(env.cfg, safety_filter=False)
        motion = env.reference_motion(angle, scale)
        first_motion = motion.copy()
        first_pos, _ = env.predict_motion(first_motion)
        first_distance = np.linalg.norm(env.goal - first_pos, axis=1)
        first_choice = None
        failed = np.zeros(env.n, dtype=bool)
        for step in range(horizon):
            if step:
                motion = trial.reference_motion()
            choice, _ = trial.greedy_network(motion)
            if first_choice is None:
                first_choice = choice.copy()
            _, _, _, _, completed = trial.step(motion, choice)
            for row in completed:
                failed[row["lane"]] |= not row["success"]
        distance = trial.geometry()[0]
        cost = trial.radio_cost_sum - env.radio_cost_sum
        score = cost + (distance - distance0) / env.cfg.potential_scale_m
        score += 1e4 * failed
        score += 1e3 * ((distance0 > 30.) & (first_distance >= distance0 - .1))
        score -= 20 * trial.ever_success
        better = score < best_score
        best_score[better] = score[better]
        best_motion[better], best_choice[better] = first_motion[better], first_choice[better]
    return best_motion, best_choice
