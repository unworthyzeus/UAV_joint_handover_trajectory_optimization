# Long Route Illustration and Communication Diagnostics

Date: 13 September 2026.

## Work and Reason

The user requested a longer route and trajectory graphics as informative as
the original thesis. Its printed p. 19, Sec. 7.2, Fig. 7 shows the station
distribution and trajectories, with radio and energy metrics in printed
p. 20, Fig. 8. The previous current paper illustration used a 222 m route
with no handovers. This revision adds geographic context and time resolved
communication behavior, without changing training, evaluation or inference.

The manuscript now contains three figures: aggregate success, two station
and trajectory panels, and eight time series. The route figure shows all
87 selected stations as triangles, a full map, an equal aspect route zoom,
start and goal, and executed handovers as circles colored by controller.
The diagnostic figure shows serving RSS, SINR, queue, service capacity,
cumulative handovers, delay proxy, consumed energy proxy and interference.
It includes the RSS and buffer limits and the offered traffic rate. Curves
retain the initial sample and every executed sample, stopping at each
episode endpoint. Lines connecting samples are visual guides, not evidence
of continuous physical connectivity.

## Selection Rule

Select the maximum Euclidean start to goal distance among **all 200** routes
in the already frozen `longer_test` split. Break ties by ascending scenario
ID. Retain seed 2101, used in the previous illustration, and the same three
controllers: original reward (V1.5), full reward (V2), and Goal radio.
Do not filter by success, handover count, performance difference or trajectory
shape. Keep every selected outcome, including a failure if present.

This chooses route `53013_0023`, index 23, distance **1784.718493 m**, from
(2328.629586, 545.023794) m to (4083.015141, 217.378520) m, load phase 7.
The selection is a reporting decision after the aggregate study; it was not
preregistered as a figure in the original study protocol. Its explicit rule
is recorded in `configs/long_route_illustration_v15.json` before dense replay.
No selected episode is added to the inferential sample count.

## Result on This Route

All three controllers succeed without sampled outage or buffer overflow.

| Metric | Original reward (V1.5) | Full reward (V2) | Goal radio |
| --- | ---: | ---: | ---: |
| Flight time (s) | 85 | 78 | 77 |
| Handovers | 18 | 1 | 2 |
| Resource changes, including handovers | 37 | 4 | 29 |
| Mean delay proxy (s) | 0.782 | 2.792 | 0.874 |
| Maximum delay proxy (s) | 24.341 | 50.605 | 9.057 |
| Maximum queue (% of capacity) | 24.62 | 99.19 | 58.98 |
| Final queue (kbit) | 123.654 | 0 | 0 |
| Minimum executed RSS (dBm) | -58 | -61 | -54 |
| Energy proxy (kJ) | 24.517 | 25.046 | 25.025 |
| Accumulated radio cost | 15.799 | 17.658 | 9.138 |
| Network filter interventions | 1 | 3 | 0 |
| Motion filter interventions | 0 | 0 | 0 |

The paths remain nearly straight and largely overlap under the shared
navigation aid. Handover locations and service curves reveal differences
that a route line alone would conceal. Full makes fewer handovers but can
accumulate substantially more queued data. Its maximum queue reaches 99.19%
of capacity, while RSS remains above the minimum. Its accumulated radio cost
is higher than original on this route, unlike the average contrast: the
illustration is not a substitute for the complete paired analysis.

The original reward's nonempty queue at successful arrival is permitted by
the declared requirements. Service capacity is a Shannon based proxy, not
measured delivered throughput, and queue divided by capacity is not a packet
latency measurement. These distinctions also appear in the paper caption.

## Verification and Reproduction

The dense trace recorder replays the same 200 route batch for each of the
three controllers, preserving inference batch size and ordering. Every field
of all **600 episode records matches exactly**, including outcomes, path,
radio metrics, queue, energy, intervention counts and raw return. Checks also
reconstruct handover counts from station changes and verify trace endpoints
and sampled means against the stored records. This repeats existing flights;
the original independent final evaluation count remains **7600**.

The recorder verifies all three source freezes, dataset hash and selected
checkpoint hashes. Its JSON records selection, source and record hashes,
station coordinates, column names, environment settings and dense samples.
The renderer verifies those source records and checkpoints before plotting.

With the private dataset at its documented location:

```powershell
python scripts/replay_long_route_illustration.py
python scripts/build_long_route_figures.py
```

The figure builder uses the committed dense trace JSON and does not require
the dataset. The complete report builder calls it automatically:

```powershell
python scripts/build_reward_comparison_report.py
```

Compile and audit the paper using [the paper build guide](../paper/README.md).
The extended audit checks the route selection, the 600 replay matches,
record and checkpoint hashes, retained 222 m figure, all original freezes,
unchanged aggregate statistics, PDF text, references, fonts and page bounds.
The final compiled pages also require visual inspection.

Final verification passed: seven compiled pages were visually reviewed,
all 20 fonts are embedded, all 35 thesis citations retain page locators,
and the final TeX pass has no overfull boxes or unresolved references.
The unchanged experiment retains its prior 73 passing tests and 7600 exact
replays; this reporting revision adds the 600 repeated batch matches and
figure provenance checks, not a new training result.

## Preserved Records and Limits

The previous 222 m figure and its hashes remain in
`results/reward_comparison/analysis_v15/previous_222m_illustration/`.
Note 40 records the motivating audit. Prior release notes describe the
version delivered at that time; this note records the subsequent revision.
The manuscript is still one current paper at its existing stable PDF path.

The private map, all 20 frozen source/protocol files, 15 checkpoint files,
original raw evaluation records, all tables, bootstrap intervals and primary
null conclusion remain unchanged. This task changes reporting only.

The new route is longer than the previous example but is not the source
Fig. 7 route and does not reproduce the original simulator. Neither a single
successful example nor more detailed visualization establishes overall
superiority. The remaining research decision is independent evaluation and
separately frozen control ablations; no such experiment was run here.
