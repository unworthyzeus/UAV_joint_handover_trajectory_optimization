# Controlled Reward Experiment Protocol

Date: 12 September 2026. Written before policy training and test evaluation.

## Purpose and Claim Boundary

Test whether the written binary approach reward and continuing arrival design
impair mission completion on the received Barcelona radio map. The original
repository remains unavailable (HTTP 404 checked on this date). This is an
explicit reimplementation with shared corrections, not a reproduction of the
thesis's trained policy, code, or reported metrics. Positive results support a
formulation diagnosis in this benchmark; they do not prove the original cause.

## What Will Be Done and Why

1. Validate radio lookup, dynamics, arrival, constraints, reward, and PPO updates.
2. Establish that a deterministic stopping controller completes the routes.
3. Pilot the training implementation on a validation set. Preserve all pilots.
4. Freeze a configuration and train five independent seeds for each treatment.
5. Evaluate the frozen final checkpoints on held out routes. No test tuning.
6. Report seed variation, paired differences, failures, and success conditional
   secondary metrics. Produce an IEEE format research draft if results support
   a positive, appropriately limited conclusion.

## Shared Environment

Use the received `Barcelona_dataset_January.h5`, SHA256
`d4630dd3a6c45419e12d0b60dd08473c4ffa4062ca4fab1decabecf2b992ea0d`.
Operator 1 has 87 stations. Lookups use nearest neighbors on the native stored
coordinate vectors; no interpolation invents powers across absent paths.
The -128 floor is treated as zero received power. This convention must still
be confirmed with the dataset creator.

All treatments receive the same observed position, goal bearing and distance,
radial and lateral velocity, speed, time, energy, buffer, prior success flag,
resource and load phase, serving SINR, outage counter, and candidate radio
measurements, positions, identities, and validity masks. Thus observation
repair is deliberately held fixed, not credited to a reward effect.

Continuous radial and lateral acceleration commands control inertial 2D
double integrator dynamics at constant 100 m altitude. Acceleration norm is
limited to 5 m/s² and speed to 25 m/s. The step is 1 s and the deadline 200 s.
This intentionally resolves the thesis's timing ambiguity and replaces its
discretized direction controls; these choices are common to every treatment.
Success requires distance at most 10 m and speed at most 2 m/s. A map boundary
crossing, battery exhaustion, or five consecutive RSS outage steps ends failure.
No obstacle collision claim is made without the original building scene.

A separate categorical policy selects stay or one of the four strongest
stations. Requests are masked to those above -96 dBm and more than 3 dB better
than the serving station, every five seconds or immediately when an RSS outage
is observed. No time to trigger timer is
claimed. Resource allocation uses a common first available rule across twelve
groups. Background occupancy is a reproducible, observable phase pattern with
six occupied groups per station, fixed within each episode. Resource choice
is not learned in this experiment.

The source describes its map as a downlink link budget. Accordingly, sum
cochannel background station powers in watts and compute a downlink SINR proxy.
Use 1.44 MHz times log2(1 + linear SINR) for an ideal rate. This is not actual
uplink interference or calibrated achievable throughput. Noise is -103.41 dBm
including the noise figure. Deterministic offered traffic is 200 kbit/s, buffer
capacity 1.28 Mbit, and each handover adds 4800 bits. Report residual buffer/rate
as a queueing delay proxy censored at the 200 s deadline when service is absent
or very low. The energy proxy integrates 100 + 0.4 speed² watts
against a 100 kJ battery. These are declared common simplifications, not
recovered original simulator parameters.

## Factorial Treatments

| Arm | Reward | End training episode on safe arrival |
| --- | --- | --- |
| legacy | Written reciprocal radio terms and +12 binary approach bonus | No |
| terminal_only | Same legacy reward | Yes |
| reward_only | Mission reward and potential shaping | No |
| fixed | Mission reward and potential shaping | Yes |

The legacy reward follows thesis Equations 13 and 14 with physically corrected
radio inputs in the shared environment. Its interference input is watts.
Safety constraints are common environment rules, so this is a reward ablation,
not an exact legacy simulator emulation.

The mission reward is a first safe arrival bonus of 20, terminal failure
penalty of 20, per step cost 0.05, and 0.05 times the sum of bounded delay,
RSS outage, and handover costs. Shaping is gamma Phi(next) - Phi(current), with
gamma 0.99 and Phi = -(distance + speed² / (2 a_max)) / 100. Set Phi to zero
at all episode terminals, including the deadline. Time and the prior success
flag are observable. Success is rewarded only once in a continuing episode.
The potential's speed component provides braking information without changing
the discounted base objective when terminal handling is correct.

The common evaluation stops at first safe arrival for every policy, regardless
of its training termination rule. Metrics therefore refer to the same completed
mission definition. Training returns across different rewards are not ranked.

## Splits and Statistics

Generate 4096 training routes with seed 42000, validation routes with seed
42001, final test routes with seed 42012, and longer final test routes with seed
42013. Initial feasibility checks used 42002 and 42003; those exploratory
route sets were retired before any policy training and will not be final tests.
Routes are new coordinate pairs in the same city, not independent cities or
geographic holdouts. Standard lengths are 200 to 1000 m; longer routes are
1000 to 1800 m. Exclude starts or destinations outside the declared margins.
Background phases are part of each saved scenario. Each training lane follows
the same ordered route stream in every treatment; arrival termination can
change how many episodes fit within an equal interaction budget.

Pilot seeds are separate from final seeds 1101 to 1105. Set the final training
budget using validation behavior and runtime, then freeze it before opening
test results. Use final checkpoints rather than selecting on test outcomes.
Show every training seed. Paired confidence intervals must account for shared
routes and seed clusters; five seeds limit statistical resolution.

## Results, Remaining Work, and Risks

At protocol creation, no policies have been trained. Implementation validation,
pilot selection, frozen comparisons, and analysis remain to be performed.
Main risks are simulator reconstruction error, sensor and action changes shared
by all arms, reward scale sensitivity, limited seeds, and single city scope.
The next decision is whether implementation tests and the deterministic
controller establish a valid experiment before PPO training begins.
