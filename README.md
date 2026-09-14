# Joint Handover and Trajectory Optimization with Strict Connectivity

Updated 14 September 2026. Non THz n3cat research project.

**V2 and its V1.5 original reward control, with a completed V2.1 service reward followup.**
**All experiments use the same Barcelona ray tracing dataset as the original
thesis.** The supplied HDF5 is preserved unchanged; the simulation and control
implementation are our own.

The [current IEEE paper](paper/UAV_joint_reward_connectivity_IEEE.pdf) is by
Guillem Moreno Garcia and Evgenii Vinogradov. Start with the
[results and every seed](docs/37_v15_reward_results.md),
[frozen protocol](docs/36_v15_reward_comparison_protocol.md), or
[dataset and model setup guide](docs/35_dataset_and_model_setup.md).

## Initial V1.5 Versus V2 Conclusion

**Replacing the original reward has not demonstrated better mission completion
under our shared V2 system.** Original reward V1.5 and full reward V2 both
achieve 95.7% standard joint success. V2 does change communication behavior:
it substantially reduces handovers and shortens flights, while increasing
delay and estimated energy consumption on matched successful flights.

The original thesis simulator and trained policies are unavailable. We built
a new implementation around the same Barcelona radio map, changing much
more than the reward relative to the thesis. **V1.5 is the original written
reward inside our V2 system; it is not the original thesis agent.** Our
experiment therefore does not establish what caused the original wandering
or demonstrate a successful repair of that original implementation.

