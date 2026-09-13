# Project Summary

Current as of 13 September 2026: V2 with V1.5 as the original reward control
on the same system. The [current paper](../paper/UAV_joint_reward_connectivity_IEEE.pdf)
excludes the historical arrival study. The [result note](37_v15_reward_results.md)
reports 95.7% standard success for both full and original rewards, and 87.3%
versus 85.8% longer success. Neither completion difference establishes improvement.
Faster flights and fewer handovers accompany higher communication delay.

The repository includes all 15 final checkpoints. The private dataset is still
required at the path in [the setup guide](35_dataset_and_model_setup.md).
There are 73 passing tests and 7,600 exactly replayed new evaluations. The
[current status](12_task_status.md) and [delivery record](38_v2_paper_and_model_release.md)
identify completed work and remaining physical model limitations.

The sections below retain the original project scope and source context.

## Research Question

Can a UAV jointly choose a safe, mission completing flight trajectory and cellular handover decisions in a realistic urban 5G channel while improving connectivity, delay, interference, energy, and handover performance?

## Inherited Asset

Marina Bermúdez Granados describes a deterministic Barcelona radio environment
[TFM, printed pp. 6–7, Sec. 3.1], A3 and resource allocation [printed p. 9,
Sec. 3.3.1, Eq. (3)], state/actions/reward [printed p. 12, Sec. 5.2,
Eqs. (13)–(14)], and PPO plus a greedy controller [printed pp. 13–14,
Secs. 5.3–5.4]. The received data and completed reimplementation are documented
in notes 17–25; this initial project summary preserves the earlier plan.

## Main Baseline Failure

The PPO policy optimized secondary telecom rewards but did not reliably reach the destination. Its reward gave a fixed bonus whenever distance decreased, kept producing positive per step radio reward, and deliberately did not terminate at arrival. Mission success was not a reported benchmark metric. The resulting wandering is therefore consistent with the stated optimization problem.

## Working Hypothesis

A mission first constrained formulation with an observable Markov state and a mixed action controller will improve success and stability. Continuous flight control should be separated from masked discrete handover and resource selection. A deterministic graph planner should remain as a reference and safety fallback.

## Minimum Defensible Result

1. Reproduce the legacy environment and greedy and PPO baselines.
2. Validate physical units, state transitions, reward, and termination.
3. Compare all methods on identical scenarios and multiple seeds.
4. Improve mission success without hiding a material regression in outage, delay, energy, or handovers.
5. Report uncertainty and conditional metrics for successful missions.

## Current Limitation

The thesis code URL returns 404 and the channel database is not locally available. Current executable results are formulation diagnostics, not trained policy results.
