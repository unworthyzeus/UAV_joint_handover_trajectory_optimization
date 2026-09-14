# V2.1 Fresh Evaluation Results

Date: 14 September 2026.

The fresh standard comparison does not establish improved completion over full V2.

The standard paired delay difference is -3.451 s and the handover difference is +9.437, conditional on common successes.

These results use **500 new standard and 500 new longer routes**, seeds 54012 and 54013. They are separate from every 53012/53013 result in the original reward comparison. Five V2.1 models were trained from scratch with seeds 2101-2105 and 524,288 interactions each. The ten V1.5 and full V2 controls were reused with their original hashes, the same training pool and per policy budget.

| Controller | Standard success | Longer success | Evaluations per split | Original thesis comparison |
| --- | ---: | ---: | ---: | --- |
| V2.1 service | 95.48% | 88.60% | 2,500 | Comparable original joint success NR [printed pp. 16-20, Sec. 7]. |
| Full V2 | 96.92% | 91.84% | 2,500 | Comparable original joint success NR [printed pp. 16-20, Sec. 7]. |
| Original reward V1.5 | 96.04% | 89.48% | 2,500 | Comparable original joint success NR [printed pp. 16-20, Sec. 7]. |
| Goal radio | 97.40% | 91.80% | 500 | Comparable original joint success NR [printed pp. 16-20, Sec. 7]. |
| Joint one step | 96.20% | 91.40% | 500 | Comparable original joint success NR [printed pp. 16-20, Sec. 7]. |
| Joint three step | 94.00% | 92.80% | 500 | Comparable original joint success NR [printed pp. 16-20, Sec. 7]. |

## Completion and Failure Counts

| Contrast: V2.1 minus reference | Standard difference (pp), 95% interval | Longer difference (pp), 95% interval |
| --- | --- | --- |
| Full V2 | -1.440 [-3.160, 0.320] | -3.240 [-5.640, -0.880] |
| Original reward V1.5 | -0.560 [-2.040, 0.760] | -0.880 [-2.921, 1.160] |
| Goal radio | -1.920 [-3.480, -0.360] | -3.200 [-6.040, -0.280] |
| Joint one step | -0.720 [-2.400, 0.960] | -2.800 [-5.720, 0.120] |
| Joint three step | +1.480 [-1.000, 3.960] | -4.200 [-7.160, -1.280] |

Primary: V2.1 minus full V2 on standard routes. Crossed seed/route bootstrap uses 5,000 draws and seed 64000. Other contrasts and metric intervals are secondary and unadjusted for multiplicity. The deterministic comparator record is paired with each learned seed without counting those reused pairings as additional evaluations.

| Arm / split | RSS failures | Buffer failures | Energy | Boundary | Timeout | Total failures |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| V2.1 service / test | 111 | 2 | 0 | 0 | 0 | 113 |
| V2.1 service / longer_test | 276 | 4 | 0 | 0 | 5 | 285 |
| Full V2 / test | 71 | 6 | 0 | 0 | 0 | 77 |
| Full V2 / longer_test | 160 | 39 | 0 | 0 | 5 | 204 |
| Original reward V1.5 / test | 96 | 3 | 0 | 0 | 0 | 99 |
| Original reward V1.5 / longer_test | 244 | 14 | 0 | 0 | 5 | 263 |
| Goal radio / test | 13 | 0 | 0 | 0 | 0 | 13 |
| Goal radio / longer_test | 37 | 3 | 0 | 0 | 1 | 41 |
| Joint one step / test | 17 | 0 | 0 | 0 | 2 | 19 |
| Joint one step / longer_test | 38 | 2 | 0 | 0 | 3 | 43 |
| Joint three step / test | 7 | 0 | 0 | 0 | 23 | 30 |
| Joint three step / longer_test | 12 | 0 | 0 | 0 | 24 | 36 |

## Conditional Service: V2.1 versus Full V2

Values below are means on common successful seed/route pairs. Each contrast has its own intersection; do not compare a reference mean from one intersection with a V2.1 mean from another.

| Metric | Standard reference | Standard V2.1 | Difference, 95% interval | Longer reference | Longer V2.1 | Difference, 95% interval |
| --- | ---: | ---: | --- | ---: | ---: | --- |
| Flight time (s), lower | 28.347 | 28.594 | +0.246 [0.020, 0.520] | 60.409 | 60.785 | +0.376 [0.039, 0.747] |
| Delay proxy (s), lower | 4.742 | 1.291 | -3.451 [-3.957, -2.962] | 6.199 | 1.583 | -4.616 [-4.957, -4.287] |
| Handovers, lower with service | 0.402 | 9.839 | +9.437 [8.968, 9.897] | 1.442 | 23.058 | +21.616 [20.923, 22.287] |
| Consumed energy (kJ), lower | 7.873 | 7.868 | -0.005 [-0.014, 0.005] | 19.057 | 19.032 | -0.025 [-0.049, 0.002] |
| SINR (dB), higher | -8.916 | -7.457 | +1.459 [1.296, 1.628] | -9.745 | -7.978 | +1.767 [1.662, 1.870] |
| Interference (µW), lower | 0.736 | 0.725 | -0.011 [-0.019, -0.002] | 0.763 | 0.755 | -0.009 [-0.016, -0.002] |
| Fixed V2 radio cost, lower | 5.174 | 6.923 | +1.749 [1.520, 1.983] | 13.437 | 16.269 | +2.832 [2.377, 3.280] |
| Path length (m) | 557.362 | 557.482 | +0.120 [-0.321, 0.497] | 1356.774 | 1356.988 | +0.214 [-0.315, 0.717] |
| Queue at arrival (kbit), lower | 282.172 | 21.100 | -261.072 [-292.349, -231.059] | 352.926 | 17.985 | -334.941 [-365.717, -304.963] |
| Network filter interventions | 0.448 | 0.039 | -0.409 [-0.475, -0.344] | 1.709 | 0.117 | -1.592 [-1.710, -1.476] |
| Motion filter interventions | 0.005 | 0.004 | -0.001 [-0.008, 0.005] | 0.027 | 0.018 | -0.009 [-0.030, 0.009] |

