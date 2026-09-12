# Training, Validation, and Test Separation

Date: 12 September 2026.

## What Was Checked and Why

Checked the saved scenario file, experiment runner, PPO evaluation calls, and
frozen protocol against the original thesis's experimental methods. This
answers whether the positive results use separate development and evaluation
missions and whether the original work documents the same separation.

## Current Experiment

| Split | Routes | Scenario seed | Purpose |
| --- | ---: | ---: | --- |
| Training | 4096 | 42000 | Pool of missions used for policy gradient updates |
| Validation | 64 | 42001 | Pilot learning checks and choice of final training budget |
| Standard test | 200 | 42012 | Final evaluation on routes of 200–1000 m |
| Longer test | 200 | 42013 | Final evaluation on routes of 1000–1800 m |

The saved coordinates are in `configs/controlled_scenarios.json`. An exact
comparison of ordered start and destination coordinate pairs found zero
duplicates between every pair of splits. Different routes can still cross
the same map locations. Seeds 41 and 42 were used for pilots; the final five
training seeds were 1101–1105. These training seeds are distinct from the
scenario generation seeds shown above.

Validation episodes do not enter PPO gradient updates. They were used during
development and are therefore not an independent final test. The final
configuration and interaction budget were frozen before learned policy test
evaluation. All final policies use their last checkpoint, without test based
checkpoint selection. Every treatment and training seed evaluates the same
200 standard and 200 longer routes.

Initial feasibility inspections used separate route seeds 42002 and 42003;
those sets were retired before training. The retained final test results have
now been inspected and must not become tuning feedback for an allegedly
untouched repeat evaluation.

## Meaning of the Separation

This is a separation of mission scenarios within one Barcelona radio map.
The underlying HDF5 radio entries were not split into disjoint geographic
training and test regions. All splits use the same stations, frequency,
altitude, and deterministic background load structure. Scenario resource phase
rotates group labels and does not constitute independent traffic variation.

The reported 100% mission success therefore concerns unseen start and
destination pairs in this shared environment. It is not evidence of success
in an unseen city, independent channel realization, or held out geographic area.
The longer test probes route length extrapolation within the same map.

## Original Thesis

Reviewed the complete thesis text and visually checked Sections 6.1–6.3,
printed pages 14–16 (PDF pages 16–18). Section 6.2, "Optimizing PPO," describes
hyperparameter tuning and reports 300 episodes and 2000 timesteps in Table 4.
Section 6.3, "Configurations," describes PPO versus the greedy benchmark and
experiments varying reward weights. The results then present radio metrics
and example trajectories.

The thesis does not document a three way training, validation, and test
partition, distinct route counts for those purposes, or an independent
geographic holdout. Its references to testing do not themselves establish a
held out test set. No protocol separating tuning feedback from final reported
evaluation is specified in those methods sections.

The defensible conclusion is **not documented**, rather than a claim that
the missing implementation certainly reused the same missions. Original code
and detailed experiment artifacts would be needed to determine its actual
sampling and evaluation behavior. This documentation gap limits confidence in
generalization; it does not by itself prove leakage or establish the cause of
the original navigation failure.

Source: `sources/UAV_Bermudez_Granados_2026_MSc_thesis.pdf`, Sections 6.1–6.3
and 7. No source PDF, experiment code, or paper results were changed for this
comparison.

## Remaining Work and Next Decision

The question is resolved for the saved experiment and the written thesis.
Original implementation details remain unknown. Stronger generalization claims
would require a new frozen experiment with independent geographic or traffic
conditions, while preserving the current scenario split and reported results.
