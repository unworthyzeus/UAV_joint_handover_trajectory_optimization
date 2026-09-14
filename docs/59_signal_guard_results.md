# V2.3 Signal Path Results and Reproduction

Date: 14 September 2026.

## What Changed and Why

The user asked to improve signal quality further. A separately versioned controller considers predicted SNR when choosing among near equal progress paths. It retains the V2.2 rollout machinery, network choice and all physical and mission requirements. The frozen protocol is note 58.

## Development: Every Candidate

These are selection data, not final improvement evidence. Each row uses its own common successful pairs. Differences are candidate minus V2.2. All development seeds and sample arrays are preserved.

| Allowance / split | Successes V2.2 / candidate (higher is better) | SNR difference (dB, higher is better) | Delay difference (s, lower is better) | Handovers difference (lower is better) | Selection gate |
| --- | --- | ---: | ---: | ---: | --- |
| 1 m / test | 252 / 252 of 256 | +0.421 | -0.139 | -0.492 | Pass |
| 1 m / longer_test | 122 / 122 of 128 | +0.297 | -0.103 | -0.689 | Pass |
| 3 m / test | 252 / 250 of 256 | +0.959 | -0.298 | -1.052 | Fail |
| 3 m / longer_test | 122 / 123 of 128 | +1.331 | -0.382 | -3.750 | Pass |
| 6 m / test | 252 / 250 of 256 | +1.168 | -0.323 | -1.212 | Fail |
| 6 m / longer_test | 122 / 120 of 128 | +1.554 | -0.417 | -4.390 | Fail |

Selected allowance: 1 m. Larger allowances failed the completion first selection. The 3 m and 6 m standard time increases also exceed the declared 2% limit.

## Final Result

V2.3 does not pass the declared combined improvement gate; V2.2 remains the default.

Standard: SNR +0.377 dB; delay -26.5%; handovers -7.8%; flight time +0.64%; consumed energy +0.19%. Failed gates: completion.
Longer: SNR +0.284 dB; delay -19.5%; handovers -5.9%; flight time +0.35%; consumed energy +0.08%. Failed gates: completion.

Standard completion misses the gate's nonnegative point requirement, although its interval excludes a loss of 1 percentage point. The interval includes zero, so the observed decrease is not statistically resolved.
Longer completion misses the gate's nonnegative point requirement, although its interval excludes a loss of 1 percentage point. The interval includes zero, so the observed decrease is not statistically resolved.

| Split / gate | Passed | Interpretation |
| --- | --- | --- |
| test / completion | False | Nonnegative point difference and interval lower bound above −1 pp. |
| test / delay | True | Nonpositive point difference and upper bound below +0.05 s. |
| test / handovers | True | Nonpositive point difference and upper bound below +0.25 switches per flight. |
| test / time | True | Upper bound for candidate time minus 1.02 × baseline time below zero. |
| test / energy | True | Upper bound for candidate energy minus 1.02 × baseline energy below zero. |
| test / snr | True | SNR lower bound above 0.1 dB standard or zero longer. |
| longer_test / completion | False | Nonnegative point difference and interval lower bound above −1 pp. |
| longer_test / delay | True | Nonpositive point difference and upper bound below +0.05 s. |
| longer_test / handovers | True | Nonpositive point difference and upper bound below +0.25 switches per flight. |
| longer_test / time | True | Upper bound for candidate time minus 1.02 × baseline time below zero. |
| longer_test / energy | True | Upper bound for candidate energy minus 1.02 × baseline energy below zero. |
| longer_test / snr | True | SNR lower bound above 0.1 dB standard or zero longer. |

## Every Policy Seed and Failure

| Seed | Standard V2.2 / V2.3 successes, higher is better | Longer V2.2 / V2.3 successes, higher is better |
| --- | --- | --- |
| 2101 | 493 / 493 of 500 | 471 / 469 of 500 |
| 2102 | 493 / 492 of 500 | 467 / 469 of 500 |
| 2103 | 493 / 494 of 500 | 468 / 467 of 500 |
| 2104 | 493 / 492 of 500 | 469 / 467 of 500 |
| 2105 | 493 / 493 of 500 | 468 / 468 of 500 |

