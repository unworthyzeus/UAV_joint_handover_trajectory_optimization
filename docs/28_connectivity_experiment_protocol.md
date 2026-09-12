# Strict Connectivity Experiment Protocol

Study: `connectivity_v2`. Development began 12 September 2026. This file becomes
immutable when `configs/frozen_connectivity_v2.json` is created. Development
observations belong in note 29; final results belong in note 30.

## User Requirement and Research Question

The user requested the same communication requirements as the original thesis.
The suggested new 2 s packet deadline and empty queue completion condition were
not accepted and are not used. We retain the original distinction between
constraints and optimized quantities.

The written original TFM requires RSS at least its minimum at every modeled
time and a queue within capacity [TFM, printed p. 11, Eq. (12), C2 and C4]. It
optimizes delay, interference, and handovers [TFM, printed p. 10, Eq. (11)],
using reciprocal learning utilities [TFM, printed p. 12, Eqs. (13)–(14)].
The numeric values used here are RSS minimum −96 dBm, buffer 160 KB interpreted
as 1,280,000 bits, and weights 0.35/0.30/0.35 with beta values 10/100000/100
[TFM, printed p. 15, Table 3]. References identify printed pages; PDF viewer
pages are two greater. See note 25 for the complete original definition index.

The question is whether explicit communication feasibility and restoration of
all three radio objectives can support arrival while improving communication
costs. A visually curved route is not a success criterion.

## Scope and Shared Model

This remains an explicit surrogate, not a reproduction of the unavailable TFM
code. The six frozen v1 files, raw dataset, original trained policies, and
original results are preserved. New code uses separate modules and result paths.

All v2 treatments share the native operator 1 radio map, deterministic half
occupied RBG pattern, downlink cochannel interference proxy, Shannon SINR
capacity proxy, deterministic 200,000 bit/s traffic, and the v1 inertial motion
and energy proxies. The previous assumptions remain limitations, not newly
verified features of the original simulator.

The motion decision interval remains 1 s, acceleration limit 5 m/s², speed limit
25 m/s, deadline 200 s, and energy budget 100,000 J. These are our prior shared
surrogate settings. In particular, they do not recover the TFM's 0.1 s table
step or 100 m/s speed setting [TFM, printed p. 15, Table 3], or resolve the
contradictory 1 ms step in the source prose [TFM, printed p. 14, Sec. 6.1].
The current claim concerns constraints at modeled decision samples; it is not
a mathematical guarantee of radio continuity between samples.

The source's service equations use SNR and contain a dimensionally problematic
printed rate expression [TFM, printed p. 10, Eqs. (7)–(8)]. We retain the declared
v1 SINR capacity replacement to avoid changing propagation and service equations
simultaneously with this repair. Neither our interference nor capacity proxy
is a validated uplink model. Packet latency is not directly simulated.

## Joint Mission Endpoint

Success requires all of the following:

1. Reach within 10 m of the destination and reduce speed to at most 2 m/s by
   200 s. The distance comes from the TFM [printed p. 15, Table 3]; the numeric
   stop speed is our explicit interpretation of stopping at the destination
   [TFM, printed p. 9, Sec. 3.2].
2. Meet serving RSS ≥ −96 dBm at the initial sample and every completed flight
   sample. Equality is valid, following the written C2 inequality [TFM, printed
   p. 11, Eq. (12)]. A single lower sample ends a failed joint mission.
3. Never exceed the queue capacity after the sampled arrival/service update.
   Any overflow ends a failed joint mission. Queue clipping for numerical
   storage cannot erase that violation. The queue discretization remains the
   v1 model; it is not continuous within the 1 s update.
4. Satisfy the shared map, speed, and energy conditions.

Failure takes precedence over arrival when both occur on the same sample.
Arrival with outstanding queued data is allowed, provided no constraint was
violated. The TFM does not define an empty queue arrival requirement. We retain
final queue size as a diagnostic and do not describe arrival as complete data
delivery. Likewise, a short capacity deficit is not itself an RSS outage.

Every treatment uses this same joint endpoint and terminates at successful
arrival or its first violation. Report failure reason counts explicitly.

A shared model based safety filter checks the proposed next sample. It first
tries a feasible station/RBG alternative for the same motion. If none is
available, it uses the one step local motion/network controller below. If the
available alternatives remain infeasible, the step fails normally. This is a
finite candidate filter, not a proof of global reachability. It preserves the
A3 and resource masks, cannot override the RSS or buffer thresholds, and cannot
relabel a violated flight as successful. Network and motion proposal overrides
are counted independently. All final learned and deterministic controllers use
the same filter, which has prospective access to the known map.

## Network Actions and Observations

The source includes BS and RBG choices [TFM, printed p. 12, Sec. 5.2] and an RSS
improvement handover condition [TFM, printed p. 9, Eq. (3)]. V2 exposes 61 network
choices: stay, or five station candidate slots by 12 RBGs. Candidate slots are
the serving station followed by the four strongest RSS stations. Duplicate
serving station slots and occupied RBGs are masked. Repeating the serving
station's current RBG remains legal, as does the explicit stay action; this
allows a stable resource selection without an artificial alternating mask.
A new station requires current
RSS more than 3 dB above the serving RSS and at least −96 dBm. These numerical
thresholds follow the source [TFM, printed p. 15, Table 3].

RBG reassignment within the serving station is allowed and separately counted.
It is not charged as a handover. Resource changes have no switching interruption
model or additional cost; this is an explicit limitation. Handover traffic is
4,800 bits as in v1 and the source table [TFM, printed p. 15, Table 3].
Network decisions occur every 1 s instead of v1's 5 s interval. All new arms
share this change. The source describes decisions per environment step but does
not establish v1's five second interval [TFM, printed pp. 9, 12, Secs. 3.3.1, 5.2].

