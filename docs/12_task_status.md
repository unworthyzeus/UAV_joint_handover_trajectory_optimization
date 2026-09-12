# Research Task Status

Updated 12 September 2026 after paper consolidation for the requested GitHub release.

The current deliverable is the single 15 page
[consolidated IEEE paper](../paper/UAV_joint_reward_connectivity_IEEE.pdf),
covering both studies with 104 pinpoint TFM citations and detailed appendices.
Note 33 records consolidation, validation, and release scope. Earlier PDFs are
historical versions; no experiment was rerun or revised for consolidation.

The v2 objective and endpoint repair is complete. The full learned controller
achieves 96.6% standard and 89.7% longer joint success; the simpler radio
controller achieves 98.0% and 92.5%. Every reported success satisfies sampled
RSS and buffer constraints. Delay tradeoffs and remaining failures are retained.
There are 51 passing tests, 5,600 exact v2 evaluation replays, the consolidated
IEEE paper, and complete change notes. See notes 28–33 for current results and
limits. This does not establish an overall PPO advantage or real continuity
between the one second samples.

The table below preserves the completed earlier v1 study's status and counts.

| Task | Status | Evidence | Remaining scope |
| --- | --- | --- | --- |
| Inspect ray tracing data | Complete for received file | Full scan, checksum, schema, and coverage in note 17 | Confirm exact thesis version and sentinel convention |
| Replicate original baseline | Externally blocked | Headline map specifications agree with thesis | Original code, scene, routes, seeds, and checkpoints absent |
| Explicitly reimplement reward comparison | Complete | Shared environment and hybrid PPO, notes 18–19 | Does not establish source equivalence |
| Diagnose reward formulation | Positive controlled evidence | Four treatments, five seeds each, note 21 | Confirm diagnosis in original code |
| Train and document learning | Complete | Six pilots and twenty final policies; note 20 | New studies need fresh protocols and test routes |
| Controlled benchmark | Complete | 8000 learned test episodes and 400 reference episodes | Same city and static background load |
| Validate implementation | Complete | 34 passing tests and exact 200 episode checkpoint replay | Physical model requires independent validation |
| Analyze uncertainty | Complete | Paired crossed seed and route bootstrap, all seeds retained | Five seeds limit tail inference |
| Visualize and report | Complete | Generated figures, Markdown record, IEEE manuscript and PDF with requested authors | Draft requires venue review before submission |

## Earlier v1 Claim

In this declared reimplementation, legacy reward success is 21.4% on standard
routes and 0% on longer routes. Reward replacement alone reaches 100% on both,
while the combined reward and training termination change reaches 99.7% and
36.1%. Termination alone reaches 0%. All evaluation ends at first safe arrival.
The positive gate passed. This updates the earlier assumption that success
termination would necessarily improve learning.

The deterministic reference also completes all routes and is faster. The result
supports objective repair under the shared assumptions; it does not demonstrate
superiority over classical control or Marina's actual saved policy.

## Why and What Remains

The completed experiment makes the reward hypothesis testable with available
assets. The requested implementation, controlled test, Markdown record,
and conditional IEEE paper are complete. Future research should recover the
original simulator and validate the stated radio, traffic, energy, and obstacle
assumptions. That separate replication remains dependent on external assets.

See notes 21–23 for results, reproduction, and final audit. Preserve frozen
source hashes and test results when starting any follow up study.
