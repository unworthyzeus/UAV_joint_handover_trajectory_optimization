# V2.2 Guard Results and Recovered Metrics

Date: 14 September 2026.

The primary fresh comparison supports improved standard mission completion.

The supervisor uses the existing full V2 weights, without new training or a changed reward. It changes action selection through finite lookahead. Development evaluated horizons 3, 5 and 8 on the same 96 validation routes with seed 2101. Full V2 completed 91/96; Goal radio 92/96. Guard totals were 90/96, 92/96 and 92/96. The declared delay tie breaker selected horizon 5.

Fresh tests use 500 standard and 500 longer routes, seeds 55012/55013, and five fixed policy seeds per learned arm. All mission and connectivity requirements remain V2. Results are separate from 53012/53013 and 54012/54013. No controller change followed the fresh tests.

| Controller | Standard success (%), higher is better | Longer success (%), higher is better | Episodes per split | Original thesis comparison |
| --- | ---: | ---: | ---: | --- |
| V1.5 original reward | 93.80 | 89.12 | 2500 | Comparable original joint success NR [printed pp. 16-20]. |
| Full V2 | 94.44 | 90.64 | 2500 | Comparable original joint success NR [printed pp. 16-20]. |
| V2.1 service | 93.16 | 88.64 | 2500 | Comparable original joint success NR [printed pp. 16-20]. |
| V2.2 guarded V2 | 96.44 | 96.32 | 2500 | Comparable original joint success NR [printed pp. 16-20]. |
| Goal radio | 93.60 | 91.60 | 500 | Comparable original joint success NR [printed pp. 16-20]. |
| Joint one step | 94.20 | 87.80 | 500 | Comparable original joint success NR [printed pp. 16-20]. |
| Joint three step | 91.60 | 87.40 | 500 | Comparable original joint success NR [printed pp. 16-20]. |

## Matched Completion Contrasts

| V2.2 minus reference: higher is better for V2.2 | Standard difference (pp), 95% interval | Longer difference (pp), 95% interval |
| --- | --- | --- |
| Full V2 | +2.000 [0.320, 3.681] | +5.680 [3.200, 8.280] |
| V1.5 original reward | +2.640 [0.920, 4.480] | +7.200 [5.160, 9.320] |
| V2.1 service | +3.280 [1.800, 4.880] | +7.680 [5.520, 9.960] |
| Goal radio | +2.840 [0.999, 4.840] | +4.720 [2.360, 7.200] |
| Joint one step | +2.240 [0.360, 4.200] | +8.520 [5.440, 11.600] |
| Joint three step | +4.840 [2.400, 7.400] | +8.920 [6.000, 11.920] |

The primary contrast is guarded versus full V2 standard completion. Intervals use 5,000 crossed seed/route bootstrap draws, seed 65000. Other contrasts are secondary and unadjusted for multiplicity. The five seeds represent reused learned policies, not five new supervisor training runs.

## Service on Common Successful Pairs

### V2.2 versus Full V2

