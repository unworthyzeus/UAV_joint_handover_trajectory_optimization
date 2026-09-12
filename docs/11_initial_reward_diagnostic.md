# Initial Reward Diagnostic

## Purpose

The first executable experiment tests whether the legacy reward structure can prefer repeated approach behavior over mission completion when radio conditions are held identical.

## Design

The diagnostic uses hand written distance traces, identical nonnegative telecom
costs, and the reward structure in the TFM [printed p. 12, Eqs. (13)–(14)],
with parameters from [printed p. 15, Table 3]. Add two for PDF page numbers.

The traces include:

1. Direct arrival followed by holding at the goal because the legacy episode does not terminate there.
2. Oscillation that repeatedly moves closer and farther without completing the mission.
3. A corrected mission first evaluation that terminates on safe arrival, gives explicit success and failure outcomes, charges time, and uses actual distance progress.

## Interpretation Rule

Clarification, 12 September 2026: the supplied mission labels are handcrafted.
The oscillating trace is 4 to 5 metres from the goal, inside the thesis's listed
10 metre position tolerance [TFM, printed p. 15, Table 3], and its dynamics and terminal velocity were not
validated. Its name `never_arrive_oscillation` means that it never reaches the
exact target coordinate in this toy construction. It is not a demonstrated
failure under the original simulator's success criterion. See
`17_received_dataset_assessment.md` for the updated evidence and required
physical replay.

This is an incentive audit, not policy training and not scientific evidence of improved flight performance. Its only claim is structural: if an unsuccessful trace can receive more reward than a successful trace under identical radio metrics, the scalar reward is not aligned with the stated mission.

## Command

```powershell
python scripts/run_reward_diagnostic.py
```

Expected outputs:

1. `results/tables/reward_alignment_diagnostic.csv`
2. `results/tables/reward_alignment_diagnostic.json`
3. `results/figures/reward_alignment_diagnostic.png`

The generated files are engineering diagnostics only. They are not trained
performance and must not be used as evidence that a new controller outperforms
Marina's policy.

## Validated Result

The command completed on 15 July 2026 and all diagnostic ordering assertions
passed.

| Formulation | Direct arrival discounted return | Never arrive discounted return | Preferred trace |
| --- | ---: | ---: | --- |
| Legacy Equations 13 and 14 | 69.95 | 79.65 | Never arrives |
| Mission first audit reward | 21.05 | -18.17 | Direct arrival |

Under the legacy formulation, the direct trace reaches the goal at step 5 and
then holds until the shared 12 step horizon. The unsuccessful trace alternates
between four and five meters from the goal. Identical radio inputs are used for
both. The unsuccessful trace wins because each new approach receives the fixed
closer bonus while the retreat is not charged an equal distance penalty.

This establishes an incentive counterexample for the stated reward. It does
not establish how often Marina's trained policy exploited it or how a new
controller performs in the missing Barcelona environment.
