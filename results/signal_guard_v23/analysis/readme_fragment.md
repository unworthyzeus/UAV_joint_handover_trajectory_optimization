## V2.3 Signal Aware Path Selection

**V2.3 does not pass the declared combined improvement gate; V2.2 remains the default.**

This is a new fixed weight controller comparison on the same Barcelona ray tracing dataset as the original thesis. It allows up to 1 m less predicted goal progress within the existing five step rollout score when a path predicts stronger SNR with no extra delay or handovers. This is not a 1 m total detour limit. The original mission, RSS, buffer, A3 masks and executed safety filter remain unchanged.

Development tested 1, 3 and 6 m allowances on 192 new routes with two saved policies (1,536 episodes). Only 1 m qualified. The other candidates improved SNR more but lost standard completions. The selected version was frozen before 500 fresh standard and 500 fresh longer routes, seeds 56012/56013, were generated. Both controllers used all five full V2 policies: 10,000 final episodes, all exactly replayed. These results are separate from every earlier test set.

| Fresh split; completion: higher is better | V2.2 success | V2.3 success | Difference (pp), 95% interval | Original thesis comparison |
| --- | ---: | ---: | --- | --- |
| Standard | 98.60% (2465/2500) | 98.56% (2464/2500) | -0.040 [-0.600, 0.520] | Comparable joint success NR [printed pp. 16–20]. |
| Longer | 93.72% (2343/2500) | 93.60% (2340/2500) | -0.120 [-0.880, 0.720] | Comparable joint success NR [printed pp. 16–20]. |

| Metric and preferred direction | Standard V2.2 / V2.3 | Difference, 95% interval | Longer V2.2 / V2.3 | Difference, 95% interval | Original thesis definition / comparability |
| --- | --- | --- | --- | --- | --- |
| Mean flight SNR (dB), higher is better | 64.710 / 65.087 | +0.377 [0.340, 0.415] | 64.696 / 64.979 | +0.284 [0.245, 0.327] | Source Eq. (8), p. 10; plotted scale remains unverified. |
| Mean SINR (dB), higher is better | -5.616 / -5.236 | +0.380 [0.342, 0.420] | -6.026 / -5.738 | +0.288 [0.247, 0.333] | SINR NR; source reports SNR, p. 10, Eq. (8). |
| Delay proxy (s), lower is better | 0.377 / 0.277 | -0.100 [-0.120, -0.081] | 0.492 / 0.396 | -0.096 [-0.119, -0.074] | Queue/rate definition p. 9, Eq. (4); comparable result NR. |
| Handovers per flight, lower is better while preserving service | 4.626 / 4.266 | -0.360 [-0.449, -0.278] | 10.868 / 10.230 | -0.639 [-0.786, -0.494] | Source count normalization unknown, pp. 18/20, Figs. 6/8. |
| Flight time (s), lower is better | 28.579 / 28.762 | +0.183 [0.132, 0.237] | 61.419 / 61.634 | +0.215 [0.165, 0.266] | Matched arrival time NR; source arrival does not terminate, p. 12, Sec. 5.2. |
| Consumed energy (kJ), lower is better | 7.940 / 7.955 | +0.015 [0.010, 0.020] | 19.437 / 19.453 | +0.016 [0.010, 0.021] | Different energy model; source remaining display is not kJ, pp. 10/15, Eq. (10)/Table 3. |
| Remaining energy (kJ), higher is better | 92.060 / 92.045 | -0.015 [-0.020, -0.010] | 80.563 / 80.547 | -0.016 [-0.021, -0.010] | Verified source kJ result NR, pp. 10/15. |
| Cochannel downlink interference (µW), lower is better | 0.555030 / 0.554698 | -0.000331 [-0.001240, 0.000591] | 0.595312 / 0.594628 | -0.000684 [-0.001298, -0.000066] | Comparable source result NR, p. 10, Eq. (9). |
| All neighbor RSS power (µW), lower is better | 1.360490 / 1.358880 | -0.001610 [-0.003212, -0.000106] | 1.464220 / 1.463080 | -0.001140 [-0.002298, -0.000088] | Our linear interpretation of Eq. (9), p. 10; source aggregation unverified. |
| Handovers per second, lower is better while preserving service | 0.161 / 0.147 | -0.014 [-0.017, -0.011] | 0.177 / 0.165 | -0.011 [-0.014, -0.009] | Comparable source denominator NR, pp. 18/20. |
| Path length (m), lower is better while preserving service | 561.015 / 562.016 | +1.001 [0.896, 1.114] | 1382.287 / 1383.323 | +1.035 [0.918, 1.197] | Source trajectory illustrations, pp. 17/19; aggregate length NR. |
| Accumulated V2 radio cost, lower is better while preserving service | 3.321 / 2.969 | -0.352 [-0.404, -0.305] | 7.911 / 7.343 | -0.568 [-0.676, -0.464] | Our transformed reporting cost; source returns not comparable, pp. 10/12, Eqs. (11)–(14). |
| Pooled sample SNR median (dB), higher is better | 65.410 / 65.410 | +0.000; descriptive | 65.410 / 66.410 | +1.000; descriptive | Source aggregation and scale unverified, pp. 18/20; note 57 gives a separate conditional correction. |

