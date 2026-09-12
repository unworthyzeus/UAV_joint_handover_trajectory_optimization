# Joint Handover and Trajectory Optimization in 5G Connected UAVs

Research workspace for the non THz n3cat UAV proposal. Updated 13 September 2026.

**Run the project:** [dataset, checkpoints and quick start](#setup-dataset-and-model-checkpoints), with the [complete setup guide](docs/35_dataset_and_model_setup.md).

**Full thesis comparison:** [all twelve implementation and methodology categories](#complete-inventory-of-differences-from-the-original-thesis), including every PPO setting, both observation layouts, original page citations and the final v2 changes.

## Setup: Dataset and Model Checkpoints

**A Git clone includes code, configurations and recorded results. It does not
currently include the private radio map or trained checkpoint binaries.** Every
simulated flight needs the dataset; PPO evaluation also needs a checkpoint.
Saved results and the paper can be inspected without either binary artifact.

Place the original HDF5 at this exact path relative to the repository root:

```text
UAV_joint_handover_trajectory_optimization/
  README.md
  requirements-experiments.txt
  dataset/
    Barcelona_dataset_January.h5
  results/
    connectivity_experiment/
      confirmatory_v2/
        full_seed_2101/
          checkpoint.pt
```

Use `dataset/Barcelona_dataset_January.h5`, with `dataset` singular. The current
evaluators do not read from `data/raw/`, `data/processed/` or the parent research
folder, and have no `--dataset` argument. Obtain the unchanged file separately
from its owner; there is no public download in the repository. Expected size:
**2,327,593,160 bytes**. Expected SHA256:

```text
d4630dd3a6c45419e12d0b60dd08473c4ffa4062ca4fab1decabecf2b992ea0d
```

Restore the checkpoint separately from the locally retained study, or retrain
with a fresh output label using the full guide. The example uses the first
declared v2 full reward seed, not a model selected for its test result. Other
weight locations are accepted through `--checkpoint`. V1 weights need the v1
evaluator; the versions are not interchangeable.

The recorded setup is Python 3.12 on Windows with CPU PyTorch. From the
repository root in PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-experiments.txt
Test-Path -LiteralPath dataset/Barcelona_dataset_January.h5
```

Run a custom flight with the deterministic radio controller, which needs the
dataset but no weights:

```powershell
.\.venv\Scripts\python.exe scripts/evaluate_connectivity_controller.py --controller straight_radio --start 1000 1000 --goal 1800 1300 --output outputs/quickstart_radio
```

With a restored v2 checkpoint, evaluate the 200 standard test routes:

```powershell
.\.venv\Scripts\python.exe scripts/evaluate_connectivity_controller.py --checkpoint results/connectivity_experiment/confirmatory_v2/full_seed_2101/checkpoint.pt --split test --output outputs/quickstart_full_test
```

Coordinates are local map meters, not latitude/longitude. `--output` is a file
prefix: the first example writes `outputs/quickstart_radio.json` and
`outputs/quickstart_radio.csv`, and prints a summary. Reusing a prefix overwrites
its output files. The [complete guide](docs/35_dataset_and_model_setup.md)
includes cloning, the local absolute dataset path, checksum verification,
both model versions, all splits, custom PPO routes, retraining and troubleshooting.

## Consolidated IEEE Paper

Read [the single paper covering both studies](paper/UAV_joint_reward_connectivity_IEEE.pdf),
authored by Guillem Moreno Garcia and Evgenii Vinogradov. Its 15 pages include
the reward experiment, connectivity audit and correction, all principal results,
trajectory figures, splits, failed development designs, and detailed thesis
comparisons with 104 printed page citations. The
[paper guide](paper/README.md) explains the build; [note 33](docs/33_unified_paper_and_github_release.md)
records the consolidation and GitHub release scope. Earlier PDFs remain historical records.

## Latest Result: Connectivity Constraints

The v2 study corrects the connectivity omission. A successful mission now has
to satisfy the thesis's RSS and buffer constraints at every simulated sample,
as well as arrive and stop. The full reward restores delay, interference and
handover costs, with available resource choices and a shared safety filter.
No new packet deadline or empty queue arrival requirement was added.

| Controller | Standard joint success | Longer joint success |
| --- | ---: | ---: |
| PPO with arrival cost and strict constraints | 96.9% | 86.3% |
| PPO with full radio cost and strict constraints | 96.6% | 89.7% |
| Goal directed controller with radio selection | 98.0% | 92.5% |

Full PPO reduces weighted radio cost on paired successful routes by 24.5% and
14.7%, but increases delay and does not establish a completion advantage.
The radio selection reference improves longer completion over strongest RSS
selection by 5.5 points, 95% interval [1.5, 9.5]. All four deterministic
references and every learned seed are retained in the complete results.

Read [the results and commands](docs/30_connectivity_results_and_reproduction.md),
[every connectivity change with thesis pages](docs/31_exact_connectivity_changes.md),
or [the consolidated IEEE paper](paper/UAV_joint_reward_connectivity_IEEE.pdf).
There are 51 passing tests and 5,600 exact replayed final evaluations. The
dataset and both experiment freezes are unchanged. The one second surrogate
sampling does not establish physical continuity between samples.

## Earlier Arrival Reward Study

Reward replacement restored mission completion in a documented reimplementation
on the received Barcelona radio map. Twenty PPO policies were trained using
four treatments and five seeds, with 524,288 interactions per policy. Each
policy evaluated the same 200 standard and 200 longer test routes.

| Training treatment | Standard mission success | Longer mission success |
| --- | ---: | ---: |
| Legacy reward | 21.4% | 0.0% |
| Termination change only | 0.0% | 0.0% |
| Reward replacement only | 100.0% | 100.0% |
| Reward and termination changes | 99.7% | 36.1% |
| Deterministic reference | 100.0% | 100.0% |

Standard routes span 200–1000 m; longer routes span 1000–1800 m. Safe arrival
requires distance at most 10 m and speed at most 2 m/s within 200 s. Every
evaluation stops at safe arrival, including policies trained with continuing
episodes. The primary combined versus legacy gain is 78.3 percentage points,
with a paired crossed bootstrap 95% interval of [66.2, 89.5]. The prespecified
positive result gate passed.

Reward replacement is the essential tested intervention. Adding termination
was less reliable on longer routes. The deterministic reference completed all
routes and was faster; these results do not establish a learning advantage
over classical control.

## Scope

This is a validated reimplementation of the written reward structure, not a
reproduction of Marina Bermúdez Granados's original simulator or policy. All
treatments share repaired observations, continuous flight actions, masked
handover choices, and explicit radio and energy proxies. The experiment does
not isolate observation repair or prove the exact cause of the original
policy's behavior. Original code, checkpoints, collision scene, and exact
dataset version confirmation remain unavailable.

The received 2.33 GB map is preserved at
`dataset/Barcelona_dataset_January.h5` and excluded from Git. It has not been
published. Study I's historical recorded feasible success checks buffer overflow and outage:
reward replacement alone achieved 98.7% standard and 96.0% longer feasible
success. Mission success alone is not a complete safety claim.

The [connectivity audit](docs/27_connectivity_objective_audit.md) showed why
Study I did not establish the full joint objective. In 1,000 standard
reward replacement flights, arrival is 100%, but only 92.2% have no sampled RSS
outage; capacity falls below offered traffic for a mean 26.6% of flight time,
and 20.2% arrive with data still queued. Short capacity deficits can be buffered
and are not themselves disconnections. Study II repairs the sampled RSS and
buffer endpoint; it still does not establish service between samples or a
packet latency guarantee. The audit exactly replayed 4,400 frozen episodes
without changing training or original results.

## Complete Inventory of Differences from the Original Thesis

Updated 13 September 2026. This is the complete documented inventory of the
implemented choices across both studies, including retained settings and details
the original text leaves unspecified. It expands the conversation's comparison
directly in the repository README. The underlying reviewed records are
[the original TFM versus v1 comparison](docs/25_exact_changes_from_tfm.md) and
[the complete v1 versus v2 comparison](docs/31_exact_connectivity_changes.md).

**We built a reimplementation and changed substantially more than the reward.**
The original executable simulator and trained checkpoints remain unavailable.
The comparison is therefore with the written TFM, not a verified diff against
its source code. Our `legacy` arm retains the written reward structure inside
our shared environment; it is not the original trained policy.

- **v1 / Study I:** the four arm reward and arrival termination experiment.
- **v2 / Study II:** the final two arm strict sampled connectivity experiment,
  with resource actions, residual motion and a prospective safety filter.
- **Reading the tables:** v1 tables describe the initial executed foundation.
  V2 retains that foundation except for the explicitly listed v2 changes.
  The 42 dimensional observation, permissive outage rule and direct motion
  policy belong to v1, not the final v2 controller.
- **Evidence labels:** a documented replacement is a change from the written
  formulation. An unspecified original setting is an evidence gap; our explicit
  choice does not prove that the original implementation lacked that feature.
- **Causal scope:** v1 varies reward replacement and training termination; v2
  varies inclusion of the complete radio cost. Shared observation, dynamics,
  radio, optimizer, filter and training distribution choices are not individually
  ablated. Differences between v1 and v2 do not isolate reward effects.

All TFM locators below refer to **printed pages** of
[Marina Bermúdez Granados's original thesis](sources/UAV_Bermudez_Granados_2026_MSc_thesis.pdf).
For those pages, **PDF viewer page = printed page + 2**. Equation and table
numbers belong to the original TFM. For example, Eq. (14) on printed p. 12 is
on viewer page 14. [Note 25](docs/25_exact_changes_from_tfm.md#original-thesis-definition-index)
contains the complete verified definition index.

Navigate the inventory:

1. [Implementation, data and geometry](#1-implementation-data-and-geometry)
2. [Motion, arrival and connectivity endpoints](#2-motion-arrival-and-connectivity-endpoints)
3. [Observations and every feature index](#3-observations-and-every-feature-index)
4. [Handover, resources and action timing](#4-handover-resources-and-action-timing)
5. [Radio, traffic, queues and energy](#5-radio-traffic-queues-and-energy)
6. [Reward functions and terminal handling](#6-reward-functions-and-terminal-handling)
7. [Residual motion and the safety filter](#7-residual-motion-and-the-safety-filter)
8. [PPO and all numerical settings](#8-ppo-and-all-numerical-settings)
9. [Deterministic reference controllers](#9-deterministic-reference-controllers)
10. [Training, validation, tests and budgets](#10-training-validation-tests-and-budgets)
11. [Metrics, statistics and verification](#11-metrics-statistics-and-verification)
12. [Event ordering, retained values and limits](#12-event-ordering-retained-values-and-limits)

### 1. Implementation, Data and Geometry

The following choices apply to both studies. Matching map metadata does not
establish that the received file is the exact version used for the thesis runs.

| Item | Original TFM and locator | Executed experiment and status |
| --- | --- | --- |
| Source code | Stable Baselines and custom environment described, TFM, p. 13, Sec. 5.3 | New Python implementation; original code and checkpoints unavailable. |
| Channel generation | MATLAB deterministic ray tracing on a 3D GloBFP/STL scene with Minetur station locations, TFM, pp. 6–7, Sec. 3.1 | We consume the received HDF5; we did not rerun MATLAB, rebuild the scene, or recollect stations. |
| Propagation settings | Two reflections, diffraction disabled, three sectors, 120° azimuth/30° elevation, −12° downtilt, 3 m rooftop masts, TFM, pp. 6–7, Sec. 3.1 and Table 2 | Inherited only through the received RSS values; not independently regenerated or varied. |
| Frequency and altitude | 2.1 GHz and 100 m, TFM, p. 7, Table 2 | Retained in received map metadata; no frequency or altitude control. |
| Transmit power and sectors | 46 dBm; strongest sector per station retained, TFM, p. 7, Table 2 and Eq. (1) discussion | Stored RSS used directly; 46 dBm is not added again; sectors are not independent actions. |
| Area and stations | 5000 × 3500 m; 133 sites; operators with 87/59/41 sites, TFM, pp. 6–7; Operator 1 used, p. 14, Sec. 6.1 | Same headline area and counts; select the first operator's 87 stations. Matching metadata does not prove exact thesis version identity. |
| Grid indexing | Nominal 1 m resolution, TFM, p. 7, Table 2; indexing convention not specified | Native array resolution, axes `(station, x, y)`; nearest coordinate index using spacings 1.00020004 and 1.00028580 m; coordinate lookup clipped to array bounds. |
| Quantization and missing paths | RSS in dBm, TFM, p. 7, Eq. (1); integer encoding and sentinel not specified | Preserve int8 storage; promote values to float for arithmetic; provisionally treat −128 as zero received watts. Sentinel convention remains unconfirmed. |
| Raw data preservation | Final database described, TFM, p. 7 | Read only HDF5; SHA256 `d4630dd3a6c45419e12d0b60dd08473c4ffa4062ca4fab1decabecf2b992ea0d`; no dataset publication. |
| Buildings and collisions | 3D geometry explicitly used for RF propagation, TFM, p. 6, Sec. 3.1.1; collision handling not specified | No obstacle collision model. Do not describe this as removing a proven original collision constraint. |

Implementation: [RadioMap and scenario generation](src/uav_joint_optimization/experiment_env.py), methods `RadioMap.__init__`, `query`, and `make_scenarios`. The received file's exact schema and full scan are in note 17.

### 2. Motion, Arrival and Connectivity Endpoints

**Initial v1 foundation.** These are the original reconstruction choices,
including the permissive connectivity rules subsequently replaced in v2.

| Item | Original TFM and locator | Executed experiment and status |
| --- | --- | --- |
| Position and velocity | Scalar speed with selected angle in a uniformly accelerated position update, TFM, p. 9, Eq. (2) | Inertial 2D velocity persists across steps; velocity update then trapezoidal position integration. This changes turning dynamics. |
| Motion actions | Five acceleration bins from −5 to 5 m/s² and eight headings, TFM, p. 12, Sec. 5.2; p. 15, Table 3 | Two continuous radial/lateral acceleration components relative to the goal bearing; no discrete heading branch or turn rate model. |
| Acceleration bound | Scalar range −5 to 5 m/s², TFM, p. 15, Table 3 | Preserve numerical maximum 5, now as a vector norm bound. Tanh policy actions are clipped and projected into the unit disk. |
| Speed | Penalty at 100 m/s, TFM, p. 12, Eq. (14); p. 15, Table 3 | Hard velocity norm projection to 25 m/s; legacy arm has no additional speed penalty. |
| Time step | Prose says 1 ms, TFM, p. 14, Sec. 6.1; table says 0.1 s, p. 15, Table 3 | Explicitly 1 s. This is a new discretization, not a verified recovery of the original duration. |
| Mission deadline | 2000 timesteps listed, TFM, p. 16, Table 4; physical duration depends on inconsistent step definitions | 200 steps = 200 s. Not claimed to match the original wall clock horizon. |
| Initial motion | Start from rest intended, TFM, p. 9, Sec. 3.2 | Start every episode with zero velocity. |
| Position tolerance | 10 m, TFM, p. 15, Table 3 | Retain distance ≤10 m. |
| Stopping requirement | Halt at goal intended, TFM, p. 9, Sec. 3.2; no numerical speed tolerance specified | Add speed ≤2 m/s to the success predicate. Arrival is checked after motion and radio/energy updates. |
| Arrival termination | Explicitly absent, TFM, p. 12, Sec. 5.2 | Varied only during training. All evaluation ends at first safe arrival. |
| Energy failure | Exhaustion ends episode and overrides reward, TFM, p. 12, Sec. 5.2 | End at consumed energy ≥100 kJ. Legacy reward override remains −10, but the energy model and budget differ. |
| Boundary | Formal bound and penalty, TFM, p. 11, C1; p. 12, Eq. (14) | A proposed step outside the map ends a failure; position is clipped for storage/lookup. Boundary termination is additional, not recovered from the text. |
| Connectivity | Formal RSS bound and per step penalty, TFM, p. 11, C2; p. 12, Eq. (14) | RSS ≤−96 dBm marks outage; five consecutive samples end failure. We allow brief outages instead of enforcing C2 at every step. |
| Simultaneous events | Exact event order not specified, TFM, p. 12, Sec. 5.2 | Physical failure takes precedence over new arrival. Valid arrival on the deadline is successful. No success test at the initial reset. |
| Packet overflow | Queue capacity in C4; dedicated reward penalty removed, TFM, p. 11; pp. 20–21, Sec. 7.3 | Clip queue, record dropped bits, continue episode. Overflow disqualifies recorded feasible success, but not mission success. |
| Recorded feasibility | No matching success conditioned definition given in TFM, pp. 16–20, Sec. 7 | Mission success AND outage fraction ≤5% AND zero dropped bits; not obstacle/airframe certification. |

Implementation: `UAVBatch.reset`, `geometry`, and `step` in [experiment_env.py](src/uav_joint_optimization/experiment_env.py). All these shared rules apply to all four arms except the specified training arrival termination factor.

**Final v2 endpoint changes.** The written TFM already formulates minimum RSS
and bounded queue occupancy. V2 explicitly enforces those requirements at our
modeled samples; this is not evidence about enforcement in unavailable original
code. The five outage allowance below was our v1 choice.

| Item | v1 executed behavior | Final v2 executed behavior | Original source relationship |
| --- | --- | --- | --- |
| Minimum RSS | RSS ≤ −96 dBm counts as outage. | RSS < −96 dBm counts as violation; equality is allowed. | Follow C2's ≥ inequality [TFM, p. 11, Eq. (12)] and the numeric minimum [p. 15, Table 3]. |
| Initial RSS | Strongest station selected at reset; no separate persistent initial violation flag. | Check the initial serving RSS and preserve any violation until failure. | Include the initial modeled sample in C2 [TFM, p. 11]. |
| Failure rule | Five consecutive sampled outages terminate a flight. | Any single sampled RSS violation terminates a failed joint mission. | Enforce the written C2 at modeled samples [TFM, p. 11], rather than reproduce the source's soft reward penalty [p. 12, Eq. (14)]. |
| Buffer overflow | Count lost bits, clip queue, continue flight; disqualify only the subsequent feasible label. | Any overflow ends failure; clipping cannot erase it. | Enforce C4 at the sampled queue update [TFM, p. 11, Eq. (12)]. Source removal of a direct dump penalty is described on pp. 20–21, Sec. 7.3. |
| Joint success | Arrival is primary; recorded feasibility permits up to 5% RSS outage and zero drops. | Arrival plus no prior sampled RSS violation, no overflow, and no physical failure. No additional permissive feasibility label. | Combine source communication constraints [TFM, p. 11] with explicit destination completion. |
| Event precedence | Some physical failures override arrival; overflow does not. | RSS, overflow, boundary and energy failure override simultaneous arrival. | New explicit ordering; original source ordering is unspecified [TFM, p. 12, Sec. 5.2]. |
| Outstanding queue at arrival | Allowed. | Still allowed and reported. | The source does not specify an empty queue arrival test [TFM, pp. 9–12, Secs. 3.2–5.2]. We do not claim all generated data has been delivered. |

Every v2 training and evaluation episode terminates at joint success or first
failure. Success requires distance at most 10 m, speed at most 2 m/s and arrival
by 200 s, with no sampled RSS violation, overflow, boundary or energy failure.
The initial RSS is included; an arrival exactly at the deadline can succeed if
no failure occurs. The v2 serialized `max_consecutive_outage: 5` field is unused
by its step function and does not allow five outages.

Following the user's selection of the thesis requirements, we added no two
second packet deadline, minimum throughput requirement or final queue draining
condition. A remaining queue is allowed and reported. Constraints are sampled
every second, not certified continuously within the step. A temporary capacity
deficit is not automatically an RSS outage.

### 3. Observations and Every Feature Index

**v1 interface and exact indices:**

The original vector is `[x, y, serving BS, RBG, energy, buffer]` and its action
is `[acceleration, direction, requested BS, requested RBG]` [TFM, p. 12,
Sec. 5.2]. We replace these with a 42 dimensional observation, two continuous
motion actions, and one masked five choice categorical action. No original
normalization or complete network architecture is inferred from library defaults.

The exact zero based observation layout in `UAVBatch.observe` is:

| Indices | Features and scaling |
| --- | --- |
| 0–1 | Position divided by `(5000, 3500)` |
| 2–3 | Unit vector toward goal; `(1, 0)` fallback at effectively zero distance |
| 4 | Goal distance / 1000 m |
| 5–6 | Velocity projected onto radial and lateral directions / 25 m/s |
| 7 | Speed / 25 m/s |
| 8 | Elapsed steps / 200; determines remaining time |
| 9 | Queue bits / 1,280,000 |
| 10 | Consumed energy / 100,000 J, rather than remaining energy |
| 11 | Whether first safe arrival already occurred |
| 12–13 | Resource label phase / 11 and allocated RBG / 11 |
| 14 | `(step mod 5) / 5` |
| 15 | Serving SINR in dB / 30 |
| 16 | Consecutive outage samples / 5 |
| 17–21 | Five candidate RSS values, each transformed as `(RSS + 70) / 60` |
| 22–31 | Candidate station x/y offsets from UAV, both divided by 5000 m |
| 32–36 | Candidate indices within selected operator / 86, not global station IDs or one hot vectors |
| 37–41 | Five Boolean admissibility flags represented as float features |

**Final v2 interface changes:**

| Item | v1 executed behavior | Final v2 executed behavior | Original source relationship |
| --- | --- | --- | --- |
| Observation | 42 features. | 156 features, detailed below. | Original source has six listed state elements [TFM, p. 12, Sec. 5.2]. Both are reimplementations with repaired state. |

| Zero based indices | Definition |
| --- | --- |
| 0–1 | Position / map dimensions |
| 2–3 | Destination direction unit vector |
| 4 | Destination distance / 1,000 m |
| 5–6 | Radial and lateral velocity / 25 m/s |
| 7 | Speed / 25 m/s |
| 8 | Elapsed decision count / 200 |
| 9 | Queue / 1,280,000 bits |
| 10 | Consumed energy / 100,000 J |
| 11–12 | Background phase / 11 and serving RBG / 11 |
| 13 | Serving SINR in dB / 30 |
| 14–18 | Candidate RSS, transformed as `(RSS + 70) / 60` |
| 19–28 | Candidate station x/y offsets / 5,000 m |
| 29–33 | Candidate station index / 86 |
| 34–94 | `log(1 + option_capacity / 200000)` for all 61 network choices |
| 95–155 | Corresponding Boolean action masks as float features |

The earlier ever arrived feature, consecutive outage counter, and five second
decision phase are removed from the learned observation. Arrival and RSS
violation now terminate the modeled mission immediately.

Both versions use explicit fixed feature scales. Neither fits an observation
normalizer. Goal, velocity, time and radio option information are common to all
arms within a study, so their independent contribution is not estimated.

### 4. Handover, Resources and Action Timing

**v1 network and resource implementation:**

| Item | Original TFM and locator | Executed experiment and status |
| --- | --- | --- |
| Candidates | Requests over station identities, TFM, p. 12, Sec. 5.2; 87 stations in p. 15, Table 3 | Stay/serving station plus four highest RSS stations, stable sorting. Serving may also occur in top four; duplicate self requests are masked. |
| Mask | A3 request acceptance specified, TFM, p. 9, Eq. (3); policy action masking not specified | Mask categorical choices before sampling/scoring. Stay always allowed; candidate must differ from serving, exceed serving RSS by 3 dB, and exceed −96 dBm. |
| A3 direction and units | Eq. (3) requires requested RSS > serving RSS + offset; nearby prose reverses the verbal comparison; offset labeled dBm in Table 3, TFM, pp. 9, 15 | Follow Eq. (3), interpret the difference as 3 dB. Do not infer the original code followed the conflicting prose. |
| Network timing | Requests described each time step; greedy viability counters, TFM, pp. 10, 13–14 | Decisions at steps divisible by five or whenever the observed serving RSS is ≤−96 dBm. No cumulative time to trigger counters. |
| Invalid requests | RBG fallback and A3 rejection described, TFM, p. 9, Sec. 3.3.1 | Invalid categorical requests make no handover; valid choices execute before motion, with no simulated handover interruption time. |
| Learned resources | RBG requested by policy; preserve previous group if unsuccessful, or first available after handover, TFM, p. 9 and p. 12 | Remove RBG policy branch entirely. Shared allocator chooses a free group initially and on handover; otherwise group is retained. |
| Resource occupancy | At least 50% randomly occupied, TFM, p. 14; 12 RBGs, p. 15, Table 3 | Exactly six of twelve occupied in a deterministic station pattern. For station index k, phase z, group g is occupied when `(g − (7k+z)) mod 12 < 6`; assign `(7k+z+6) mod 12`. |
| Scenario phase | Independent traffic or seed schedule not specified, TFM, pp. 14–16 | z is an integer 0–11 shared across stations in an episode. It rotates labels globally; it does not create independent random occupancy patterns. |
| Initial association | Reset station rule not specified in TFM, Secs. 3–6 | Highest RSS station at start; corresponding first available group. |
| Other active UAVs | Other UE and single BS/RBG association described, TFM, pp. 5, 9, 11 | Each vector lane is an independent single UAV episode. Lanes do not interact; terrestrial traffic is an occupancy proxy, not individual simulated users. |

**Final v2 network changes and retained rules:**

| Item | v1 executed behavior | Final v2 executed behavior | Original source relationship |
| --- | --- | --- | --- |
| Network decision timing | Every five seconds, with observed outage exception. | Every modeled second. | Source describes choices each environment step [TFM, pp. 9, 12, Secs. 3.3.1, 5.2]; a five second interval was our prior assumption. |
| Network action | Stay plus four strongest candidate stations: five categorical choices. | Stay plus five candidate station slots by 12 groups: 61 choices. | Restores resource choice from the source's BS/RBG action [TFM, p. 12, Sec. 5.2]. |
| Station candidate selection | Serving plus strongest four, stable RSS ordering. | Retained. Duplicate serving station slots are masked. | Restricted candidate interface is ours; source lists full BS/RBG choices [TFM, p. 12]. |
| A3 condition | Candidate RSS > serving RSS + 3 dB. | Retained; prospective filter cannot bypass it. | Follow the inequality, not the reversed nearby prose [TFM, p. 9, Eq. (3); p. 15, Table 3]. |
| Resource allocation | Deterministic first free RBG at reset and handover. | That initialization remains; the controller can choose any currently free RBG, including within the same station. | Source allows RBG requests with fallback [TFM, p. 9, Sec. 3.3.1]. The exact masking implementation is ours. |
| Repeating a resource choice | No learned resource choice. | Current serving station/group pair remains a valid pair action; explicit stay also remains. | Avoid a new artificial alternating action mask; this is an implementation decision. |
| Resource change count | Not independently reported. | Count every station/group change, including same station RBG changes. | Diagnostic addition. Same station resource changes are not counted as handovers. |
| Switching interruption | Not modeled. | Still not modeled; no extra RBG switching cost. | Source does not provide a calibrated interruption duration [TFM, p. 9, Sec. 3.3.1; p. 15, Table 3]. This remains a limitation, not a verified original behavior. |

The 61 options are explicit stay plus five candidate slots by twelve RBGs;
some options are masked. Candidate zero is the serving cell. A new station must
exceed the current serving RSS by more than 3 dB and meet RSS ≥ −96 dBm. Duplicate
serving candidate slots and occupied groups are rejected, while the current
serving cell/group pair remains valid. The prospective filter cannot bypass A3.

### 5. Radio, Traffic, Queues and Energy

These shared physical proxies were introduced in v1 and retained in v2. The
v2 change is immediate failure on overflow, not a new queue or propagation model.
In particular, **200 kbit/s is our surrogate assumption**, not a verified
conversion of the original thesis traffic after resolving its time units.

| Item | Original TFM and locator | Executed experiment and status |
| --- | --- | --- |
| RSS | Downlink budget in dBm, TFM, p. 7, Eq. (1) | Use stored RSS directly; for values above −128, convert to watts with `10 ** ((RSS − 30)/10)`. |
| Interference | Sum of neighboring BS RSS labeled uplink, TFM, p. 10, Eq. (9) | Sum linear downlink received powers only from selected operator stations whose background uses the UAV's group; exclude serving station. This changes link interpretation and cochannel selection as well as arithmetic. |
| Link quality | SNR = RSS − thermal noise − noise figure, TFM, p. 10, Eq. (8) | SINR = serving watts / (interference watts + noise watts). Logarithm floor 1e−15 for reported SINR dB. |
| Noise | −112.41 dBm thermal noise and 9 dB figure, TFM, pp. 14–15, Table 3 | Retain combined noise of −103.41 dBm, converted to watts before addition. |
| Bandwidth | 180 kHz per RRB and eight per group, TFM, p. 15, Table 3 | Retain 1.44 MHz service bandwidth. No additional learned bandwidth allocation. |
| Rate | Printed `(WB × groupsize) + log2(SNR_dB)`, TFM, p. 10, Eq. (7) | `1.44e6 × log2(1 + SINR_linear)` bit/s. Ideal service proxy, without modulation, coding, scheduler efficiency, or empirical throughput calibration. |
| General arrivals | Poisson based expression, TFM, pp. 9–10, Eqs. (5)–(6); mean 100 packets, p. 15 | Constant 200,000 bits/s. We do not sample packets or multiply by the printed Poisson probability. |
| Data packet size | 1000 bits in prose, TFM, p. 14; 2000 in Table 3, p. 15 | Fixed bit rate rather than individual packets. 200 kbit/s is our declared rate, not an assertion of original equivalence after time conversion. |
| Handover overhead | Four 1200 bit packets, TFM, pp. 14–15, Table 3 | Retain 4800 bits per executed handover; no separate interruption delay. |
| Queue bounds and ordering | Queue equation and capacity constraint, TFM, p. 9, Eq. (5); p. 11, C4; p. 15, Table 3 | Start empty. Add traffic and overhead, subtract this step's service, clamp at zero, then count overflow and cap at 1,280,000 bits. KB interpreted as decimal. |
| Delay | Buffer/rate ratio, TFM, p. 9, Eq. (4) | Postservice capped backlog / `max(rate,1 bit/s)`, capped at 200 s. This is censored residual backlog/service, not individual packet latency. |
| Energy state and model | Remaining energy expression involving mass, speed, efficiency, lift-to-drag and electronics, TFM, p. 10, Eq. (10) | Accumulate consumed energy using `(100 + 0.4 × speed²) × dt` joules, evaluated at end step speed. |
| Airframe parameters | 3 kg, lift-to-drag 5, efficiency 55%, electronics 0.1 kW, TFM, p. 15, Table 3 | Mass, lift-to-drag and efficiency are not modeled. Keep the numerical 100 W electronics floor inside a new uncalibrated proxy; coefficient 0.4 is our choice. |
| Energy capacity | 1000 kW label, TFM, p. 15, Table 3 | Choose 100 kJ budget. It is not a unit conversion from the printed capacity. Eq. (10) also lacks a clear integrated time factor; original code remains unknown. |

### 6. Reward Functions and Terminal Handling

**v1 factorial reward definitions:**

The source reward definitions are Eqs. (13)–(14), printed p. 12. Their numeric
parameters are Table 3, printed p. 15. Energy override and absence of arrival
termination are on printed p. 12. The earlier energy and overflow reward terms
were removed in the final source formulation [TFM, pp. 20–21, Sec. 7.3]; we
do not describe those removed terms as part of the final original baseline.

| Component | Original TFM | Our legacy arms | Our reward replacement arms |
| --- | --- | --- | --- |
| Radio reward | Positive reciprocals of delay, interference, handover, Eq. (13), p. 12 | Same algebra, but new shared delay and interference inputs | Replace with `−0.05 × (clip(delay,0,1) + outage + handover)` |
| Equal policy weights | `(0.35, 0.30, 0.35)`, Table 3, p. 15 | Retained | Removed; no direct interference reward |
| Reciprocal scales | `(10, 1e5, 100)`, Table 3, p. 15 | Retained; interference now in watts | Removed |
| Specialized weights | One 0.8 and two 0.2 values in Table 3, p. 15, despite sum-to-one requirement in Eq. (11), p. 10 | Not used | Not used; factorial experiment replaces weight priority comparison |
| Approach term | `+12` whenever distance decreases, Eq. (14), p. 12; Table 3, p. 15 | Retained, independent of progress magnitude | Replace with `gamma × Phi(next) − Phi(now)` |
| Potential | Not part of Eqs. (13)–(14), p. 12 | None | `Phi = −(distance + speed²/(2 × 5))/100`, gamma 0.99 |
| Arrival bonus | None in Eq. (14), p. 12 | None | +20 once on first safe arrival; prior arrival is observed |
| Per step time cost | None in Eq. (14), p. 12 | None | −0.05 every active step |
| Boundary and outage | −10 each, Eq. (14), p. 12; Table 3, p. 15 | Same penalties on events in the new common model | Outage enters bounded radio cost; terminal failure before first arrival costs −20 |
| Speed penalty | −10 at threshold, Eq. (14), p. 12; Table 3, p. 15 | Removed because common dynamics hard cap speed at 25 m/s | No extra speed penalty; same cap and stopping potential |
| Energy exhaustion | Overrides reward with −10, Sec. 5.2, p. 12; Table 3, p. 15 | Override retained using new energy model | Included in the −20 terminal failure term; not a whole reward override |
| Deadline failure | Fixed episode length; no separate arrival failure payment specified, pp. 12, 16 | No new deadline penalty | −20 if ending without any safe arrival |
| Terminal potential | Not applicable to source Eq. (14), p. 12 | None | Set next potential to zero at every terminal, including timeout |
| Training after arrival | Explicitly continues, Sec. 5.2, p. 12 | `legacy` continues; `terminal_only` ends | `reward_only` continues; `fixed` ends |
| Evaluation after arrival | No corresponding position and numerical speed endpoint defined in reported results, pp. 16–20 | Always end on first safe arrival | Always end on first safe arrival |

After a first arrival in continuing training, another arrival gives no bonus
and a later failure gives no −20 failure payment. Episode logs for continuing
training track whether an arrival ever occurred; evaluation never includes
postarrival motion. Buffer overflow has no direct reward term in any arm.
Raw shaping telescopes only before PPO normalization and clipping. The study
tests that entire training recipe, not a proof that transformed optimization
exactly preserves the base objective.

**Final v2 communication cost changes:**

| Item | v1 executed behavior | Final v2 executed behavior | Original source relationship |
| --- | --- | --- | --- |
| Delay cost | `0.05 * min(D, 1)` inside fixed reward. | `0.35 * 10D / (1 + 10D)` in full arm. No flat reward plateau at one second. | One minus original reciprocal utility [TFM, p. 12, Eq. (13)] with equal configuration values [p. 15, Table 3]. Smooth saturation remains. |
| Interference cost | Absent from fixed reward, although measured. | Restore `0.30 * 100000I / (1 + 100000I)`. | Same reciprocal utility scales and weights [TFM, pp. 12, 15]. I remains our downlink proxy. |
| Handover cost | `0.05 * H`. | `0.35 * 100H / (1 + 100H)`. | Restore normalized source utility [TFM, p. 12, Eq. (13); p. 15, Table 3]. |
| Positive per step radio utility | Present in reimplemented legacy reward, removed in v1 fixed reward. | Subtract communication cost, so simply staying active does not earn that utility bonus. | Changes the positive reciprocal reward structure [TFM, p. 12, Eqs. (13)–(14)] while preserving the three normalized tradeoff components. |

Both final v2 learned arms use the same strict failure rules, terminal arrival,
observation, residual action decoder, filter, PPO and base reward:

```text
Phi(s) = -(distance + speed² / (2 × acceleration_limit)) / 100
shaping = 0.99 × Phi(next) - Phi(current), with terminal Phi(next) = 0
base = shaping - 0.05 + 20 × joint_success - 20 × terminal_failure

C = 0.35 × (10D)/(1 + 10D)
  + 0.30 × (100000I)/(1 + 100000I)
  + 0.35 × (100H)/(1 + 100H)

v2 arrival arm = base
v2 full arm    = base - C
```

Here D is the postservice backlog/service proxy in seconds, I is downlink
cochannel interference in watts, and H is the executed handover indicator.
Weights 0.35/0.30/0.35 and scales 10/100000/100 are the source's equal priority
configuration [TFM, p. 15, Table 3]. Each cost is one minus its original
reciprocal utility [TFM, p. 12, Eq. (13)]. Subtracting the cost removes the
positive utility for merely remaining active. It does not imply that the
termination objective is unchanged or that delay is guaranteed: the reciprocal
still saturates and the numerical delay proxy remains censored at 200 s.

### 7. Residual Motion and the Safety Filter

These final v2 additions are shared by both learned arms. They change the
controller architecture as well as the information used to execute an action.

| Item | v1 executed behavior | Final v2 executed behavior | Original source relationship |
| --- | --- | --- | --- |
| Continuous action | Two direct radial/lateral acceleration commands. | Projected reference command plus two bounded learned residuals of scale 0.5, followed by physical projection. | New controller prior; differs from original discrete acceleration and heading [TFM, p. 12, Sec. 5.2; p. 15, Table 3]. |
| Safety filter | None. | Predict the next sample; repair unsafe network choice if possible, otherwise try local motion/network alternatives; still fail if unresolved. | New model based constraint handling component; original source describes reward penalties [TFM, p. 12, Eq. (14)]. |
| Prospective radio access | Learned policy observes current candidates. | PPO still observes current options. Its shared filter and model based references query the known map at predicted positions. | New information/control architecture, not reproduced source logic. |

The action decoder projects the destination braking reference to the unit
disk, adds `0.5 × tanh(latent)` componentwise, and applies the acceleration norm
projection. PPO optimizes likelihoods of its proposed residual and network
actions. Physical projection and the filter are environment transformations.

The filter checks the proposed next position, serving RSS and queue. It first
tries another admissible station/RBG pair with the same motion. If none repairs
the step, it tries the local motion/network controller. An unresolved proposal
still fails. The RSS, buffer, A3 and resource rules are never relaxed.
Network and motion overrides are counted separately. All four deterministic
references share the same filter. Prospective access to the known map and the
braking prior are explicit controller components, not learned competence or
proof of global reachability.

### 8. PPO and All Numerical Settings

The following tables give the v1 implementation, covering every original
Table 4 setting plus our explicit choices where the source is incomplete.
V2 retains these optimizer and numerical settings, replacing the observation,
network head and motion decoder as described above. Its policy count is ten,
whereas the v1 budget row below describes twenty policies.

The original uses Stable Baselines [TFM, p. 13, Sec. 5.3, Algorithm 1].
Every reported parameter in its Table 4 [TFM, p. 16] is compared below.
Unspecified library settings are not filled in from guessed defaults.

| Parameter | Original TFM, p. 16, Table 4 | Executed experiment |
| --- | --- | --- |
| Number of episodes | 300 | No fixed episode budget; equal interaction budget |
| Episode timesteps | 2000 | 200, with explicit mission/failure terminals |
| Steps per environment before update | 8 | 128 |
| Learning rate | 0.00003 | 0.0003, constant |
| Batch size | 32 | 512 per optimization minibatch |
| Gamma | 0.99 | 0.99, retained and matched to shaping |
| GAE lambda | 0.95 | 0.95, retained |
| PPO clip range | 0.2 | 0.2, retained |
| Value coefficient | 0.5 | Configured 0.5; local value loss itself is half MSE, so its total coefficient is 0.25 MSE |
| Entropy coefficient | 0.01 | 0.005 |
| Target KL | 0.03 | No target or KL early stopping; diagnostic KL only |

Additional executed implementation choices, not fully specified by the source's
Sec. 5.3/Algorithm 1 or Sec. 6.2/Table 4 [TFM, pp. 13, 15–16]:

| Component | Exact executed choice |
| --- | --- |
| Runtime and optimizer | Python 3.12, PyTorch 2.4.1 CPU, NumPy 2.3.5; Adam epsilon 1e−5; two PyTorch threads |
| Parallel rollout | 64 independent lanes × 128 steps = 8192 samples per update |
| Interaction budget | 524,288 per final policy = 64 rollout updates; 20 final policies |
| Optimization passes | Four epochs; new NumPy random permutation each epoch; 16 minibatches per epoch |
| Networks | Separate actor and critic, each two 64 unit tanh hidden layers; linear value head |
| Actor heads | Independent 2D Gaussian and masked five choice categorical head |
| Initialization | Orthogonal weights; gain sqrt(2) for hidden layers, 0.01 for action heads, 1 for value head; zero biases |
| Motion variance | Learned two component log standard deviation, initialized −0.5, clamped to [−2.3, 0.5] when used |
| Action transform | Tanh Gaussian sample followed by shared acceleration norm projection |
| Policy likelihood | Sum latent Gaussian log probability and categorical log probability; stored latent sample used again for PPO ratio |
| Entropy | Sum latent Gaussian and masked categorical entropy, not entropy after nonlinear projection |
| Mask numerics | Invalid logits replaced by −1e9; stay valid in all observations |
| Reward scaling | Running variance of discounted returns across lanes; no reward mean subtraction; divide by sqrt(var + 1e−8), clip to [−10,10]; return state cleared at terminal |
| Normalizer initialization | Mean 0, variance 1, count 0.0001; float64 return accumulators |
| Observation scaling | Fixed transforms listed in Section 3 above; no fitted observation normalizer |
| Advantage scaling | Subtract minibatch mean and divide by minibatch standard deviation + 1e−8 |
| Value optimization | Unclipped `0.5 × mean((V − return)²)` before configured value coefficient; no value clipping |
| Gradient clipping | Total parameter gradient norm ≤0.5 |
| KL diagnostic | Mean of `(exp(logratio) − 1) − logratio`; does not stop optimization |
| Bootstrap | GAE bootstraps at nonterminal rollout boundaries; no bootstrap across actual mission, failure, or finite horizon terminals |
| Training randomization | Seed Python random, NumPy, and PyTorch; shared deterministic route stream per lane; no pretrained model or imitation data |
| Checkpoint policy | Periodic checkpoint overwrites within a run; use final checkpoint for comparison; checkpoint includes policy, dimensions, config metadata, and step count |
| Resume scope | Saved policy supports inference replay; optimizer, RNG, normalizer, and environment state are not all saved for exact training resumption |
| Evaluation action | Gaussian mean through tanh and norm projection; categorical argmax; no exploration sampling |
| Evaluation returns | Evaluator uses common fixed raw reward by default for every policy; `raw_return` is its undiscounted episode sum, not original training reward or normalized PPO return |

Implementation: [experiment_ppo.py](src/uav_joint_optimization/experiment_ppo.py), `PPOConfig`, `HybridPolicy`, `RewardNormalizer`, `gae`, `train`, and `evaluate`. These details are declarations of our code, not claims that every one differs from the missing source implementation.

**V2 network head change:**

| Item | v1 executed behavior | Final v2 executed behavior | Original source relationship |
| --- | --- | --- | --- |
| PPO network head | Five categorical logits. | 61 categorical logits; continuous and value heads retained. | Original architecture details are not sufficiently specified [TFM, p. 13, Sec. 5.3]. |

### 9. Deterministic Reference Controllers

**v1 reference compared with the written greedy controller:**

| Item | Original TFM and locator | Executed experiment and status |
| --- | --- | --- |
| Reference motion | Constant speed and closest discrete heading, TFM, p. 13, Sec. 5.4 | Continuous desired velocity toward goal with braking: `min(25, 0.7 × sqrt(2 × 5 × max(distance−4,0)))`; acceleration tracks desired velocity and uses common bounds. Not the original greedy policy. |
| Reference handover | Viability counters per station and first available RBG, TFM, pp. 13–14, Sec. 5.4 | Request strongest station when its candidate is admissible; otherwise stay. Same mask and allocator as learned policies; no counters. |

**Final v2 reference set:**

| Item | v1 executed behavior | Final v2 executed behavior | Original source relationship |
| --- | --- | --- | --- |
| Deterministic references | Destination braking and strongest admissible RSS. | Four nominal control laws with the same filter: Goal RSS, Goal radio, one step joint search, and three step joint search. | New references, not a recreation of the thesis's discrete constant velocity greedy controller [TFM, pp. 13–14, Sec. 5.4]. |

Four deterministic references share all v2 physical and communication rules:

- `straight_rss`: destination directed braking control, strongest admissible
  RSS association, and the first free RBG. This reconstructs the v1 reference
  logic with the shared v2 network timing and strict endpoint.
- `straight_radio`: the same motion, with model based station/RBG selection
  for its predicted next position. Feasible options take priority, followed by
  the original normalized communication cost.
- `joint_mpc`: a declared local search over motion primitives and network
  choices. The controller uses the known map for a single predicted step. It
  is a model based local reference, not a globally optimal route planner.
- `joint_lookahead`: the same nine initial motion primitives, each followed by
  two predicted destination directed steps and greedy radio choices. It scores
  three sampled communication costs plus distance progress, rejects predicted
  violations preferentially, and applies a first step progress preference.
  It is also a local reference and can still time out or violate a constraint.

The nine primitives are the reference direction at speed scales 1, 0.6 and 0,
and scale 1 with angles −1.2, −0.6, −0.3, 0.3, 0.6 and 1.2 radians relative to
the destination direction. The one step search uses cost plus distance change
divided by 100 m, with a 10,000 penalty for predicted radio/buffer infeasibility,
a 100,000 boundary penalty, and a 20 arrival preference. A 1,000 progress
penalty applies beyond 30 m when the predicted first step reduces distance by
less than 0.1 m. These are controller search priorities, not new user QoS
requirements. The three step search uses the same progress and arrival
preferences and a 10,000 penalty for any predicted failure. See the versioned
code for event ordering and exact arithmetic.

The `straight` labels describe nominal reference motion. The shared safety
filter can alter that motion; its intervention counts and actual paths are
reported. They must not be presented as strictly straight trajectories after
filter intervention.

The radio and joint references have prospective map access; PPO proposes
actions from current radio observations and shares the prospective safety
filter. Any comparison must disclose this architecture and information access.
All controller details and candidate motions are versioned in the frozen v2 source.

### 10. Training, Validation, Tests and Budgets

The original tuning/comparison sections do not document an equivalent independent
training/validation/test split [TFM, pp. 15–16, Secs. 6.2–6.3]. This is a limit
of the written description, not proof that the unavailable code reused its test
data. We define and save the split explicitly.

**v1 experimental design:**

| Item | Original TFM and locator | Executed experiment and status |
| --- | --- | --- |
| Comparison type | PPO vs greedy plus different reward weights, TFM, p. 16, Sec. 6.3 | Four reward/termination treatments plus deterministic reference; all share the new physical and action model. |
| Route sampling | Start and goal concept, TFM, pp. 5, 9–10; sampling distribution and split counts not specified in pp. 14–16 | Start uniform in `[250,4750] × [250,3250]`; direction uniform over full circle; distance uniform over specified interval; reject goals outside `[150,4850] × [150,3350]`. |
| Training and validation | No independent three way split documented, TFM, pp. 15–16, Secs. 6.2–6.3 | 4096 training routes, seed 42000; 64 validation routes, seed 42001. Validation is excluded from gradient updates. |
| Standard test | No separate set specified, TFM, pp. 15–16 | 200 routes, seed 42012, lengths 200–1000 m. Same ordered pairs for every arm and seed. |
| Longer test | No such extrapolation set specified, TFM, pp. 15–16 | 200 routes, seed 42013, lengths 1000–1800 m, same map. |
| Geographic separation | All experiments on Barcelona map, TFM, p. 14, Sec. 6.1 | Same city retained. New coordinate pairs have no exact cross-split duplicates, but trajectories may visit the same geographic locations. |
| Development | Extensive tuning described, TFM, pp. 15–16, Sec. 6.2 | Six pilots with seeds 41/42. Corrected common emergency handover during pretraining validation; retired exploratory route seeds 42002/42003. |
| Final training seeds | Not specified in reported protocol, TFM, pp. 15–16 | Five independent initializations, 1101–1105, per treatment. Same scenario streams; termination changes episode exposure under equal interaction budget. |
| Checkpoint selection | Tuning described; independent test selection rule not specified, TFM, p. 16, Sec. 6.2 | Frozen settings and budget; final checkpoint only; no test tuning or early stopping. |

**Final v2 design changes:**

| Item | v1 executed behavior | Final v2 executed behavior | Original source relationship |
| --- | --- | --- | --- |
| Learning comparison | Four reward/termination arms; direct acceleration learning. | Two arms: arrival base only versus arrival base minus all three radio costs. Both use strict failure, termination and the same new controller architecture. | A new controlled comparison; neither arm is the source's trained policy. |
| Training route lengths | 200–1000 m. | 200–1800 m; longer tests lie within this range. | New study design; original route distribution and independent splits are not documented [TFM, pp. 15–16, Secs. 6.2–6.3]. |
| Final route identities | Seeds 42012 and 42013. | Fresh seeds 52012 and 52013. Exact pairs are disjoint from v1 and other v2 splits. | Our explicit split protocol; same map remains shared. |
| Training seeds | 1101–1105. | 2101–2105. | New repeated experiment; original seed list is unspecified [TFM, pp. 15–16]. |
| Final budget | 524,288 interactions each; 20 policies. | Same interactions per policy; 10 policies. | Our PPO budget remains different from 300 episodes and 2,000 maximum steps in the source [TFM, p. 16, Table 4]. |

The executed splits and final budgets are:

| Item | v1 | Final v2 |
| --- | --- | --- |
| Training routes | 4,096, seed 42000, lengths 200–1000 m | 4,096, seed 52010, lengths 200–1800 m |
| Standard validation | 64, seed 42001 | 64, seed 52001 |
| Longer validation | No separate final longer validation pool | 32, seed 52002 |
| Standard test | 200, seed 42012, lengths 200–1000 m | 200, seed 52012, lengths 200–1000 m |
| Longer test | 200, seed 42013, lengths 1000–1800 m | 200, seed 52013, lengths 1000–1800 m |
| Final training seeds per arm | 1101–1105 | 2101–2105 |
| Learned arms / final policies | Four / twenty | Two / ten |
| Interactions per final policy | 524,288 | 524,288 |
| Total final interactions | 10,485,760 | 5,242,880 |
| Final learned evaluations | 8,000 | 4,000 |
| Final reference evaluations | 400 | 1,600 |

Validation never contributes gradient updates. Exact coordinate pairs are
disjoint across the declared final splits and between studies, but all use the
same city, altitude, frequency and static load construction. Routes may visit
the same locations. Five training seeds are not five independent maps or loads.
Longer routes test length extrapolation in v1; final v2 training already covers
their lengths, so v2 longer results are not an extrapolation improvement claim.

V1 retains six pilots using seeds 41 and 42. V2 retains six pilots: direct motion
without a filter (seed 51, 524,288 interactions per arm), direct motion with a
filter (52, 1,048,576), and residual motion with the filter and full length range
(53, 524,288). Early v2 designs used training route seed 52000 and lengths
200–1000 m. Those retired versions have their own snapshots. No pilot checkpoint
initializes final training. All development failures are in
[note 29](docs/29_connectivity_development_log.md).

Source, protocol and budget freezes precede final test evaluation. Final
checkpoints use deterministic actions without test selection. Equal interaction
budgets do not imply equal numbers of missions: earlier termination changes
episode exposure. Combining reward, filter, prior and training range changes
between versions does not isolate any single one of them.

### 11. Metrics, Statistics and Verification

**v1 additions relative to the written reporting protocol:**

| Item | Original TFM and locator | Executed experiment and status |
| --- | --- | --- |
| Primary outcome | Radio metrics and trajectories, TFM, pp. 16–20, Sec. 7 | Mission success first; failures and final distance retained separately. |
| Secondary outcomes | SNR, outage, interference, remaining energy, handovers, TFM, pp. 16–20 | Time, path, consumed energy proxy, handovers, outage, dropped bits, delay, interference, SINR mean and within-episode fifth percentile; summarize conditional on success with counts. |
| Uncertainty | No matching seed/route uncertainty procedure specified, TFM, pp. 16–20 | All five seeds, sample SD, paired crossed bootstrap over seeds and routes; 10,000 draws, seed 73021. Routes are not treated as independent trained models. |
| Primary contrast and gate | No equivalent protocol described, TFM, pp. 15–20 | Both changes minus legacy on standard routes; success ≥90%, recorded feasible success ≥90%, positive lower 95% paired bound. Frozen locally before learned test results. |
| Figure selection | Examples shown, TFM, pp. 17, 19, Figs. 5, 7; selection mechanism unspecified | First predefined test route and first declared training seed; separate pilot figure clearly labeled exploratory. |
| Verification artifacts | Written methods and source reference, TFM, pp. 13–16; no usable original package received | 34 passing tests; frozen source/config hashes; raw JSON/CSV records; exact replay of 200 episodes; retained policies and scripts. |

**Final v2 paired reporting change:**

| Item | v1 executed behavior | Final v2 executed behavior | Original source relationship |
| --- | --- | --- | --- |
| Secondary comparison | Success conditioned summaries and selected matched comparisons. | Explicit intersections of successful route/seed pairs for radio comparisons, with counts and crossed bootstrap intervals. | Source does not report a matching conditional joint success protocol [TFM, pp. 16–20, Sec. 7]. |

V2 makes joint completion the primary outcome and preserves every failure
reason. Secondary radio comparisons use the intersection of successful paired
routes and report its size. Both accumulated and per sample cost are retained,
alongside time, path, energy, handovers, resource changes, delay, interference,
SINR and final queue. An aggregate benefit cannot conceal increased delay or
failed flights.

V1 uses 10,000 crossed bootstrap draws with analysis seed 73021. V2 uses 5,000
draws with seed 62000, resampling both training seeds and route identities with
pairing preserved. Deterministic comparisons resample routes only. V2's strong
learned improvement gate requires a positive lower confidence limit for joint
completion change and a negative upper limit for accumulated radio cost change.
That gate is not met on either final split. Conditional secondary estimates
describe jointly successful pairs, not the excluded failed flights.

The initial v1 suite had 34 tests; v2 adds 17, for 51 passing checks recorded
in the final delivery. The v1 connectivity audit exactly replayed 4,400 flights;
all 5,600 final v2 evaluations replay exactly. The 4,400 figure is an audited
subset of v1's 8,400 final evaluations, not a claim to have replayed every v1
arm in that later audit. The earlier 200 episode checkpoint check is separate.
This README expansion reruns no training or simulation and adds no new result.

The frozen v2 statistics include an inappropriate generic relative percentage
field for logarithmic SINR. A separate reporting copy sets only those fields
to null and records the source hash; absolute dB differences, all other estimates
and intervals remain unchanged. The original estimator and raw statistics are
preserved. See [the delivery audit](docs/32_connectivity_delivery_audit.md).

### 12. Event Ordering, Retained Values and Limits

**V1 event ordering and historical artifact boundaries:**

Each active step applies an admissible handover and allocation from the current
observation, advances bounded motion, clips/checks the boundary, increments
time, samples radio at the new position, updates outage and queue, accumulates
energy, checks physical failure and safe arrival, applies the training terminal
rule, computes reward, records metrics, and obtains the next observation. The
source does not fully prescribe this ordering [TFM, Secs. 3.2–5.2, pp. 9–12].

The frozen experiment executes `experiment_env.py` and `experiment_ppo.py`.
Earlier package modules for objective design, legacy action auditing, and radio
utilities are supporting historical work; their proposed settings are not
silently part of this experiment. Likewise, earlier Markdown proposals for
graph planning, constrained optimization, learned RBG allocation, or observation
ablations are not claims about what was trained here.

The hand written initial reward trace is an abstract diagnostic, not a failed
physical flight. Its 4–5 m distance lies inside the source's 10 m position
tolerance [TFM, p. 15, Table 3]. The later physical witness uses the real map
but its arriving reference drops packets, so it only demonstrates a completion
incentive reversal, not universal feasibility. Neither witness is included in
the learned success percentages.

**Final v2 event differences.** The prospective filter acts on the proposed
motion and network decision before executing the step. Strict RSS and overflow
failure supersede the permissive v1 checks. Failure precedes simultaneous
arrival; otherwise arrival ends the episode. Initial RSS violations are
preserved. The five second decision gate and five outage allowance are not
executed in v2, even if an inherited compatibility field appears in metadata.
All remaining map, queue, service, motion and energy arithmetic is the declared
shared surrogate.

**Retained source values and objectives.** These are not all new requirements:

| Value or requirement | Relationship to the original TFM |
| --- | --- |
| Barcelona map, 2.1 GHz, 100 m, 133 sites, first operator with 87 stations | Matching received metadata and selected operator [TFM, pp. 6–7, Sec. 3.1, Table 2; p. 14, Sec. 6.1]; exact experiment version unconfirmed |
| 46 dBm transmitter setting and strongest sector retention | Inherited through stored RSS; power is not added again and sectors are not actions [TFM, p. 7, Table 2 and Eq. (1) discussion] |
| 10 m position tolerance | Retained; the additional numeric 2 m/s stop criterion is ours [TFM, p. 9, Sec. 3.2; p. 15, Table 3] |
| Maximum acceleration magnitude 5 m/s² | Numeric magnitude retained, changed from scalar bins to a vector bound [TFM, pp. 12, 15, Sec. 5.2 and Table 3] |
| RSS minimum −96 dBm and bounded queue | Written C2/C4 restored at final v2 samples, including equality; 160 KB interpreted as decimal 1.28 Mbit [TFM, p. 11, Eq. (12); p. 15, Table 3] |
| A3 margin 3 dB | Follow the Eq. (3) inequality and interpret the difference in dB [TFM, p. 9, Eq. (3); p. 15, Table 3] |
| Twelve RBGs and 1.44 MHz bandwidth | Retained numerical resource count and group bandwidth [TFM, p. 15, Table 3] |
| Combined noise −103.41 dBm | Retain −112.41 dBm thermal noise plus 9 dB noise figure, converted to watts [TFM, pp. 14–15, Sec. 6.1 and Table 3] |
| Handover overhead 4,800 bits | Four 1,200 bit control packets, without modeled interruption [TFM, pp. 14–15, Table 3] |
| Delay, interference and handover objectives | All active again in final v2 full reward, using equal weights 0.35/0.30/0.35 and scales 10/100000/100 [TFM, p. 10, Eq. (11); p. 12, Eq. (13); p. 15, Table 3] |
| Gamma 0.99, GAE 0.95, PPO clip 0.2 and configured value weight 0.5 | Retained configuration numbers; numerical value loss convention is explicit above [TFM, p. 16, Table 4] |

**Outstanding assumptions.** The sentinel convention, exact source dataset
version, original simulator behavior, calibrated uplink interference, real packet
latency, rotorcraft energy, switching interruption, dynamic load, obstacle safety
and radio continuity between samples remain unverified. We introduced no new
application deadline, minimum throughput or complete delivery requirement. Direct
paths can satisfy the stored RSS field; curvature itself is not an objective.

**What the evidence identifies.** V1 supports reward replacement within its
shared reconstruction. V2 enforces the sampled joint endpoint and reports the
tradeoff from restoring communication costs within its richer controller.
Neither result demonstrates a one line repair of the unavailable original
simulator, independent benefits from every shared change, or PPO superiority
over the deterministic references.

Both studies retain raw outcomes, settings, seeds, snapshots, Markdown notes and
the [consolidated IEEE draft](paper/UAV_joint_reward_connectivity_IEEE.pdf).
The six v1 and seven v2 frozen source/protocol files are immutable. Private map
and checkpoint binaries remain outside Git; source and evaluation records are
available in this repository. [Note 34](docs/34_readme_thesis_inventory.md)
records this documentation expansion and its validation.

## Read and Reproduce

- [Confirmed results and every seed](docs/21_confirmed_results.md)
- [Everything changed from the original TFM, with precise source pages](docs/25_exact_changes_from_tfm.md)
- [Reproduction commands and artifact map](docs/22_reproduction_guide.md)
- [IEEE manuscript and build instructions](paper/README.md)
- [Documentation index](docs/README.md)
- [Current task status](docs/12_task_status.md)

The complete suite has 51 passing tests. The earlier v1 study had 34 tests
and an exact 200 episode replay for its first reward replacement seed; final v2
has 5,600 exact replays. Checkpoint binaries remain local. The following commands
reproduce the v1 analysis and checkpoint check; use [note 30](docs/30_connectivity_results_and_reproduction.md)
for v2 commands:

```powershell
python -m pytest tests -q
python scripts/analyze_controlled_experiment.py
python scripts/evaluate_checkpoint.py --checkpoint results/controlled_experiment/confirmatory_v1/reward_only_seed_1101/checkpoint.pt --split test
```

Use the recorded dependencies in `requirements-experiments.txt` and obtain the
private map separately from its owner. The analysis verifies frozen source
hashes; use a new experiment label for new training, preserving the completed
comparison.

## Structure

| Path | Purpose |
| --- | --- |
| `docs/` | Dataset audit, design, validation, pilots, results, risks, and logbook |
| `src/uav_joint_optimization/` | Environment, hybrid PPO, and earlier audit utilities |
| `scripts/` | Training, analysis, checkpoint replay, diagnostics, and paper tables |
| `configs/` | Frozen source hashes, settings, route coordinates, and seeds |
| `results/controlled_experiment/` | V1 pilots, twenty final policy records, episodes, statistics, and figures; checkpoint binaries local |
| `results/connectivity_experiment/` | V2 development, ten final policy records, four references, paired statistics, and exact replays; checkpoint binaries local |
| `paper/` | IEEE source, generated tables, compiled PDF, and build guide |
| `sources/` | Research PDFs, including the original thesis |

Earlier notes numbered 01–16 document the predata investigation and proposals.
Their historical blocked status and hypotheses are superseded by notes 17–23.
The old hand written reward diagnostic is not trained evidence and its distance
trace does not satisfy the current meaning of a failed mission; see its revised
limitations in `docs/11_initial_reward_diagnostic.md`.

The next research decision is to repeat the reward ablation in the recovered
original simulator, then test independent traffic and geographic conditions.

The baseline thesis is preserved at
`sources/UAV_Bermudez_Granados_2026_MSc_thesis.pdf`, with the official
[UPCommons record](https://upcommons.upc.edu/entities/publication/a8ce08c2-c238-4145-a5ab-5d39b12c6553).
