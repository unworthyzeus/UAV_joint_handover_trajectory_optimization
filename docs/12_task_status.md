# Research Task Status

Updated 14 September 2026 after the V2.1 reward improvement attempt.

The current [paper](../paper/UAV_joint_reward_connectivity_IEEE.pdf) contains
V2 and its V1.5 original reward control, plus the separate V2.1 followup.
Historical V1 is excluded from the
final paper and reduced to one brief note in the root README.

The new candidate does not meet the user's completion first priority: fresh
standard success is 95.48% versus full V2's 96.92%, and longer success is
88.60% versus 91.84%. It remains an evaluated research candidate rather than
the main model. [Note 48](48_service_reward_results.md) reports the paired
uncertainty, service metrics and all failures. [Note 49](49_service_reward_models_and_reproduction.md)
documents the additional five weights and reproduction commands. The source
comparison table now includes our numerical values and preferred metric
directions; [note 45](45_metric_directions_and_interpretation.md) explains them.

The table below preserves the status of the initial V1.5/V2 comparison.

| Task | Status | Evidence |
| --- | --- | --- |
| Original reward on identical V2 system | Complete | Reward adapter, transition identity tests and frozen protocol, note 36 |
| New training | Complete | Five seeds, 524,288 interactions each; 2,621,440 new interactions |
| Reused V2 weights | Verified | All ten policies fixed by hash before new training and tests |
| Fresh paired evaluation | Complete | 400 new routes, 7,600 final episodes, note 37 |
| Primary completion result | No improvement established | Both 95.7% standard; full minus original 0.0 points [-2.8, 2.7] |
| Longer completion | Uncertain difference | Full 87.3%, original 85.8%; +1.5 points [-2.9, 6.1] |
| Communication interpretation | Tradeoff retained | Full reduces handovers and flight time but increases delay and energy; no overall superiority |
| Verification | Complete | 73 tests and 7,600 exact replays; all three source freezes match |
| Model release | 15 final policies | Five V1.5 plus ten V2, 2,054,910 bytes; manifest under models |
| Current documentation and paper | Updated | Notes 35-38, V2 README, generated paper tables and figures |
| Private dataset | Required separately | Exact path and SHA256 in setup guide |

The [result note](37_v15_reward_results.md) contains all seeds, failures and
paired secondary metrics. The [delivery note](38_v2_paper_and_model_release.md)
records the manuscript and model publication. The [setup guide](35_dataset_and_model_setup.md)
explains installation, checkpoints, dataset placement and exact commands.

## Remaining Research Scope

The result is conditional on the V2 navigation prior and filter. It neither
reproduces the original simulator nor isolates the cause of its behavior.
Single map, static load, ideal service, uncalibrated energy, no obstacle model
and one second sampling limit inference. No new application deadline or empty
queue condition is imposed. Next work requires independent tests and separately
frozen component ablations, not retuning on the current routes.
