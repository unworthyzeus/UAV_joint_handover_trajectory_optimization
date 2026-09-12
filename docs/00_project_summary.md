# Project Summary

The latest completed work is the strict connectivity study in notes 28–32.
It restores the sampled RSS and buffer constraints and all three thesis radio
costs. Full PPO reaches 96.6% / 89.7% standard/longer joint success, while the
goal directed radio controller reaches 98.0% / 92.5%. Weighted cost improves
but PPO delay worsens; learned completion differences are uncertain. The
four page `paper/UAV_connectivity_repair_IEEE.pdf` reports the results. Earlier
arrival reward findings remain a separate, preserved study.

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
