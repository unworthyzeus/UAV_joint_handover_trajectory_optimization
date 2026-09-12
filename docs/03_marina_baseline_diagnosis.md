# Marina Baseline Diagnosis

Updated 12 September 2026 with pinpoint source references and the completed
experiment's limits. TFM means the [original thesis](../sources/UAV_Bermudez_Granados_2026_MSc_thesis.pdf).
Pages are printed pages; add two for the PDF viewer counter. The complete
definition index and executed comparison are in [note 25](25_exact_changes_from_tfm.md).

## What the Original Work Established

The thesis describes a Barcelona radio environment with deterministic ray
tracing and real station locations [TFM, pp. 6–7, Sec. 3.1, Table 2], A3 and
resource allocation [TFM, p. 9, Sec. 3.3.1, Eq. (3)], queue and energy models
[TFM, pp. 9–10, Eqs. (4)–(10)], and PPO plus a greedy reference [TFM,
pp. 13–14, Secs. 5.3–5.4]. The source simulator and checkpoints remain
unavailable, so written definitions must not be mistaken for verified code.

## Confirmed Written Formulation

The state is `[x, y, serving BS, allocated RBG, energy, buffer]` and the action
is `[acceleration, direction, requested BS, requested RBG]` [TFM, p. 12,
Sec. 5.2]. There are five acceleration bins, eight headings, 87 selected
operator stations, and twelve resource groups [TFM, pp. 14–15, Sec. 6.1,
Table 3]. Their nominal product is 41,760 combinations. This is our count;
a factorized action policy need not explicitly enumerate the product.

The reward transforms delay, interference, and handover costs into positive
reciprocals and applies penalties [TFM, p. 12, Eqs. (13)–(14)]. The approach
bonus is 12 [TFM, p. 15, Table 3]. Energy exhaustion ends the episode and
overrides reward, while arrival explicitly does not terminate it [TFM, p. 12,
Sec. 5.2, final paragraphs].

The reported evaluation measures SNR, outage, interference, remaining energy,
and handover count, without a reported mission success rate, arrival time,
or terminal distance [TFM, pp. 16–20, Sec. 7, Figs. 5–8].

## Reward Interpretation and Its Evidence Limit

Our interpretation is that the positive ongoing terms and fixed approach bonus
can reward slow or repeated approach without making mission completion decisive
[source incentive: TFM, p. 12, Eqs. (13)–(14); p. 15, Table 3]. This is a
mathematical diagnosis, not an observed exploit in the unavailable source code.
The original navigation discussion shows overshoot and correction [TFM, p. 19,
Sec. 7.2, Fig. 7], and its conclusion reports priority for persistent
connectivity [TFM, p. 21, Sec. 8].

The old abstract reward diagnostic gives its nominal oscillating trace 79.65
versus 69.95 for direct arrival. Its 4–5 m distance is inside the source's
10 m position tolerance [TFM, p. 15, Table 3], and its velocity is not
physically validated. Those labels therefore do not prove a failed physical
mission outranks a successful one. Notes 19–21 separately document the later
physical witness and actual trained comparison.

## Observation and Action Interpretation

1. Velocity is absent from the listed state [TFM, p. 12, Sec. 5.2], although
   motion depends on speed [TFM, p. 9, Eq. (2)]. That observation alone does
   not specify the full motion state.
2. The destination is also absent from the vector [TFM, p. 12, Sec. 5.2]. A
   policy for variable goals would need additional information or assumptions.
3. Candidate measurements, group availability, and time are not listed despite
   station and resource actions [TFM, p. 12, Sec. 5.2]. Unreported wrappers
   cannot be inferred from this omission.
4. Motion is discretized [TFM, pp. 12, 15, Sec. 5.2, Table 3]. Our continuous
   interface and expanded observation are shared changes, not separately
   tested interventions in the completed reward experiment.

## Printed Formula and Parameter Ambiguities

1. Rate adds bandwidth to a logarithm of SNR [TFM, p. 10, Eq. (7)].
2. Interference sums RSS values and labels the result uplink, although the
   stored RSS is defined by a downlink budget [TFM, p. 10, Eq. (9); p. 7,
   Eq. (1)]. Our replacement changes link interpretation as well as units.
3. SNR excludes interference [TFM, p. 10, Eq. (8)]; ours uses SINR.
4. The energy equation has unclear integration/units [TFM, p. 10, Eq. (10)]
   and capacity is labeled 1000 kW [TFM, p. 15, Table 3]. Our 100 kJ budget
   and energy model are new choices, not a verified conversion.
5. Time step is 1 ms in prose [TFM, p. 14, Sec. 6.1] and 0.1 s in Table 3
   [TFM, p. 15]. Data packet size similarly differs between prose and table.
6. Specialized weights total 1.2 [TFM, p. 15, Table 3], despite a sum of one
   requirement [TFM, p. 10, Eq. (11) discussion]. We use only the equal-policy
   weights in the legacy reward arms.
7. Arrival is stated in prose [TFM, p. 10, Sec. 4] but is absent from the
   displayed constraints [TFM, p. 11, Eq. (12), C1–C6].

These discrepancies may be notation problems or implementation problems. The
thesis alone cannot distinguish them.

## Result, Remaining Work, and Next Decision

The completed four treatment experiment supports replacing the reward within
our explicitly reconstructed environment. It does not establish a one line
fix to the original simulator. In particular, adding training arrival
termination did not improve longer route performance. Both the unchanged
reference values and every shared replacement are listed in note 25.

Recover the source to verify the written definitions and repeat the ablation
there, or design a new independently frozen study. The current comparison,
its negative arms, and the distinction between diagnosis and reproduction
must remain visible when reporting the result.
