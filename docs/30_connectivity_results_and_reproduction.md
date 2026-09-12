# Connectivity Repair: Frozen Results and Reproduction

Date: 12 September 2026. Study: `connectivity_v2`.

## Outcome

The implementation now enforces the thesis's sampled RSS and buffer constraints
as part of joint mission success and restores all three communication costs.
The controller study is complete, with retained positive and negative outcomes.
It does **not** establish an overall PPO advantage or continuous physical
connectivity between simulator samples.

The full PPO reward reduces weighted communication cost, mainly by avoiding
handovers, but increases delay substantially. Joint completion differences
between learned reward arms are uncertain. The goal directed controller with
prospective radio selection has the highest observed completion among the
tested controllers. On longer routes it improves completion over the strongest
RSS reference while also reducing weighted communication cost on paired
successful routes. This is a useful deterministic control result, not evidence
that learning is necessary.

## What Was Implemented

The original thesis specifies RSS ≥ −96 dBm and queue occupancy within capacity
[TFM, printed p. 11, Eq. (12), C2/C4; p. 15, Table 3], and optimizes delay,
interference and handovers [TFM, printed p. 10, Eq. (11); p. 12, Eq. (13)].
V2 implements first violation failure at modeled samples, 61 admissible
station/resource actions, all three normalized costs, and a shared prospective
safety filter. PPO learns motion corrections to a braking reference. The
complete changes and source locators are in [note 31](31_exact_connectivity_changes.md).

The user selected the thesis requirements. No 2 s packet deadline, minimum
throughput constraint, or empty queue arrival requirement was introduced.
All successful flights stop within the arrival tolerances and have no observed
RSS violation or overflow. Outstanding data at arrival remains allowed and
reported; success does not mean every generated bit has been delivered.

## Design and Validation

The final protocol was frozen before test evaluation, with five training seeds
2101–2105, 524,288 interactions per arm/seed, and ten final policies. Total final
training is 5,242,880 interactions. Recorded training plus final validation
time is 865.68 s on CPU; it excludes map loading, final tests, and artifact work.
Six earlier development policies are retained separately in note 29.

Training uses 4,096 routes spanning 200–1800 m, with separate 64 standard and
32 longer validation routes. Final tests use 200 fresh standard and 200 fresh
longer routes. Five learned policies repeat each route set. Both length ranges
are within the final training range, and every split uses the same radio map.
This is neither geographic holdout nor length extrapolation.

All 51 tests pass, including 17 new behavioral checks. Every one of the 5,600
final evaluations replayed exactly: 4,000 learned and 1,600 deterministic
episodes. The dataset SHA256 and both experiment freezes match their originals.

## Joint Mission Success

| Controller | Standard success | Longer success | Evaluations per split |
| --- | ---: | ---: | ---: |
| PPO, arrival cost only, with strict constraints | 96.9% | 86.3% | 1,000 |
| PPO, full thesis radio cost, with strict constraints | 96.6% | 89.7% | 1,000 |
| Goal RSS, with shared filter | 97.0% | 87.0% | 200 |
| Goal radio, with shared filter | **98.0%** | **92.5%** | 200 |
| Joint one step search, with shared filter | 96.5% | 90.0% | 200 |
| Joint three step search, with shared filter | 95.0% | 90.5% | 200 |

The labels `straight_rss` and `straight_radio` in saved files refer to the
nominal goal directed motion law. The filter can modify it; actual paths and
proposal override counts are retained. The local planning references have
prospective map access, and learned policies share a prospective filter.

Every learned seed is retained:

| Seed | Arrival standard | Full standard | Arrival longer | Full longer |
| --- | ---: | ---: | ---: | ---: |
| 2101 | 96.0% | 96.0% | 84.5% | 89.0% |
| 2102 | 97.0% | 97.0% | 88.5% | 91.0% |
| 2103 | 97.5% | 96.5% | 87.5% | 88.5% |
| 2104 | 96.5% | 97.0% | 87.5% | 89.0% |
| 2105 | 97.5% | 96.5% | 83.5% | 91.0% |

