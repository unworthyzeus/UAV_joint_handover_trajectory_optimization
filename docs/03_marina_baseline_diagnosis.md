# Marina Baseline Diagnosis

## Sources Reviewed

1. [Official UPCommons record](https://upcommons.upc.edu/entities/publication/a8ce08c2-c238-4145-a5ab-5d39b12c6553).
2. [Full thesis PDF](https://upcommons.upc.edu/server/api/core/bitstreams/f92e8ad3-4ad0-4410-971c-e842a2f55477/content).
3. Local thesis copy under `sources/`.
4. The code URL printed in the thesis, which currently returns 404.

## What the Baseline Did Well

The thesis created a 5,000 by 3,500 meter Barcelona environment with deterministic ray tracing, real base station locations, 3GPP A3 handover logic, resource block allocation, packet buffering, energy accounting, a greedy reference, and PPO. This is substantially more realistic than an abstract grid world.

## Confirmed Formulation

The listed state on thesis page 12 is:

```text
[x, y, serving base station, allocated RBG, energy, buffer]
```

The listed action is:

```text
[acceleration, direction, requested base station, requested RBG]
```

Acceleration used 5 bins, direction used 8 bins, the tested operator had 87 base stations, and each base station had 12 resource groups. The nominal joint product is 41,760 combinations. A factorized `MultiDiscrete` policy need not enumerate all combinations, but it must still learn strongly coupled decisions across four branches.

The reward on thesis pages 12 and 13 transformed delay, interference, and handover costs into positive rewards, applied several penalties, and added 12 points whenever distance decreased. The thesis explicitly states that arrival did not terminate the episode.

The evaluation on thesis pages 16 through 20 reported SNR, outage, interference, remaining energy, and handover count, but not mission success rate, arrival time, or terminal distance.

## The Big Problem

The objective did not make task completion decisive.

The controller could collect positive radio reward for remaining active. It received a large one sided bonus for every approach step, no equal cost for moving away, no terminal success reward, and no success termination. Repeated approach and retreat can therefore generate more reward than arriving and stopping. The thesis figures show long detours, overshoot, correction, and wandering. Its conclusion states that persistent connectivity was prioritized over task completion.

This is reward and MDP misalignment, not proof that PPO is intrinsically unsuitable.

The executable counterexample in `docs/11_initial_reward_diagnostic.md` holds
radio inputs constant. Its handcrafted never arrive trace obtains a discounted
return of 79.65, compared with 69.95 for direct arrival under the legacy reward.
This proves that the stated incentive can rank noncompletion above completion,
but it is not a trained policy comparison.

## Additional State and Action Problems

1. Velocity is absent even though acceleration and braking depend on it. The listed state is therefore not Markov for the movement dynamics.
2. Goal relative position is absent, which prevents a clean goal conditioned policy across route pairs.
3. Candidate base station measurements and RBG availability are absent even though the action chooses them.
4. Continuous motion was coarsened into bins and coupled to telecom decisions at every step.
5. The state does not expose remaining time, terminal speed error, or recent handover history.

## High Risk Formula Checks

These may be notation errors, code errors, or both. They must be resolved against the original implementation before reproducing metrics.

1. The written rate equation adds bandwidth to `log2(SNR)` instead of using bandwidth times `log2(1 + SNR_linear)`.
2. The written interference equation sums RSS values directly even though powers in dBm must be converted to linear units first.
3. The reported SNR excludes interference although the proposal now targets SINR.
4. Energy capacity and remaining energy are labeled in kW, which is a power unit.
5. The prose gives a 1 ms step while the parameter table gives 0.1 s.
6. The specialized reward weight rows sum to 1.2 although the formulation requires a sum of 1.
7. The formal constraints do not include terminal arrival despite stating that the goal must be reached.

## Audit Conclusion

The simulator is the main inherited contribution. The learning objective, observability, mixed action representation, termination, and evaluation hierarchy require redesign before longer training is meaningful.
