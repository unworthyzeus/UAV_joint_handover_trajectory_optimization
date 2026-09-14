### SNR Comparison for the Current Controller

**V2.2 already improves valid SNR.** The older source comparison below shows V1.5 and full V2 on 53012/53013 routes; those 63.410 values are not V2.2 results. This table uses the same fresh 55012/55013 routes for full V2 and V2.2, with identical units and aggregation within each row.

| SNR statistic and preferred direction | Full V2 (dB) | V2.2 (dB) | Difference (dB) | Original thesis comparison |
| --- | ---: | ---: | --- | --- |
| Standard mean flight SNR: higher is better | 62.238 | 64.667 | +2.429; 95% interval [2.282, 2.576] | Verified source mean NR [printed p. 10, Eq. (8); pp. 18, 20, Figs. 6/8]. |
| Standard pooled sample CDF median: higher is better | 62.410 | 65.410 | +3.000; descriptive | Source plotted medians remain unverified; no numerical improvement over that scale is claimed [pp. 18, 20]. |
| Longer mean flight SNR: higher is better | 62.045 | 64.707 | +2.662; 95% interval [2.563, 2.757] | Verified source mean NR [printed p. 10, Eq. (8); pp. 18, 20, Figs. 6/8]. |
| Longer pooled sample CDF median: higher is better | 62.410 | 65.410 | +3.000; descriptive | Source plotted medians remain unverified; no numerical improvement over that scale is claimed [pp. 18, 20]. |

The comparisons use 2,331 standard and 2,225 longer common successful pairs. A mean flight SNR gives each flight equal weight; the pooled sample median gives each executed one second sample equal weight, so longer flights contribute more samples. Median differences are descriptive, not new confidence intervals or new independent trials.

**Why 122–127 dB is not an optimization target:** using the thesis formula and settings, `SNR = RSS + 112.41 − 9`. The maximum RSS in the same Operator 1 map is −25 dBm, giving `−25 + 112.41 − 9 = 78.41 dB`. The original plotted values exceed that bound. Their source inputs or implementation need clarification [printed p. 10, Eq. (8); p. 15, Table 3; pp. 18, 20, Figs. 6/8]. The 78.41 dB bound is the best value anywhere on the map, not an attainable average along every mission.

Further SNR gains must preserve completion and communication service. SNR alone excludes interference; the SINR, delay, handover and failure rows above remain necessary. [Reporting clarification and sample counts](docs/56_snr_comparison_clarification.md).
