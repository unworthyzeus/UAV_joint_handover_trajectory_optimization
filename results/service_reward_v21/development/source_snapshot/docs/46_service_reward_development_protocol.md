# V2.1 Completion and Service Reward Development Protocol

Date: 14 September 2026. Written before the development runs below.

## Purpose and Priorities

The user requested better mission completion first, followed by better delay
and handover behavior. The existing V1.5/V2 findings stay unchanged. A new
version must earn a favorable conclusion from measurements; improving the
wording or selecting favorable test routes cannot establish improvement.

The current full V2 delay cost saturates: 0.35 times 10D/(1+10D) is about
0.318 at one second, 0.344 at six seconds and 0.347 at ten seconds. The
instantaneous handover cost is about 0.347. This gives a specific reason to
test a delay penalty that remains sensitive at larger delays, a smaller
handover cost, and an explicit penalty for approaching buffer capacity.
It is a mechanistic hypothesis, not proof that a trained candidate improves.

## Fixed System and Reward Candidates

All candidates use the unchanged V2 dataset, dynamics, traffic, capacity,
energy, action space, observations, navigation aid, safety filter and episode
termination. The same dataset is used by the original thesis. The -96 dBm
RSS and 160 KB buffer requirements remain. No packet deadline, new minimum
rate or empty queue arrival condition is imposed.

`service_reward_env.py` delegates transitions to the frozen V2 implementation
and replaces the reward after each step. Its filter and recorded radio cost
still use the original V2 cost. In particular, changing a reward must not
silently change which actions the filter executes.

The reward retains V2 potential shaping, time cost 0.05 and success payment
20, and subtracts the following service cost and failure penalty:

```text
service_cost = 0.10 log(1 + D / 1 second)
             + queue_weight (q / buffer_capacity)^2
             + 0.03 executed_handover
             + 0.30 (100000 I) / (1 + 100000 I)
             + rss_weight softplus((-80 dBm - serving_RSS) / 10 dB)
```

One second is a reward scale, not an application deadline. The -80 dBm
reference is a soft shaping reference, not a new feasibility threshold.
The softplus term and failure penalty target completion, while delay and
queue terms target service. No real world calibration is claimed.

| Development arm | Queue weight | RSS weight | Terminal failure penalty | Original thesis comparison |
| --- | ---: | ---: | ---: | --- |
| Full V2 control | Uses unchanged V2 reward | Uses unchanged V2 reward | 20 | Different from source positive reciprocal reward [printed p. 12, Eqs. (13)-(14)]. |
| Service | 0.20 | 0 | 20 | New logarithmic delay, queue and handover reward, not source Eq. (14). |
| Reliability | 0.20 | 0.10 | 60 | Adds soft RSS shaping and a stronger terminal penalty; source penalties are -10 [printed p. 15, Table 3]. |
| Reliability strong | 0.40 | 0.25 | 100 | Same proposed package with stronger queue, RSS and terminal terms. |

All four arms start from scratch with pilot seed 2199, 524,288 interactions,
and the unchanged PPO settings and training route pool. All pilot checkpoints
and outcomes are retained. One seed is development evidence only. These
package candidates do not isolate the individual causal effect of each term.

## Development Selection and Stop Rule

Use only the existing 64 standard and 32 longer validation routes. Do not run
the existing 53012/53013 tests for tuning. Evaluate final budget checkpoints,
not the best checkpoint in a training curve. Select the candidate with:

1. Highest total joint validation successes, over both splits.
2. Lowest mean delay on common successful routes with the full V2 pilot
   control, breaking completion ties.
3. Fewest handovers on those same routes, breaking remaining ties.
4. Candidate declaration order if still tied.

A candidate advances only if it has at least as many total validation
successes as the full V2 pilot and no larger mean delay on common successes
in either split. This is a development gate, not a significance test. All
three candidates are evaluated, including worse candidates. If none pass,
report a failed development attempt and do not open a new test set. No
additional candidate is added based on test outcomes.

## Fresh Evaluation if the Gate Passes

Freeze the selected coefficients, source hashes and final protocol before
final training. Train five selected candidate policies from scratch with
seeds 2101-2105 and 524,288 interactions each. Compare against the five
existing V1.5 original and five full V2 checkpoints, matched by seed and
with the same training pool and budget. The original models' historical
development was different and their prior outcomes are known.

Use 500 new standard and 500 new longer routes generated with seeds 54012
and 54013, disjoint from all prior saved routes. Generate and save them only
after development selection. All controllers receive the identical routes
and load phases. Include Goal radio, joint one step and joint three step
references. There are 18,000 evaluation episodes: 15,000 learned and 3,000
deterministic. New routes remain within the training distance range on the
same city, not geographic generalization.

Primary contrast: selected V2.1 minus full V2 standard joint success. Report
a 95% crossed seed/route bootstrap interval, 5,000 draws, bootstrap seed
64000. Lower interval bound above zero is evidence for improved completion
on that split. Secondary contrasts include longer routes, V1.5 and the
references. Report delay, handovers, energy, flight time, SINR, interference,
queue at arrival and the fixed V2 radio cost on common successful pairs,
with all failure counts separate. Intervals for secondary metrics are
descriptive and unadjusted for multiplicity.

A statement of improved completion without a delay regression additionally
requires the paired delay difference interval upper bound to be at most
zero for the primary standard comparison. This is a reporting criterion,
not a new mission constraint. Any claim about V1.5 must be supported by its
own paired comparison. A success difference interval including zero does
not prove equivalence or noninferiority. No overall dominance claim follows
unless all relevant metrics support it.

Save final weights and their hashes before testing, evaluate once, replay
every final record exactly, and retain every seed. Do not retrain or choose
another candidate after looking at the new tests. The final conclusions
must include negative and mixed outcomes.

## Verification, Remaining Work and Risks

Before training, verify transition identity, original V2 metric identity,
constraint and terminal semantics, finite reward values and reward sensitivity.
Verify PPO implementation identity apart from the adapter import. Recheck
all three historical source freezes. Record development and fresh evaluation
results in separate notes; this protocol is not an outcome report.

The general motivation for keeping feasibility explicit is consistent with
[Achiam et al., Constrained Policy Optimization](https://proceedings.mlr.press/v70/achiam17a.html).
This experiment still uses PPO and the existing sampled filter, not CPO or
a new feasibility guarantee. Repeated seed uncertainty remains relevant,
as discussed by [Agarwal et al., Deep Reinforcement Learning at the Edge of
the Statistical Precipice](https://papers.neurips.cc/paper_files/paper/2021/hash/f514cec81cb148559cf475e7426eed5e-Abstract.html).

The next decision is the declared validation gate. Five final seeds, if
trained, are still only five independent training runs. Same map evaluation,
static traffic, proxy energy, ideal handovers, unverified sentinel meaning
and the unavailable original simulator continue to limit scientific claims.