Full minus arrival success is **−0.3 percentage points**, 95% crossed bootstrap
interval **[−2.6, 2.0]**, on standard routes. On longer routes it is **+3.4
points [−1.0, 8.1]**. Both intervals include zero. The prespecified strong joint
improvement claim for the full learned objective is not met on either split.

## Failures Remain Visible

| Controller | Standard: RSS / buffer / timeout | Longer: RSS / buffer / timeout |
| --- | ---: | ---: |
| PPO arrival | 31 / 0 / 0 | 136 / 1 / 0 |
| PPO full | 32 / 2 / 0 | 77 / 26 / 0 |
| Goal RSS | 6 / 0 / 0 | 26 / 0 / 0 |
| Goal radio | 4 / 0 / 0 | 15 / 0 / 0 |
| Joint one step | 7 / 0 / 0 | 20 / 0 / 0 |
| Joint three steps | 2 / 0 / 8 | 7 / 0 / 12 |

There were no boundary or energy failures. These are first failure reasons;
episodes stop at their first violation, so later hypothetical outcomes are
unknown. The full reward shifts the pattern toward fewer RSS failures and
more buffer failures on longer missions. It does not remove failures.

## Communication Tradeoffs on Matched Successful Routes

The learned comparison includes 945 common successful standard evaluations and
802 longer evaluations. Each comparison uses the same training seed and route
on both sides. Values below are averages within that common subset, not means
over different successful populations.

| Metric | Standard arrival → full | Longer arrival → full |
| --- | ---: | ---: |
| Accumulated normalized radio cost | 6.56 → 4.95 (**−24.5%**) | 16.31 → 13.92 (**−14.7%**) |
| Mean delay proxy | 1.47 → 4.21 s (**+186.7%**) | 1.83 → 6.62 s (**+261.1%**) |
| Handovers | 8.55 → 0.38 (**−95.5%**) | 21.07 → 1.51 (**−92.8%**) |
| Mean interference | 0.727 → 0.734 µW | 0.788 → 0.785 µW |
| Mean SINR | −7.86 → −8.95 dB | −8.31 → −9.89 dB |
| Arrival time | 27.60 → 27.41 s | 61.40 → 61.05 s |

Accumulated cost differences have 95% intervals [−2.016, −1.230] on standard
routes and [−3.317, −1.488] on longer routes. Mean delay differences are
[2.030, 3.474] s and [4.180, 5.397] s. Interference differences are inconclusive.
SINR differences are reported in dB, not percentages of logarithmic values.

The original reciprocal cost saturates smoothly. Preserving its weighting can
favor fewer handovers despite much higher delay. This is not a latency guarantee
and not an improvement in every radio metric. The queue/service delay proxy
also remains different from measured packet latency.

## What the Deterministic Comparisons Establish

Goal radio versus Goal RSS improves longer completion by **5.5 points [1.5,
9.5]**, while accumulated radio cost is **41.0% lower** on 171 paired successful
routes. On standard routes its completion difference is +1.0 points [−1.5,
3.5] and cost is 47.6% lower on 192 common successes. These are prespecified
secondary controller comparisons with route bootstrap uncertainty.

One step joint planning reduces cost relative to Goal radio by 17.9% standard
and 20.3% longer on 191 and 173 common successes, but completion differences
are −1.5 points [−4.0, 1.0] and −2.5 points [−7.0, 1.5]. Three step planning
reduces cost by 41.1% and 42.9% on 188 and 173 common successes, but completion
differences are −3.0 points [−6.0, 0.0] and −2.0 points [−6.5, 2.5]. Its timeout
failures must not be hidden by the successful flight radio averages.

The useful positive result is that better network selection can improve the
strict joint task over the strongest RSS rule. Additional local path planning
offers a radio cost versus completion tradeoff. A learned superiority claim is
unsupported.

