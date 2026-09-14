# Clarifying the SNR Comparison and Improvement Target

Date: 14 September 2026.

## What Changed and Why

The user asked whether the SNR row should improve. That row compared the
initial V1.5/full V2 controllers, not the newer V2.2 supervisor. It also
placed unverified source plot readings next to valid Eq. (8) measurements,
which could suggest that the numerical gap was an achievable improvement.

The README now separates the unverified source scale from valid measurements
and links directly to a fresh full V2/V2.2 SNR table. It reports both the
mean flight SNR and pooled executed sample median on the same common
successful route/seed pairs, with higher is better and dB throughout.

## Result and Interpretation

V2.2 already improves mean SNR over full V2 by 2.429 dB on standard routes
and 2.662 dB on longer routes. The existing descriptive 95% intervals are
[2.282, 2.576] and [2.563, 2.757] dB. These service comparisons accompany the
positive completion finding and do not replace it.

The source formula is `SNR = RSS + 112.41 - 9`
[TFM, printed p. 10, Eq. (8); p. 15, Table 3]. The same Operator 1 map has
maximum RSS -25 dBm, implying a maximum possible value of 78.41 dB. Source
plot medians around 122-127 dB exceed that bound [printed pp. 18, 20,
Figs. 6/8]. Their implementation or inputs need clarification. The bound
is a maximum anywhere in the map, not a universally attainable mission
average or evidence that another 14 dB can be gained by changing a policy.

## Verification and Reproduction

`scripts/report_snr_comparison.py` reads the unchanged final JSON and NPZ
records, matches scenario IDs, and retains only common successful pairs.
It checks every mean against the existing frozen analysis before adding the
pooled sample medians. The
[derived report](../results/thesis_metrics_v22/analysis/snr_comparison.json)
records the input hashes and exact sample counts. There are 2,331 standard
and 2,225 longer common successful pairs.

```powershell
python scripts/update_thesis_metrics_readme.py
python scripts/audit_thesis_metrics_delivery.py
```

The first command regenerates the SNR summary as well as the README. A mean
flight SNR weights flights equally; a pooled median weights each executed
one second sample equally. The median difference is descriptive; no new
confidence interval is inferred. No training, controller, trajectory, frozen
statistic or paper changed for this reporting clarification.

## Limits and Next Decision

Further valid SNR improvement is a reasonable research objective only while
preserving completion and communication service. SNR excludes interference,
so SINR, delay, handovers and failures must remain visible. New controller
tuning would require a separately declared study and untouched evaluation
routes. This update identifies the correct existing comparison and the
unresolved source scale; it does not claim another model improvement.
