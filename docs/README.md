# Research Documentation Index

Updated 14 September 2026. This index separates the completed received data
study from historical proposals and asset searches, preventing obsolete blocked
status or preliminary hypotheses from being mistaken for current findings.

## Current V2 Study and Original Reward Control

The current paper contains the V2/V1.5 comparison and a separately declared
V2.1 service reward followup. V1.5 is the original written reward
on the complete V2 system. The initial comparison does not establish improved
completion from reward replacement: both reach 95.7% on standard routes;
full reaches 87.3% versus 85.8% on longer routes, with both difference intervals
including zero. Lower aggregate radio cost coexists with substantially higher
delay. Those initial results use test seeds 53012 and 53013.

The V2.1 followup uses new 54012/54013 routes and adds five trained policies.
It does not meet the completion first priority: 95.48% versus 96.92% standard
success and 88.60% versus 91.84% longer success for V2.1 versus full V2.
Its complete uncertainty and service results are in note 48. The failed
improvement attempt remains part of the record; V2.1 is not promoted as the
main model.

The supplied Barcelona HDF5 is **the same dataset used in the original
thesis**. [Note 43](43_confirmed_thesis_dataset_identity.md) records the
confirmation and supersedes earlier uncertainty about dataset identity.

| Document | Purpose |
| --- | --- |
| [35: Dataset and model setup](35_dataset_and_model_setup.md) | Dataset path, 15 included weights, installation, evaluation and retraining |
| [36: Frozen V1.5 comparison protocol](36_v15_reward_comparison_protocol.md) | Original reward definition, identical V2 controls, reused weights and fresh tests |
| [37: New results and every seed](37_v15_reward_results.md) | Null primary finding, failures, paired metrics and interpretation |
| [38: Paper and model release](38_v2_paper_and_model_release.md) | Current paper, model manifest, replay and delivery checks |
| [40: Trajectory figure context audit](40_trajectory_figure_context_audit.md) | Missing station markers, a 222 m example without handovers, and the limits of visual comparison |
| [41: Long route figure revision](41_long_route_figure_revision.md) | A 1,784.7 m illustration with station context, handovers, eight diagnostics and 600 exact replay matches |
| [42: Current findings and thesis differences in the README](42_readme_current_findings_and_thesis_differences.md) | Shared changes, the reward contrast, general results, visible failures and revised causal conclusions |
| [43: Confirmed thesis dataset identity](43_confirmed_thesis_dataset_identity.md) | Confirmation that the supplied HDF5 is the same dataset as the original thesis; current paper and README corrected |
| [44: Original thesis comparisons throughout the README](44_readme_original_thesis_comparisons.md) | Original parameters and results beside current values, approximate figure readings, unavailable metrics and comparability limits |
| [45: Metric directions and interpretation](45_metric_directions_and_interpretation.md) | Current values beside source readings, higher or lower guidance, service tradeoffs and the improvement request |
| [46: V2.1 development protocol](46_service_reward_development_protocol.md) | Bounded reward candidates, completion first selection, fixed requirements and a fresh evaluation gate |
| [47: V2.1 development results](47_service_reward_development.md) | Every pilot, the selected service reward and unsuccessful stronger penalty candidates |
| [48: V2.1 fresh evaluation](48_service_reward_results.md) | New 54012/54013 results, completion first verdict, all seeds, failures and matched service metrics |
| [49: V2.1 models and reproduction](49_service_reward_models_and_reproduction.md) | Five additional final weights, dataset location, standalone evaluation and separate reproduction labels |
| [50: Clear metric descriptions and consistent units](50_clear_metric_descriptions_and_units.md) | Physical meaning, common interference units and separate rows for incompatible source quantities |
| [Current status](12_task_status.md) | Completed current work and remaining research questions |
| [Paper](../paper/README.md) | Current manuscript and build commands |

## Earlier Study Records

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
| [35: Dataset and model setup](35_dataset_and_model_setup.md) | Exact artifact paths, installation, checkpoint compatibility, execution examples, outputs, and troubleshooting |
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

The current comparison is complete: five new original reward policies, ten
reused V2 policies, 400 fresh routes, 73 tests and 7,600 exact replays.
The primary completion contrast is null. Full reward reduces handovers and
flight time but increases delay and proxy energy; no overall superiority is
established. Notes 36-38 are the current protocol, result and delivery record.

Earlier numbered notes preserve their contemporaneous findings and limitations.
They are not current release status. Future work needs independent tests and
separate component ablations, with all existing freezes preserved.
