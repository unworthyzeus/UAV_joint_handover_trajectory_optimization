# Clear Metric Descriptions and Consistent Units

Date: 14 September 2026.

## What Changed and Why

The user pointed out that the table explained signs rather than the meaning
of signal quality, and mixed different units within rows. Rewrote the README
descriptions around the physical quantity, preferred direction and measured
tradeoff. The metric guide in note 45 uses the same explanations.

SINR now describes the desired signal relative to interference plus noise.
Higher SINR indicates a cleaner radio link; the measured V2 decrease means
worse signal quality on common successful flights. Interference describes
unwanted received power. Delay describes queued data divided by service
capacity. Energy describes estimated consumption under the declared model.
These explanations replace commentary about the ordering of negative numbers.

## Unit and Quantity Rules

Each source comparison row now declares its unit once, applying it to every
numerical result in that row. All README interference results use µW, with
source uplink and our downlink results in separate rows.
The approximate source readings are converted with:

```text
P(µW) = 1000 × 10^(P(dBm) / 10)
```

The original Fig. 6 readings, approximately -35 and -28 dBm, become
approximately 0.316 and 1.585 µW. The Fig. 8 readings, approximately -40,
-40 and -38 dBm, become approximately 0.100, 0.100 and 0.158 µW. Source
locations remain printed p. 18, Fig. 6 and p. 20, Fig. 8. Three displayed
decimals describe the conversion; they do not increase the precision of
the original visual readings. Note 44 retains the source scale and method.

Four source quantities now have separate rows:

1. Source SNR is separate from our SINR. Both use dB, but the denominator,
   source arithmetic and reported statistic differ [printed p. 10, Eq. (8)].
2. Source remaining energy bars retain their printed kW label. That is a
   power unit, so these are unresolved plot readings, not values convertible
   into our consumed kJ [printed p. 10, Eq. (10); p. 15, Table 3].
3. Source handover CDF positions are separate from executed handovers per
   flight. The printed scaling and reference to 200 episodes do not specify
   how to recover a count [printed pp. 18, 20, Figs. 6, 8].
4. Source uplink interference is separate from our downlink interference.
   Our uplink cells say not evaluated; source downlink cells say not reported.
   A numerical comparison requires the same link direction and quantity,
   not only the same unit [printed p. 10, Eq. (9)].

This fourth separation addresses the user's subsequent correction: the
first unit revision still placed source uplink and our downlink results
together. Removed the source uplink figures from the paired downlink table
as well, and separated the corresponding physical model definitions.
No matched uplink measurement or model is introduced by this table edit.

Following the user's additional instruction, every result metric row now
states "higher is better" or "lower is better" explicitly. Success columns
carry the same direction for every controller. Handovers retain the service
condition; remaining energy and raw handover displays state the intended
direction alongside their unresolved interpretation. Trajectory behavior
refers to higher mission success, without assigning a numeric preference
to path shape. Parameter values and sample counts are not performance scores.

Removed outage durations from the failure count row and replaced the
trajectory row's sample counts with descriptions of trajectory behavior.
The common success sample sizes remain immediately above the comparison.
All original plot readings are retained; unavailable results remain NR.

The physical model table also expresses time steps in seconds, energy
consumption and budget in kJ, and retains incompatible source energy model
parameters in the accompanying prose. This changes the display units only.

## Results and Verification

This is a documentation correction. No model, raw evaluation, statistic,
figure, paper, dataset or frozen experiment implementation changes. All
completion and service conclusions remain the same.

The metric audit checks the 28 current means in the expanded comparison,
28 means in the preceding paired table, all five displayed source interference
conversions, completion and failure counts, and separation of the incompatible
source quantities. It also rejects rows that mix uplink and downlink and
verifies the missing measurement labels. The delivery audit checks Markdown links,
the four source freezes, all twenty weights and the existing paper hash.
The metric audit also requires an explicit better direction in every result
metric row and in the success column headings.

```powershell
python scripts/audit_metric_interpretation.py
python scripts/audit_service_delivery.py
```

## Limitations and Next Decision

Consistent units do not make source uplink medians comparable to our
downlink means or resolve the source energy and handover definitions.
The original raw records and plotting code would be needed to settle those
ambiguities. No further experiment is required for this wording correction;
future scientific work still needs the separate protocol described in note 48.
