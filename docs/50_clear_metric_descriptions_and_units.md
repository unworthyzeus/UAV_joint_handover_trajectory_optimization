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
numerical result in that row. Both README interference comparisons use µW.
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

Three source quantities now have separate rows:

1. Source SNR is separate from our SINR. Both use dB, but the denominator,
   source arithmetic and reported statistic differ [printed p. 10, Eq. (8)].
2. Source remaining energy bars retain their printed kW label. That is a
   power unit, so these are unresolved plot readings, not values convertible
   into our consumed kJ [printed p. 10, Eq. (10); p. 15, Table 3].
3. Source handover CDF positions are separate from executed handovers per
   flight. The printed scaling and reference to 200 episodes do not specify
   how to recover a count [printed pp. 18, 20, Figs. 6, 8].

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
28 means in the preceding paired table, all displayed conversions in both
interference rows, completion and failure counts, and separation of the
incompatible source quantities. The delivery audit checks Markdown links,
the four source freezes, all twenty weights and the existing paper hash.

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
