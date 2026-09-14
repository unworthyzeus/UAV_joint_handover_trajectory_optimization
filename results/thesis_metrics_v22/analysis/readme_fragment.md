## Recovered Thesis Metrics and V2.2 Controller Test

**We now report SNR, remaining energy, all neighbor RSS power, handover distributions and all flight outage.** The all neighbor power is a declared linear interpretation of the thesis Eq. (9), not a calibrated physical uplink measurement. The original 4,000 V1.5/full V2 flights were replayed without changing any prior result; the source comparison further below now includes the recoverable metrics.

**New controller test:** a five-step lookahead supervisor uses the existing full V2 policy weights. It changes motion/network action selection; there is no new PPO training or isolated reward change. Three declared horizons were tested on validation before selecting five steps. It retains the thesis RSS and buffer requirements through the unchanged V2 system. These results use **fresh 55012/55013 routes**, separate from the earlier tables.

| Controller | Standard success (%), higher is better | Longer success (%), higher is better | Episodes per split | Original thesis comparison |
| --- | ---: | ---: | ---: | --- |
| V1.5 original reward | 93.80 | 89.12 | 2500 | Comparable original joint success NR [printed pp. 16-20]. |
| Full V2 | 94.44 | 90.64 | 2500 | Comparable original joint success NR [printed pp. 16-20]. |
| V2.1 service | 93.16 | 88.64 | 2500 | Comparable original joint success NR [printed pp. 16-20]. |
| V2.2 guarded V2 | 96.44 | 96.32 | 2500 | Comparable original joint success NR [printed pp. 16-20]. |
| Goal radio | 93.60 | 91.60 | 500 | Comparable original joint success NR [printed pp. 16-20]. |
| Joint one step | 94.20 | 87.80 | 500 | Comparable original joint success NR [printed pp. 16-20]. |
| Joint three step | 91.60 | 87.40 | 500 | Comparable original joint success NR [printed pp. 16-20]. |

**The primary fresh comparison supports improved standard mission completion.**
V2.2 minus full V2 completion is +2.000 percentage points [0.320, 3.681] on standard routes and +5.680 [3.200, 8.280] on longer routes (95% intervals).

| Recovered or service metric | Standard full V2 / V2.2 | Difference, 95% interval | Longer full V2 / V2.2 | Difference, 95% interval | Original thesis definition / comparability |
| --- | --- | --- | --- | --- | --- |
| SNR (dB), higher is better | 62.238 / 64.667 | +2.429 [2.282, 2.576] | 62.045 / 64.707 | +2.662 [2.563, 2.757] | Eq. (8), printed p. 10. The source plotted SNR cannot follow from its stated inputs; see the bound below. |
| All neighbor RSS power (µW), lower is better | 1.447 / 1.386 | -0.061 [-0.066, -0.057] | 1.536 / 1.465 | -0.072 [-0.075, -0.068] | Linear interpretation of Eq. (9), printed p. 10; source conversion/aggregation unverified. No physical uplink comparison. |
| Remaining energy (kJ), higher is better | 91.766 / 91.762 | -0.003 [-0.012, 0.006] | 80.620 / 80.607 | -0.012 [-0.024, 0.001] | Our remaining energy under V2 accounting. Source Eq. (10), printed p. 10, has unresolved arithmetic and units. |
| Executed handovers, lower is better while preserving service | 0.466 / 4.811 | +4.345 [4.133, 4.564] | 1.607 / 10.527 | +8.920 [8.584, 9.233] | Source Figs. 6/8, printed pp. 18/20, have unknown count normalization; no numerical source comparison. |
| Delay proxy (s), lower is better | 5.404 / 0.429 | -4.975 [-5.536, -4.441] | 6.609 / 0.498 | -6.111 [-6.472, -5.744] | Queue/rate in Eq. (4), printed p. 9; source numerical delay NR. |
| Flight time (s), lower is better | 29.384 / 29.392 | +0.008 [-0.079, 0.075] | 61.330 / 61.288 | -0.042 [-0.157, 0.054] | Matched arrival time NR; source continues after arrival [printed p. 12, Sec. 5.2]. |
| SINR (dB), higher is better | -9.355 / -5.775 | +3.580 [3.426, 3.732] | -9.828 / -6.035 | +3.793 [3.684, 3.896] | Corresponding SINR NR; source reports SNR [printed p. 10, Eq. (8)]. |
| Cochannel downlink interference (µW), lower is better | 0.741 / 0.566 | -0.174 [-0.182, -0.167] | 0.775 / 0.594 | -0.180 [-0.186, -0.175] | Corresponding cochannel downlink result NR [printed p. 10, Eq. (9)]. |
| Consumed energy (kJ), lower is better | 8.234 / 8.238 | +0.003 [-0.006, 0.012] | 19.380 / 19.393 | +0.012 [-0.001, 0.024] | V2 energy accounting. Source Eq. (10), printed p. 10, cannot be converted into this consumed energy metric. |
| Handovers per second, lower is better while preserving service | 0.014 / 0.161 | +0.147 [0.141, 0.153] | 0.026 / 0.171 | +0.145 [0.140, 0.150] | Explicit switches/flight duration. Source Figs. 6/8, printed pp. 18/20, do not specify this denominator. |