Service means use 2,459 standard and 2,325 longer common successful pairs. Every failure remains in completion denominators. Mean flight SNR weights flights equally; the pooled sample median weights every executed second equally. A better median alone is not the declared improvement test.

**How to read the result:** positive SNR or SINR differences favor V2.3; negative delay and handover differences favor V2.3. Positive time and consumed energy differences are costs. Completion is checked first: its point difference must be nonnegative and its interval must exclude a loss of 1 percentage point. This does not establish identical reliability. Delay, handover, time and energy margins are study choices, not thesis requirements. Secondary metric intervals are descriptive and unadjusted.

Standard: SNR +0.377 dB; delay -26.5%; handovers -7.8%; flight time +0.64%; consumed energy +0.19%. Failed gates: completion.
Longer: SNR +0.284 dB; delay -19.5%; handovers -5.9%; flight time +0.35%; consumed energy +0.08%. Failed gates: completion.

Standard completion misses the gate's nonnegative point requirement, although its interval excludes a loss of 1 percentage point. The interval includes zero, so the observed decrease is not statistically resolved.
Longer completion misses the gate's nonnegative point requirement, although its interval excludes a loss of 1 percentage point. The interval includes zero, so the observed decrease is not statistically resolved.

| Controller / split | RSS / buffer / timeout / boundary / energy failures (counts), lower is better | Mean sampled outage (s), lower is better | Original thesis comparison |
| --- | --- | ---: | --- |
| V2.2 standard | 30 / 0 / 5 / 0 / 0 | 0.0120 | Source first failure counts NR; outage bars pp. 18/20 do not use our strict termination. |
| V2.2 longer | 157 / 0 / 0 / 0 / 0 | 0.0628 | Source first failure counts NR; outage bars pp. 18/20 do not use our strict termination. |
| V2.3 standard | 31 / 0 / 5 / 0 / 0 | 0.0124 | Source first failure counts NR; outage bars pp. 18/20 do not use our strict termination. |
| V2.3 longer | 160 / 0 / 0 / 0 / 0 | 0.0640 | Source first failure counts NR; outage bars pp. 18/20 do not use our strict termination. |

Sampled outage stops at the first violation, so its mean is censored by termination. Zero outage on successful flights is a requirement, not independent proof of better connectivity.

No new weights or PPO training were added. The source thesis agent remains unavailable; neither its conditional SNR correction nor its plotted outcomes are matched numerical baselines for this study.

![V2.3 signal and service distributions](results/signal_guard_v23/analysis/signal_service_cdfs.png)

[Declared protocol](docs/58_signal_guard_protocol.md), [complete results, failed candidates, all seeds and reproduction](docs/59_signal_guard_results.md), [numerical analysis](results/signal_guard_v23/analysis/statistics.json).

Try one saved route or your own coordinates with the existing weights and `dataset/Barcelona_dataset_January.h5`:

```powershell
python scripts/evaluate_signal_guard_controller.py --controller signal --seed 2101 --split test --scenario-index 0 --output outputs/v23_example
python scripts/evaluate_signal_guard_controller.py --controller signal --seed 2101 --start 1000 1000 --goal 1800 1300 --output outputs/v23_custom
```

These commands save one route and all metric samples. Use `--controller v22` for the baseline. Use a new output prefix for each run; the full study runner is required for exact batch replay.
