# Baseline Reproduction Protocol

## Current Blocker

The thesis points to `https://github.com/Nara-On/JointHandoverTrajectoryOptimization`, but the URL currently returns 404 and the author's public repositories do not contain the project. The channel database is not present in the available local workspace.

## Asset Intake

When the assets are received:

1. Store the original repository under `external/` or as a documented submodule without modifying it.
2. Record the commit hash and file hashes.
3. Store the original channel database outside Git under `data/raw/` and record its hash and source.
4. Capture the Python, Gymnasium, Stable Baselines, NumPy, and PyTorch versions.
5. Preserve original configurations and checkpoints.

## Static Audit Before Execution

Check:

1. Coordinate and time units.
2. dBm and linear power conversions.
3. SNR and SINR definitions.
4. Rate and buffer equations.
5. Energy and power units.
6. A3 condition and timer behavior.
7. Action space type and invalid action handling.
8. Observation completeness.
9. Success, failure, and timeout termination.
10. Random number generation and seed propagation.

## Reproduction Runs

1. Run the original greedy controller without modifications.
2. Evaluate the original PPO checkpoint if available.
3. Retrain the original PPO across at least five seeds.
4. Recreate the thesis plots and compare their distributions.
5. Add mission metrics without changing the controller.
6. Document every mismatch before repairing the environment.

## Repair Sequence

Apply one controlled change at a time:

1. Correct units and physical formulas.
2. Add missing state variables.
3. Correct termination and reward.
4. Add action masks.
5. Restore continuous flight control.
6. Change the learning algorithm last.

This ordering separates baseline bugs from algorithmic gains.

