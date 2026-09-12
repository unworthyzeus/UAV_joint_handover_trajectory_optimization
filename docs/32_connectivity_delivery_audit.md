# Connectivity Study Delivery Audit

Date: 12 September 2026.

Publication addendum: the user subsequently requested one consolidated paper
and a GitHub push. Note 33 records that release. The statements below about
local delivery and no push describe the earlier delivery, before that request.
The current paper is `paper/UAV_joint_reward_connectivity_IEEE.pdf`; the four
page report below remains an unchanged historical artifact.

## Completed Work

Implemented a separately versioned sampled connectivity repair using the
thesis's RSS and buffer requirements and its delay/interference/handover
tradeoff. The user declined new packet deadlines or empty queue arrival rules.
The new study includes resource actions, a prospective safety filter, residual
motion learning, and deterministic radio and joint planning references.

The final five seed comparison and every development run are complete. All
artifacts are local. No dataset, manuscript, message, or repository change was
published, submitted, committed, or pushed. No training remains running.

## Results and Claim Boundary

Full PPO joint success is 96.6% standard and 89.7% longer. Arrival only PPO,
under the same strict constraints and architecture, achieves 96.9% and 86.3%.
The full reward reduces accumulated weighted radio cost by 24.5% and 14.7% on
paired successful routes, but delay rises substantially and completion
differences are uncertain. The strong learned joint improvement gate is not met.

Goal radio has the highest observed completion, 98.0% and 92.5%. On longer
routes it improves completion over Goal RSS by 5.5 percentage points, interval
[1.5, 9.5], and reduces accumulated weighted cost by 41.0% on 171 paired
successful routes. Local joint planning offers lower successful flight costs
with remaining completion tradeoffs. These are separate controller findings,
not an established PPO advantage.

The full results, all seeds, failure counts, uncertainty, metrics and commands
are in note 30. Note 31 explains every implementation difference with printed
TFM page references. Notes 28 and 29 retain the frozen protocol and development
history. The original v1 study and IEEE PDF remain separate historical artifacts.

## Verification Evidence

| Check | Result |
| --- | --- |
| Complete unit suite | 51 passed, including 17 new behavioral checks |
| Final trained policies | 10 checkpoints, five seeds for each of two arms |
| Final training budget | 5,242,880 interactions total |
| Development policies retained | 6 checkpoints across three designs |
| Learned final evaluations | 4,000 episodes |
| Deterministic final evaluations | 1,600 episodes across four references |
| Exact evaluation replay | All 5,600 original episode records match |
| Successful mission constraints | All reported successes have sampled RSS ≥ −96 dBm, zero overflow, and valid arrival/stopping tolerances |
| Original v1 freeze | All six hashed files match |
| New v2 freeze | All seven hashed files match |
| Raw dataset | SHA256 matches the original received file |
| Final IEEE PDF | Four pages, 18 embedded fonts, no Type 3 fonts |
| Original TFM manuscript citations | 24, all with printed page locators |
| References and layout | No unresolved references or overfull boxes; final rendered pages visually reviewed |

The environment remains a one second surrogate with static occupancy and
uncalibrated downlink capacity, interference, and energy models. Tests and exact
replay establish implementation consistency, not physical validation. The
written original C2 and C4 are on printed p. 11, Eq. (12); numerical RSS and
buffer settings are on printed p. 15, Table 3. Their original simulator has
not been recovered.

## Reporting Correction

The frozen estimator has a generic relative percentage field for all secondary
metrics. Percentages of logarithmic SINR values are not physically interpretable.
The original `statistics.json` and frozen estimator are preserved. A separate
`finalize_connectivity_statistics.py` creates `report_statistics.json`, setting
only those unused SINR percentage fields to null and recording the original
file hash. Absolute dB differences, all other estimates, and all confidence
intervals are unchanged. The manuscript uses absolute SINR differences.

This is a disclosed reporting correction, not a test driven change to the
controller, metric values, or statistical estimator. It is recorded outside
the experiment freeze.

## Manuscript and Reproduction Files

- `paper/UAV_connectivity_repair_IEEE.pdf`: final four page IEEE format research report.
- `paper/connectivity.tex`: editable manuscript with requested authors Guillem
  Moreno Garcia and Evgenii Vinogradov.
- `paper/connectivity_macros.tex`, `connectivity_results_table.tex`, and
  `connectivity_paired_table.tex`: generated values and tables.
- `paper/build_connectivity/compile_report.json`: final Tectonic build record.
- `results/connectivity_experiment/analysis_v2/artifact_audit.json`: PDF, source,
  dataset, citation and replay checks.
- `results/connectivity_experiment/replay_v2/audit.json`: all exact replay counts
  and checkpoint hashes; adjacent files contain detailed first route traces.
- `scripts/evaluate_connectivity_controller.py`: evaluate a saved checkpoint
  or deterministic controller on saved or custom in bounds routes.
- `scripts/build_connectivity_paper_artifacts.py`: figures and generated TeX.
- `scripts/audit_connectivity_artifacts.py`: reproducible file and PDF checks.

The evaluation CLI was exercised with a custom route and the first final full
checkpoint on validation. Those 65 interface checks are not added to the 5,600
frozen test evaluations and are not new confirmatory evidence.

The paper is a local research draft. It reports the useful positive radio
selection result and the mixed learned results; it is not an accepted IEEE
publication or proof that the original thesis has been fully reproduced.

## Remaining Research

The formulation and endpoint omission has been corrected within the declared
model. Remaining failures, large allowed delay, and physical modeling limits
are explicit. A claim of uninterrupted real flight connectivity needs finer
sampling and independent physical validation. A stronger controller claim needs
a new, independently frozen study. No new application service requirement
should be introduced without matching the intended task.
