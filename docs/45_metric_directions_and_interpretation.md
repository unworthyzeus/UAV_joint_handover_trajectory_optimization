# More Numerical Comparisons and Metric Interpretation

Date: 14 September 2026.

## What Changed and Why

The user asked for more numbers in the original thesis comparison table,
an explanation of whether lower or higher is preferable, and an improved
model. The README now places current V1.5 and full V2 numbers directly
beside the source readings, with separate standard and longer columns.
Each row states its preferred direction and explains the interpretation.
The source equal PPO and greedy readings share a column to keep the table
width manageable. No missing original result is filled with an invented value.

Added current SINR, interference, consumed energy, handovers, delay and fixed
radio cost to the source comparison table. Also added RSS and buffer failure
counts, sample denominators and the common success sample sizes. All current
numbers come from the existing saved V1.5 analysis; this is not a new
evaluation of those models on the old tests.

## Direction and Meaning

| Quantity | Preferred direction | How to interpret it | Original thesis locator |
| --- | --- | --- | --- |
| Joint success | Higher | Primary: reaching and stopping at the goal within time and sampled connectivity limits. | Mission and constraints: printed pp. 10-11, Eqs. (11)-(12); comparable source success rate NR. |
| Flight time | Lower on common successes | An early failed flight is not a faster completed mission. | Source does not terminate on arrival, printed p. 12, Sec. 5.2. |
| SNR or SINR | Higher | A less negative dB value is higher. Source SNR is not our interference inclusive SINR. | Printed p. 10, Eq. (8); p. 18, Fig. 6; p. 20, Fig. 8. |
| Outage and failures | Lower | Zero outage among successes follows from the success definition; all failures still count. | Original outage bars: printed pp. 18, 20, Figs. 6, 8. |
| Interference | Lower | More negative dBm denotes less power; lower linear watts also denotes less power. Cross study physical and statistical definitions differ. | Printed p. 10, Eq. (9); pp. 18, 20, Figs. 6, 8. |
| Energy | Higher remaining; lower consumed | These directions are opposite. Source bars labeled kW cannot be converted into our consumed kJ by assumption. | Printed p. 10, Eq. (10); p. 15, Table 3; pp. 18, 20, Figs. 6, 8. |
| Handovers | Usually lower while maintaining service | Fewer switches can reduce control overhead, but excessive reluctance to switch can worsen service. | Source counts are shown on an unexplained scaled axis, printed pp. 18, 20, Figs. 6, 8. |
| Delay proxy | Lower | Backlog divided by capacity, not a tracked packet latency distribution. | Printed p. 9, Eq. (4); numerical source delay results NR. |
| Fixed V2 radio cost | Lower under fixed weights | Combines transformed delay, interference, handovers and flight duration. It does not establish improvement in every component. | Different from the source objective/reward, printed p. 10, Eq. (11); p. 12, Eqs. (13)-(14). |

The original source approximations and units retain the reading convention
in note 44. Their statistical aggregation and physical meaning are not
silently made equivalent to our common success means.

## Interpretation of the Existing Results

The existing standard completion rate is identical at 95.7%. Full V2 reduces
handovers by 93.5% and flight time by about 3.14 s, but its delay increases
from 1.942 to 5.827 s, its energy increases by about 0.137 kJ, and its mean
SINR decreases by about 0.983 dB on common successful flights. Interference
differences remain uncertain. These are service tradeoffs, not overall
dominance of full V2.

Longer full V2 completion is 87.3% versus 85.8%, but its interval includes
no improvement. On common successes, it saves about 5.25 s and 14.30
handovers while adding about 3.96 s of delay and 0.434 kJ of proxy energy.
All figures retain the original 53012/53013 test set and matched subsets.

The delay cost 0.35 times 10D/(1+10D) saturates quickly. Its value is about
0.318, 0.344 and 0.347 at delays of 1, 6 and 10 s, while one handover adds
about 0.347 in a step. This is a direct algebraic observation about the
written implemented reward, not experimental attribution of its behavior.

## New Model Work and Claim Boundaries

The user clarified that the next model should prioritize completion first,
then delay and handovers. Note 46 declares a bounded V2.1 development study
before its pilot results, retaining all candidates and using validation
only for selection. The new adapter changes rewards while preserving
physical transitions, sampled requirements, filters and reporting metrics.

A favorable conclusion is a possible outcome to test, not a required label.
The old results stay unchanged. Any new completion or service claim needs
its own fresh paired evaluation and uncertainty. A failed candidate remains
part of the record. Original thesis success statistics remain unavailable,
so improving our model does not establish a direct numerical improvement
over the unavailable original thesis implementation.

## Verification and Next Decision

Checked all 28 current means added to the source comparison, all 28 means
in the preceding paired table, four completion rates, eight first failure
counts, ten derived changes and 68 local links before the followup was
integrated. Source plot readings are preserved, with Markdown table structure
and code fences verified. The new adapter is checked
for transition, filter, terminal and reporting identity; the PPO estimator
is unchanged apart from its environment import. Preserve all historical
source freezes, weights and published experiment records.

The validation gate in note 46 selected the service candidate; note 48 records
its fresh evaluation and the missed completion first objective. No additional
candidate was selected using those tests. The next research decision requires
a separate declared study and new evaluation routes. The single city, static
traffic, proxy energy, ideal switching and one second sampling limits still apply.