The 156 dimensional learned observation retains destination, position, velocity, elapsed time,
energy, queue, serving SINR, candidate RSS/positions/IDs and action masks. It
adds each network option's current modeled capacity relative to offered traffic.
Resource phase and current group remain observable. The network head has 61
outputs. The continuous head produces two bounded residuals in the radial and
lateral acceleration frame. First project the deterministic braking controller's
command to the unit disk, add `0.5 * tanh(latent)` componentwise, then apply the
shared acceleration projection. This controller prior is new; both learned
arms use it. It is not a policy trained from scratch to discover basic flight.
PPO optimizes likelihoods of the residual proposals; the physical projection
and safety filter are deterministic parts of the environment action decoder.

## Reward Comparison

Both learned treatments use the same hard joint failure and terminal arrival
rules, potential, time cost, PPO implementation, observation and action spaces.

```text
Phi = -(distance + speed² / (2 * acceleration_limit)) / 100
shaping = gamma * Phi(next) - Phi(now), with terminal Phi = 0
base reward = shaping - 0.05 + 20 * joint_success - 20 * terminal_failure

C = 0.35 * (10 D)/(1 + 10 D)
  + 0.30 * (100000 I)/(1 + 100000 I)
  + 0.35 * (100 H)/(1 + 100 H)

arrival arm: base reward
full arm:    base reward - C
```

D is the sampled backlog/service delay proxy in seconds, I the downlink
interference proxy in watts, and H the current handover indicator. The transform
is one minus each original reciprocal utility [TFM, printed p. 12, Eq. (13)],
using the equal weight configuration [TFM, printed p. 15, Table 3]. Subtracting
cost removes the original positive reward for remaining alive. It does not
remove communication objectives. Delay no longer has v1's flat penalty above
one second, and interference again directly affects the learning objective.
The delay proxy is still numerically censored at 200 s as in v1.

The new arrival arm is an explicitly radio unweighted ablation with hard
constraints. It is not the v1 reward only checkpoint and not the original TFM
reward. Comparing the two new arms isolates inclusion of the radio cost under
the shared v2 interface. It does not isolate every change from v1 or the thesis.

## References

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
All controller details and candidate motions are versioned in the new source.

## Separation, Budget, and Reporting

New routes are generated independently: 4,096 training routes (seed 52010,
lengths uniformly sampled from 200 to 1800 m),
64 validation routes (52001), 32 longer validation routes (52002), 200 standard
test routes (52012), and 200 longer test routes (52013). The generated pairs are
checked for exact duplicates within v2 and against all v1 route pools. All
still use the same geographic radio map. There is no independent city holdout.
Both standard and longer final route lengths lie inside the final training
range. The longer set is no longer an extrapolation test. Earlier development
pilots used seed 52000 and 200–1000 m training routes; their source/configuration
snapshots preserve that retired design.

Development uses only training and validation. The final source and protocol
hashes, PPO budget, and training seeds must be frozen before test evaluation.
The final training seeds are 2101–2105, each with 524,288 interactions per arm.
There are ten final policies and 5,242,880 final training interactions. PPO
otherwise retains v1's 64 lanes, 128 step rollouts, two 64 unit tanh layers,
four epochs, 512 sample minibatches, learning rate 0.0003, gamma 0.99, GAE 0.95,
clip 0.2, entropy 0.005, value weight 0.5, gradient norm limit 0.5, running return
variance normalization, and normalized reward clipping to [−10, 10]. No KL
early stopping rule is used. Five seeds are training replicates, not traffic
or geographic replicates.

Final checkpoint evaluation uses deterministic actions. Do not select a new
checkpoint or change a controller using final tests.

Record every seed's joint success and failure counts. Report secondary costs
conditional on joint success, and compare controllers' communication costs on
the intersection of successful route pairs. State intersection counts. Show
both accumulated and per sample communication cost so that a slow mission
cannot appear better solely through an average. Preserve time, path, energy,
handover and resource change counts, delay, interference, SINR, and final queue.

The primary learned comparison is full minus arrival joint success, paired by
training seed and route. A communication benefit requires reporting any
completion tradeoff alongside paired communication cost changes. Five training
seeds are used, each with the same final interaction budget. Report variation
and paired crossed bootstrap intervals; do not treat repeated routes as
independent training runs. The deterministic references are not five seed runs.
Use 5,000 crossed bootstrap draws with analysis seed 62000. For deterministic
comparisons, resample routes only. Paired secondary estimates are descriptive
on jointly successful routes and do not describe the excluded failures.

A strong positive claim for including the full radio cost requires a positive
lower confidence limit for joint completion improvement and a negative upper
confidence limit for accumulated radio cost change on paired successful routes.
If that combined evidence is absent, report the components and tradeoffs
without claiming an overall superior learned controller. This claim rule is
not an application constraint or a definition imported from the TFM.

## Verification, Risks, and Next Decision

Before final training, test RSS equality and first violation failure, initial
RSS, buffer overflow precedence, allowed nonempty arrival queues, all three
cost terms, resource masks, network power arithmetic, motion prediction, and
shared transitions across reward arms. Preserve executable tests and replayable
checkpoints. Verify v1 frozen hashes throughout.

The intended repair is a faithful sampled communication feasibility definition
and restored objectives within the surrogate. It does not establish continuous
real flight connectivity, obstacle safety, calibrated interference, superiority
to the unavailable original controller, or novelty of PPO. If learned joint
performance is insufficient, retain that result instead of relaxing the thesis
requirements. The next decision then concerns policy design or a separate
physical model study, not redefining success after seeing test outcomes.
