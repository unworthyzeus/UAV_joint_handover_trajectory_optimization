# Exact Comparison with the Original TFM

Date: 12 September 2026. This is the definitive comparison for the frozen
`confirmatory_v1` experiment. It compares the **written thesis** with the code
actually executed. It cannot establish differences from unavailable original
implementation details.

## What We Did and What the Experiment Identifies

We received the Barcelona RSS map, built a new environment and hybrid PPO
implementation around it, and compared four reward/termination treatments
inside that shared implementation. We did **not** take Marina's executable
simulator and change only its reward. Every shared change below also applies
to the arm named `legacy`, which means legacy reward structure, not the
original saved policy or an exact reproduction of its simulator.

Only two factors were independently varied: replacement of the raw reward and
termination during training at safe arrival. Their joint effects are measured
in the shared reconstructed environment. Observation repair, dynamics, radio
proxies, scheduling, PPO implementation, and hyperparameters were not separately
ablated. Differences in these foundations cannot individually be credited for
the measured gain, and interactions with the reward remain possible.

This record was created to make every source definition, implemented choice,
retained value, and unresolved assumption reviewable. The full result remains
in note 21; this documentation does not change any policy or test outcome.

## Citation Convention

**TFM** means Marina Bermúdez Granados, *Deep Reinforcement Learning-Based Joint
Handover and Trajectory Optimization for 5G-Connected UAV*, 11 May 2026,
[original PDF](../sources/UAV_Bermudez_Granados_2026_MSc_thesis.pdf).
All page numbers below are the **printed page numbers**, not the PDF viewer
counter. For the cited body pages, **PDF page = printed page + 2**. Thus
`TFM, p. 12, Eq. (14)` is on PDF page 14. Source equations keep their original
numbers; our manuscript has its own equation numbering.

“Not specified” means the written thesis does not give enough information to
determine the original setting. It does not mean the original code lacked it.
“Ambiguous” means the text or units are inconsistent. Our explicit replacement
is a modeling choice, not proof of a corrected original implementation bug.

## Original Thesis Definition Index

| Definition | Exact original location | PDF pages |
| --- | --- | --- |
| Mission and system sketch | TFM, p. 5, Sec. 3 and Fig. 1 | 7 |
| Buildings, station distribution, operators | TFM, p. 6, Sec. 3.1.1 and Fig. 2 | 8 |
| Ray tracer, sectors, frequency, altitude, resolution | TFM, pp. 6–7, Sec. 3.1.2 and Table 2 | 8–9 |
| Downlink RSS budget and strongest sector retention | TFM, p. 7, Eq. (1) and following paragraphs | 9 |
| RSS and serving cell illustrations | TFM, p. 8, Figs. 3–4 | 10 |
| Position update and intention to stop at destination | TFM, p. 9, Sec. 3.2, Eq. (2) | 11 |
| A3 inequality and RBG request handling | TFM, p. 9, Sec. 3.3.1, Eq. (3) | 11 |
| Delay ratio and queue update | TFM, p. 9, Sec. 3.3.2, Eqs. (4)–(5) | 11 |
| Poisson arrival formulation | TFM, p. 10, Eq. (6) | 12 |
| Rate and SNR expressions | TFM, p. 10, Eqs. (7)–(8) | 12 |
| Interference expression | TFM, p. 10, Sec. 3.3.3, Eq. (9) | 12 |
| Energy expression | TFM, p. 10, Sec. 3.3.4, Eq. (10) | 12 |
| Weighted objective and sum of weights | TFM, p. 10, Sec. 4, Eq. (11) | 12 |
| Optimization and constraints C1–C6 | TFM, p. 11, Eq. (12) and constraint list | 13 |
| State and action vectors | TFM, p. 12, Sec. 5.2, first paragraph | 14 |
| Reciprocal reward terms and combined reward | TFM, p. 12, Eqs. (13)–(14) | 14 |
| Energy termination, reward override, continued arrival | TFM, p. 12, Sec. 5.2, final paragraphs | 14 |
| PPO implementation and pseudocode | TFM, p. 13, Sec. 5.3, Algorithm 1 | 15 |
| Greedy motion, counters, and RBG allocation | TFM, pp. 13–14, Sec. 5.4 | 15–16 |
| Setup prose, time step, traffic, and random occupancy | TFM, p. 14, Sec. 6.1 | 16 |
| Simulation values, reward scales, weights, and penalties | TFM, p. 15, Table 3 | 17 |
| Tuning and PPO parameter values | TFM, pp. 15–16, Sec. 6.2, Table 4 | 17–18 |
| Types of reported comparisons | TFM, p. 16, Sec. 6.3 | 18 |
| Metrics and greedy comparison | TFM, pp. 16–18, Secs. 7–7.1, Figs. 5–6 | 18–20 |
| Weight comparisons and navigation interpretation | TFM, pp. 19–20, Sec. 7.2, Figs. 7–8 | 21–22 |
| Removed energy and overflow reward terms | TFM, pp. 20–21, Sec. 7.3 | 22–23 |
| Wandering, connectivity priority, and future work | TFM, p. 21, Sec. 8 | 23 |

## 1. Data, Geometry, and Scope

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

Implementation: [RadioMap and scenario generation](../src/uav_joint_optimization/experiment_env.py), methods `RadioMap.__init__`, `query`, and `make_scenarios`. The received file's exact schema and full scan are in note 17.

## 2. Motion, Mission, and Failure Rules

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