Common successes: 2335 standard and 2086 longer pairs. Higher SINR is preferable; no SINR percentage change is computed. A shorter path or fewer interventions is not intrinsically better if it compromises service or mission success.

## Conditional Service: V2.1 versus Original reward V1.5

Values below are means on common successful seed/route pairs. Each contrast has its own intersection; do not compare a reference mean from one intersection with a V2.1 mean from another.

| Metric | Standard reference | Standard V2.1 | Difference, 95% interval | Longer reference | Longer V2.1 | Difference, 95% interval |
| --- | ---: | ---: | --- | ---: | ---: | --- |
| Flight time (s), lower | 31.539 | 28.598 | -2.941 [-3.303, -2.601] | 65.768 | 60.799 | -4.968 [-5.593, -4.371] |
| Delay proxy (s), lower | 2.017 | 1.285 | -0.732 [-1.578, 0.014] | 2.624 | 1.576 | -1.048 [-2.200, -0.046] |
| Handovers, lower with service | 6.835 | 9.823 | +2.988 [0.862, 5.138] | 15.609 | 22.993 | +7.384 [1.885, 12.923] |
| Consumed energy (kJ), lower | 7.739 | 7.870 | +0.131 [0.108, 0.155] | 18.627 | 19.038 | +0.411 [0.355, 0.468] |
| SINR (dB), higher | -8.036 | -7.448 | +0.587 [0.107, 1.067] | -8.620 | -7.981 | +0.639 [0.174, 1.100] |
| Interference (µW), lower | 0.731 | 0.724 | -0.007 [-0.014, -0.001] | 0.764 | 0.757 | -0.006 [-0.011, -0.001] |
| Fixed V2 radio cost, lower | 7.004 | 6.908 | -0.096 [-0.363, 0.196] | 16.254 | 16.243 | -0.010 [-0.724, 0.738] |
| Path length (m) | 553.913 | 557.627 | +3.713 [3.014, 4.428] | 1353.571 | 1357.405 | +3.834 [3.135, 4.451] |
| Queue at arrival (kbit), lower | 95.535 | 21.055 | -74.480 [-150.240, -11.469] | 105.803 | 17.734 | -88.069 [-166.212, -15.004] |
| Network filter interventions | 0.128 | 0.041 | -0.087 [-0.175, -0.010] | 0.410 | 0.113 | -0.297 [-0.626, -0.023] |
| Motion filter interventions | 0.009 | 0.004 | -0.005 [-0.014, 0.002] | 0.027 | 0.017 | -0.010 [-0.033, 0.010] |

Common successes: 2334 standard and 2056 longer pairs. Higher SINR is preferable; no SINR percentage change is computed. A shorter path or fewer interventions is not intrinsically better if it compromises service or mission success.

## Every Training Seed

| Seed | V1.5 standard / longer | Full V2 standard / longer | V2.1 standard / longer |
| --- | --- | --- | --- |
| 2101 | 95.20% / 89.20% | 96.80% / 91.20% | 95.00% / 87.20% |
| 2102 | 96.60% / 89.20% | 97.20% / 91.20% | 96.40% / 89.00% |
| 2103 | 97.00% / 89.80% | 97.00% / 92.60% | 95.40% / 88.40% |
| 2104 | 95.40% / 89.00% | 96.60% / 91.40% | 96.00% / 88.40% |
| 2105 | 96.00% / 90.20% | 97.00% / 92.80% | 94.60% / 90.00% |

## Conclusion, Validation and Remaining Work

The fresh standard comparison does not establish improved completion over full V2.
The longer route interval supports lower completion than full V2.
The standard paired delay difference is -3.451 s and the handover difference is +9.437, conditional on common successes.
The failure breakdown explains why fewer overflows did not improve completion: standard RSS failures increase from 71 to 111 while buffer failures decrease from 6 to 2; longer RSS failures increase from 160 to 276 while buffer failures decrease from 39 to 4. Timeout counts stay unchanged. This identifies the recorded failure category, not the isolated causal contribution of switching or motion.
V2.1 remains an evaluated research candidate. It is not promoted as a replacement for full V2 unless the declared completion and delay reporting gate is met. Lower delay alone does not satisfy the user's completion first priority.
The prespecified joint completion and delay reporting gate is **not met**. A null completion result is not equivalence. Any service improvement is conditional on the declared common successes; it does not prove a better controller on every objective or improvement over the unavailable thesis simulator.
All 18,000 final episodes replayed exactly. The five V2.1 checkpoint hashes were fixed before testing; the ten reused control checkpoint hashes and all historical freezes still match. No retraining, new candidate, checkpoint selection or test route selection followed test outcomes. The 88 implementation tests assess software behavior, not physical calibration.
The next decision must respect completion first: retain unfavorable outcomes, investigate the shared control limits with a separately declared study, and reserve new evaluation data for any further tuning. The same map, static traffic, energy proxy, ideal switching and sampled connectivity limits remain. The original thesis results are still limited to its reported figures and definitions [printed pp. 16-21, Secs. 7-8].
