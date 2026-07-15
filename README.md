# Joint Handover and Trajectory Optimization in 5G Connected UAVs

Research workspace for the I2R proposal on joint UAV flight, handover, and radio resource optimization in a deterministic 3D ray traced urban environment.

## Current Finding

Marina Bermúdez Granados built the valuable part that should be preserved: a realistic Barcelona channel environment, 3GPP A3 handover logic, resource allocation, and a PPO baseline. The main failure was objective misalignment. The learned controller accumulated connectivity rewards but did not reliably finish the flight. The thesis itself concludes that the policy favored persistent connectivity over task completion.

This was not simply a weak PPO configuration. The listed state omitted velocity and goal relative information, the natural motion variables were discretized and combined with base station and resource choices, arrival did not terminate the episode, and the evaluation omitted trajectory success rate. Under that formulation, wandering can score well.

## What This Project Optimizes

The optimization hierarchy is:

1. Reach the destination within the deadline and terminal speed tolerance.
2. Respect map, speed, energy, buffer, and minimum connectivity constraints.
3. Among feasible successful missions, minimize flight time, propulsion energy, transmission delay, uplink interference, outage, and redundant handovers while maximizing SINR.

The first proposed architecture is a constrained mixed action controller:

1. A graph or A* reference planner provides a mission completing route and a deterministic benchmark.
2. A continuous flight policy controls acceleration and heading.
3. A masked discrete policy selects valid handover and resource actions at a slower decision rate.
4. A constrained or lexicographic objective prevents secondary radio metrics from replacing the mission.

## Current Status

Completed now:

1. Proposal extraction and task map.
2. Visual and textual audit of Marina's 2026 thesis.
3. Formal diagnosis of the reward, state, action, termination, and evaluation design.
4. Initial literature map for constrained control, continuous control, and mixed action reinforcement learning.
5. Executable reward alignment diagnostic and mission first metric utilities.

The current action class is deliberately an unmasked audit interface for the
legacy 87 base station by 12 resource group choice. The masked candidate action
described above remains blocked on the missing channel and resource adapter.

Blocked external inputs:

1. The GitHub repository printed in the thesis currently returns 404.
2. The deterministic channel database, processed station snapshot, exact
   geometry transform, routes, seeds, checkpoints, and logs are unavailable.

An exhaustive local and public search found the upstream 3D GloBFP geometry and
a promising Barcelona geometry substitute, but not Marina's exact
reproducibility bundle. See
[`docs/16_missing_asset_search.md`](docs/16_missing_asset_search.md) for the
complete asset list, every location searched, sources found, and limitations.
Exact baseline replication and model training cannot be claimed until the
critical assets are obtained or a clearly labeled replacement environment is
built.

## Structure

| Path | Purpose |
| --- | --- |
| `docs/` | Proposal map, baseline diagnosis, formulation, method, protocol, risks, and logbook |
| `src/uav_joint_optimization/` | Reusable reward, action, and evaluation logic |
| `scripts/` | Reproducible diagnostics and later training entrypoints |
| `configs/` | Versioned objective and experiment settings |
| `data/` | Raw and derived channel data, ignored except placeholders |
| `results/` | Diagnostic and future benchmark tables and figures |
| `references/` | Proposal and source page shortcuts |
| `sources/` | Local research PDFs, including Marina's thesis |
| `experiments/` | Versioned experiment definitions and notes |
| `paper/` | Reserved for the final report or paper |

## Run the Initial Audit

```powershell
python scripts/run_reward_diagnostic.py
python -m pytest tests
```

The reward diagnostic uses hand written traces to expose an incentive bug. It is not a trained performance comparison and must not be cited as evidence that the proposed learning algorithm outperforms the legacy policy.

The validated audit gives the never arrive trace a discounted return of 79.65
and direct arrival 69.95 under the legacy equations. The mission first audit
reverses that order to -18.17 and 21.05 respectively. See
`results/figures/reward_alignment_diagnostic.png` and
`docs/11_initial_reward_diagnostic.md` for the protocol and limitations.

## Primary Sources

The canonical proposal is at `references/proposals/I2R_proposal_UAV.pdf`.

The baseline thesis is at `sources/UAV_Bermudez_Granados_2026_MSc_thesis.pdf`, with the official [UPCommons record](https://upcommons.upc.edu/entities/publication/a8ce08c2-c238-4145-a5ab-5d39b12c6553).