Implementation: `UAVBatch.reset`, `geometry`, and `step` in [experiment_env.py](../src/uav_joint_optimization/experiment_env.py). All these shared rules apply to all four arms except the specified training arrival termination factor.

## 3. Observation and Network Action Interface

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

## 4. Radio, Queue, and Energy Equations

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

## 5. Reward and Termination Treatments

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

## 6. PPO and Numerical Implementation

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

Implementation: [experiment_ppo.py](../src/uav_joint_optimization/experiment_ppo.py), `PPOConfig`, `HybridPolicy`, `RewardNormalizer`, `gae`, `train`, and `evaluate`. These details are declarations of our code, not claims that every one differs from the missing source implementation.

## 7. Reference Controller, Scenarios, and Evaluation

| Item | Original TFM and locator | Executed experiment and status |
| --- | --- | --- |
| Reference motion | Constant speed and closest discrete heading, TFM, p. 13, Sec. 5.4 | Continuous desired velocity toward goal with braking: `min(25, 0.7 × sqrt(2 × 5 × max(distance−4,0)))`; acceleration tracks desired velocity and uses common bounds. Not the original greedy policy. |
| Reference handover | Viability counters per station and first available RBG, TFM, pp. 13–14, Sec. 5.4 | Request strongest station when its candidate is admissible; otherwise stay. Same mask and allocator as learned policies; no counters. |
| Comparison type | PPO vs greedy plus different reward weights, TFM, p. 16, Sec. 6.3 | Four reward/termination treatments plus deterministic reference; all share the new physical and action model. |
| Route sampling | Start and goal concept, TFM, pp. 5, 9–10; sampling distribution and split counts not specified in pp. 14–16 | Start uniform in `[250,4750] × [250,3250]`; direction uniform over full circle; distance uniform over specified interval; reject goals outside `[150,4850] × [150,3350]`. |
| Training and validation | No independent three way split documented, TFM, pp. 15–16, Secs. 6.2–6.3 | 4096 training routes, seed 42000; 64 validation routes, seed 42001. Validation is excluded from gradient updates. |
| Standard test | No separate set specified, TFM, pp. 15–16 | 200 routes, seed 42012, lengths 200–1000 m. Same ordered pairs for every arm and seed. |
| Longer test | No such extrapolation set specified, TFM, pp. 15–16 | 200 routes, seed 42013, lengths 1000–1800 m, same map. |
| Geographic separation | All experiments on Barcelona map, TFM, p. 14, Sec. 6.1 | Same city retained. New coordinate pairs have no exact cross-split duplicates, but trajectories may visit the same geographic locations. |
| Development | Extensive tuning described, TFM, pp. 15–16, Sec. 6.2 | Six pilots with seeds 41/42. Corrected common emergency handover during pretraining validation; retired exploratory route seeds 42002/42003. |
| Final training seeds | Not specified in reported protocol, TFM, pp. 15–16 | Five independent initializations, 1101–1105, per treatment. Same scenario streams; termination changes episode exposure under equal interaction budget. |
| Checkpoint selection | Tuning described; independent test selection rule not specified, TFM, p. 16, Sec. 6.2 | Frozen settings and budget; final checkpoint only; no test tuning or early stopping. |
| Primary outcome | Radio metrics and trajectories, TFM, pp. 16–20, Sec. 7 | Mission success first; failures and final distance retained separately. |
| Secondary outcomes | SNR, outage, interference, remaining energy, handovers, TFM, pp. 16–20 | Time, path, consumed energy proxy, handovers, outage, dropped bits, delay, interference, SINR mean and within-episode fifth percentile; summarize conditional on success with counts. |
| Uncertainty | No matching seed/route uncertainty procedure specified, TFM, pp. 16–20 | All five seeds, sample SD, paired crossed bootstrap over seeds and routes; 10,000 draws, seed 73021. Routes are not treated as independent trained models. |
| Primary contrast and gate | No equivalent protocol described, TFM, pp. 15–20 | Both changes minus legacy on standard routes; success ≥90%, recorded feasible success ≥90%, positive lower 95% paired bound. Frozen locally before learned test results. |
| Figure selection | Examples shown, TFM, pp. 17, 19, Figs. 5, 7; selection mechanism unspecified | First predefined test route and first declared training seed; separate pilot figure clearly labeled exploratory. |
| Verification artifacts | Written methods and source reference, TFM, pp. 13–16; no usable original package received | 34 passing tests; frozen source/config hashes; raw JSON/CSV records; exact replay of 200 episodes; retained policies and scripts. |

Implementation: [runner](../scripts/run_controlled_experiment.py),
[analysis](../scripts/analyze_controlled_experiment.py),
[frozen protocol](../configs/frozen_comparison_v1.json), and
[all scenarios](../configs/controlled_scenarios.json).

## 8. Event Ordering and Artifacts Not to Confuse

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

## Result, Limitations, and Next Decision

The current frozen evidence supports reward replacement within the shared
reimplementation. It does not establish a one line fix to the original TFM,
a reproduced original baseline, or an advantage over the deterministic
reference. Our simpler action interface, altered physical proxies, and selected
PPO settings can affect how easily the objective is learned.

The requested comparison and pinpoint citations are complete. The original
code could resolve the settings marked unknown and the printed inconsistencies.
The next scientific decision is to repeat the reward ablation there or freeze
a new independent study. Keep the six hashed protocol/source files and the
reported trained results unchanged. The paper provides page specific citations
and comparison tables; this companion record supplies the full implementation
inventory without assigning invented settings to the original author.
