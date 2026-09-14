# Recovered Thesis Metrics and Source Consistency Audit

Date: 14 September 2026.

The README is the main result entry point. These measurements add to the unchanged initial 53012/53013 flights. All 4,000 underlying V1.5/full V2 episodes replayed exactly before metrics were added; this is not new independent performance evidence.

## Same Formula, Unresolved Source Figures

The native Operator 1 map has maximum RSS -25 dBm. Source Eq. (8), RSS + 112.41 - 9, therefore cannot exceed 78.41 dB anywhere in this map. Source Fig. 6/8 medians around 122-127 dB cannot follow from that equation, Table 3 noise values and this same dataset. This identifies an unresolved source inconsistency, not its coding cause [TFM, printed p. 10, Eq. (8); p. 15, Table 3; pp. 18, 20, Figs. 6, 8].

The new all neighbor RSS power is a linear power interpretation of Eq. (9). It excludes the serving station and includes all other Operator 1 stations regardless of cochannel occupancy. The thesis labels the quantity uplink but does not specify how RSS powers are summed. Our metric is a source equation proxy, not a physical uplink estimate. The literal raw integer sum, including sentinel entries, is kept only as an arithmetic diagnostic. Missing serving paths (-128) produce no valid SNR sample; their sample count is recorded instead of interpreting the sentinel as signal power.

Remaining energy is now reported in kJ under our V2 accounting. The literal source Eq. (10) score is also retained separately, initialized to 1000 with the printed plus electronics term and no timestep. It increases for every speed allowed by V2, including when stationary. It has no validated physical unit or meaningful better direction; it must not be compared with source remaining energy bars as a successful energy improvement [printed pp. 10, 15].

## Added Initial Comparison Metrics

| Metric and preferred direction | Standard V1.5 / full V2 | Longer V1.5 / full V2 | Original thesis definition |
| --- | --- | --- | --- |
| SNR (dB), higher is better | 63.445 / 62.429 | 63.237 / 62.046 | SNR, printed p. 10, Eq. (8); noise values, p. 15, Table 3. |
| All neighbor RSS power (µW), lower is better | 1.452 / 1.462 | 1.537 / 1.555 | Linear power interpretation of printed p. 10, Eq. (9); physical link direction remains uncalibrated. |
| Remaining energy (kJ), higher is better | 92.349 / 92.212 | 81.477 / 81.043 | Our V2 energy accounting; source Eq. (10), p. 10, and Table 3, p. 15, do not define this physical metric. |
| Handovers per second, lower is better while preserving service | 0.214 / 0.014 | 0.241 / 0.025 | Explicit switches per second; source Figs. 6/8, pp. 18/20, have unspecified normalization. |

These means use the original 925 standard and 781 longer common successful pairs. The raw archive also stores pooled step CDF medians separately in `analysis/initial_recovered_metrics.json`. Neither a per flight mean nor our declared pooled sample median silently reproduces unspecified source CDF aggregation.

## What Was Done, Verified and Remains

Added source SNR, all neighbor RSS power, remaining energy, explicit handover frequency and complete sample arrays. Preserved all original episode fields and source files. The missing physical uplink model and original handover normalization remain unresolved. A direct source agent comparison needs its implementation or validated raw records. The separately declared guard improvement is evaluated in note 53; it does not resolve those source ambiguities.