## Are the Paths Still Straight?

Mostly, for the residual PPO and goal directed references. The full PPO's mean
successful path/start to goal distance ratio is 1.0019 standard and 1.0007
longer. The three step reference's ratios are 1.0572 and 1.0432. These ratios
are descriptive; the 10 m arrival tolerance means exact goal position is not
required and individual ratios may be below one.

This is consistent with dense RSS coverage and inexpensive resource changes
under this surrogate. The new experiment does not award curvature. It allows
radio choices and, where helpful, motion changes to satisfy the defined task.
The paper's trajectory and RSS plot uses the first declared standard route,
not a route selected for attractive bends.

## Reproduce or Inspect

Start with [the dataset and model setup guide](35_dataset_and_model_setup.md)
for exact file locations, dependency installation, checkpoint compatibility,
output filenames and troubleshooting. A clone currently includes neither the
private HDF5 nor the trained `.pt` files.

Use system Python with the versions in `requirements-experiments.txt`. The
private map must already be present. Existing trained policies are sufficient
for evaluation:

```powershell
python -m pytest tests -q
python scripts/evaluate_connectivity_controller.py --controller straight_radio --split test
python scripts/evaluate_connectivity_controller.py --checkpoint results/connectivity_experiment/confirmatory_v2/full_seed_2101/checkpoint.pt --split test
python scripts/evaluate_connectivity_controller.py --controller straight_radio --start 1000 1000 --goal 1800 1300 --output outputs/custom_connectivity_route
```

Regenerate the analysis, exact replay audit, and paper inputs:

```powershell
python scripts/analyze_connectivity_experiment.py
python scripts/finalize_connectivity_statistics.py
python scripts/replay_connectivity_experiment.py
python scripts/build_connectivity_paper_artifacts.py
```

The frozen estimator produces `statistics.json`. Its generic relative change
field is inappropriate for logarithmic SINR. The reporting finalizer preserves
that file and creates `report_statistics.json` with those unused percentage
fields set to null. All absolute dB differences, estimates, intervals and
primary results remain identical. This reporting correction is documented and
does not change the frozen source or tests.

To retrain the fixed design in a new output directory:

```powershell
python scripts/run_connectivity_experiment.py --phase confirmatory --label independent_reproduction --seeds 2101 2102 2103 2104 2105 --steps 524288
```

This is a reproduction using the already frozen tests, not a new confirmatory
study. The standard analysis script reads `confirmatory_v2`; use the original
directory for the delivered results. New model choices require a separate
study and new held out tests. The runner refuses to overwrite saved policies.

## Artifacts, Limits, and Next Decision

- `configs/frozen_connectivity_v2.json`: final configuration and source hashes.
- `results/connectivity_experiment/confirmatory_v2/`: all final policies and episodes.
- `results/connectivity_experiment/analysis_v2/report_statistics.json`: reporting results and uncertainty.
- `results/connectivity_experiment/replay_v2/`: exact replay audit and detailed route traces.
- `paper/UAV_connectivity_repair_IEEE.pdf`: four page IEEE format report with mixed results.
- `docs/28_connectivity_experiment_protocol.md`: frozen definitions and analysis plan.
- `docs/29_connectivity_development_log.md`: every development result and decision.
- `docs/31_exact_connectivity_changes.md`: every v2 change with source page locators.

The objective and endpoint omission has been corrected in the executable
surrogate. The full original simulator and a universally successful controller
have not been recovered. Sampling, static load, instantaneous switching,
uncalibrated downlink and energy proxies, shared geography, and exact map access
remain limitations. Outstanding queues and high delay are allowed by the
selected thesis requirements, so they must remain visible.

The next research decision is whether to retain the simple radio controller as
the operational research reference, or pursue a new study of stronger local
planning and physical model robustness. The current tests must not be reused
to tune and then claim new independent confirmation. No further permission,
asset request, or hidden background training is pending for this completed study.
