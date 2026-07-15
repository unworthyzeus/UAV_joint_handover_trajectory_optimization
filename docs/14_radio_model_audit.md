# Radio Model Audit

## What Was Implemented

`src/uav_joint_optimization/radio.py` provides unit explicit conversions and reference calculations for:

1. dBm to milliwatts and back.
2. Summing multiple powers through the linear domain.
3. SINR from serving signal, interferers, and noise.
4. Ideal Shannon rate `B log2(1 + SINR_linear)`.

## Why

The thesis writes interference as a sum of RSS values and writes transmission rate as bandwidth plus a logarithm of SNR. Those expressions are dimensionally unsafe if implemented literally. The proposal also targets SINR, which requires interference to be included in the rate calculation.

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

