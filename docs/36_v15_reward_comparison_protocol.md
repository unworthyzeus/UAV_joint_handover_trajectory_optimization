# V1.5 Original Reward Versus V2: Frozen Comparison Protocol

Date: 13 September 2026. Written before new training and test evaluation.

## Question and Scope

Does replacing the written thesis reward improve strict joint mission success
when every other component is the final V2 system? V1.5 denotes the original
reward on V2, not the historical V1 environment. The name describes a controlled
intervention created after V2, not a chronological intermediate release.
We do not label the original reward inferior before observing the result.

Historical V1 repaired arrival in a more permissive communication task and
removed direct interference cost. It motivates this comparison but is not its
baseline. The new comparison changes the full reward package; it does not
identify the individual effect of potential shaping, terminal payments or
removal of a positive per step utility. The original simulator is unavailable.

## Arms and Source Definition

Primary comparison: V2 `full` minus V1.5 `original`.
V2 `arrival` and all four existing deterministic references are contextual
controls. All policies use the same strict sampled success criterion.

For V1.5, reconstruct the equal policy in TFM printed p. 12, Eqs. (13)-(14),
and p. 15, Table 3:

```text
r_original = 0.35/(1 + 10 D) + 0.30/(1 + 100000 I) + 0.35/(1 + 100 h)
             + 12 * 1[d_after < d_before]
             - 10 * 1[outside map] - 10 * 1[RSS <= -96 dBm]
             - 10 * 1[speed >= 100 m/s]
```

Energy exhaustion overrides the entire reward with -10 [TFM, printed p. 12,
Sec. 5.2; p. 15, Table 3]. Delay D is the shared V2 postservice queue/rate
proxy in seconds, I is shared downlink interference in watts, and h denotes
an executed handover. These inputs are V2 model choices, not recovered original
simulation values. Use executed postfilter actions. Boundary violations are
identified before clipping by the unchanged V2 transition.

Preserve the written reward's RSS `<=` inequality, even though V2's joint
constraint permits equality at -96 dBm [TFM, printed p. 11, Eq. (12), C2].
Preserve the source reward speed threshold of 100 m/s; it cannot activate under
V2's hard 25 m/s cap. Substituting 25 m/s would introduce a new reward penalty
on routine cruising. No extra overflow, timeout or arrival term is added to
V1.5. The removed historical energy utility and data dump penalty are not
restored [TFM, printed pp. 20-21, Sec. 7.3]. PDF viewer pages equal printed
pages plus two; see note 25 for the complete verified source index.

V2 `full` retains its frozen potential difference, -0.05 time cost, negative
weighted radio cost, +20 joint success and -20 terminal failure. V2 `arrival`
omits only the direct radio cost. Reward normalization and clipping are shared;
the intervention therefore includes their response to changed raw rewards.

## What Remains Exactly V2

The unchanged V2 environment supplies motion, queues, energy, radio inputs,
156 observations, 61 masked network choices, initial states, resets, residual
motion decoding, reference braking and the prospective safety filter. Arrival
and every failure terminate both training and evaluation in every arm. The
source's continued training after arrival is deliberately not restored: the
user requested the original reward with all other components kept at V2.

The wrapper calls V2's transition once, replacing only the returned reward
and accumulated raw return. Full and arrival delegate unchanged. The PPO module
is an exact source copy with only its environment import and module description
changed; a structural test checks equality of all other Python syntax.

PPO uses all frozen V2 settings, including 64 environments, 128 step rollouts,
four epochs, batches of 512, two 64 unit hidden layers, learning rate 0.0003,
discount 0.99, GAE 0.95, clipping 0.2, entropy 0.005, value weight 0.5,
gradient norm 0.5, two CPU threads and 524,288 interactions per seed.
Seeds 2101-2105 pair policy initialization and training route schedules.
Different learned trajectories cause different episode exposure; an equal
interaction budget does not imply identical realized transitions.

## Training, Validation and New Tests

Reuse the exact 4,096 V2 training routes and development pools of 64 standard
and 32 longer routes. Train five new original reward policies from scratch;
new training totals 2,621,440 interactions. No hyperparameter search, pilot
selection or test driven changes are planned. Use final budget checkpoints.

Reuse all ten already completed V2 checkpoints, fixed by SHA256 in the new
freeze before training or new test evaluation. They used the identical training
data, initialization seeds and budget. This avoids unnecessary retraining and
does not select the best seed. Their past V2 test results are known; the new
comparison is prospective relative to the new test routes, not preregistered
before the earlier V2 study or independently registered with a third party.

Generate 200 fresh standard routes of 200-1000 m using seed 53012 and 200
fresh longer routes of 1000-1800 m using seed 53013. Check exact route pair
disjointness against every historical V1 and V2 split. Store routes before
testing and use the same routes and load phases for every controller.
Both distance ranges occur in V2 training; this is route holdout on one map,
not geographic holdout or distance extrapolation. The map is unchanged.

Evaluate original, full and arrival for five seeds on both test splits, plus
four deterministic controllers on both splits: 7,600 final episodes in total.
Keep these records separate from the previous 5,600 V2 test evaluations.

## Outcomes and Analysis Fixed Before Testing

Primary outcome: standard route strict joint success difference, full minus
original, in percentage points. A positive difference with a 95% crossed seed
and route bootstrap interval entirely above zero supports improved completion
under this design. Longer route completion is a prespecified secondary outcome.
Use 5,000 bootstrap draws and seed 63000. Report all five seed rates, all first
failure reasons and intervals whether favorable, null or negative. Five seeds
and 200 shared routes are not 1,000 independent training replications.

Report time, path, energy, delay, interference, SINR, handovers, radio cost and
filter interventions conditional on success. For a contrast, use only the
matched seed/route pairs on which both arms succeed, with their count visible.
Also show the unconditional success difference and failure counts. A lower
aggregate radio cost does not establish better delay or better completion.
No percentage change is computed for logarithmic SINR in dB. Secondary intervals
are descriptive and unadjusted for multiple comparisons. No joint superiority
claim is made from a favorable subset of secondary metrics.

Archive raw episode records, checkpoint hashes, logs, configuration, all source
hashes and a fresh exact replay of every new final evaluation. Preserve both
old freezes and their results. Public weights cover the five new V1.5 and ten
final V2 policies, not historical V1 or development checkpoints; the private
dataset remains excluded.

## Risks, Remaining Work and Next Decision

V2's strong navigation reference and shared filter may largely compensate for
the original reward. That is a valid outcome, not a reason to weaken those
components in this comparison. The result applies conditional on V2 and cannot
isolate the cause of wandering in the unavailable original simulator.

The task remains a one second sampled surrogate with static background load,
ideal downlink service, uncalibrated energy and no obstacle collision model.
No packet deadline or empty queue arrival requirement is introduced. Remaining
work at protocol freeze is training, fresh evaluation, analysis, replay and
the V2 focused paper. The next decision is the interpretation supported by
the completed primary contrast, not whether to retune until it is positive.
