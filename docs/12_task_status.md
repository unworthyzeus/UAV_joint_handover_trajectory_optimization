# Research Task Status

Updated 15 July 2026.

| Task | Status | Evidence | Main gap |
| --- | --- | --- | --- |
| 1.1 Inspect ray tracing results | Blocked | Comprehensive local and public asset audit in `docs/16_missing_asset_search.md` | Exact channel database unavailable; public geometry only |
| 1.2 Replicate legacy baseline | Blocked | GitHub, archives, research repositories, UPC bundles, and local files audited | No source, radio map, routes, seeds, or checkpoints |
| 1.3 Diagnose baseline | Initial completion | `docs/03_marina_baseline_diagnosis.md`, reward audit code | Must verify against source when recovered |
| 2.1 Literature review | Initial completion | `docs/06_literature_map.md` | Expand after baseline reproduction |
| 2.2 Propose solution | Initial completion | `docs/04_optimization_objective.md`, `docs/05_solution_architecture.md` | Select final algorithm after deterministic baseline |
| 2.3 Define state, action, reward, interface | Initial completion | Tested package and aligned config | Channel adapter unavailable |
| 3.1 Implement framework | Started | Reward, action, radio, and evaluation utilities; 22 tests | Requires environment assets |
| 3.2 Train and tune | Not started | None | Requires validated environment |
| 3.3 Document learning | Not started | Protocol only | Requires training runs |
| 4.1 Controlled benchmark | Designed | `docs/08_evaluation_protocol.md` | No runnable environment |
| 4.2 Quantitative evaluation | Not started | Diagnostic is not performance evidence | Requires baselines and trained models |
| 4.3 Visualize and report | Started | Validated reward diagnostic figure | Requires real trajectories |

## Honest Current Claim

The workspace has a source backed diagnosis, an executable reward alignment
check, and a documented exhaustive asset search. It does not yet have a
reproduced baseline, trained improved controller, or real comparative result.
