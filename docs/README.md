# Research Documentation Index

Updated 13 September 2026. This index separates the completed received data
study from historical proposals and asset searches, preventing obsolete blocked
status or preliminary hypotheses from being mistaken for current findings.

## Completed Experiment

| Note | Purpose |
| --- | --- |
| [17: Received dataset assessment](17_received_dataset_assessment.md) | Full data audit, provenance, and reward hypothesis |
| [18: Experiment protocol](18_experiment_protocol.md) | Frozen model, physical units, treatments, and evaluation |
| [19: Implementation and validation](19_implementation_and_validation.md) | Environment corrections, 34 tests, exact checkpoint replay |
| [20: Pilots and frozen comparison](20_pilots_and_frozen_comparison.md) | Development history, seeds, budget, and freeze |
| [21: Confirmed results](21_confirmed_results.md) | Every final seed, uncertainty, and retained negative outcomes |
| [22: Reproduction guide](22_reproduction_guide.md) | Runtimes, commands, checkpoints, and artifact locations |
| [23: Manuscript and final audit](23_manuscript_and_final_audit.md) | Paper build, quality review, final checks, and remaining limits |
| [24: Training, validation, and test separation](24_train_validation_test_comparison.md) | Verified split counts and comparison with the original thesis's methods |
| [25: Exact changes from the TFM](25_exact_changes_from_tfm.md) | Complete comparison, every implemented parameter, and original page/equation/table index |
| [26: TFM citation revision](26_tfm_traceability_revision.md) | Manuscript revision, pinpoint citation checks, and frozen experiment integrity |
| [27: Connectivity objective audit](27_connectivity_objective_audit.md) | 4,400 exact flight replays, service deficits, and the gap between arrival and maintaining connectivity |
| [28: Strict connectivity protocol](28_connectivity_experiment_protocol.md) | Frozen thesis requirements, controller design, splits, budget, and analysis |
| [29: Connectivity development log](29_connectivity_development_log.md) | Six pilots, all failed designs, and final freeze decision |
| [30: Connectivity results and reproduction](30_connectivity_results_and_reproduction.md) | Five seed results, deterministic comparisons, uncertainty, failures, and commands |
| [31: Exact connectivity changes](31_exact_connectivity_changes.md) | Complete v1 to v2 differences and original TFM page references |
| [32: Connectivity delivery audit](32_connectivity_delivery_audit.md) | Final paper, integrity checks, reporting correction, and retained limitations |
| [33: Unified paper and GitHub release](33_unified_paper_and_github_release.md) | Single consolidated paper, complete appendices, PDF review, byte preservation, and release scope |
| [34: Complete thesis inventory in the README](34_readme_thesis_inventory.md) | Exhaustive twelve category inventory, both study versions, all numerical settings, source pages, and documentation checks |
| [Current status](12_task_status.md) | Completed work versus original replication dependency |
| [Logbook](13_logbook.md) | Chronological decisions and corrected interpretations |
| [IEEE paper](../paper/README.md) | Manuscript, PDF, build instructions, and claim boundaries |

## Earlier Work

Notes 00–08 record the proposal, original thesis diagnosis, literature map,
initial solution design, and earlier evaluation plan. Notes 09–16 record data
sources, risks, the first abstract reward diagnostic, radio equation audit,
and missing asset search. They preserve history rather than define the final
frozen training run. In particular, the old abstract distance trace should not
be counted as a failed physical mission under the final 10 m arrival tolerance.

## Result and Next Decision

The latest v2 study repairs the sampled connectivity endpoint and restores the
full communication cost. Full PPO achieves 96.6% standard and 89.7% longer
joint success; Goal radio achieves 98.0% and 92.5%. Weighted cost improves while
PPO delay worsens. The learned completion difference is uncertain. Notes 28–32
are the current record; notes 17–27 preserve the earlier study and diagnosis.

The following paragraph describes the earlier v1 arrival study:

Reward replacement alone achieved 100% mission success on both route splits;
the deterministic reference did too. Success termination during training was
not sufficient and reduced longer route performance when combined with the
replacement reward. This supports the reward hypothesis in the reimplementation.

The requested study and paper are complete. Direct replication of the original
policy remains dependent on its simulator and artifacts. Future experiments
should preserve this freeze and independently test traffic, geography, and
physical assumptions before claiming broader controller usefulness.

The connectivity audit in note 27 limited that v1 completion statement: arrival
and its permissive feasibility label did not establish the joint objective.
The separate v2 study in notes 28–32 now corrects the sampled communication
endpoint using the thesis requirements. Remaining failures and the distinction
between sampled feasibility and real continuous service remain explicit.
