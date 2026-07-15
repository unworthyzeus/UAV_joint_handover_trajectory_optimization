# Work Plan

This plan follows the four proposal tasks and marks evidence requirements explicitly.

## Task 1: Simulation and Baseline Analysis

1. Obtain the original source repository and deterministic channel database.
2. Record file hashes, coordinate system, map resolution, radio units, height, base station identities, and resource occupancy model.
3. Add environment checks for movement, handover, throughput, interference, energy, termination, and Gymnasium compliance.
4. Reproduce greedy and PPO results with the original configuration.
5. Add missing success, travel time, path efficiency, and terminal speed metrics.

Current progress: thesis and formulation audit complete. Exact replication is blocked by missing source and data.

## Task 2: Solution Exploration and Design

1. Implement a deterministic minimum cost graph or A* baseline.
2. Define a goal conditioned state with velocity, heading, deadline, radio candidates, and resource masks.
3. Define continuous motion actions and masked discrete telecom actions.
4. Treat arrival and safety as hard or lexicographic requirements.
5. Compare PPO, Soft Actor Critic, and a mixed action method only after environment validation.

Current progress: formulation and initial method selected. Reward, action,
radio, and mission first evaluation utilities have 22 passing unit tests.

## Task 3: Implementation and Training

1. Integrate the recovered channel database behind a versioned environment adapter.
2. Train the simplest viable controller first.
3. Use multiple seeds, held out route pairs, and fixed evaluation scenarios.
4. Record return components, success rate, violations, sample count, wall time, policy entropy, and critic diagnostics.
5. Tune on validation scenarios only.

Current progress: the reusable formulation layer is started, but environment
integration and training are blocked because the assets are unavailable.

## Task 4: Controlled Evaluation

1. Compare greedy, shortest path, radio aware graph search, reimplemented legacy PPO, and the new controller.
2. Use paired scenario seeds and identical starts, goals, deadlines, traffic, and channel states.
3. Report mission success first, followed by conditional navigation and telecom metrics.
4. Plot paths on the same urban grid.
5. Report confidence intervals, failure modes, and the Pareto tradeoff surface.

Current progress: metric protocol designed; no trained comparison yet.

## Immediate External Request

Ask the supervisor or Marina for:

1. `JointHandoverTrajectoryOptimization` source at the thesis commit.
2. The channel database and its generation metadata.
3. Original PPO checkpoints and training logs if retained.
4. Exact seeds and route pairs behind Figures 5 through 10.
