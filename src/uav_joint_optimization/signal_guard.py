"""Signal aware path selection around the unchanged V2.2 rollout rule."""
from copy import copy
from dataclasses import replace

import numpy as np

from .connectivity_guard import strongest_feasible_network


def signal_guard_action(env, proposal, allowance_m, diagnostics=False):
    if allowance_m not in (0, 1, 3, 6):
        raise ValueError('Allowances are 1, 3 or 6 m; zero checks V2.2 identity.')
    horizon = 5
    distance0 = env.geometry()[0]
    primitives = [proposal] + [env.reference_motion(angle, scale) for scale, angle in
        [(1., 0.), (.6, 0.), (0., 0.)] + [(1., a) for a in (-.6, -.3, .3, .6, -1.2, 1.2)]]
    scores, signals, delays, switches, failures, networks = [], [], [], [], [], []
    for first_motion in primitives:
        trial = copy(env)
        trial.__dict__ = {k: v.copy() if isinstance(v, np.ndarray) else v for k, v in env.__dict__.items()}
        trial.cfg = replace(env.cfg, safety_filter=False)
        failed = np.zeros(env.n, dtype=bool)
        survival = np.full(env.n, horizon, dtype=int)
        first_pos, _ = env.predict_motion(first_motion)
        first_distance = np.linalg.norm(env.goal-first_pos, axis=1)
        signal_sum = np.zeros(env.n); counts = np.zeros(env.n, dtype=int)
        first_network = None
        for step in range(horizon):
            active = ~trial.done.copy()
            motion = first_motion if step == 0 else trial.reference_motion()
            network = strongest_feasible_network(trial, motion)
            if step == 0:
                first_network = network.copy()
            _, _, _, _, completed = trial.step(motion, network)
            index = np.clip(trial.t-1, 0, trial.cfg.horizon-1)
            rss = trial.rss_history[trial.rows, index]
            signal_sum += np.where(active, rss+103.41, 0.)
            counts += active
            for row in completed:
                if not row['success']:
                    failed[row['lane']] = True
                    survival[row['lane']] = step+1
            if trial.done.all():
                break
        score = (1e6*failed + 1e4*(horizon-survival) + trial.geometry()[0]
                 - 1e5*trial.ever_success
                 + 1e3*((distance0 > 30.) & (first_distance >= distance0-.1)))
        scores.append(score); signals.append(signal_sum/np.maximum(counts, 1))
        delays.append((trial.delay_sum-env.delay_sum)/np.maximum(counts, 1))
        switches.append(trial.handovers-env.handovers); failures.append(failed)
        networks.append(first_network)
    scores, signals, delays, switches, failures = map(np.asarray, (scores, signals, delays, switches, failures))
    baseline = scores.argmin(axis=0)
    selected = baseline.copy(); lanes = env.rows
    if allowance_m:
        eligible = ((scores <= scores[baseline, lanes]+allowance_m)
                    & ~failures & ~failures[baseline, lanes]
                    & (delays <= delays[baseline, lanes])
                    & (switches <= switches[baseline, lanes])
                    & (signals > signals[baseline, lanes]+1e-6)
                    & (distance0 > 50.) & ~env.done)
        for i in range(len(primitives)):
            better = eligible[i] & ((signals[i] > signals[selected, lanes])
                | ((signals[i] == signals[selected, lanes]) & (scores[i] < scores[selected, lanes])))
            selected[better] = i
    motion = np.asarray(primitives)[selected, lanes]
    network = np.asarray(networks)[selected, lanes]
    if diagnostics:
        return motion, network, {'baseline': baseline, 'selected': selected, 'score': scores,
            'snr': signals, 'delay': delays, 'handovers': switches, 'failed': failures}
    return motion, network