Service means use 2331 standard and 2225 longer common successful pairs. All failures count in mission success. Secondary intervals are descriptive and unadjusted for multiple comparisons.

**Interpretation:**

For the declared completion first, then service priority, V2.2 is the preferred controller among the tested V2 variants in this simulator. It passes the primary completion criterion and reduces delay. This conclusion is about the complete supervised controller, including its extra lookahead computation.

Delay falls by 92.1% on standard and 92.5% on longer common successes. SNR improves by 2.429 and 2.662 dB; SINR also improves, and both all neighbor power and cochannel interference decrease. SNR measures signal relative to noise alone; SINR also accounts for interfering transmitters. The neighbor sum is a map based equation proxy, not measured physical uplink interference.

The cost is more handovers than full V2: 0.466 to 4.811 per standard flight and 1.607 to 10.527 per longer flight. These are executed station switches and therefore extra control overhead. Flight time and energy differences versus full V2 have intervals containing zero; we do not claim an energy saving.

Against the V1.5 original reward control on these same fresh routes, completion improves by 2.640 points [0.920, 4.480] standard and 7.200 [5.160, 9.320] longer. Delay, flight time, signal quality and handover count also improve on their common successes, but V2.2 consumes 0.148 and 0.454 kJ more. It does not improve every objective. These secondary comparisons have unadjusted intervals, and V1.5 is our original reward control on V2, not the unavailable original thesis agent.

| Controller | Standard RSS / buffer / timeout failures, lower is better | Longer RSS / buffer / timeout failures, lower is better | All flight mean outage standard / longer (s), lower is better | Original thesis comparison |
| --- | --- | --- | --- | --- |
| V1.5 original reward | 151 / 4 / 0 | 249 / 19 / 4 | 0.0604 / 0.0996 | Source outage bars are approximate; first failure counts NR [printed pp. 18, 20, Figs. 6/8]. |
| Full V2 | 124 / 15 / 0 | 178 / 55 / 1 | 0.0496 / 0.0712 | Source outage bars are approximate; first failure counts NR [printed pp. 18, 20, Figs. 6/8]. |
| V2.1 service | 171 / 0 / 0 | 278 / 5 / 1 | 0.0684 / 0.1112 | Source outage bars are approximate; first failure counts NR [printed pp. 18, 20, Figs. 6/8]. |
| V2.2 guarded V2 | 89 / 0 / 0 | 87 / 0 / 5 | 0.0356 / 0.0348 | Source outage bars are approximate; first failure counts NR [printed pp. 18, 20, Figs. 6/8]. |
| Goal radio | 31 / 1 / 0 | 39 / 2 / 1 | 0.0620 / 0.0780 | Source outage bars are approximate; first failure counts NR [printed pp. 18, 20, Figs. 6/8]. |
| Joint one step | 29 / 0 / 0 | 57 / 2 / 2 | 0.0580 / 0.1140 | Source outage bars are approximate; first failure counts NR [printed pp. 18, 20, Figs. 6/8]. |
| Joint three step | 18 / 0 / 24 | 27 / 0 / 36 | 0.0360 / 0.0540 | Source outage bars are approximate; first failure counts NR [printed pp. 18, 20, Figs. 6/8]. |

These failure counts use 2,500 flights per learned arm and 500 per deterministic reference in each split. Energy and boundary failures are zero. Mean outage includes successful and failed flights, but is censored by termination at the first violation. It is not a full continuing episode outage duration.

![New standard route metric comparisons](results/thesis_metrics_v22/analysis/metric_comparison_test.png)

![New longer route metric comparisons](results/thesis_metrics_v22/analysis/metric_comparison_longer_test.png)

**Source consistency finding:** the same dataset has maximum Operator 1 RSS of -25 dBm. With the thesis Eq. (8) and Table 3 noise settings, SNR cannot exceed **78.41 dB**. Its plotted medians around 122-127 dB therefore cannot be reproduced from the stated inputs. This is an unresolved source inconsistency, not evidence that our controller should aim for those numbers.

[Recovered metrics and source audit](docs/52_recovered_thesis_metrics.md), [all new results, failures and policy seeds](docs/53_v22_guard_results.md), [declared protocol](docs/51_thesis_metrics_and_guard_protocol.md) and [model usage and reproduction](docs/54_thesis_metrics_reproduction.md).