Read the [main differences](#main-differences-from-the-thesis),
[general results](#general-results) and
[conclusions](#conclusions-and-revised-diagnosis) first. The detailed inventory
below retains every observation, action, physical assumption, reward term,
PPO setting, split and reproduction command.

## V2.1 Followup on Fresh Routes

**A new candidate was trained and tested with completion first, then service as the priority.** Three declared candidates and a fresh V2 pilot control were evaluated on validation routes. The service candidate completed 91/96 versus 90/96 for control; the stronger failure penalty candidates completed 87/96 and 89/96. The selected reward uses logarithmic delay cost, a queue fraction penalty and a smaller handover payment. Physical transitions, the safety filter and all mission requirements stay V2.

The following results use **new seeds 54012 and 54013: 500 standard and 500 longer routes**, five training seeds per learned arm and 18,000 final episodes including references. They are separate from the 53012/53013 tables below; results from different test sets are not pooled.

| Controller | New standard success | New longer success | Episodes per split | Original thesis comparison |
| --- | ---: | ---: | ---: | --- |
| V2.1 service | 95.48% | 88.60% | 2,500 | Comparable original joint success NR [printed pp. 16-20, Sec. 7/Figs. 5-8]; V1.5 is our reward control, not the source agent. |
| Full V2 | 96.92% | 91.84% | 2,500 | Comparable original joint success NR [printed pp. 16-20, Sec. 7/Figs. 5-8]; V1.5 is our reward control, not the source agent. |
| Original reward V1.5 | 96.04% | 89.48% | 2,500 | Comparable original joint success NR [printed pp. 16-20, Sec. 7/Figs. 5-8]; V1.5 is our reward control, not the source agent. |
| Goal radio | 97.40% | 91.80% | 500 | Comparable original joint success NR [printed pp. 16-20, Sec. 7/Figs. 5-8]; V1.5 is our reward control, not the source agent. |
| Joint one step | 96.20% | 91.40% | 500 | Comparable original joint success NR [printed pp. 16-20, Sec. 7/Figs. 5-8]; V1.5 is our reward control, not the source agent. |
| Joint three step | 94.00% | 92.80% | 500 | Comparable original joint success NR [printed pp. 16-20, Sec. 7/Figs. 5-8]; V1.5 is our reward control, not the source agent. |

**The fresh standard comparison does not establish improved completion over full V2.** The candidate fails the declared completion first gate and is not promoted as the main model. The primary V2.1 minus full V2 difference is -1.440 percentage points, 95% interval [-3.160, 0.320]. The longer difference is -3.240 points [-5.640, -0.880]. The longer interval supports worse completion. An interval containing zero does not prove equivalence. The paired bootstrap uses 5,000 crossed seed/route draws.

| Metric and preferred direction | New standard: full V2 / V2.1 | Paired difference, 95% interval | New longer: full V2 / V2.1 | Paired difference, 95% interval | Original thesis comparison |
| --- | --- | --- | --- | --- | --- |
| Flight time (s), lower | 28.347 / 28.594 | +0.246 [0.020, 0.520] | 60.409 / 60.785 | +0.376 [0.039, 0.747] | Comparable mean arrival time NR; source continues after arrival [p. 12, Sec. 5.2]. |
| Delay proxy (s), lower | 4.742 / 1.291 | -3.451 [-3.957, -2.962] | 6.199 / 1.583 | -4.616 [-4.957, -4.287] | Queue/rate defined [p. 9, Eq. (4)]; numerical delay results NR in Figs. 6 and 8 [pp. 18, 20]. |
| Handovers, lower with service | 0.402 / 9.839 | +9.437 [8.968, 9.897] | 1.442 / 23.058 | +21.616 [20.923, 22.287] | CDF raw scale is not a mean executed count per successful flight [pp. 18, 20, Figs. 6, 8]. |
| Consumed energy (kJ), lower | 7.873 / 7.868 | -0.005 [-0.014, 0.005] | 19.057 / 19.032 | -0.025 [-0.049, 0.002] | Source remaining energy bars labeled kW use a different model [p. 10, Eq. (10); pp. 18, 20]. |
| SINR (dB), higher | -8.916 / -7.457 | +1.459 [1.296, 1.628] | -9.745 / -7.978 | +1.767 [1.662, 1.870] | Source SNR and its CDF medians are not this metric [p. 10, Eq. (8); pp. 18, 20]. |

These service means use **2335 standard and 2086 longer common successful pairs**. All failed flights still count in completion rates. Secondary intervals are descriptive and are not adjusted for multiple comparisons. Smaller delay does not imply fewer handovers, and a new reward is not an overall better controller unless the relevant metrics support that conclusion.

[Every new result, failure count and seed](docs/48_service_reward_results.md), [all pilot outcomes](docs/47_service_reward_development.md), [frozen protocol](docs/46_service_reward_development_protocol.md) and [V2.1 model usage](docs/49_service_reward_models_and_reproduction.md) are retained. All 18,000 fresh evaluations replayed exactly. The implementation suite passed 88 tests. No additional candidate or training change followed these test outcomes.

### What the New Reward Means

This followup tests a reward package with the same neural architecture and control system. It does not isolate each reward term, improve the propagation model, reproduce the source simulator or demonstrate performance in another city. The next research decision must follow the measured completion and service tradeoffs, not a requirement to produce a favorable conclusion.

## Main Differences from the Thesis

Except for the reward, the changes below apply to both V1.5 and V2 full.
The shared changes' individual benefits have **not** been isolated experimentally. A modeling replacement
is not automatically a correction of an original implementation bug.
TFM references use printed pages; PDF viewer page = printed page + 2.
Across the tables, **NR** means not reported at the specified source location
or in its results section; **NC** means not directly comparable. Neither means
zero, and an undocumented implementation detail is unknown. Original numerical
plot readings are marked approximate; they are not reconstructed raw results.
See the [original TFM](sources/UAV_Bermudez_Granados_2026_MSc_thesis.pdf).

| Area | Original written thesis | What our current study does differently |
| --- | --- | --- |
| Executable and channel data | Custom environment with Stable Baselines PPO; MATLAB ray tracing produces the radio map [pp. 6-7, Sec. 3.1; p. 13, Sec. 5.3]. | New Python environment and PPO implementation using the same dataset as the thesis, including Operator 1's 87 station maps and coordinates. Dataset identity is confirmed; the original simulator has not been reproduced. |
| Motion and braking | Discrete acceleration and heading, with five acceleration bins and eight directions [p. 12, Sec. 5.2; p. 15, Table 3]. | Continuous radial/lateral residual actions around a hand designed command that already points toward the goal and brakes. This is a substantial control aid shared by both rewards. |
| Observations | The listed state contains position, serving station, resource group, energy and queue [p. 12, Sec. 5.2]. | 156 explicit features, including goal direction/distance, velocity, time, candidate station positions/RSS, capacity and valid actions. We do not know whether the original code added unlisted features. |
| Connectivity enforcement | Written minimum RSS and bounded queue constraints, with an RSS reward penalty [p. 11, Eq. (12), C2/C4; p. 12, Eq. (14)]. | Any sampled RSS violation or queue overflow ends failure. A prospective filter also repairs network or local motion choices when possible. This implements explicit constraints; it does not establish how the unavailable original code enforced them. |
| Arrival and termination | Stopping is intended, but arrival does not end the episode [p. 9, Sec. 3.2; p. 12, Sec. 5.2]. | Success requires distance at most 10 m, speed at most 2 m/s and no constraint violation. Arrival ends training and evaluation episodes. Constraint violations take precedence over simultaneous arrival. |
| Station and resource decisions | Station and RBG requests with A3 logic; all 87 selected stations and 12 RBGs are listed [p. 9, Sec. 3.3.1; p. 12, Sec. 5.2; p. 15, Table 3]. | Serving station plus four strongest candidates, with 61 masked stay/station/group choices. Handover requests must satisfy A3 and resource availability. The filter can inspect the known map at predicted positions. |
| Time and dynamics | Scalar speed/direction motion; 0.1 s table step, conflicting 1 ms prose, and 100 m/s speed threshold [p. 9, Eq. (2); pp. 14-15, Sec. 6.1/Table 3]. | Vector velocity and trapezoidal position updates, 1 s steps, a hard 25 m/s cap, 5 m/s² acceleration norm limit and 200 s deadline. These are explicit surrogate choices. |
| Radio service, traffic and energy | Printed queue, arrival, rate, interference and energy models; random resource occupancy [pp. 9-10, Eqs. (4)-(10); pp. 14-15, Sec. 6.1/Table 3]. | Linear cochannel downlink interference, SINR based capacity, constant 200 kbit/s offered traffic, static half occupied resource patterns and an uncalibrated energy proxy. These replacements affect the task, not just its reward. |
| Reward | Positive reciprocal radio utilities, +12 when closer, penalties and an energy override [p. 12, Eqs. (13)-(14); p. 15, Table 3]. | V1.5 reconstructs the equal weight original formula on V2 quantities. Full V2 replaces it with potential differences, time cost, negative radio cost and terminal payments. This reward package is the primary controlled intervention. |
| PPO and training | Stable Baselines PPO; 300 episodes, up to 2,000 steps, learning rate 0.00003 and batch size 32 [p. 13, Sec. 5.3; p. 16, Table 4]. | Different implementation and hyperparameters, 524,288 interactions per policy and five declared seeds. Both reward arms use the same settings, training routes, initialization seeds and budget. |
| Splits and uncertainty | Equivalent independent train/validation/test pools and repeated seed uncertainty are not documented [pp. 15-16, Secs. 6.2-6.3]. | 4,096 training routes, 64 standard and 32 longer validation routes, and 400 fresh shared test routes; report five seeds and paired bootstrap intervals. This is route separation on one city, not geographic generalization. |
| Baselines and evaluation | Constant velocity greedy navigation plus radio/energy metrics and trajectory examples [pp. 13-14, Sec. 5.4; pp. 16-20, Sec. 7]. | Four deterministic references with shared constraints and control aids. Joint success is primary; failures remain visible and secondary contrasts use only common successful seed/route pairs. No original thesis success percentage is inferred from its plots. |

We retain the thesis's RSS and buffer requirements rather than add a new
application contract: **there is no two second packet deadline, imposed
minimum throughput or requirement to empty the queue at arrival**. The source
defines delay as queue divided by service rate [p. 9, Eq. (4)] and imposes
RSS and queue bounds [p. 11, Eq. (12)]. The simulation checks those bounds at
one second samples; it does not establish continuous physical connectivity.

The [mission definition](#exact-mission-definition-and-source-pages),
[physical model](#exact-data-and-physical-model-differences),
[actions and filter](#exact-actions-navigation-prior-and-filter),
[observations](#every-observation-feature), [reward](#exact-reward-difference),
[PPO settings](#every-ppo-setting) and [splits](#splits-budgets-and-independence)
below provide the exhaustive specification behind this summary.

## What V1.5 Versus V2 Actually Tests

| Component | V1.5 original reward | V2 full reward | Original thesis |
| --- | --- | --- | --- |
| Map, motion, traffic, energy and service model | Shared V2 system | Identical | Same radio dataset; different motion, traffic, service and energy models [pp. 6-10, Secs. 3.1-3.3]. |
| Observation, action mask, navigation aid and prospective filter | Shared V2 system | Identical | Discrete acceleration/heading and BS/RBG requests; six listed state components. Our braking aid, candidate mask and prospective filter are not specified [p. 12, Sec. 5.2; p. 15, Table 3]. |
| Success, failure and arrival termination | Shared V2 rules | Identical | Stopping intended, but arrival does not terminate; equivalent strict failure ordering is unspecified [p. 9, Sec. 3.2; p. 12, Sec. 5.2]. |
| PPO settings, training routes, seeds and interaction budget | Shared V2 settings | Identical | Stable Baselines PPO with different Table 4 settings; equivalent route pools and seed schedule NR [p. 13, Sec. 5.3; pp. 15-16, Sec. 6.2]. |
| Reward | Reconstructed original equal weight formula on V2 inputs | Replacement reward package | Equal policy uses reciprocal utilities, approach bonus and penalties; also studies three alternative weightings [p. 12, Eqs. (13)-(14); p. 15, Table 3; p. 16, Sec. 6.3]. |
| Final checkpoint | Every declared seed, at the fixed budget | Every declared seed, at the fixed budget | Checkpoint selection and seed specific weights NR in the evaluation description [pp. 15-16, Secs. 6.2-6.3]; original weights unavailable to this study. |

Five V1.5 policies were trained from scratch. All five full and five arrival
V2 checkpoints were reused, fixed by hash before the fresh comparison.
Training and validation pools are shared; test routes and load phases are
identical across controllers. Equal seeds and budgets do not imply identical
realized trajectories during learning. Shared reward normalization and
clipping respond to the changed rewards, so this tests the package rather
than any one reward term in isolation.

V2 `arrival` is an additional control that omits the direct radio cost while
retaining the same constraints. Its presence does not make the primary
V1.5 versus full V2 contrast a reproduction of the thesis simulator.

## General Results

Results in this initial comparison use **test seeds 53012 and 53013**, separate from
the earlier V2 evaluation. Standard routes span 200-1000 m; longer routes
span 1000-1800 m. Both ranges occur in training. There are 200 shared routes
per split, five learned training seeds per arm, and **7,600 final episodes**
across all controllers. Five seeds on shared routes are not 1,000 independent
training replications.

### Mission Completion

| Controller | Standard joint success | Longer joint success | Episodes per split | Original thesis counterpart and reported joint success |
| --- | ---: | ---: | ---: | --- |
| PPO original reward (V1.5) | 95.7% | 85.8% | 1,000 | Written equal policy reward is the source; original PPO joint success NR. These percentages belong to our V1.5 agent [p. 15, Table 3; pp. 17-18, Sec. 7.1/Figs. 5-6]. |
| PPO full reward (V2) | 95.7% | 87.3% | 1,000 | No corresponding replacement reward arm; original PPO joint success NR [pp. 16-20, Secs. 6.3-7.2]. |
| PPO arrival reward (V2) | 94.9% | 85.1% | 1,000 | No corresponding arrival reward arm; joint success NR [pp. 16-20, Secs. 6.3-7.2]. |
| Goal RSS | 94.0% | 84.5% | 200 | Closest reference is source greedy, with different motion and handover counters; source greedy joint success NR [pp. 13-14, Sec. 5.4; pp. 17-18, Figs. 5-6]. |
| Goal radio | 96.5% | 88.5% | 200 | Source greedy is not this capacity aware controller; source greedy joint success NR [pp. 13-14, Sec. 5.4; pp. 17-18, Figs. 5-6]. |
| Joint one step | 96.0% | 90.5% | 200 | No corresponding joint one step search reported [pp. 13-14, Sec. 5.4; p. 16, Sec. 6.3]. |
| Joint three steps | 92.0% | 90.5% | 200 | No corresponding joint three step search reported [pp. 13-14, Sec. 5.4; p. 16, Sec. 6.3]. |

The primary comparison is full V2 minus original V1.5 on standard routes.
Intervals use 5,000 crossed seed/route bootstrap draws, seed 63000.

| Contrast | Observed success difference | 95% interval | Original thesis comparison |
| --- | ---: | --- | --- |
| Standard, primary | 0.0 percentage points | [-2.8, 2.7] | NR: source compares PPO with greedy and changes policy weights; no matched replacement reward success contrast or confidence interval [p. 16, Sec. 6.3; pp. 17-20, Secs. 7.1-7.2]. |
| Longer, secondary | +1.5 percentage points | [-2.9, 6.1] | NR: no separately declared longer route success contrast or confidence interval [p. 16, Sec. 6.3; pp. 17-20, Secs. 7.1-7.2]. |

**Neither interval establishes improved completion.** This is not evidence
of equivalence: meaningful differences remain compatible with the intervals,
especially on longer routes. All successful missions satisfy the sampled
constraints; every failure remains in the denominator.

### Communication and Flight Tradeoffs

The values below are means on **925 standard** and **781 longer** matched
seed/route pairs where both original and full succeed. They are not means
over all flights, and each controller's unmatched successful subset is not
substituted for the common subset. A lower value is not universally better:
higher SINR is preferable, while lower delay and fewer handovers are distinct
objectives.

| Metric | Standard V1.5 | Standard V2 | Longer V1.5 | Longer V2 | Original thesis result and comparability |
| --- | ---: | ---: | ---: | ---: | --- |
| Flight time (s); lower | 31.252 | 28.112 | 65.394 | 60.145 | NR as a mean arrival time on common successful flights; source continues after arrival [p. 12, Sec. 5.2; pp. 17-20, Figs. 5-8]. |
| Handovers; lower while preserving service | 6.843 | 0.443 | 15.826 | 1.528 | CDFs on an unexplained 1e-2 axis scale; source PPO is lower than greedy. NC with our mean executed counts per successful flight [p. 18, Fig. 6; p. 20, Fig. 8; readings below]. |
| Delay proxy (s); lower | 1.942 | 5.827 | 2.857 | 6.818 | D = q/r is defined, but no numerical delay result is reported in the five metric panels, including the delay priority experiment [p. 9, Eq. (4); pp. 18, 20, Figs. 6, 8]. |
| Energy proxy (kJ); lower | 7.651 | 7.788 | 18.523 | 18.957 | Remaining energy bars, labeled kW, approximately 370 for PPO and 440 for greedy. NC with consumed kJ under our different proxy [p. 18, Fig. 6; p. 10, Eq. (10)]. |
| SINR (dB); higher | -8.322 | -9.305 | -8.773 | -9.957 | SNR CDF medians approximately 124 dB for PPO and 127 dB for greedy. NC: source SNR and our SINR use different arithmetic, and medians are not means [p. 10, Eq. (8); p. 18, Fig. 6]. |
| Interference (µW); lower | 0.753 | 0.748 | 0.794 | 0.791 | Uplink interference CDF medians approximately -35 dBm for PPO and -28 dBm for greedy. NC with mean linear cochannel downlink power [p. 10, Eq. (9); p. 18, Fig. 6]. |
| Accumulated radio cost; lower under fixed weights | 7.094 | 5.309 | 16.800 | 13.803 | NR for our transformed cost accumulated until joint arrival; source objective and positive reward are different quantities [p. 10, Eq. (11); p. 12, Eqs. (13)-(14)]. |

Full V2 reduces handovers by 93.5% on standard pairs and 90.3% on longer
pairs, with flights shorter by 3.14 s and 5.25 s. Its delay proxy increases
by 200.1% and 138.7%, and energy proxy increases by 1.8% and 2.3%.
SINR decreases; interference differences remain inconclusive. These are
substantial service tradeoffs despite similar completion rates.

The lower accumulated radio cost combines several weighted components and
depends on flight duration. It does not establish uniformly better service.
The [complete result note](docs/37_v15_reward_results.md) retains every paired
interval; secondary intervals are descriptive and are not adjusted for
multiple comparisons.

### Failures Remain Part of the Result

Counts below use all 1,000 episodes per arm and split, not only common
successes. Each episode contributes its first failure reason.

| First failure | Standard V1.5 | Standard V2 | Longer V1.5 | Longer V2 | Original thesis result |
| --- | ---: | ---: | ---: | ---: | --- |
| Serving RSS below minimum | 40 | 34 | 136 | 112 | Failed mission count NR; outage bars show approximately 0 s for PPO and 2 s for greedy, without our first violation termination semantics [p. 18, Fig. 6]. |
| Buffer overflow | 3 | 9 | 6 | 15 | Overflow failure count NR. The source discusses removing a buffer dump reward penalty, not a measured zero overflow rate [pp. 20-21, Sec. 7.3]. |
| Total failed missions | 43 | 43 | 142 | 127 | Joint failed mission total NR; neither trajectory plots nor outage bars establish this count [pp. 17-20, Figs. 5-8]. |

Neither of these two arms has an energy, boundary or timeout failure in these
tests. Full has fewer observed RSS failures but more buffer failures. These
counts do not establish a general reliability advantage; the completion
intervals above remain the relevant comparison.

### Original Thesis Results: What the Figures Actually Report

This table includes all five outcomes plotted in the original thesis, plus
mission completion, flight time, delay and aggregate cost. The values marked
**≈ are visual readings**, rounded to the precision supported by the plots.
For a CDF, the reading is the approximate median at cumulative probability
0.5; for a bar, it is its height. These are not tabulated source means,
verified physical values, or measurements recomputed from the dataset.

The original equal PPO and greedy results come from **printed p. 18, Fig. 6**.
The three priority policies come from **printed p. 20, Fig. 8**, in the order
delay / interference / handover. We preserve the source labels and scaling
even where their physical interpretation is unresolved. The original raw
evaluation records and plotting code are unavailable to this study.

Our numerical pairs are always **V1.5 / full V2**. Flight time and service
values use the same 925 standard and 781 longer common successful pairs as
the preceding table. Completion and failure counts use all 1,000 episodes
per arm and split. Original CDF medians and bars keep their own source
aggregation; placing numbers together does not make those statistics equivalent.

| Outcome and preferred direction | Original equal PPO / greedy, Fig. 6 | Original priority PPO D / I / H, Fig. 8 | Our V1.5 / full V2: standard | Our V1.5 / full V2: longer | Interpretation and comparison limit |
| --- | --- | --- | --- | --- | --- |
| Joint mission success: higher | NR / NR | NR / NR / NR | 95.7% / 95.7% | 85.8% / 87.3% | Completion is primary. V2 differences are 0.0 pp [-2.8, 2.7] and +1.5 pp [-2.9, 6.1]; neither establishes improved completion. No original percentage can be recovered from its plots. |
| Arrival flight time: lower, conditional on success | NR / NR | NR / NR / NR | 31.252 / 28.112 s | 65.394 / 60.145 s | V2 completes common successful flights sooner. Source arrival does not terminate [p. 12, Sec. 5.2], so its episode length would not be a matched arrival time. |
| Signal quality: higher SNR or SINR | SNR CDF median ≈124 / ≈127 dB | SNR CDF median ≈122-123 dB for all three | Mean SINR -8.322 / -9.305 dB | Mean SINR -8.773 / -9.957 dB | V2 has lower SINR, by 0.983 and 1.184 dB. A less negative value is higher. NC across studies: source SNR arithmetic and CDF medians differ from our mean SINR [p. 10, Eq. (8)]. |
| Outage: lower | Bar ≈0 / ≈2 s | Bar ≈0 / ≈1 / ≈1 s | 0 / 0 s on successes | 0 / 0 s on successes | Zero is required for our successful missions, so this alone is not evidence of a better controller. All failed episodes remain in success denominators; source bars do not establish strict joint success. |
| Interference: lower | Uplink CDF median ≈-35 / ≈-28 dBm | Uplink CDF median ≈-40 / ≈-40 / ≈-38 dBm | Mean downlink 0.753 / 0.748 µW | Mean downlink 0.794 / 0.791 µW | V2 point estimates are slightly lower, but paired intervals include zero. In dBm, more negative means less power. NC across studies: source Eq. (9), power aggregation and statistic differ [p. 10]. |
| Energy: higher remaining; lower consumed | Remaining bar ≈370 / ≈440, axis kW | Remaining bar ≈310 / ≈260 / ≈770, axis kW | Consumed proxy 7.651 / 7.788 kJ | Consumed proxy 18.523 / 18.957 kJ | V2 uses more proxy energy, by 1.8% and 2.3%. NC with source remaining energy: kW is a power unit, and the energy models differ [p. 10, Eq. (10); p. 15, Table 3]. |
| Handovers: usually lower, while preserving service | CDF median raw x ≈0.0046 / ≈0.0129 | CDF median raw x ≈0.0025 / ≈0.0041 / ≈0.0033 | Mean executed count 6.843 / 0.443 | Mean executed count 15.826 / 1.528 | V2 reduces handovers by 93.5% and 90.3%, but delay worsens. NC with source raw x values: both axes say "over 200 episodes" and use 1e-2 scaling; normalization is unspecified. |
| Transmission delay: lower | NR / NR | NR / NR / NR | Mean q/r proxy 1.942 / 5.827 s | Mean q/r proxy 2.857 / 6.818 s | V2 delay increases by 200.1% and 138.7%. This is backlog divided by capacity, not measured packet latency. A delay priority policy name does not supply a source delay result [p. 9, Eq. (4); p. 16, Sec. 7]. |
| Accumulated radio cost: lower under these fixed weights | NR / NR | NR / NR / NR | 7.094 / 5.309 | 16.800 / 13.803 | V2 cost falls by 25.2% and 17.8%, despite worse delay, energy and SINR. Cost combines transformed terms and duration; it is not an overall service score. Source objective/reward are different quantities [p. 10, Eq. (11); p. 12, Eqs. (13)-(14)]. |
| RSS first failures: lower | NR; outage bars are different | NR / NR / NR | 40 / 34 out of 1,000 | 136 / 112 out of 1,000 | V2 has fewer observed RSS failures. These counts use all flights, not the common successful subset. Equivalent original mission failure counts are unreported [pp. 18, 20, Figs. 6, 8]. |
| Buffer first failures: lower | NR / NR | NR / NR / NR | 3 / 9 out of 1,000 | 6 / 15 out of 1,000 | V2 has more overflows. Zero sampled outage among successful flights does not erase these failures. Source removes a dump reward penalty but gives no measured overflow count [pp. 20-21, Sec. 7.3]. |
| Trajectory: successful feasible arrival first | PPO prioritizes radio metrics; greedy prioritizes destination | Wandering and overshoot discussed | 925 common successful pairs | 781 common successful pairs | Counts specify the subset for our flight/service means, not an original route score. Straightness alone is not a quality metric. Both rewards share our goal and braking aid [p. 17, Sec. 7.1/Fig. 5; p. 19, Sec. 7.2/Fig. 7]. |

The source's qualitative finding is lower interference and fewer handovers
for PPO than greedy [printed p. 17, Sec. 7.1]. In the priority comparison,
the author describes broadly similar SNR and outage, and discusses wandering
and overshoot [printed p. 19, Sec. 7.2]. The plot readings above preserve
what is shown, including the visible differences between energy bars; they
do not turn those descriptions into a matched statistical comparison with V2.
The [comparison provenance note](docs/44_readme_original_thesis_comparisons.md)
records the reading convention and all limits.

### How to Read These Numbers

**Completion comes first.** V2 has no measured standard completion advantage.
Its longer route point estimate is higher, but the interval still admits no
improvement. A controller that fails early can appear efficient in flight time,
energy or handovers, which is why those comparisons use common successes.

**V2 exchanges delay and signal quality for fewer handovers and shorter flights.**
For standard missions it saves about 3.14 s and 6.40 handovers, while adding
about 3.89 s to the average delay proxy and 0.137 kJ to energy consumption.
For longer missions it saves about 5.25 s and 14.30 handovers, while adding
about 3.96 s of delay and 0.434 kJ. Lower handover counts are useful only
alongside acceptable connectivity and service; zero handovers is not the goal.

**The original plots support their own limited comparisons.** Within Fig. 6,
PPO has lower plotted interference and handovers and less outage than greedy;
greedy has slightly higher plotted SNR and remaining energy. In Fig. 8, the
handover priority policy has the highest remaining energy bar, but that alone
does not demonstrate successful or efficient mission completion. Values such
as 124 dB SNR and the fractional handover axis must not be read as a numerical
advantage over our differently defined SINR and executed counts.

The cost decrease is explained by the reward tradeoff, not by uniform improvement.
For example, V2's delay cost is `0.35 × 10D / (1 + 10D)`: it is approximately
0.318 at D = 1 s, 0.344 at D = 6 s and 0.347 at D = 10 s. One handover adds
approximately 0.347 at that step. Once delay is large, making it worse adds
little immediate cost. This algebra motivates a new reward experiment; it does
not by itself establish the cause of the learned behavior or a successful fix.

## Conclusions and Revised Diagnosis

The following conclusions concern the initial 53012/53013 comparison. The V2.1 followup above has its own fresh results and interpretation.

1. **We have not demonstrated that reward replacement improves mission
   completion.** V1.5 performs similarly on the observed completion rates
   when given the same system as V2. An interval containing zero does not
   prove the controllers equivalent.
2. **The rewards are not interchangeable in their service behavior.** Full
   favors fewer handovers and faster flights, at the cost of higher delay,
   slightly higher proxy energy and lower SINR on common successful flights.
   It is not an overall better controller according to all measured goals.
3. **The earlier diagnosis attributing the thesis's wandering primarily to
   reward design was too strong.** The source itself considers reward,
   movement implementation and training difficulty as possible explanations
   [TFM, p. 19, Sec. 7.2]. Our new comparison does not identify which caused
   its difficulties. Source Fig. 7 is not a quantitative matched baseline.
4. **The shared changes could compensate for reward weaknesses.** Explicit
   velocity/goal observations, braking guidance, termination, action masks
   and the prospective filter are plausible contributors, but their
   individual causal effects have not been measured. V1.5's success neither
   validates the original reward in the original system nor proves it caused
   the original failure.
5. **No overall PPO superiority is established.** Goal radio has the highest
   observed standard completion and the joint search references have the
   highest observed longer completion in this comparison. Those rankings
   alone are not significance tests or general guarantees.
6. **The defensible contribution is a reproducible controlled comparison
   with explicit mission criteria and visible tradeoffs.** We provide the
   received map interface, source, 15 final models, shared tests, failures,
   uncertainty, exact replays and traceable thesis comparisons. We do not
   claim a reproduced fix to the unavailable thesis code or validated real
   world performance.

Dataset identity is confirmed by the researcher who supplied the file; it is
not an unresolved difference from the thesis. The [provenance update](docs/43_confirmed_thesis_dataset_identity.md)
records that confirmation. Using the same dataset does not imply the same
simulator, controller, training procedure or evaluation routes.

The study's implementation passed 73 tests and all 7,600 final evaluations
replayed exactly. The long route illustration additionally repeated 600
existing records exactly; these are not new independent samples. Such checks
verify computational consistency, not the accuracy of the physical proxies.

To explain the original failure, the next research needs the original code
or a separately declared reconstruction, followed by controlled ablations of
navigation guidance, observations, termination and filtering. Generalization
also requires independent maps and traffic conditions. Those experiments
have not been run, and the present test routes must not be used to tune them.

### Long Route Illustration

The [paper's long route illustration](results/reward_comparison/analysis_v15/reward_comparison_example.png)
shows the longest declared longer test route (1,784.7 m), all 87 base stations
and executed handovers. Its [eight diagnostic plots](results/reward_comparison/analysis_v15/reward_comparison_diagnostics.png)
show RSS, SINR, queue, capacity, handovers, delay, energy and interference.
Route selection uses distance, not outcomes; this example does not replace
the aggregate comparison. The [revision record](docs/41_long_route_figure_revision.md)
documents selection, reproduction and exact replay checks.

This 1,784.7 m example has 18, 1 and 2 handovers for original reward, full
reward and Goal radio, respectively. All three succeed, but full's queue
reaches 99.19% of capacity. Nearly straight, overlapping paths therefore do
not imply equivalent service. This example illustrates mechanisms rather
than replacing the aggregate comparison above.

## Setup: Dataset and Model Checkpoints

A clone includes source, configuration, results and **all 20 final checkpoints**:
five original reward V1.5, five full V2, five arrival V2 and five service V2.1.
Their combined size is about **2.74 MB**. The initial fifteen remain in their
original manifest; [the V2.1 manifest](models/service_reward_manifest.json) adds
five final policies and their hashes. The private map must be supplied separately by its owner.

`Barcelona_dataset_January.h5` is the same dataset used in the original
thesis. Its required location and checksum are given below.

Use these paths relative to the repository root:

```text
UAV_joint_handover_trajectory_optimization/
  dataset/
    Barcelona_dataset_January.h5
  results/
    reward_comparison/
      confirmatory_v15/
        original_seed_2101/
          checkpoint.pt
    connectivity_experiment/
      confirmatory_v2/
        full_seed_2101/
          checkpoint.pt
        arrival_seed_2101/
          checkpoint.pt
```

Each arm also includes seeds 2102 through 2105. Seed 2101 is the first declared
seed, not a selected best model. The [checkpoint manifest](models/checkpoint_manifest.json)
lists the initial fifteen paths, sizes and SHA256 values; the V2.1 manifest
lists the additional five. Checkpoints contain policy tensors and
configuration metadata, not the dataset.

The dataset belongs in singular `dataset`, not `data/raw`, `data/processed`
or the parent research folder. There is no `--dataset` override. Expected
size: **2,327,593,160 bytes**. SHA256:

```text
d4630dd3a6c45419e12d0b60dd08473c4ffa4062ca4fab1decabecf2b992ea0d
```

From the repository root, with Python 3.12 and PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-experiments.txt
Test-Path -LiteralPath dataset/Barcelona_dataset_January.h5
```

Evaluate both rewards on the same 200 new standard routes:

```powershell
.\.venv\Scripts\python.exe scripts/evaluate_reward_controller.py --checkpoint results/reward_comparison/confirmatory_v15/original_seed_2101/checkpoint.pt --split test --output outputs/original_test
.\.venv\Scripts\python.exe scripts/evaluate_reward_controller.py --checkpoint results/connectivity_experiment/confirmatory_v2/full_seed_2101/checkpoint.pt --split test --output outputs/full_test
```

A custom deterministic flight needs the dataset but no weights:

```powershell
.\.venv\Scripts\python.exe scripts/evaluate_reward_controller.py --controller straight_radio --start 1000 1000 --goal 1800 1300 --output outputs/custom_radio
```

Coordinates are local meters, x in [0,5000] and y in [0,3500]. Supply both
`--start` and `--goal`; they replace the saved split. `--output` is a file
prefix, producing JSON and CSV. Reusing a prefix overwrites those files.
JSON includes every episode record and traces for the first four routes.
The [complete guide](docs/35_dataset_and_model_setup.md) covers absolute paths,
checksum verification, splits, environment installation and troubleshooting.

For a V2.1 checkpoint, use its dedicated evaluator and a fresh output prefix:

```powershell
python scripts/evaluate_service_reward_controller.py --checkpoint results/service_reward_v21/confirmatory/service_seed_2101/checkpoint.pt --split validation --output outputs/service_validation_01
```

The [V2.1 guide](docs/49_service_reward_models_and_reproduction.md) explains its
500 route test splits, custom flights and complete reproduction under a new label.

## Exact Mission Definition and Source Pages

| Component | Current behavior | Original TFM locator or difference |
| --- | --- | --- |
| Joint objective | Complete the mission under sampled RSS and queue constraints; report all three radio costs | Weighted delay, interference and handover objective, with mission and feasibility constraints [p. 10, Eq. (11); p. 11, Eq. (12)] |
| Goal position | Within 10 m | 10 m tolerance, retained [p. 15, Table 3] |
| Goal speed | At most 2 m/s | Arrival at a halt is intended; numerical terminal speed tolerance NR [p. 9, Sec. 3.2]. Our 2 m/s tolerance is new |
| Deadline | 200 s, 200 decisions | 2,000 steps and 0.1 s imply 200 s using the tables [pp. 15-16, Tables 3-4]; prose says 1 ms [p. 14, Sec. 6.1] |
| RSS feasibility | At least -96 dBm at every modeled sample, including initial RSS | RSS bound C2 and -96 dBm minimum [p. 11, Eq. (12); p. 15, Table 3]; identical initial and terminal enforcement is not documented |
| Queue feasibility | No overflow beyond 1,280,000 bits | Bounded queue C4, 160 KB [p. 11, Eq. (12); p. 15, Table 3]; ours explicitly uses decimal KB |
| Termination | Arrival, first violation or timeout, in training and evaluation | Arrival explicitly continues; energy exhaustion terminates. Equivalent immediate RSS/overflow termination is unknown [p. 12, Sec. 5.2] |
| Event priority | Constraint violations override simultaneous arrival; boundary, energy, RSS, buffer, success, timeout reason priority | Equivalent simultaneous event priority NR in the reward/termination description [p. 12, Sec. 5.2]; original code unknown |
| Outstanding queue | Allowed at arrival and reported | Queue and delay are defined, with bounded queue C4; no empty queue arrival condition stated [p. 9, Eqs. (4)-(5); p. 11, Eq. (12)] |
| Packet deadline / minimum rate | Not imposed | No numeric packet deadline or minimum throughput requirement stated in the delay model/constraint set [p. 9, Eq. (4); p. 11, Eq. (12)] |
| Failure reporting | First RSS, buffer, boundary, energy or timeout failure | Reports radio metrics and trajectories, without our first reason joint failure counts [pp. 16-20, Sec. 7/Figs. 5-8] |
| Sampling | One second checks only | Discrete timesteps, with conflicting 0.1 s / 1 ms declarations [pp. 14-15, Sec. 6.1/Table 3]. Our one second checks do not establish physical continuity |

All TFM citations use **printed pages**. PDF viewer page = printed page + 2.
The [original PDF](sources/UAV_Bermudez_Granados_2026_MSc_thesis.pdf) is retained.
Missing original details mean unknown, not proven absent.

## Exact Data and Physical Model Differences

| Component | V2 implementation | Original definition or limitation |
| --- | --- | --- |
| Executable | New Python implementation; original simulator and policies unavailable | Stable Baselines/custom environment described on p. 13, Sec. 5.3 |
| Propagation | Use the same thesis RSS dataset at native resolution; do not rerun ray tracing | MATLAB, 3D scene and station collection, pp. 6-7, Sec. 3.1 |
| RF metadata | 2.1 GHz, 100 m altitude; 87 of 133 sites | Same thesis dataset; parameters on pp. 6-7, Table 2; Operator 1 selection on p. 14, Sec. 6.1 |
| Region | 5000 by 3500 m, fixed altitude; no collision model | Scene used for propagation, p. 6; original collision logic unspecified |
| Grid | Nearest lookup; actual spacings 1.00020004 and 1.00028580 m | Nominal one meter resolution, p. 7; indexing unspecified |
| Quantization | Preserve int8; promote before arithmetic; provisional -128 sentinel means zero watts | Storage dtype, indexing and missing value convention NR in the dataset description [pp. 6-7, Sec. 3.1]; sentinel interpretation remains unconfirmed |
| Power | Use stored RSS directly, without adding 46 dBm again | 46 dBm transmission power, sector maximum and downlink budget [p. 7, Eq. (1)/Table 2]; stored received powers already include the source budget |
| Motion | Inertial vector velocity and trapezoidal position update | Source scalar speed and chosen direction, p. 9, Eq. (2) |
| Bounds | Acceleration norm 5 m/s², hard speed cap 25 m/s | Acceleration -5 to 5 m/s² in five bins; eight directions; speed threshold 100 m/s [p. 15, Table 3] |
| Step | 1 s | Source table 0.1 s, p. 15; prose 1 ms, p. 14 |
| Interference | Sum linear cochannel downlink power, excluding serving station | Sum of neighboring RSS values, labeled uplink [p. 10, Eq. (9)]; cochannel occupancy and linear unit handling are not explicit in that equation |
| Noise | -112.41 dBm plus 9 dB = -103.41 dBm, converted to watts | Thermal noise -112.41 dBm and noise figure 9 dB, retained [p. 15, Table 3] |
| Rate | 1.44e6 × log2(1 + linear SINR) bit/s | Printed r = bandwidth + log2(SNR), with SNR = RSS minus thermal noise minus noise figure [p. 10, Eqs. (7)-(8)]; our dimensional service formula is different |
| Bandwidth | Eight 180 kHz blocks per group; 12 groups | 12 groups, eight blocks per group, 180 kHz per block, retained [p. 15, Table 3] |
| Traffic | Constant 200,000 bit/s | Poisson packet model, lambda 100; 2,000 bits per data packet in Table 3 versus 1,000 bits in prose [pp. 9-10, Eqs. (5)-(6); pp. 14-15]. Constant 200 kbit/s is our replacement, not an established source arrival rate |
| Queue order | Add traffic/overhead, subtract service, count overflow, clip | Source p. 9, Eq. (5); exact source event order unknown |
| Delay | Postservice backlog / max(rate,1), censored at 200 s | D = q/r [p. 9, Eq. (4)]; our rate floor, postservice sampling and 200 s censoring are not specified there. Neither expression directly tracks packet latency |
| Handover overhead | 4,800 bits per executed handover | Four control packets of 1,200 bits per handover, retained [pp. 14-15, Sec. 6.1/Table 3] |
| Occupancy | Static deterministic half occupied pattern with saved phase | 50% in Table 3; prose says at least 50% randomly occupied. No equivalent fixed load phase specified [pp. 14-15, Sec. 6.1/Table 3] |
| Interruption | No switching delay or separate same station resource change cost | A3/resource handling and control packets are described; calibrated switching interruption duration NR [p. 9, Sec. 3.3.1; pp. 14-15, Sec. 6.1/Table 3] |
| Energy | (100 + 0.4 × speed²) × dt J; 100 kJ budget | Eq. (10) uses velocity, 3 kg mass, lift/drag 5, efficiency 55%, electronics 0.1 kW; capacity is printed as 1000 kW [p. 10; p. 15, Table 3]. Our proxy replaces that model and is not a unit conversion |

## Exact Actions, Navigation Prior and Filter

The actor has two Gaussian radial/lateral motion variables and 61 categorical
network logits. Tanh motion residuals, scaled by 0.5, augment a projected goal
braking command. Physical projection follows. Desired speed is
`min(25, 0.7 × sqrt(2 × 5 × max(distance - 4, 0)))`. This shared prior supplies
navigation competence. Source discrete acceleration/heading actions differ
[TFM, p. 12, Sec. 5.2; p. 15, Table 3].

| Detail | Exact behavior | Original thesis definition or status |
| --- | --- | --- |
| Candidates | Serving station plus four strongest signals, stable RSS ordering | 87 Operator 1 stations; the written action requests a station, without our top four restriction [p. 12, Sec. 5.2; pp. 14-15, Sec. 6.1/Table 3]. |
| Duplicate serving slots | Masked except the designated serving slot | Candidate slots and duplicate masks NR in the listed action [p. 12, Sec. 5.2]. |
| Options | Stay plus five slots × 12 groups = 61 | Separate requested BS and requested RBG; 87 stations and 12 groups. A 61 option joint encoding is not specified [p. 12, Sec. 5.2; p. 15, Table 3]. |
| A3 | Target RSS strictly greater than serving RSS + 3 dB and at least -96 dBm [TFM, p. 9, Eq. (3); p. 15] | Eq. (3) requires target RSS > serving RSS + offset. Offset is printed as 3 dBm; we interpret the difference as 3 dB. RSS minimum is -96 dBm [p. 9, Eq. (3); p. 15, Table 3]. |
| Resources | Only free target groups; explicit stay always available | Unavailable group: keep current RBG; after a simultaneous handover, allocate the first available group. Our mask excludes unavailable requests beforehand [p. 9, Sec. 3.3.1]. |
| Decision interval | Every modeled second | Table step 0.1 s; prose says 1 ms. Greedy additionally uses consecutive viability counters; its threshold is unspecified [pp. 13-15, Secs. 5.4/6.1, Table 3]. |
| Same station group changes | Permitted; resource changes are distinct from handovers | RBG requests can be made besides BS requests; independent changes are described, but their separate cost is not specified [p. 9, Sec. 3.3.1]. |
| Initialization | Strongest RSS and first free deterministic group | Initial station selection NR; first available group is specified for greedy and as a handover fallback [p. 9, Sec. 3.3.1; pp. 13-14, Sec. 5.4]. |
| Filter | Predict next position/RSS/queue; repair network first, then local joint motion if needed | No equivalent prospective network/motion repair procedure is specified in the environment or action description [pp. 9-12, Secs. 3.2-5.2]. |
| Information | Known map and dynamics at prospective positions, shared by all arms | Offline radio map is available; lookahead map queries inside a repair controller are not specified [pp. 6-8, Sec. 3.1; p. 12, Sec. 5.2]. |
| Unresolved violation | Still terminates failure; mask cannot be bypassed | RSS penalty and energy termination are stated; equivalent strict queue/RSS termination and mask enforcement are unknown [p. 11, Eq. (12); p. 12, Sec. 5.2]. |
| Diagnostics | Network and motion interventions counted separately | Intervention counts NR in the five reported metrics [p. 16, Sec. 7; pp. 18, 20, Figs. 6, 8]. |
| PPO likelihoods | Proposed actions; projection and filtering are environment transformations | PPO probability ratio is described; likelihood handling of projected or repaired actions is unspecified [p. 13, Algorithm 1]. |

The source lists BS and RBG requests [TFM, p. 12, Sec. 5.2]. Candidate
restriction, masks, residual motion and the filter are our implementation.

## Every Observation Feature

V1.5, full V2, arrival V2 and V2.1 all have the same 156 inputs; indices are zero based.

| Indices | Definition | Original thesis listed state |
| --- | --- | --- |
| 0-1 | Position / map dimensions | x and y are listed; coordinate normalization is unspecified [p. 12, Sec. 5.2]. |
| 2-3 | Unit goal direction | Goal direction is not in the listed state [p. 12, Sec. 5.2]. |
| 4 | Goal distance / 1,000 m | Goal distance is not in the listed state [p. 12, Sec. 5.2]. |
| 5-6 | Radial and lateral velocity / 25 m/s | Velocity components are not in the listed state [p. 12, Sec. 5.2]. |
| 7 | Speed / 25 m/s | Speed is not in the listed state [p. 12, Sec. 5.2]. |
| 8 | Elapsed decision count / 200 | Elapsed or remaining time is not in the listed state [p. 12, Sec. 5.2]. |
| 9 | Queue / 1,280,000 bits | Queue q(t) is listed; normalization is unspecified [p. 12, Sec. 5.2]. |
| 10 | Consumed energy / 100,000 J | Energy E(t) is listed, defined as remaining energy on p. 10, Eq. (10); our input is consumed fraction [p. 12, Sec. 5.2]. |
| 11-12 | Background phase / 11 and serving RBG / 11 | Serving group G_ks(t) is listed; background phase is not. Normalization is unspecified [p. 12, Sec. 5.2]. |
| 13 | Serving SINR in dB / 30 | Serving SINR is not in the listed state; source instead defines SNR on p. 10, Eq. (8) [p. 12, Sec. 5.2]. |
| 14-18 | Five candidate RSS values, (RSS + 70) / 60 | Candidate RSS values are not in the listed state [p. 12, Sec. 5.2]. |
| 19-28 | Candidate x/y offsets / 5,000 m | Candidate coordinates or relative offsets are not in the listed state [p. 12, Sec. 5.2]. |
| 29-33 | Candidate station indices / 86 | Serving station k_s(t) is listed; four additional candidate indices and their encoding are not specified [p. 12, Sec. 5.2]. |
| 34-94 | log(1 + option capacity / 200000), for 61 choices | Action specific capacities are not in the listed state [p. 12, Sec. 5.2]. |
| 95-155 | Network mask | An observation mask is not in the listed state [p. 12, Sec. 5.2]. |

The source lists six state components [TFM, p. 12, Sec. 5.2]; this layout is
an explicit replacement, not a reconstruction of undocumented original tensors.

## Exact Reward Difference

| Reward component | Original thesis | V1.5 on the shared V2 system | Full V2 |
| --- | --- | --- | --- |
| Radio transform and scale | Positive 1/(1 + beta × metric); beta values 10, 100000, 100 [p. 12, Eq. (13); p. 15, Table 3] | Same written transform and scales, evaluated on V2 delay, interference and executed handovers | Negative beta × metric/(1 + beta × metric), with the same three scales |
| Equal policy weights, D / I / H | 0.35 / 0.30 / 0.35 [p. 15, Table 3] | Retained | Retained in transformed radio cost |
| Priority policy weights | Prioritized metric 0.8, each other metric 0.2 as printed; these sum to 1.2 despite the unit sum statement [p. 10, Sec. 4; p. 15, Table 3] | Not trained in this comparison | Not trained in this comparison; arrival is a separate radio cost omission control |
| Progress toward goal | +12 for a closer step [p. 12, Eq. (14); p. 15, Table 3] | Retained | Discounted potential difference including distance and stopping distance |
| Time payment | No explicit fixed time cost in Eq. (14) [p. 12] | None added | -0.05 per step |
| Boundary / RSS / speed penalties | -10 each; RSS <= -96 dBm and speed >= 100 m/s [p. 12, Eq. (14); p. 15, Table 3] | Retained; 100 m/s cannot occur under the shared cap | -20 at any terminal failure; no separate original threshold payments |
| Energy exhaustion | Overrides the whole reward with -10 and ends the episode [p. 12, Sec. 5.2; p. 15, Table 3] | Reward override retained under V2 energy accounting | Terminal failure payment -20 |
| Arrival reward and episode end | No arrival payment in Eq. (14); arrival explicitly does not terminate [p. 12, Sec. 5.2] | No new arrival payment, but shared V2 arrival termination stays | +20 for joint success, followed by termination |
| Buffer overflow / timeout | No extra explicit payment in the final Eq. (14); previous dump penalty removed [p. 12; pp. 20-21, Sec. 7.3] | No new payments; shared V2 failure termination stays | -20 terminal failure payment |
| Terminal potential | No potential shaping specified in Eq. (14) [p. 12] | None | Next potential zero at every terminal, including timeout |
| Reward normalization and clipping | Exact wrappers and settings NR [p. 13, Sec. 5.3; pp. 15-16, Sec. 6.2/Table 4] | Shared discounted return variance normalization and clipping | Identical mechanism, whose statistics respond to the different reward |

V1.5 reconstructs the source equal policy [TFM, p. 12, Eqs. (13)-(14);
p. 15, Table 3], using the same executed V2 quantities:

```text
original = 0.35/(1 + 10D) + 0.30/(1 + 100000I) + 0.35/(1 + 100h)
           + 12 × 1[distance decreases]
           - 10 × boundary - 10 × 1[RSS <= -96 dBm] - 10 × 1[speed >= 100 m/s]
energy exhaustion: override the whole reward with -10

radio_cost = 0.35 × 10D/(1 + 10D) + 0.30 × 100000I/(1 + 100000I)
             + 0.35 × 100h/(1 + 100h)
Phi = -(distance + speed²/(2 × 5))/100
full = 0.99 × Phi_next - Phi_now - 0.05 - radio_cost
       + 20 × joint_success - 20 × terminal_failure
arrival = full + radio_cost
```

`Phi_next` is zero at every terminal, including timeout. D is delay in seconds,
I is interference in watts and h denotes executed handover. V1.5 preserves
the source RSS equality penalty although joint feasibility allows equality.
Its 100 m/s reward threshold cannot activate under the shared 25 m/s cap.
No new arrival, timeout or overflow payment is added to V1.5. Removed source
energy utility and data dump terms are not restored [TFM, pp. 20-21, Sec. 7.3].

Arrival termination stays V2. The source's continued training after arrival
[TFM, p. 12, Sec. 5.2] is deliberately not restored. Both rewards undergo the
same variance normalization and clipping. This comparison isolates the reward
package, not the benefit of one component or the cause of original wandering.

## Every PPO Setting

The new PPO source differs only in its environment import and description;
a structural test checks this. Original PPO definitions are on TFM p. 13,
Sec. 5.3 and pp. 15-16, Sec. 6.2/Table 4. Current controlled settings are
compared below. Unreported details remain unknown; library defaults are not
assumed to establish the original configuration.

| Setting | Value | Original thesis setting |
| --- | --- | --- |
| Parallel environments / rollout | 64 / 128 | Environment count NR; 8 steps per environment before an update [p. 16, Table 4]. |
| Minibatch / epochs | 512 / 4 | Batch size 32; optimization epochs per update NR [p. 16, Table 4]. |
| Actor and critic | Separate networks, two 64 unit tanh layers each | NR in the PPO description and parameter table [p. 13, Sec. 5.3; pp. 15-16, Sec. 6.2/Table 4]. |
| Learning rate / Adam epsilon | 0.0003 / 1e-5 | Learning rate 0.00003; Adam epsilon NR [p. 16, Table 4]. |
| Discount / GAE | 0.99 / 0.95 | 0.99 / 0.95, retained [p. 16, Table 4]. |
| PPO clip / entropy weight | 0.2 / 0.005 | Clip 0.2, retained; entropy coefficient 0.01, reduced here to 0.005 [p. 16, Table 4]. |
| Target KL | No early stopping threshold; approximate KL is logged diagnostically | 0.03 [p. 16, Table 4]. |
| Value weight / gradient norm | 0.5 / 0.5 | Value coefficient 0.5, retained; gradient norm limit NR [p. 16, Table 4]. |
| Interactions per policy / CPU threads | 524,288 / 2 | 300 episodes, up to 2,000 steps each: nominal ceiling 600,000, not an actual interaction log. CPU threads NR [p. 16, Table 4]. |
| Hidden initialization | Orthogonal gain sqrt(2), zero biases | NR in the PPO description and parameter table [p. 13, Sec. 5.3; pp. 15-16, Sec. 6.2/Table 4]. |
| Action / value head gain | 0.01 / 1 | NR in the PPO description and parameter table [p. 13, Sec. 5.3; pp. 15-16, Sec. 6.2/Table 4]. |
| Initial motion log standard deviation | -0.5 | Actions are discrete; no Gaussian motion log standard deviation is specified [p. 12, Sec. 5.2; p. 15, Table 3]. |
| Log standard deviation clamp | [-2.3, 0.5] | No Gaussian motion clamp is specified [p. 12, Sec. 5.2; p. 15, Table 3]. |
| Invalid logits | -1e9 | No equivalent invalid action logits are specified [p. 12, Sec. 5.2; p. 13, Sec. 5.3]. |
| Reward normalization | Running variance of discounted returns; not mean centered | NR in the PPO description and parameter table [p. 13, Sec. 5.3; pp. 15-16, Sec. 6.2/Table 4]. |
| Reward clipping | [-10, 10] after normalization | NR in the PPO description and parameter table [p. 13, Sec. 5.3; pp. 15-16, Sec. 6.2/Table 4]. |
| Advantage normalization | Per minibatch, epsilon 1e-8 | NR in the PPO description and parameter table [p. 13, Sec. 5.3; pp. 15-16, Sec. 6.2/Table 4]. |
| Value loss | 0.5 × squared error, then configured value weight 0.5 | Mean squared value regression in Algorithm 1; value coefficient 0.5. Exact implementation prefactor unspecified [p. 13, Algorithm 1; p. 16, Table 4]. |
| Terminal GAE | No bootstrap or carry across any terminal, including timeout | Terminal and timeout bootstrap handling NR; arrival explicitly does not end an episode [p. 12, Sec. 5.2; p. 13, Algorithm 1]. |
| Evaluation | Gaussian mean and categorical argmax | Deterministic versus sampled evaluation action selection NR [pp. 16-20, Secs. 6.3-7.2]. |
| Checkpoint contents | Policy tensors, dimensions, config metadata and final step count | Checkpoint contents NR; original weights unavailable to this study [pp. 15-16, Secs. 6.2-6.3]. |
| Model selection | Final budget checkpoint for every declared seed | Training settings and tuning observations are described, but equivalent final checkpoint selection across declared seeds is NR [pp. 15-16, Sec. 6.2]. |

## Splits, Budgets and Independence

| Pool or budget | Size | Definition | Original thesis protocol |
| --- | ---: | --- | --- |
| Training | 4,096 routes | Exact V2 seed 52010, lengths 200-1800 m | 300 training episodes are listed, not a 4,096 route pool; route generator seed and length distribution NR [pp. 15-16, Secs. 6.2-6.3]. |
| Validation | 64 routes | Exact V2 seed 52001, lengths 200-1000 m | Equivalent independent validation pool, count and seed NR [pp. 15-16, Secs. 6.2-6.3]. |
| Longer validation | 32 routes | Exact V2 seed 52002, lengths 1000-1800 m | Equivalent longer validation pool, count and seed NR [pp. 15-16, Secs. 6.2-6.3]. |
| New standard test | 200 routes | Seed 53012, lengths 200-1000 m | Equivalent independent standard test routes and seed NR. The handover plot says 200 episodes, which does not specify route separation [p. 18, Fig. 6]. |
| New longer test | 200 routes | Seed 53013, lengths 1000-1800 m | Equivalent longer test pool and seed NR [p. 16, Sec. 6.3; pp. 18, 20, Figs. 6, 8]. |
| Policy seeds | Five per arm | 2101, 2102, 2103, 2104, 2105 | Repeated training seed count and identifiers NR [pp. 15-16, Secs. 6.2-6.3]. |
| Per policy budget | 524,288 interactions | Identical settings and budget | 300 episodes × 2,000 maximum steps = nominal ceiling 600,000; actual interactions and early terminations are not logged in the document [p. 16, Table 4]. |
| New training | 2,621,440 interactions | Five V1.5 policies from scratch | Equivalent five seed original reward retraining study NR; source trains policies under its own system [p. 16, Sec. 6.3]. |
| Reused V2 weights | Ten policies | All full and arrival seeds, fixed by hash before new training/test | This reuse is our experimental design; no corresponding source comparison [p. 16, Sec. 6.3]. |
| Final evaluations | 7,600 episodes | 6,000 learned + 1,600 deterministic | Total final evaluation count and comparable route/seed accounting NR; handover axes refer to 200 episodes [pp. 18, 20, Figs. 6, 8]. |
| Exact replay | 7,600 episodes | Every new record compared exactly | Exact replay count and record hashes NR [pp. 16-20, Secs. 6.3-7.2]. |

New test pairs are disjoint from prior saved routes. V2's earlier outcomes
were known; the new protocol was fixed before new training and fresh tests.
This is not an independent external preregistration. No new tuning or
checkpoint selection used the fresh tests. All pools share one map, and
longer distances occur in training: no geographic holdout or extrapolation.
Equal seeds pair initialization and scheduling, not realized transitions or
episode exposure. Equivalent original independent splits are not documented
[TFM, pp. 15-16, Secs. 6.2-6.3].

## References, Metrics and Uncertainty

Goal RSS and Goal radio share braking motion with different network selection.
Joint one step evaluates nine `(speed_scale, angle)` primitives: `(1,0)`,
`(0.6,0)`, `(0,0)`, and `(1,±0.3)`, `(1,±0.6)`, `(1,±1.2)`. Three step
search follows each initial choice with two reference steps. All use the known
map and shared filter. No global reachability guarantee is claimed.

Joint success is primary. The prespecified primary contrast is **full minus
original standard success**, with 5,000 crossed seed/route bootstrap draws,
seed 63000 and a 95% interval. Longer and other comparisons are secondary;
their intervals are descriptive and unadjusted for multiple comparisons.
Five learned seeds on shared routes are not 1,000 independent training runs.

Time, energy, path, delay, interference, SINR, handovers, radio cost and filter
interventions use matched successful pairs for contrasts. Their intersection
count and unconditional failures are reported alongside them. No SINR
percentage change is used. Software replay does not validate physical modeling.

## Reproduce and Audit

```powershell
python -m pytest -q
python scripts/analyze_reward_comparison.py
python scripts/evaluate_reward_controller.py --checkpoint results/reward_comparison/confirmatory_v15/original_seed_2101/checkpoint.pt --split test --output outputs/original_check
```

To retrain the original reward arm and repeat the comparison, use a fresh label:

```powershell
python scripts/run_reward_comparison.py --phase train --label local_reproduction_01
python scripts/run_reward_comparison.py --phase evaluate --label local_reproduction_01
python scripts/run_reward_comparison.py --phase replay --label local_reproduction_01
python scripts/analyze_reward_comparison.py --label local_reproduction_01
```

Do not rerun the freeze, change its hashes or overwrite delivered outputs.
The new label reuses the hash fixed V2 weights and retrains only V1.5.
Choose a different label if a previous run is incomplete. Full independent
V2 retraining is documented in [note 30](docs/30_connectivity_results_and_reproduction.md).

- [Results and every seed](docs/37_v15_reward_results.md)
- [Frozen reward protocol](docs/36_v15_reward_comparison_protocol.md)
- [Dataset and model setup](docs/35_dataset_and_model_setup.md)
- [Paper and release audit](docs/38_v2_paper_and_model_release.md)
- [Paper build instructions](paper/README.md)
- [Documentation index](docs/README.md)

## Scope and Next Research Decision

This is a controlled reimplementation using the same dataset as the thesis.
Sentinel interpretation, original simulator behavior, dynamic traffic, uplink calibration, packet delay,
switching interruption, obstacle safety, energy calibration and continuity
between samples remain unverified. No application deadline or PPO superiority
claim is inferred. Further work needs independent evaluation and separately
frozen component ablations, not tuning on these reported tests.

## Historical Note

Historical V1 was an arrival reward diagnostic with permissive communication
rules. It is absent from the final paper and is not V1.5. Its records and
[archived inventory](docs/39_historical_implementation_inventory.md) remain for
provenance; its weights are not needed for the current study.

## Repository Layout

| Path | Contents | Original thesis counterpart |
| --- | --- | --- |
| `dataset/` | Required private HDF5, excluded from Git | Same Barcelona ray tracing dataset described on pp. 6-7, Sec. 3.1; this relative path and checksum manifest are our packaging. |
| `models/checkpoint_manifest.json` | The initial 15 published paths, sizes and SHA256 values | No original checkpoint bundle is available to us; these are our 15 policies, not original thesis weights [source PPO: p. 13, Sec. 5.3]. |
| `models/service_reward_manifest.json` | Five additional V2.1 final weights, sizes and hashes | Our followup models; no original thesis weights are available [source PPO: p. 13, Sec. 5.3]. |
| `src/uav_joint_optimization/` | Frozen V2 system, original reward adapter and PPO | Our implementation of a related problem; original executable unavailable [source environment/PPO: pp. 12-13, Secs. 5.2-5.3]. |
| `configs/` | Frozen settings, source hashes and route pools | Source parameters are in Tables 3-4, pp. 15-16; machine readable freezes and route pools are provided here. |
| `results/connectivity_experiment/confirmatory_v2/` | Ten reused final V2 models and prior V2 records | Our prior V2 artifacts, not original thesis evaluations or weights [source experiment design: p. 16, Sec. 6.3]. |
| `results/reward_comparison/` | V1.5 models, fresh evaluations, analysis, figures and replay | Our reward replacement comparison; source instead compares PPO/greedy and priority weights [p. 16, Sec. 6.3]. |
| `docs/` | Protocol, results, setup and source traceability | Our methods, provenance and limitations notes; source definitions and results remain in the original PDF, pp. 5-21. |
| `paper/` | Current IEEE draft, source, generated tables and build instructions | Our IEEE study; the original MSc thesis is a separate source, not this paper. |
| `sources/` | Original TFM and research references | Contains the original thesis PDF, including Tables 3-4 and Figs. 5-8 on printed pp. 15-20. |
| `outputs/` | Custom evaluations and scratch checks, excluded from Git | Local outputs generated by our tools; no original raw episode or plotting files are available to this study. |
