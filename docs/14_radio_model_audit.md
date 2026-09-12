# Radio Model Audit

## What Was Implemented

`src/uav_joint_optimization/radio.py` provides unit explicit conversions and reference calculations for:

1. dBm to milliwatts and back.
2. Summing multiple powers through the linear domain.
3. SINR from serving signal, interferers, and noise.
4. Ideal Shannon rate `B log2(1 + SINR_linear)`.

## Why

The thesis writes interference as a sum of RSS values [TFM, printed p. 10,
Eq. (9)] and rate as bandwidth plus a logarithm of SNR [TFM, printed p. 10,
Eq. (7)]. SNR is defined in dB [TFM, printed p. 10, Eq. (8)], while the RSS
budget is explicitly downlink [TFM, printed p. 7, Eq. (1)]. These expressions
are dimensionally unsafe if implemented literally. Our experiment replaces
them with a linear downlink cochannel proxy and SINR rate; this changes the
model as well as power arithmetic. Original implementation behavior remains
unverified. Add two to printed pages for the PDF counter; see
[note 25](25_exact_changes_from_tfm.md) for the complete comparison.

## Current Result

Reference unit tests cover round trips, the 3.0103 dB increase from summing two equal powers, SINR with noise and interference, and the 1 bit per second per hertz capacity at 0 dB SINR.

## Remaining Work

1. Compare these functions with the recovered legacy implementation.
2. Confirm whether ray tracing values represent received downlink power, path gain, or another quantity.
3. Define uplink interference at the affected base stations rather than assuming downlink RSS at the UAV is equivalent.
4. Add modulation, coding, scheduler, and resource occupancy effects if the study requires achievable rather than ideal rate.

## Risk

Correcting the equations may change all delay, buffer, outage, and reward distributions. Legacy numbers must therefore be preserved as a reproduction result and clearly separated from a physically corrected benchmark.

## Next Step

Run these reference calculations against a small set of raw channel database entries as soon as the data is available.
