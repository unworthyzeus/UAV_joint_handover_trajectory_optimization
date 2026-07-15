# Legacy Asset Request

The following text can be sent to Marina or the supervisors.

## Request

Subject: Source code and channel data for the UAV handover and trajectory baseline

I am continuing the I2R project “Joint Handover and Trajectory Optimization in 5G Connected UAVs” and need to reproduce the 2026 baseline before modifying the formulation.

Could you provide:

1. The `JointHandoverTrajectoryOptimization` repository at the commit used for the thesis. The GitHub URL printed in the thesis currently returns 404.
2. The deterministic Barcelona ray tracing RSS database, its schema and
   checksum, and the MATLAB generation scripts.
3. The processed Barcelona STL or source geometry, crop bounds, projection,
   local origin, axis orientation, and grid indexing.
4. The Minetur or Infoantenas export used on 20 May 2024, including the 133
   sites, 43 shared site decisions, operators, sectors, frequencies, antenna
   data, and deduplication rules.
5. The exact Python and MATLAB environments or lock files, including toolbox
   versions.
6. Original PPO checkpoints, normalization statistics, training logs,
   configurations, and tuning records if available.
7. The exact start and destination pairs, scenario splits, resource and traffic
   realizations, and random seeds used for Figures 5 through 10.
8. Raw per episode trajectories and metrics and the scripts used to generate
   the thesis figures.
9. Clarification of the timestep, time to trigger behavior, radio power units,
   SINR or SNR calculation, energy units, and resource occupancy observability.

The files will be kept unchanged as raw research assets. Reproduction results will be separated from any corrected formulation or new algorithm.
