# Attempt to Recover the Original Thesis SNR

Date: 14 September 2026.

## What Was Done and Why

The user requested the actual original SNR value after the map audit found
that the thesis plot exceeds the bound implied by its equation and settings.
We inspected the original equations, experimental setup and complete figure
pages, rechecked source code availability, and digitized the median crossings
of the embedded SNR images. No simulation, training or historical result changed.

## What Can Be Recovered

The plotted medians are approximately 124 dB for equal PPO, 127 dB for greedy,
and 123/122/123 dB for the delay/interference/handover policies
[TFM, printed pp. 18, 20, Figs. 6/8]. These are readings of the published
plot scale, not verified Eq. (8) measurements.

The PDF contains raster charts and no embedded supplementary files. Its
[linked source repository](https://github.com/Nara-On/JointHandoverTrajectoryOptimization)
and the corresponding GitHub repository API both returned 404 on this date.
The author profile API was accessible and listed five unrelated repositories.
The earlier comprehensive search is retained in [note 16](16_missing_asset_search.md).
A 404 does not establish whether the repository is private, deleted or renamed.
No original raw SNR samples, plotting code or verified correction were recovered.

## A Specific Conditional Explanation

Eq. (8) defines `SNR = RSS − Nt − Nf` [printed p. 10]. Section 6.1 explicitly
describes an initial noise value of −174 and a bandwidth adjusted value of
−112.41 dBm, using 180 kHz per resource block and eight blocks per group
[printed p. 14; p. 15, Table 3]. The document labels the initial value dBm;
when used in a bandwidth integration it represents a density in dBm/Hz.

The bandwidth is 1,440,000 Hz, and `10 log10(1,440,000) = 61.583624921 dB`.
The following calculation uses the thesis's printed final value, −112.41,
for consistency with all current Eq. (8) measurements. The resulting offset
is exactly 61.59 dB at that printed precision.

If the plotting implementation used −174 instead of −112.41, while retaining
the same RSS and 9 dB noise figure, then:

```text
plotted SNR = RSS + 174 − 9 = RSS + 165
intended SNR = RSS + 112.41 − 9 = RSS + 103.41
intended SNR = plotted SNR − 61.59 dB
```

A fixed translation also translates the median. Therefore the conditional
medians would be about 62.4 dB for equal PPO, 65.4 dB for greedy, and
61.4/60.4/61.4 dB for the three priority policies. Allow approximately ±1 dB
for plot extraction, calibration and rounding. This allowance is not a
statistical interval and does not express uncertainty about the cause.

**This explanation is unconfirmed.** Indeed, the source prose says the
bandwidth conversion is implemented. A plot offset alone cannot prove that
it was omitted in the run or plotting path that generated these figures.
For example, a separate additive 60 dB conversion error would also yield
values within the same map bound, but different corrected medians. The map
and figure cannot distinguish these alternatives. An unknown aggregation
or other arithmetic error need not even admit a constant correction.

## Reproducible Extraction

[The recovery script](../scripts/recover_source_snr.py) reads the unchanged
[source PDF](../sources/UAV_Bermudez_Granados_2026_MSc_thesis.pdf) and extracts
image xrefs 44 and 60 directly, at their native 640 by 480 pixel resolution.
These are the top left SNR panels on printed pp. 18 and 20, respectively.

The CDF endpoints are pixel rows 422 and 20; the median is row 221. We scan
rows 219–223 and fit a linear x calibration from the five labeled ticks
40, 60, 80, 100 and 120 dB. Color masks recover each curve's median crossing.
The red handover curve overlaps the purple delay curve in Fig. 8; purple
remains detectable in the blended edge pixels on both sides of red.
The full source pages and this overlap were visually inspected.

The numerical report preserves the PDF and embedded image hashes, tick
positions, calibration residuals, every selected pixel, unrounded estimates,
rounded published readings and conditional transformed values. We round
plot readings to whole dB instead of presenting raster precision as raw data.
The ±1 dB allowance covers this rounding and the approximately 0.2 dB per
pixel horizontal scale, with room for line thickness and calibration.

```powershell
python scripts/recover_source_snr.py
python scripts/update_thesis_metrics_readme.py
python scripts/audit_thesis_metrics_delivery.py
```

The outputs are [the numerical provenance record](../results/thesis_metrics_v22/analysis/source_snr_recovery.json)
and [the README table fragment](../results/thesis_metrics_v22/analysis/source_snr_readme_fragment.md).
Running the README updater regenerates both. The paper and its report builder
include the same conditional explanation.

## Interpretation and Next Decision

The README now gives concrete conditional numbers without filling verified
source result cells with estimates. V2.2's actual pooled sample median is
65.41 dB on both fresh splits. Even under the proposed correction, the
source greedy median would be about the same. These are unmatched routes,
unknown source failure handling and unspecified source aggregation, so no
statistical comparison or improvement over the thesis follows.

The actual corrected original result remains unidentified. Resolving it
requires the source calculation and plotting version plus the figure data,
or original trajectories and enough metadata to recompute their SNR. The
conditional estimates should be replaced only when those inputs establish
the correction. The current controller conclusions remain based on the
controlled fresh comparisons, not this forensic hypothesis.
