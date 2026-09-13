# Joint Handover and Trajectory Optimization with Strict Connectivity

Updated 13 September 2026. Non THz n3cat research project.

**Current study: V2, with V1.5 as the original reward control on the same system.**
The [current IEEE paper](paper/UAV_joint_reward_connectivity_IEEE.pdf) is by
Guillem Moreno Garcia and Evgenii Vinogradov. Start with the
[results and every seed](docs/37_v15_reward_results.md),
[frozen protocol](docs/36_v15_reward_comparison_protocol.md), or
[dataset and model setup guide](docs/35_dataset_and_model_setup.md).

## Current Conclusion

**Replacing the original reward has not demonstrated better mission completion
under our shared V2 system.** Original reward V1.5 and full reward V2 both
achieve 95.7% standard joint success. V2 does change communication behavior:
it substantially reduces handovers and shortens flights, while increasing
delay and estimated energy consumption on matched successful flights.

The original thesis simulator and trained policies are unavailable. We built
a new implementation around the received Barcelona radio map, changing much
more than the reward relative to the thesis. **V1.5 is the original written
reward inside our V2 system; it is not the original thesis agent.** Our
experiment therefore does not establish what caused the original wandering
or demonstrate a successful repair of that original implementation.

Read the [main differences](#main-differences-from-the-thesis),
[general results](#general-results) and
[conclusions](#conclusions-and-revised-diagnosis) first. The detailed inventory
below retains every observation, action, physical assumption, reward term,
PPO setting, split and reproduction command.

## Main Differences from the Thesis

Except for the reward, the changes below apply to both V1.5 and V2 full.
The shared changes' individual benefits have **not** been isolated experimentally. A modeling replacement
is not automatically a correction of an original implementation bug.
TFM references use printed pages; PDF viewer page = printed page + 2.
See the [original TFM](sources/UAV_Bermudez_Granados_2026_MSc_thesis.pdf).

| Area | Original written thesis | What our current study does differently |
| --- | --- | --- |
| Executable and channel data | Custom environment with Stable Baselines PPO; MATLAB ray tracing produces the radio map [pp. 6-7, Sec. 3.1; p. 13, Sec. 5.3]. | New Python environment and PPO implementation consuming the received HDF5. We retain Operator 1's 87 station maps and coordinates, but have not reproduced the original simulator or verified exact dataset version identity. |
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

| Component | V1.5 original reward | V2 full reward |
| --- | --- | --- |
| Map, motion, traffic, energy and service model | Shared V2 system | Identical |
| Observation, action mask, navigation aid and prospective filter | Shared V2 system | Identical |
| Success, failure and arrival termination | Shared V2 rules | Identical |
| PPO settings, training routes, seeds and interaction budget | Shared V2 settings | Identical |
| Reward | Reconstructed original equal weight formula on V2 inputs | Replacement reward package |
| Final checkpoint | Every declared seed, at the fixed budget | Every declared seed, at the fixed budget |

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

All current results use **fresh test seeds 53012 and 53013**, separate from
the earlier V2 evaluation. Standard routes span 200-1000 m; longer routes
span 1000-1800 m. Both ranges occur in training. There are 200 shared routes
per split, five learned training seeds per arm, and **7,600 final episodes**
across all controllers. Five seeds on shared routes are not 1,000 independent
training replications.

### Mission Completion

| Controller | Standard joint success | Longer joint success | Episodes per split |
| --- | ---: | ---: | ---: |
| PPO original reward (V1.5) | 95.7% | 85.8% | 1,000 |
| PPO full reward (V2) | 95.7% | 87.3% | 1,000 |
| PPO arrival reward (V2) | 94.9% | 85.1% | 1,000 |
| Goal RSS | 94.0% | 84.5% | 200 |
| Goal radio | 96.5% | 88.5% | 200 |
| Joint one step | 96.0% | 90.5% | 200 |
| Joint three steps | 92.0% | 90.5% | 200 |

The primary comparison is full V2 minus original V1.5 on standard routes.
Intervals use 5,000 crossed seed/route bootstrap draws, seed 63000.

| Contrast | Observed success difference | 95% interval |
| --- | ---: | --- |
| Standard, primary | 0.0 percentage points | [-2.8, 2.7] |
| Longer, secondary | +1.5 percentage points | [-2.9, 6.1] |

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

| Metric | Standard V1.5 | Standard V2 | Longer V1.5 | Longer V2 |
| --- | ---: | ---: | ---: | ---: |
| Flight time (s) | 31.252 | 28.112 | 65.394 | 60.145 |
| Handovers | 6.843 | 0.443 | 15.826 | 1.528 |
| Delay proxy (s) | 1.942 | 5.827 | 2.857 | 6.818 |
| Energy proxy (kJ) | 7.651 | 7.788 | 18.523 | 18.957 |
| SINR (dB) | -8.322 | -9.305 | -8.773 | -9.957 |
| Interference (µW) | 0.753 | 0.748 | 0.794 | 0.791 |
| Accumulated radio cost | 7.094 | 5.309 | 16.800 | 13.803 |

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

| First failure | Standard V1.5 | Standard V2 | Longer V1.5 | Longer V2 |
| --- | ---: | ---: | ---: | ---: |
| Serving RSS below minimum | 40 | 34 | 136 | 112 |
| Buffer overflow | 3 | 9 | 6 | 15 |
| Total failed missions | 43 | 43 | 142 | 127 |

Neither of these two arms has an energy, boundary or timeout failure in these
tests. Full has fewer observed RSS failures but more buffer failures. These
counts do not establish a general reliability advantage; the completion
intervals above remain the relevant comparison.

## Conclusions and Revised Diagnosis

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

A clone includes source, configuration, results and **all 15 final checkpoints**:
five original reward V1.5, five full V2 and five arrival V2. Total size is about
2.05 MB. The private map must be supplied separately by its owner.

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
lists every path, size and SHA256. Checkpoints contain policy tensors and
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

## Exact Mission Definition and Source Pages

| Component | Current behavior | Original TFM locator or difference |
| --- | --- | --- |
| Joint objective | Complete the mission under sampled RSS and queue constraints; report all three radio costs | p. 10, Eq. (11); p. 11, Eq. (12) |
| Goal position | Within 10 m | Retains p. 15, Table 3 |
| Goal speed | At most 2 m/s | New numerical tolerance; stopping intent, p. 9, Sec. 3.2 |
| Deadline | 200 s, 200 decisions | Shared surrogate; source 2,000 steps and 0.1 s table step, pp. 15-16 |
| RSS feasibility | At least -96 dBm at every modeled sample, including initial RSS | C2, p. 11; value p. 15 |
| Queue feasibility | No overflow beyond 1,280,000 bits | C4, p. 11; decimal interpretation of 160 KB, p. 15 |
| Termination | Arrival, first violation or timeout, in training and evaluation | V2 enforcement; source continues after arrival, p. 12, Sec. 5.2 |
| Event priority | Constraint violations override simultaneous arrival; boundary, energy, RSS, buffer, success, timeout reason priority | New explicit ordering; original code unknown |
| Outstanding queue | Allowed at arrival and reported | No added empty queue condition inferred from pp. 9-12 |
| Packet deadline / minimum rate | Not imposed | No new application contract added |
| Failure reporting | First RSS, buffer, boundary, energy or timeout failure | Added joint evaluation semantics |
| Sampling | One second checks only | No physical continuity guarantee between samples |

All TFM citations use **printed pages**. PDF viewer page = printed page + 2.
The [original PDF](sources/UAV_Bermudez_Granados_2026_MSc_thesis.pdf) is retained.
Missing original details mean unknown, not proven absent.

## Exact Data and Physical Model Differences

| Component | V2 implementation | Original definition or limitation |
| --- | --- | --- |
| Executable | New Python implementation; original simulator and policies unavailable | Stable Baselines/custom environment described on p. 13, Sec. 5.3 |
| Propagation | Consume native received RSS; do not rerun ray tracing | MATLAB, 3D scene and station collection, pp. 6-7, Sec. 3.1 |
| RF metadata | 2.1 GHz, 100 m altitude; 87 of 133 sites | Matching pp. 6-7, Table 2; exact source version unverified |
| Region | 5000 by 3500 m, fixed altitude; no collision model | Scene used for propagation, p. 6; original collision logic unspecified |
| Grid | Nearest lookup; actual spacings 1.00020004 and 1.00028580 m | Nominal one meter resolution, p. 7; indexing unspecified |
| Quantization | Preserve int8; promote before arithmetic; provisional -128 sentinel means zero watts | Generator convention unconfirmed |
| Power | Use stored RSS directly, without adding 46 dBm again | Downlink budget/strongest sector, p. 7, Eq. (1) |
| Motion | Inertial vector velocity and trapezoidal position update | Source scalar speed and chosen direction, p. 9, Eq. (2) |
| Bounds | Acceleration norm 5 m/s², hard speed cap 25 m/s | Source discretizes acceleration/heading and lists 100 m/s threshold, p. 15 |
| Step | 1 s | Source table 0.1 s, p. 15; prose 1 ms, p. 14 |
| Interference | Sum linear cochannel downlink power, excluding serving station | Source calls it uplink, p. 10, Eq. (9); not calibrated source reproduction |
| Noise | -112.41 dBm plus 9 dB = -103.41 dBm, converted to watts | Retains table values, p. 15 |
| Rate | 1.44e6 × log2(1 + linear SINR) bit/s | Replaces printed rate/SNR expressions, p. 10, Eqs. (7)-(8) |
| Bandwidth | Eight 180 kHz blocks per group; 12 groups | Retains p. 15, Table 3 |
| Traffic | Constant 200,000 bit/s | Replaces packet/Poisson model, pp. 9-10, Eqs. (5)-(6); not an asserted unit conversion |
| Queue order | Add traffic/overhead, subtract service, count overflow, clip | Source p. 9, Eq. (5); exact source event order unknown |
| Delay | Postservice backlog / max(rate,1), censored at 200 s | Queue/rate concept, p. 9, Eq. (4); not actual packet delay |
| Handover overhead | 4,800 bits per executed handover | Four 1,200 bit packets, pp. 14-15 |
| Occupancy | Static deterministic half occupied pattern with saved phase | Source describes random occupancy, pp. 14-15 |
| Interruption | No switching delay or separate same station resource change cost | No calibrated duration supplied by source |
| Energy | (100 + 0.4 × speed²) × dt J; 100 kJ budget | New uncalibrated proxy, not a conversion of p. 10, Eq. (10), or p. 15 capacity |

## Exact Actions, Navigation Prior and Filter

The actor has two Gaussian radial/lateral motion variables and 61 categorical
network logits. Tanh motion residuals, scaled by 0.5, augment a projected goal
braking command. Physical projection follows. Desired speed is
`min(25, 0.7 × sqrt(2 × 5 × max(distance - 4, 0)))`. This shared prior supplies
navigation competence. Source discrete acceleration/heading actions differ
[TFM, p. 12, Sec. 5.2; p. 15, Table 3].

| Detail | Exact behavior |
| --- | --- |
| Candidates | Serving station plus four strongest signals, stable RSS ordering |
| Duplicate serving slots | Masked except the designated serving slot |
| Options | Stay plus five slots × 12 groups = 61 |
| A3 | Target RSS strictly greater than serving RSS + 3 dB and at least -96 dBm [TFM, p. 9, Eq. (3); p. 15] |
| Resources | Only free target groups; explicit stay always available |
| Decision interval | Every modeled second |
| Same station group changes | Permitted; resource changes are distinct from handovers |
| Initialization | Strongest RSS and first free deterministic group |
| Filter | Predict next position/RSS/queue; repair network first, then local joint motion if needed |
| Information | Known map and dynamics at prospective positions, shared by all arms |
| Unresolved violation | Still terminates failure; mask cannot be bypassed |
| Diagnostics | Network and motion interventions counted separately |
| PPO likelihoods | Proposed actions; projection and filtering are environment transformations |

The source lists BS and RBG requests [TFM, p. 12, Sec. 5.2]. Candidate
restriction, masks, residual motion and the filter are our implementation.

## Every Observation Feature

All three learned arms have the same 156 inputs; indices are zero based.

| Indices | Definition |
| --- | --- |
| 0-1 | Position / map dimensions |
| 2-3 | Unit goal direction |
| 4 | Goal distance / 1,000 m |
| 5-6 | Radial and lateral velocity / 25 m/s |
| 7 | Speed / 25 m/s |
| 8 | Elapsed decision count / 200 |
| 9 | Queue / 1,280,000 bits |
| 10 | Consumed energy / 100,000 J |
| 11-12 | Background phase / 11 and serving RBG / 11 |
| 13 | Serving SINR in dB / 30 |
| 14-18 | Five candidate RSS values, (RSS + 70) / 60 |
| 19-28 | Candidate x/y offsets / 5,000 m |
| 29-33 | Candidate station indices / 86 |
| 34-94 | log(1 + option capacity / 200000), for 61 choices |
| 95-155 | Network mask |

The source lists six state components [TFM, p. 12, Sec. 5.2]; this layout is
an explicit replacement, not a reconstruction of undocumented original tensors.

## Exact Reward Difference

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
Sec. 5.3 and pp. 15-16, Sec. 6.2/Table 4. Current controlled settings are:

| Setting | Value |
| --- | --- |
| Parallel environments / rollout | 64 / 128 |
| Minibatch / epochs | 512 / 4 |
| Actor and critic | Separate networks, two 64 unit tanh layers each |
| Learning rate / Adam epsilon | 0.0003 / 1e-5 |
| Discount / GAE | 0.99 / 0.95 |
| PPO clip / entropy weight | 0.2 / 0.005 |
| Value weight / gradient norm | 0.5 / 0.5 |
| Interactions per policy / CPU threads | 524,288 / 2 |
| Hidden initialization | Orthogonal gain sqrt(2), zero biases |
| Action / value head gain | 0.01 / 1 |
| Initial motion log standard deviation | -0.5 |
| Log standard deviation clamp | [-2.3, 0.5] |
| Invalid logits | -1e9 |
| Reward normalization | Running variance of discounted returns; not mean centered |
| Reward clipping | [-10, 10] after normalization |
| Advantage normalization | Per minibatch, epsilon 1e-8 |
| Value loss | 0.5 × squared error, then configured value weight 0.5 |
| Terminal GAE | No bootstrap or carry across any terminal, including timeout |
| Evaluation | Gaussian mean and categorical argmax |
| Checkpoint contents | Policy tensors, dimensions, config metadata and final step count |
| Model selection | Final budget checkpoint for every declared seed |

## Splits, Budgets and Independence

| Pool or budget | Size | Definition |
| --- | ---: | --- |
| Training | 4,096 routes | Exact V2 seed 52010, lengths 200-1800 m |
| Validation | 64 routes | Exact V2 seed 52001, lengths 200-1000 m |
| Longer validation | 32 routes | Exact V2 seed 52002, lengths 1000-1800 m |
| New standard test | 200 routes | Seed 53012, lengths 200-1000 m |
| New longer test | 200 routes | Seed 53013, lengths 1000-1800 m |
| Policy seeds | Five per arm | 2101, 2102, 2103, 2104, 2105 |
| Per policy budget | 524,288 interactions | Identical settings and budget |
| New training | 2,621,440 interactions | Five V1.5 policies from scratch |
| Reused V2 weights | Ten policies | All full and arrival seeds, fixed by hash before new training/test |
| Final evaluations | 7,600 episodes | 6,000 learned + 1,600 deterministic |
| Exact replay | 7,600 episodes | Every new record compared exactly |

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

This is a controlled reimplementation. Exact source dataset version, sentinel,
original simulator behavior, dynamic traffic, uplink calibration, packet delay,
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

| Path | Contents |
| --- | --- |
| `dataset/` | Required private HDF5, excluded from Git |
| `models/checkpoint_manifest.json` | All 15 published paths, sizes and SHA256 values |
| `src/uav_joint_optimization/` | Frozen V2 system, original reward adapter and PPO |
| `configs/` | Frozen settings, source hashes and route pools |
| `results/connectivity_experiment/confirmatory_v2/` | Ten reused final V2 models and prior V2 records |
| `results/reward_comparison/` | V1.5 models, fresh evaluations, analysis, figures and replay |
| `docs/` | Protocol, results, setup and source traceability |
| `paper/` | Current IEEE draft, source, generated tables and build instructions |
| `sources/` | Original TFM and research references |
| `outputs/` | Custom evaluations and scratch checks, excluded from Git |
