# Proposal Task Map

Source: `references/proposals/I2R_proposal_UAV.pdf`, pages 1 and 2.

| Proposal item | Required artifact | Acceptance evidence | Current state |
| --- | --- | --- | --- |
| 1.1 Inspect ray tracing results | Dataset inventory and visual audit | Shapes, units, coverage, missing values, representative slices | Blocked by missing database |
| 1.2 Replicate legacy baseline | Reproducible greedy and PPO runs | Config, seeds, checkpoints, raw traces, metric match | Blocked by missing code and database |
| 1.3 Diagnose previous results | Baseline failure report | Thesis evidence, reward audit, environment tests | Initial report complete |
| 2.1 Review methods | Literature map | Primary sources and method comparison | Initial map complete |
| 2.2 Propose solution | Formal method note | Objective, constraints, algorithm, failure safeguards | Initial design complete |
| 2.3 Map state, action, reward, and interface | Environment specification | Typed schema and transition contract | Initial typed reward, mixed action, radio, and metric code complete |
| 3.1 Implement framework | Training code | Unit tests and environment checks | Formulation utilities tested; environment waiting for assets |
| 3.2 Train and tune | Versioned experiments | Multiple seeds and validation only tuning | Not started |
| 3.3 Document learning behavior | Training report | Convergence, sample efficiency, stability | Not started |
| 4.1 Controlled benchmark | Benchmark runner | Same scenarios for all methods | Protocol drafted |
| 4.2 Evaluate improvements | Result tables | Success plus conditional telecom and navigation metrics | Not started |
| 4.3 Visualize and report | Path figures and final report | Reproducible figures and documented limits | Reward diagnostic figure complete; real trajectory figures not started |

## Proposal Objective

Maximize trajectory success and SINR while minimizing transmission delay, energy use, flight time, uplink interference, and redundant handovers.

The proposal does not specify how to trade these quantities. This project interprets mission success and safety as requirements, not just additional weighted terms.
