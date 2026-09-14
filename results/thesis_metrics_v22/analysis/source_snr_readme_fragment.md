### Recovering the Original Thesis SNR

**The actual corrected source result is still unverified.** We recovered the plot medians from the original embedded images. A specific possible explanation is omission of the noise bandwidth conversion: the thesis starts from −174 and explicitly gives −112.41 dBm after accounting for 180 kHz × 8 [printed p. 14, Sec. 6.1; p. 15, Table 3]. If its plotted calculation used the initial value instead, each SNR would be too high by 61.59 dB. The resulting conditional estimates are:

| Original thesis policy (SNR: higher is better) | Plotted CDF median (dB) | Conditional corrected CDF median (dB) | Source location |
| --- | ---: | ---: | --- |
| Equal PPO | ≈124 | ≈62.4 | Printed p. 18, Fig. 6. |
| Greedy | ≈127 | ≈65.4 | Printed p. 18, Fig. 6. |
| Transmission delay PPO | ≈123 | ≈61.4 | Printed p. 20, Fig. 8. |
| Interference PPO | ≈122 | ≈60.4 | Printed p. 20, Fig. 8. |
| Handover PPO | ≈123 | ≈61.4 | Printed p. 20, Fig. 8. |

**Conditional calculation:** `corrected median = plotted median − 61.59 dB`. Allow approximately ±1 dB for image reading and rounding; this is not a confidence interval. It does not quantify uncertainty about the assumed error. The figure has no raw samples or clear CDF aggregation specification, and the linked source repository still returned 404 on 14 September 2026. **These are estimates under a hypothesis, not recovered actual measurements.**

V2.2 has a measured pooled sample median of 65.41 dB on both fresh splits. The conditional greedy estimate is also about 65.4 dB, so even this hypothesis does not establish superiority over the thesis. Routes, failure handling and aggregation are unmatched. The verified source result rows below remain NR; the conditional values belong only in this explicitly labeled table.

[Full derivation, pixel extraction and limitations](docs/57_source_snr_recovery.md).