| Controller / split | All outcomes, lower failure counts are better | Mean sampled outage (s), lower is better |
| --- | --- | --- |
| v22_test | connectivity: 30; success: 2465; timeout: 5 | 0.0120 |
| signal_test | connectivity: 31; success: 2464; timeout: 5 | 0.0124 |
| v22_longer_test | connectivity: 157; success: 2343 | 0.0628 |
| signal_longer_test | connectivity: 160; success: 2340 | 0.0640 |

Outage ends at the first failed sample and is censored, so it is not complete outage duration under continued operation. Success still requires zero sampled outage and no overflow.

## Recorded Evaluation Runtime

| Controller / split | Mean wall time per 500 route evaluation (s), lower is better under matched conditions |
| --- | ---: |
| v22 / test | 242.77 |
| v22 / longer_test | 249.14 |
| signal / test | 255.63 |
| signal / longer_test | 247.78 |

These times exclude model/map loading and the separate replay. Jobs ran concurrently on the same workstation; three early V2.2 records used three workers and the remaining jobs used six. CPU contention and scheduling differ, so these are workload records, not a controlled speed comparison or onboard latency estimate. The restart retained every completed record and reran its exact replay. The orchestration note and runtime package versions are saved in the analysis folder.

## Complete Means and Sample Aggregates

The following copy preserves the same numerical table as the README. All service rows are conditional on common success.

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

## Reproduction and Existing Models

Place the private unchanged map at `dataset/Barcelona_dataset_January.h5`. Its expected SHA256 is `d4630dd3a6c45419e12d0b60dd08473c4ffa4062ca4fab1decabecf2b992ea0d`. Use the five already committed full V2 checkpoints in `results/connectivity_experiment/confirmatory_v2/full_seed_2101/checkpoint.pt` through seed 2105. No extra model download or training is needed.

```powershell
python -m pytest -q
python scripts/run_signal_guard_study.py --phase confirmatory --workers 3
python scripts/analyze_signal_guard_study.py --phase confirmatory
python scripts/build_signal_guard_report.py
python scripts/audit_signal_guard_delivery.py
```

For a single route demonstration with the same controller and weights:

```powershell
python scripts/evaluate_signal_guard_controller.py --controller signal --seed 2101 --start 1000 1000 --goal 1800 1300 --output outputs/v23_custom
```

The command saves JSON episode metrics and NPZ sample arrays. It reports failure normally when a custom route fails the mission. A one route inference batch is a demonstration; the complete frozen runner above is used for exact original batch replay.

The evaluator verifies existing records by replay and refuses to overwrite conflicting results. Development selection and freeze are already complete; do not rerun those phases to pick a new candidate. The frozen runner, analysis and protocol are archived under both source snapshot folders. A new experiment needs a new name, protocol and routes.

For custom integration, load the ordinary full V2 `HybridPolicy`, decode its deterministic residual with `env.decode_residual`, and call `signal_guard_action(env, proposal, 1)` from `uav_joint_optimization.signal_guard`. Pass the returned motion and network action to the unchanged `ConnectivityBatch.step`. Observations and the action mask must come from that same environment state. The full executable loop is in `scripts/run_signal_guard_study.py`.

## Limitations and Next Decision

This is not an independent map test or newly trained network. Five fixed policies reuse the same route pools, so uncertainty resamples both policies and routes. Finite planning, static occupancy, sampled connectivity, ideal handovers and proxy energy still limit claims. Gains are conditional on common successes and additional map access. No inference about an actual correction to the original thesis or global SNR optimality follows.

All 10,000 final episode records and all saved sample arrays matched exact replay. The complete implementation suite passed 100 tests. Runtime is measured with concurrent workstation batches, not as onboard latency. The next experiment should use independent maps or a declared controller component ablation, not retuning against these final routes.
