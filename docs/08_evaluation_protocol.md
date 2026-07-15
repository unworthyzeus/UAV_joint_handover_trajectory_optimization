# Evaluation Protocol

## Primary Outcomes

Report these first:

1. Mission success rate.
2. Constraint feasible success rate.
3. Final distance to goal for failures.
4. Terminal speed for arrivals.
5. Timeout, energy, connectivity, map, and safety failure counts.

## Navigation Metrics

Report among successful missions and also provide the sample count:

1. Arrival time.
2. Path length.
3. Path efficiency, defined as straight line distance divided by traveled distance.
4. Propulsion energy in joules or watt hours.
5. Minimum energy reserve.

## Telecom Metrics

1. Mean, median, and fifth percentile SINR.
2. Outage time and outage fraction.
3. Mean and tail transmission delay.
4. Packet loss or overflow count.
5. Uplink interference in a physically valid linear or logarithmic unit.
6. Handover count.
7. Ping pong handover count and rate.

## Learning Metrics

1. Environment interactions to a fixed success threshold.
2. Wall time and hardware.
3. Return components, not only total return.
4. Policy entropy, value error, and constraint multiplier behavior.
5. Variation across training seeds.

## Controlled Comparison

Every method receives the same:

1. Start and goal pairs.
2. Deadline and terminal tolerances.
3. Deterministic channel map.
4. Resource occupancy and traffic seeds.
5. Initial energy, buffer, serving cell, and velocity.

Use paired scenario differences and bootstrap confidence intervals. Do not tune on test route pairs. Show empirical distributions or confidence intervals rather than only one trajectory.

## Ranking Rule

1. Discard or separately classify policies that violate mandatory constraints.
2. Compare success rate.
3. Compare secondary metrics conditional on success.
4. Use Pareto dominance or clearly declared preferences for remaining tradeoffs.

This prevents a controller with good SINR but failed missions from being ranked above a successful controller.

## Current Utility Limit

The initial evaluator labels a result `recorded_feasible_success` only when an
arrival has no recorded boundary, minimum RSS, or speed violation. It does not
yet claim full constraint feasibility because the missing environment adapter
must still provide battery reserve, buffer, obstacle, and episode outage limit
checks. Infeasible arrivals and mission failures remain separate outcome
classes. Secondary metrics are not collapsed across unlike units.
