# Pilots and Frozen Comparison

Date: 12 September 2026. Final comparison frozen before trained policy test results.

## What Was Done and Why

Ran six pilot policies on the native radio map, with the fixed environment and
PPO settings in the protocol. Used only validation routes to check learning
and choose an equal interaction budget. Kept all checkpoints, configurations,
training logs, episode records, and validation trajectories.

## Pilot Results

Each policy received 524,288 environment interactions. Validation has 64 routes.

| Seed | Arm | Mission success | Recorded feasible success | Successful mean time |
| --- | --- | --- | --- | --- |
| 41 | legacy | 10.9375% | 10.9375% | 125.57 s |
| 41 | fixed | 100% | 96.875% | 34.56 s |
| 42 | legacy | 4.6875% | 4.6875% | 136.00 s |
| 42 | terminal_only | 0% | 0% | Undefined |
| 42 | reward_only | 100% | 98.4375% | 60.22 s |
| 42 | fixed | 100% | 100% | 39.59 s |

Successful subsets differ; their time means are descriptive, not matched route
comparisons. The deterministic controller completed all 64 validation routes
after the common emergency handover correction, with 95.3125% recorded feasible
success. These are pilot results, not final evidence.

The legacy validation success initially improved and then deteriorated with
continued training. This is consistent with optimizing a misaligned objective,
but remains an observation rather than proof about the original thesis agent.

## Frozen Final Design

1. Four arms: legacy, terminal_only, reward_only, fixed.
2. Five new training seeds: 1101, 1102, 1103, 1104, 1105.
3. Exactly 524,288 interactions per policy; no early stopping or test checkpoint
   selection. This doubles the approximately 262,144 interactions by which
   corrected pilot policies reached reliable validation completion.
4. Identical shared environment, observations, action interface, learner, and
   hyperparameters. PPO uses 64 lanes, 128 step rollouts, four epochs, 512
   sample minibatches, learning rate 0.0003, gamma 0.99, GAE lambda 0.95, clip
   0.2, latent plus categorical entropy coefficient 0.005, and reward variance
   normalization applied equally to all arms.
5. Final deterministic policy evaluation on 200 new standard routes, seed 42012,
   and 200 longer routes, seed 42013. The same routes and background conditions
   apply to every policy and the deterministic reference.
6. Primary contrast: fixed minus legacy mission success on standard routes.
   Report a paired bootstrap that resamples training seeds and route identities,
   preserving pairing. Other contrasts and the longer route evaluation are
   secondary and reported in full.
7. A positive repair result requires mean standard mission success at least
   90%, mean recorded feasible success at least 90%, and a positive lower 95%
   bootstrap confidence bound for the primary contrast. This is a practical
   gate for drafting a paper, not proof of deployment readiness or novelty.

## Risks and Remaining Work

Five seeds provide limited evidence about training variability. The radio map
is a single received artifact with unresolved original version provenance.
The modeled phase rotates resource labels globally, so it does not constitute
independent stochastic traffic variation. No claim of stochastic load robustness
will be made. Shared velocity and action repairs mean that this factorial study
isolates rewards within a repaired interface, not the original partial state.

The next action is to complete all twenty frozen runs, verify their manifests
and paired scenario identities, and analyze every result without retuning.
