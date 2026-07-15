# Project Summary

## Research Question

Can a UAV jointly choose a safe, mission completing flight trajectory and cellular handover decisions in a realistic urban 5G channel while improving connectivity, delay, interference, energy, and handover performance?

## Inherited Asset

Marina Bermúdez Granados established a deterministic ray traced Barcelona environment, an MDP, 3GPP A3 handover behavior, radio resource allocation, a greedy controller, and a PPO controller. The environment is the foundation to recover. The controller formulation is the part to redesign.

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

