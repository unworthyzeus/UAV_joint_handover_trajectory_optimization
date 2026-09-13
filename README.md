# Joint Handover and Trajectory Optimization with Strict Connectivity

Updated 13 September 2026. Non THz n3cat research project.

**Current study: V2, with V1.5 as the original reward control on the same system.**
The [current IEEE paper](paper/UAV_joint_reward_connectivity_IEEE.pdf) is by
Guillem Moreno Garcia and Evgenii Vinogradov. Start with the
[results and every seed](docs/37_v15_reward_results.md),
[frozen protocol](docs/36_v15_reward_comparison_protocol.md), or
[dataset and model setup guide](docs/35_dataset_and_model_setup.md).

## What the New Comparison Establishes

V1.5 uses the original written reward; V2 full uses the replacement. Both share
strict sampled connectivity, arrival termination, dynamics, observations,
actions, navigation prior, safety filter, PPO settings, training routes, seeds
and interaction budget. The intervention changes the reward package only.

**The new comparison does not establish improved mission completion.**
Both rewards achieve 95.7% standard joint success. Full minus original is
0.0 percentage points, 95% interval [-2.8, 2.7]. On longer routes full achieves
87.3% versus 85.8%, a difference of +1.5 points [-2.9, 6.1]. An interval
containing zero is not proof of equivalence.

On 925 common successful standard seed/route pairs, full reduces accumulated
radio cost by 25.2%, handovers from 6.84 to 0.44, and flight time by 3.14 s.
Delay rises from 1.94 to 5.83 s, proxy energy rises 1.8%, and mean SINR falls
0.98 dB. Longer results show the same broad tradeoff. A lower weighted cost
is not a uniformly better connection.

Every current result below uses **fresh test seeds 53012 and 53013**, separate
from the prior V2 evaluation on seeds 52012 and 52013.

| Controller | Standard joint success | Longer joint success | Episodes per split |
| --- | ---: | ---: | ---: |
| PPO original reward (V1.5) | 95.7% | 85.8% | 1,000 |
| PPO full reward (V2) | 95.7% | 87.3% | 1,000 |
| PPO arrival reward (V2) | 94.9% | 85.1% | 1,000 |
| Goal RSS | 94.0% | 84.5% | 200 |
| Goal radio | 96.5% | 88.5% | 200 |
| Joint one step | 96.0% | 90.5% | 200 |
| Joint three steps | 92.0% | 90.5% | 200 |

All successful missions meet sampled RSS and buffer constraints. Failures stay
in the denominators and are broken down in the result note. The shared motion
prior and filter can help both rewards; their separate effects are not isolated.
No overall PPO superiority claim is supported.

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
| Event priority | Failure overrides simultaneous arrival; boundary, energy, RSS, buffer, success, timeout reason priority | New explicit ordering; original code unknown |
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
