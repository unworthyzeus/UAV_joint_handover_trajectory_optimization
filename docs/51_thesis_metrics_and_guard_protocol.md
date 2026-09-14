# Thesis Metric Recovery and V2.2 Guard Protocol

Date: 14 September 2026. Declared before development runs.

## Objective

The user requested the metrics reported by the thesis but missing from our
tables, together with an attempt to improve them. Mission completion remains
first, followed by communication service. Existing experiments are immutable.
This study adds measurement and tests an explicit controller change; it does
not rename downlink interference as physical uplink interference.

## Recoverable Metrics and Source Limits

Use the same unchanged Barcelona dataset and the frozen V2 physical system.
At every executed step, record serving RSS, SNR, all neighboring RSS powers,
cochannel interference, energy and handovers. Initial observations are kept
in illustrative traces but excluded from per step metric averages and CDFs.
Failed missions remain in completion and failure denominators; compare
service on common successful route/seed pairs. Also show all flight outage
distributions so the zero outage success condition is not mistaken for an
independent reliability result.

- **SNR, dB:** implement source Eq. (8), `RSS - (-112.41) - 9`
  [printed p. 10; Table 3, p. 15]. Report per flight means and pooled executed
  sample CDFs, retaining the definition of each. Source CDF aggregation is
  unspecified. Verify the possible SNR range against the map; do not claim
  that a discrepancy with the source figure is a model improvement.
- **All neighbor RSS power, µW:** sum received powers from every other
  Operator 1 base station, excluding the serving station, after conversion
  to linear power. This is an explicit linear power interpretation of
  Eq. (9) [printed p. 10]. It is not restricted to occupied cochannel groups.
  The thesis labels Eq. (9) uplink, but its inputs are downlink RSS maps and
  it provides no UAV uplink power, reciprocity calibration or power control.
  Label this a source equation proxy, not measured or calibrated uplink.
  Keep our cochannel downlink metric separate. Record literal sums of dBm
  as a diagnostic of the alternative arithmetic, not as valid received power.
- **Remaining energy, kJ:** report `100 - consumed_energy_j / 1000`
  under the unchanged V2 proxy. Higher is better on common successful flights.
  Source Eq. (10) has a plus electronics term and no timestep, while capacity
  is labeled kW [printed pp. 10, 15]. Record its literal recurrence from
  1000, `E_next = E - 3*v/(370*.55*5) + .1`, once per executed V2 step as
  an explicitly unitless arithmetic diagnostic. Never call this kJ, battery
  energy or a reproduced source result. Under the V2 speed cap it increases
  even during flight, so it cannot validate physical efficiency.
- **Handovers:** publish executed counts per flight and their empirical CDF,
  plus switches per second with the denominator explicit. Do not guess the
  source's unexplained `1e-2` normalization [printed pp. 18, 20, Figs. 6, 8].
- **Outage, seconds:** retain sampled duration, all failure types and both
  successful and all flight summaries. Termination at the first violation
  differs from the source and limits direct comparison of outage totals.

The source Fig. 6/8 readings remain approximate, with their original labels.
Computing matching formulas does not recover original trajectories, timing,
aggregation, implementation or simulator code.

## Improvement Hypothesis and Fixed Candidates

The prior service reward lowered delay but increased RSS failures. Test a
different intervention: a model based supervisor around the existing full
V2 PPO policy. Reuse all five unchanged full V2 weights; do not call this new
PPO training or an isolated reward change.

For each decision, consider the PPO motion proposal and the nine existing
motion primitives used by the joint search reference. Simulate each primitive
followed by the shared goal/braking command over a finite horizon. At each
simulated step, choose a currently admissible network option that preserves
RSS and buffer feasibility, then prioritizes serving RSS, with capacity as
a small tie breaker. The A3 rule, candidate set, masks and shared filter
remain enforced. This targets stronger SNR and lower all neighbor RSS power
without replacing the transition or mission requirements.

Rank motion rollouts by avoiding failure first, reaching the goal next, then
remaining goal distance. Penalize a nonprogressing first move outside 30 m
to avoid the existing stationary trap. When every rollout fails, prefer
later failure rather than interpreting it as safe. This is finite lookahead,
not a global connectivity guarantee. No physical interpolation guarantee,
new deadline, traffic contract or empty queue arrival condition is added.

Declare exactly three candidates: guard horizons 3, 5 and 8 executed steps.
Use full V2 seed 2101 and the existing 64 standard and 32 longer validation
routes for development. Also evaluate unmodified full V2 and Goal radio as
references. Do not use any previous test route for controller selection.
Keep every development outcome and controller configuration.

## Selection and Fresh Evaluation

A guard may advance only if its total validation completion is at least
that of full V2 and its matched mean delay is no higher in either split.
Rank eligible candidates by total completion, then lower matched delay,
then fewer handovers, then shorter horizon. A small validation gain is not
final evidence of improvement. If no candidate qualifies, retain the failed
attempt and still publish the new metrics for fixed existing controllers.

After selection, freeze source, protocol, candidate and all reused weight
hashes. Generate 500 fresh standard and 500 fresh longer routes with seeds
55012 and 55013; verify disjointness from all prior saved route pairs.
The fresh route set is generated only after the selection record exists.
Evaluate unchanged V1.5, full V2 and V2.1 service across seeds 2101-2105,
the selected guard using the five full V2 policies if eligible, and Goal
radio, joint one step and joint three step references. All get identical
routes and traffic phases. No tuning follows these tests.

Primary contrast: guarded full V2 minus unmodified full V2 standard mission
success. Use 5,000 crossed seed/route bootstrap draws with seed 65000.
A positive claim requires the lower 95% bound above zero. Separately report
longer success and all common success service differences, including newly
recovered metrics, with descriptive, unadjusted intervals. Any claim against
V1.5 requires its own matched comparison. No direct numerical superiority
over the unavailable original agent is established by beating V1.5.

## Verification and Next Decision

Test metric formulas, station exclusion, linear conversion, monotonic
energy diagnostic, one record per executed step, admissible actions and
state preservation during planning. Exact replay must recover every final
episode and added metric. Preserve all four historical freezes and weights.
Record runtime and every selected horizon. Publish source/configuration,
metrics, CDFs, outcomes and reproduction commands in the repository and
integrate the findings into the single paper, including negative results.

The next decision is the validation gate, followed by the frozen fresh
evaluation. Source arithmetic ambiguities, one city, five reused policy
seeds, static traffic, ideal switching and sampled connectivity limit claims.
