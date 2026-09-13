# Original Thesis Comparisons throughout the README

Date: 13 September 2026.

## Work and Purpose

The user requested comparisons with the original thesis in every README
table, including results. Every root README table now contains an original
thesis column or an explicit source comparison. Added a reward component
table and a source result table covering all five metrics plotted by the
thesis, as well as the mission outcomes it does not quantify.

The comparison covers the dataset and physical model, mission requirements,
actions, navigation and filtering, all observation features, reward terms,
PPO settings, route pools, budgets, model packaging, success, uncertainty,
communication metrics and failure counts. Source references use printed
pages with sections, equations, tables or figures. PDF viewer page numbers
are two greater than printed page numbers.

The preceding dataset correction remains in effect: the HDF5 is the same
dataset used by the original thesis, as confirmed by the researcher who
supplied it. Note 43 records that provenance. V1.5 is our reconstruction of
the written original reward inside the complete V2 system; it is not the
original thesis agent or an original thesis result.

## Source Result Reading Convention

Inspected the text and rendered pages of
`sources/UAV_Bermudez_Granados_2026_MSc_thesis.pdf`, especially printed
pp. 16-21, Secs. 6.2-8. Read the original figure images directly, including
their legends, units, scientific notation and axes. Figures 6 and 8 are
on printed pp. 18 and 20. They show SNR, outage time, uplink interference,
remaining energy and handovers; they do not show numerical transmission
delay results, despite the name of the delay priority policy.

The README labels every numerical source plot reading with an approximation
sign. A CDF value is the approximate x coordinate at probability 0.5, while
a bar value is its approximate height. These are visual readings, not exact
source data, source means or reproduced simulations. The priority policy
order is delay, interference, then handover, regardless of legend or color
ordering in individual panels.

| Metric and source axis | Fig. 6: equal PPO / greedy | Fig. 8: delay / interference / handover | Interpretation limit |
| --- | --- | --- | --- |
| SNR CDF median, dB | Approximately 124 / 127 | Approximately 122-123 for all three | Source SNR and current mean SINR differ in definition, arithmetic and statistic. |
| Outage bar, seconds | Approximately 0 / 2 | Approximately 0 / 1 / 1 | An outage bar is not a strict joint mission success percentage or first failure count. |
| Uplink interference CDF median, dBm | Approximately -35 / -28 | Approximately -40 / -40 / -38 | Current interference is a mean of linear cochannel downlink power in watts. |
| Remaining energy bar, labeled kW | Approximately 370 / 440 | Approximately 310 / 260 / 770 | Retain the printed power unit; do not convert it to consumed energy in joules. |
| Handover CDF median, raw plotted x value | Approximately 0.0046 / 0.0129 | Approximately 0.0025 / 0.0041 / 0.0033 | Both x axes display a 1e-2 multiplier and refer to 200 episodes; normalization is unspecified. |

The raw source episode records and plotting code are unavailable to this
study. In particular, we do not multiply or divide the handover axis by 200,
repair the energy unit by assumption, infer completion from trajectories,
equate CDF medians with conditional means, or compute a percentage improvement
against these source readings. All original plotted metrics are represented,
including results that do not admit a numerical comparison with our outputs.

NR means not reported in the cited description or result section. NC means
not directly comparable. Neither means zero, and absence from the listed
state or parameter table does not establish absence from the unavailable
original code. The original result and our result remain separately labeled.

## Additional Parameter Details Made Explicit

The expanded tables now state the original values beside ours rather than
providing only a page reference. Among the material details are:

- Original rollout length 8, learning rate 0.00003, batch size 32, entropy
  coefficient 0.01 and target KL 0.03 [printed p. 16, Table 4]. Our learner
  has no KL stopping threshold and only logs approximate KL. Unreported
  architecture, optimizer and wrapper settings are not filled with assumed
  library defaults.
- The source lists 300 episodes and 2,000 steps [printed p. 16, Table 4].
  Their product is a nominal ceiling, not evidence of 600,000 actual logged
  interactions, an independent training route pool or a test split.
- Timestep 0.1 s in Table 3 versus 1 ms in prose, and data packet size
  2,000 bits in the table versus 1,000 bits in prose [printed pp. 14-15,
  Sec. 6.1/Table 3]. Our 1 s step and constant 200 kbit/s traffic are
  explicit modeling replacements.
- Priority weights are printed as 0.8, 0.2, 0.2, summing to 1.2, despite
  the unit sum statement [printed p. 10, Sec. 4; p. 15, Table 3]. The
  present controlled comparison uses the equal policy weights, not these
  priority settings.
- Original resource requests have fallback rules [printed p. 9,
  Sec. 3.3.1]; our mask precludes unavailable requests. Original greedy
  uses constant velocity and consecutive handover viability counters
  [printed pp. 13-14, Sec. 5.4]. Our deterministic references are different.

## Result and Verification

The README now permits direct inspection of what is retained, changed,
unreported and numerically incompatible. The original thesis does not
report a comparable strict joint success rate, so no original success
percentage is inserted. The current conclusion remains unchanged: V1.5
and full V2 both reach 95.7% standard success; longer success is 85.8%
and 87.3%, with both difference intervals including zero.

Checked Markdown table structure and local links, current success rates,
paired means, failure counts and intervals against the saved analysis,
and preservation of all previously reported numerical result cells. Checked
the 20 frozen source/protocol files and all 15 checkpoint hashes. Original
thesis plot readings were visually checked against the source figures.
The check covered all 15 README tables, 253 preserved existing table cells,
14 success rates, 28 paired means, 12 failure counts, two success intervals
and 77 local documentation links. The dataset clarification is already incorporated in the rebuilt current
paper; the additional approximate cross thesis result readings are confined
to the README and this provenance note.

No training, evaluation, test route selection or numerical analysis was
rerun. The dataset, experiment source, frozen protocols, raw episode records,
aggregate statistics, figures and models are unchanged. Prior experiment
tests and exact replays remain historical validation; this revision adds
documentation and artifact checks, not new experimental evidence.

## Remaining Work, Risks and Next Decision

Shared dataset identity cannot establish shared simulator behavior. Direct
numerical benchmarking against the original agent still requires its code,
weights, evaluation records and plotting definitions, or a separately
declared and validated reconstruction. Approximate figure readings cannot
replace those assets. The README keeps this boundary beside the numbers
instead of presenting missing values as poor performance.

The next research decision remains controlled ablations of the shared V2
navigation, observation, termination and filtering changes, followed by
independent evaluation. The current results do not identify the cause of
the original wandering or establish an overall improvement over that agent.