| Metric and preferred direction | Standard reference / V2.2 | Difference, 95% interval | Longer reference / V2.2 | Difference, 95% interval |
| --- | --- | --- | --- | --- |
| SNR (dB), higher is better | 62.238 / 64.667 | +2.429 [2.282, 2.576] | 62.045 / 64.707 | +2.662 [2.563, 2.757] |
| All neighbor RSS power (µW), lower is better | 1.447 / 1.386 | -0.061 [-0.066, -0.057] | 1.536 / 1.465 | -0.072 [-0.075, -0.068] |
| Remaining energy (kJ), higher is better | 91.766 / 91.762 | -0.003 [-0.012, 0.006] | 80.620 / 80.607 | -0.012 [-0.024, 0.001] |
| Executed handovers, lower is better while preserving service | 0.466 / 4.811 | +4.345 [4.133, 4.564] | 1.607 / 10.527 | +8.920 [8.584, 9.233] |
| Delay proxy (s), lower is better | 5.404 / 0.429 | -4.975 [-5.536, -4.441] | 6.609 / 0.498 | -6.111 [-6.472, -5.744] |
| Flight time (s), lower is better | 29.384 / 29.392 | +0.008 [-0.079, 0.075] | 61.330 / 61.288 | -0.042 [-0.157, 0.054] |
| SINR (dB), higher is better | -9.355 / -5.775 | +3.580 [3.426, 3.732] | -9.828 / -6.035 | +3.793 [3.684, 3.896] |
| Cochannel downlink interference (µW), lower is better | 0.741 / 0.566 | -0.174 [-0.182, -0.167] | 0.775 / 0.594 | -0.180 [-0.186, -0.175] |
| Consumed energy (kJ), lower is better | 8.234 / 8.238 | +0.003 [-0.006, 0.012] | 19.380 / 19.393 | +0.012 [-0.001, 0.024] |
| Handovers per second, lower is better while preserving service | 0.014 / 0.161 | +0.147 [0.141, 0.153] | 0.026 / 0.171 | +0.145 [0.140, 0.150] |

Common successes: 2331 standard and 2225 longer. All failures remain in the completion denominator. Different references have different common success subsets.

### V2.2 versus V1.5 original reward

| Metric and preferred direction | Standard reference / V2.2 | Difference, 95% interval | Longer reference / V2.2 | Difference, 95% interval |
| --- | --- | --- | --- | --- |
| SNR (dB), higher is better | 63.346 / 64.676 | +1.331 [0.921, 1.740] | 63.163 / 64.712 | +1.549 [1.100, 1.996] |
| All neighbor RSS power (µW), lower is better | 1.435 / 1.389 | -0.047 [-0.059, -0.034] | 1.530 / 1.474 | -0.055 [-0.068, -0.042] |
| Remaining energy (kJ), higher is better | 91.931 / 91.783 | -0.148 [-0.163, -0.132] | 81.054 / 80.600 | -0.454 [-0.490, -0.420] |
| Executed handovers, lower is better while preserving service | 6.996 / 4.785 | -2.211 [-4.372, -0.032] | 15.933 / 10.575 | -5.358 [-10.431, -0.242] |
| Delay proxy (s), lower is better | 1.991 / 0.417 | -1.574 [-2.377, -0.843] | 2.779 / 0.496 | -2.283 [-3.437, -1.290] |
| Flight time (s), lower is better | 32.576 / 29.335 | -3.241 [-3.578, -3.005] | 66.756 / 61.306 | -5.449 [-5.989, -5.074] |
| SINR (dB), higher is better | -8.237 / -5.771 | +2.466 [2.018, 2.908] | -8.743 / -6.053 | +2.690 [2.208, 3.168] |
| Cochannel downlink interference (µW), lower is better | 0.740 / 0.567 | -0.173 [-0.180, -0.165] | 0.783 / 0.599 | -0.185 [-0.192, -0.177] |
| Consumed energy (kJ), lower is better | 8.069 / 8.217 | +0.148 [0.132, 0.163] | 18.946 / 19.400 | +0.454 [0.420, 0.490] |
| Handovers per second, lower is better while preserving service | 0.210 / 0.161 | -0.049 [-0.113, 0.016] | 0.238 / 0.172 | -0.066 [-0.142, 0.010] |

Common successes: 2303 standard and 2193 longer. All failures remain in the completion denominator. Different references have different common success subsets.

## Failures and All Flight Outage

