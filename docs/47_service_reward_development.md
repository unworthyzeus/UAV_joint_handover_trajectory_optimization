# V2.1 Development Results

Date: 14 September 2026.

The four declared pilot policies were trained before any 54012/54013 evaluation. Each used seed 2199, 524,288 interactions, the same training pool and identical PPO settings. Selection used 64 standard and 32 longer validation routes. These are development results, not a final superiority test.

| Candidate | Standard successes / 64 | Longer successes / 32 | Total / 96 | Matched delay difference versus control, standard / longer (s) |
| --- | ---: | ---: | ---: | --- |
| full_control | 63 | 27 | 90 | +0.000 / +0.000 |
| service | 63 | 28 | 91 | -3.422 / -4.861 |
| reliability | 62 | 25 | 87 | -3.375 / -5.015 |
| reliability_strong | 62 | 27 | 89 | -3.150 / -4.599 |

The selected candidate was **service**, following the declared completion first rule. It achieved 91/96 successes versus 90/96 for control and reduced matched delay in both splits. The stronger failure penalty candidates achieved 87/96 and 89/96, so neither was advanced.
The selected cost uses logarithmic delay weight 0.10, queue fraction squared weight 0.20, handover weight 0.03, the unchanged interference transform with weight 0.30, and failure penalty 20. No RSS shaping term was selected. It preserves every physical transition, action mask, filter and metric.
All four pilot result folders, source snapshots, logs and checkpoint hashes are retained. Pilot weights remain local development artifacts and can be regenerated; the five final V2.1 checkpoints are published separately. After pilot completion, the runner gained a reproduction label option and a standalone inference CLI was included in the final source freeze. These packaging changes did not alter candidate rewards, training or selection. The original pilot source snapshot preserves the version actually used.
The full implementation suite passed 88 tests, including 15 new reward adapter checks. The estimator is identical to V2 apart from the adapter import. All historical freezes were verified. A small validation gain is not evidence of a reliable population improvement; the next decision was the frozen fresh test.
See note 46 for the prespecified gate and note 48 for the independent evaluation. The original thesis supplies no comparable joint success rate [printed pp. 16-20, Sec. 7/Figs. 5-8].
