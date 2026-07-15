# Optimization Objective

## Mission Definition

For start position `p0`, goal `g`, deadline `Tmax`, goal tolerance `delta`, and stop speed `vstop`, success is:

```text
success = distance(pT, g) <= delta
          and speed(T) <= vstop
          and T <= Tmax
```

Arrival terminates the episode. Timeout, energy exhaustion, an unrecoverable map violation, or an unrecoverable safety violation ends the episode as failure.

## Optimization Hierarchy

The preferred formulation is a constrained MDP or a lexicographic objective.

```text
Primary:
    maximize P(success)

Constraints:
    speed <= speed_limit
    energy >= reserve
    buffer <= capacity
    outage_fraction <= outage_limit
    map and obstacle constraints satisfied

Secondary vector among successful feasible missions:
    minimize [arrival_time,
              propulsion_energy,
              transmission_delay,
              packet_loss,
              uplink_interference,
              handovers,
              ping_pong_handovers]
    maximize [mean_SINR, fifth_percentile_SINR]
```

A weighted sum may be used inside an algorithm, but it must not replace separate reporting of each component or the mission constraints.

## State

The proposed observation includes:

1. Position and velocity in a common coordinate frame.
2. Heading and, if required by the dynamics, acceleration.
3. Goal relative displacement, distance, and bearing.
4. Remaining time, energy, and buffer occupancy.
5. Serving base station, serving SINR, current resource group, and time since last handover.
6. Features and validity masks for the top `K` candidate base stations.
7. Observable resource occupancy or an uncertainty representation when occupancy is hidden.
8. A local obstacle or channel context window if the policy cannot infer it from position.

## Action

The action is mixed rather than fully discretized:

```text
continuous flight action = [longitudinal acceleration, heading]
discrete network action = [stay or candidate handover, optional valid RBG]
```

Network actions can be evaluated less frequently than flight control. Candidate and resource masks remove physically impossible or protocol invalid choices.

The initial executable interface uses absolute heading because it matches the
direction variable documented in the thesis. A bounded turn rate can replace
it once the recovered simulator establishes the exact vehicle dynamics and
control interval.

The current typed action utility still exposes all 87 base station indices and
12 resource group indices without masks. It exists to audit the legacy action
cardinality. The candidate mapping, stay action, and validity masks are the
target interface and require the missing channel and resource adapter.

## Reward Used for Learning

The learning signal should contain:

1. A decisive terminal success reward.
2. A decisive failure or timeout penalty.
3. A small time cost.
4. Distance progress proportional to actual progress, not a Boolean closer indicator.
5. Normalized energy, outage, delay, interference, and handover costs.
6. Optional smooth control and terminal braking costs.

Potential based shaping should use the same discount factor as the learner if policy invariance is required. The executable first audit uses a transparent distance delta and labels it as an engineering diagnostic.

## Why This Solves the Identified Failure

Success termination removes the opportunity to collect continuing reward after arrival. A time cost makes needless wandering expensive. Goal and velocity observations make route following and braking learnable. Constraints prevent connectivity and safety from being traded away silently. Separate continuous and discrete actions reduce the combinatorial burden.
