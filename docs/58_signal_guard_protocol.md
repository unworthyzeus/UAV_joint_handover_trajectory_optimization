# V2.3 Signal Aware Path Selection Protocol

Date: 14 September 2026. Declared before development evaluations.

## Objective and Unchanged Requirements

Test stronger SNR than V2.2 while preserving mission completion and service.
This is a new controller study on the same unchanged Barcelona dataset, not
a correction to source thesis SNR, new PPO training or a reward experiment.
Reuse the five full V2 checkpoints and all V2 dynamics, network masks, A3
handover rules, traffic, buffer, energy and executed safety filter.

The source RSS and buffer requirements remain unchanged [TFM, printed
pp. 11–12, Secs. 5.1–5.2; p. 15, Table 3]. No extra packet deadline, empty
queue arrival rule, or relaxation of sampled connectivity is introduced.
All five previous source freezes, datasets, weights and records are immutable.

## Fixed Candidate Family

V2.2 already selects the strongest feasible connection but ranks motion
rollouts primarily by goal progress. Retain its ten first motion candidates,
five step horizon, following goal/braking policy and network selection.
Measure the predicted mean SNR, queue delay and handover count of each
rollout, counting only active executed steps. Reproduce V2.2's original
winning motion first; this is the baseline action for the current state.

Outside 50 m of the goal, a replacement must:

1. Have an original V2.2 rollout score at most a fixed allowance above the
   original winning score. Test exactly 1, 3 and 6 m allowances. These are
   allowances in predicted terminal goal distance within the same failure,
   arrival and progress class, not total mission detour limits.
2. Predict no failure, with mean delay and handover count no higher than
   those of the original winning rollout.
3. Have strictly higher predicted mean SNR. Select the highest mean SNR,
   breaking ties by the original rollout score and then primitive order.

At or within 50 m, retain the original action to preserve its braking
behavior. If the baseline predicts failure, retain it; this study does not
claim an improved emergency recovery. Failed or already completed lanes
must not affect another lane. The original score's large penalties exceed
all three allowances, so no favorable SNR can buy a worse safety class.
The executed safety filter remains unchanged. Finite lookahead cannot
guarantee future connectivity or complete mission performance.

## Development and Selection

Generate 128 standard routes with seed 56001 and 64 longer routes with seed
56002. Check exact start/goal pair disjointness from every earlier saved
scenario manifest. Use fixed policy seeds 2101 and 2102 for every candidate
and unmodified V2.2. Retain all 1,536 episodes and sample arrays, irrespective
of whether a candidate succeeds. These routes are development data only.

For each split, a candidate is eligible if its completion count is at least
V2.2's, its common success mean SNR increases, its matched mean delay and
handovers do not increase, and its matched time and energy increases do not
exceed 2%. Require at least a 0.1 dB SNR gain in the standard split. Rank
eligible candidates by total completion, then the smaller of their two SNR
gains, then lower delay, then smaller allowance. These are engineering
selection rules, not statistical evidence. If none qualify, report the
failed development attempt and keep V2.2; do not open the final test or
change this family after seeing results.

## Freeze and Independent Final Evaluation

Only after selection, freeze the controller, evaluator, analysis, protocol,
tests, selection record, dependencies and checkpoint hashes. Then generate
500 standard and 500 longer routes with seeds 56012 and 56013, checking
disjointness from development and all previous manifests. Evaluate V2.2
and the selected candidate on both splits with seeds 2101–2105, totaling
10,000 episodes. Use identical routes, initial conditions and inference
batch size for the paired arms. Retain every failure and exactly replay
every final record and sample array. No final test tuning is permitted.

Mission completion remains the first gate. For a signal improvement claim,
require in both splits a nonnegative completion point difference and a
95% interval lower bound above −1 percentage point. This is a newly declared
uncertainty margin for this study, not a thesis requirement or proof of
equal completion. An actual completion improvement claim requires its
lower bound above zero.

Next require a nonpositive matched delay point difference and its 95%
upper bound below 0.05 s, and nonpositive handover difference with upper
bound below 0.25 switches per flight. Require the upper interval for
relative mean time and energy increases below 2%. These practical margins
are declared here, not attributed to the source thesis. They do not relax
the environment's success requirements or permit hiding a negative point
estimate through favorable wording.

Subject to these gates, the primary signal contrast is candidate minus
V2.2 mean flight SNR on standard common successful pairs; require its 95%
lower bound above 0.1 dB and a positive lower bound in longer routes.
Use 5,000 crossed seed/route bootstrap draws, seed 66000. Publish individual
gate results even when the combined gate fails. Requiring all gates is
an intersection claim; other metric intervals are descriptive and unadjusted.

## Reporting, Limits and Next Decision

Report completion, every failure reason, common success time, energy, delay,
SNR, SINR, both interference quantities and handovers. Give the direction
and same units within each row. Include sample CDF medians with aggregation
explicit, runtime and all policy seeds. Mark timing as a workstation batch
measurement, not onboard latency. Do not compare conditional source SNR
estimates as if they were matched observations.

Update the README, a complete results note and the single IEEE paper with
the outcome, including negative results. New code is separately versioned
and must not change any old frozen study. The next decision is the declared
development gate. One map, static traffic, five reused policies, finite
planning and sampled connectivity still limit generalization.
