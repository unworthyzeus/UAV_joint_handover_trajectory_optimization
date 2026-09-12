# Confirmed Reward Experiment Results

Date: 12 September 2026.

## What Was Done and Why

Completed the frozen four treatment, five seed experiment and verified source hashes, configurations, complete route pairing, and every successful episode's position and speed criteria. The purpose is to isolate reward and termination effects within the declared reimplementation.

## Main Results

| Arm | Standard success, mean ± seed SD | Longer success, mean ± seed SD | Standard recorded feasible success |
| --- | --- | --- | --- |
| Legacy reward | 21.4% ± 14.3 | 0.0% ± 0.0 | 20.8% |
| Termination only | 0.0% ± 0.0 | 0.0% ± 0.0 | 0.0% |
| Reward only | 100.0% ± 0.0 | 100.0% ± 0.0 | 98.7% |
| Reward + termination | 99.7% ± 0.7 | 36.1% ± 12.6 | 97.8% |

Primary paired difference: 78.3 percentage points, 95% crossed seed and route bootstrap interval [66.2, 89.5]. There are five independent training seeds and 200 shared routes per split, not 1000 independent training runs.

Prespecified practical positive gate passed: **True**.

## Deterministic Reference and Limits

For test, the deterministic reference achieved 100.0% mission success. Across 997 matched successful learned/reference episodes, the fixed policy used 7.94 s more time, 193.2 J more proxy energy, and 0.62 more handovers on average. These signed differences are learned minus reference. They do not establish superiority to classical control.
For longer_test, the deterministic reference achieved 100.0% mission success. Across 361 matched successful learned/reference episodes, the fixed policy used 14.58 s more time, 589.5 J more proxy energy, and 1.24 more handovers on average. These signed differences are learned minus reference. They do not establish superiority to classical control.

Success conditional metrics for all methods and every training seed are in `per_seed_summary.csv`. Comparing secondary averages across different successful subsets is subject to selection bias. Detailed failure counts, downlink SINR, censored delay, energy proxy, interference, handovers, and bootstrap contrasts are in `statistics.json`.

## Every Seed

| Split | Arm | Seed | Mission success | Recorded feasible success |
| --- | --- | --- | --- | --- |
| test | legacy | 1101 | 27.0% | 26.0% |
| longer_test | legacy | 1101 | 0.0% | 0.0% |
| test | legacy | 1102 | 18.0% | 18.0% |
| longer_test | legacy | 1102 | 0.0% | 0.0% |
| test | legacy | 1103 | 18.0% | 17.0% |
| longer_test | legacy | 1103 | 0.0% | 0.0% |
| test | legacy | 1104 | 2.5% | 2.5% |
| longer_test | legacy | 1104 | 0.0% | 0.0% |
| test | legacy | 1105 | 41.5% | 40.5% |
| longer_test | legacy | 1105 | 0.0% | 0.0% |
| test | terminal_only | 1101 | 0.0% | 0.0% |
| longer_test | terminal_only | 1101 | 0.0% | 0.0% |
| test | terminal_only | 1102 | 0.0% | 0.0% |
| longer_test | terminal_only | 1102 | 0.0% | 0.0% |
| test | terminal_only | 1103 | 0.0% | 0.0% |
| longer_test | terminal_only | 1103 | 0.0% | 0.0% |
| test | terminal_only | 1104 | 0.0% | 0.0% |
| longer_test | terminal_only | 1104 | 0.0% | 0.0% |
| test | terminal_only | 1105 | 0.0% | 0.0% |
| longer_test | terminal_only | 1105 | 0.0% | 0.0% |
| test | reward_only | 1101 | 100.0% | 99.5% |
| longer_test | reward_only | 1101 | 100.0% | 96.0% |
| test | reward_only | 1102 | 100.0% | 100.0% |
| longer_test | reward_only | 1102 | 100.0% | 95.5% |
| test | reward_only | 1103 | 100.0% | 97.5% |
| longer_test | reward_only | 1103 | 100.0% | 94.5% |
| test | reward_only | 1104 | 100.0% | 97.0% |
| longer_test | reward_only | 1104 | 100.0% | 96.5% |
| test | reward_only | 1105 | 100.0% | 99.5% |
| longer_test | reward_only | 1105 | 100.0% | 97.5% |
| test | fixed | 1101 | 100.0% | 97.5% |
| longer_test | fixed | 1101 | 45.5% | 45.0% |
| test | fixed | 1102 | 100.0% | 98.5% |
| longer_test | fixed | 1102 | 27.5% | 26.0% |
| test | fixed | 1103 | 100.0% | 98.5% |
| longer_test | fixed | 1103 | 19.0% | 18.5% |
| test | fixed | 1104 | 98.5% | 96.5% |
| longer_test | fixed | 1104 | 39.5% | 38.5% |
| test | fixed | 1105 | 100.0% | 98.0% |
| longer_test | fixed | 1105 | 49.0% | 48.0% |

## Risks and Remaining Work

The source simulator remains unavailable. These results use shared full observations, continuous motion, candidate masking, emergency handovers, deterministic traffic, a downlink interference proxy, and uncalibrated energy. They cannot be reported as reproducing or beating Marina's trained baseline. A single city and five seeds limit generalization and uncertainty estimates. No field or obstacle safety validation was performed.

## Manuscript and Next Decision

The positive result is documented in the IEEE research draft under `paper/`; see note 23 for its final audit. It includes the deterministic reference, all ablations, the private dataset dependency, and the distinction from original baseline reproduction. The raw shaping identity precedes PPO reward normalization and clipping; the experiment does not isolate those interactions. Next research should recover the original environment and test independent traffic and maps before claiming a broadly useful new control method.