| Controller / split | RSS failures, lower is better | Buffer failures, lower is better | Timeouts, lower is better | Other failures, lower is better | Mean sampled outage (s), lower is better |
| --- | ---: | ---: | ---: | ---: | ---: |
| V1.5 original reward / test | 151 | 4 | 0 | 0 | 0.0604 |
| V1.5 original reward / longer_test | 249 | 19 | 4 | 0 | 0.0996 |
| Full V2 / test | 124 | 15 | 0 | 0 | 0.0496 |
| Full V2 / longer_test | 178 | 55 | 1 | 0 | 0.0712 |
| V2.1 service / test | 171 | 0 | 0 | 0 | 0.0684 |
| V2.1 service / longer_test | 278 | 5 | 1 | 0 | 0.1112 |
| V2.2 guarded V2 / test | 89 | 0 | 0 | 0 | 0.0356 |
| V2.2 guarded V2 / longer_test | 87 | 0 | 5 | 0 | 0.0348 |
| Goal radio / test | 31 | 1 | 0 | 0 | 0.0620 |
| Goal radio / longer_test | 39 | 2 | 1 | 0 | 0.0780 |
| Joint one step / test | 29 | 0 | 0 | 0 | 0.0580 |
| Joint one step / longer_test | 57 | 2 | 2 | 0 | 0.1140 |
| Joint three step / test | 18 | 0 | 24 | 0 | 0.0360 |
| Joint three step / longer_test | 27 | 0 | 36 | 0 | 0.0540 |

Lower counts and shorter outage are preferable, but the simulator terminates at the first violation. Outage duration is therefore censored and cannot reproduce a continuing source episode.

## Every Fixed Policy Seed

| Seed | V1.5 success standard / longer (%), higher is better | Full V2 success standard / longer (%), higher is better | V2.1 success standard / longer (%), higher is better | V2.2 success standard / longer (%), higher is better |
| --- | --- | --- | --- | --- |
| 2101 | 94.40 / 88.20 | 95.00 / 91.20 | 92.00 / 89.80 | 96.60 / 96.40 |
| 2102 | 95.00 / 90.20 | 94.60 / 91.80 | 94.00 / 88.20 | 96.40 / 96.40 |
| 2103 | 93.20 / 89.00 | 94.60 / 92.80 | 93.40 / 89.80 | 96.40 / 96.40 |
| 2104 | 93.20 / 88.40 | 94.60 / 88.00 | 93.80 / 88.20 | 96.40 / 96.00 |
| 2105 | 93.20 / 89.80 | 93.40 / 89.40 | 92.60 / 87.20 | 96.40 / 96.40 |

Higher success is better in every seed column. The supervisor retains the same five full V2 weights.

## Conclusions and Limits

The primary fresh comparison supports improved standard mission completion.

For the declared completion first, then service priority, V2.2 is the preferred controller among the tested V2 variants in this simulator. It passes the primary completion criterion and reduces delay. This conclusion is about the complete supervised controller, including its extra lookahead computation.

Delay falls by 92.1% on standard and 92.5% on longer common successes. SNR improves by 2.429 and 2.662 dB; SINR also improves, and both all neighbor power and cochannel interference decrease. SNR measures signal relative to noise alone; SINR also accounts for interfering transmitters. The neighbor sum is a map based equation proxy, not measured physical uplink interference.

The cost is more handovers than full V2: 0.466 to 4.811 per standard flight and 1.607 to 10.527 per longer flight. These are executed station switches and therefore extra control overhead. Flight time and energy differences versus full V2 have intervals containing zero; we do not claim an energy saving.

Against the V1.5 original reward control on these same fresh routes, completion improves by 2.640 points [0.920, 4.480] standard and 7.200 [5.160, 9.320] longer. Delay, flight time, signal quality and handover count also improve on their common successes, but V2.2 consumes 0.148 and 0.454 kJ more. It does not improve every objective. These secondary comparisons have unadjusted intervals, and V1.5 is our original reward control on V2, not the unavailable original thesis agent.

SNR, remaining energy, all neighbor RSS power, handover distributions and all flight outage are now recorded. Source SNR figures exceed the maximum implied by its stated equation and this dataset; source energy and handover scaling remain unresolved. The all neighbor metric is an Eq. (9) proxy, not calibrated physical uplink. Any improvement here concerns the specified shared simulator and compared controllers, not a validated repair of the original agent. See note 52 for the source consistency audit.

The next decision must follow the completion and service intervals, including regressions. Further tuning requires another declared protocol and untouched evaluation routes. No such extra tuning is included here.
