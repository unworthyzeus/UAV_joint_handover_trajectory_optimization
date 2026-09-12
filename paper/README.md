# IEEE Research Paper

## Current Consolidated Paper

[UAV_joint_reward_connectivity_IEEE.pdf](UAV_joint_reward_connectivity_IEEE.pdf)
is the single current paper covering the entire study, by Guillem Moreno Garcia
and Evgenii Vinogradov. The editable sources are `unified.tex` and
`unified_appendices.tex`. It is a 15 page IEEE format research draft, including
five pages of detailed appendices, with 104 pinpoint TFM citations and a shared
bibliography. It is not an accepted or submitted IEEE publication.

The narrative integrates the original diagnosis, received data, controlled
reward/termination experiment, subsequent connectivity audit, strict connectivity
study, all principal results and negative findings, and the limits of inference.
Appendices retain the original model/PPO comparison, every v1 to v2 change,
both exact observation layouts, development failures, and the artifact map.
Arrival success in Study I and strict sampled joint success in Study II are
distinct endpoints. The paper does not infer a causal reward effect across
studies, or claim a PPO advantage.

The existing generated tables, macros and figures supply both studies' numbers.
No frozen source, original result, trained policy or prior manuscript was
changed during consolidation. The two earlier PDFs below are historical
versions; use the consolidated PDF for current reading and sharing.

Build from `paper/` using Tectonic:

```powershell
tectonic -X compile unified.tex --outdir build_unified
Copy-Item -LiteralPath build_unified/unified.pdf -Destination UAV_joint_reward_connectivity_IEEE.pdf
```

The validated build uses the bundled LaTeX compile helper, whose JSON output
is retained as `build_unified/compile_report.json`. After retaining that build
report, run `python scripts/audit_unified_paper.py` from the project root with
PyMuPDF and Pillow available. The audit renders every page, checks fonts and
citations, and verifies both experiment freezes. It records the manuscript and
statistics hashes in `../results/tables/unified_paper_audit.json`. Visual review
is a separate step. [Note 33](../docs/33_unified_paper_and_github_release.md)
records the final checks and publication scope.

The private map and checkpoint binaries are excluded from Git. Public source
and evaluation records support inspection; rerunning training requires authorized
access to the map, and saved policy replay also requires local checkpoints.

## Historical Connectivity Report (v2)

`UAV_connectivity_repair_IEEE.pdf` is the archived four page IEEE format report,
authored by Guillem Moreno Garcia and Evgenii Vinogradov. Its source is
`connectivity.tex`. It reports the separately frozen v2 repair with strict
sampled RSS and buffer constraints, all three thesis radio costs, ten final
PPO policies, four deterministic references, and 5,600 exactly replayed
evaluations. It includes 24 thesis citations with printed page locators.

The result is mixed: full PPO achieves 96.6% standard and 89.7% longer joint
success. Weighted communication cost improves, while delay worsens; the
prespecified strong learned improvement claim is not met. The simpler Goal
radio controller achieves 98.0% and 92.5%. Its improvement over strongest RSS
selection on longer routes is the useful positive deterministic finding.
This is a local research draft, not an accepted or submitted publication.

Generated inputs are `connectivity_macros.tex`, `connectivity_results_table.tex`,
and `connectivity_paired_table.tex`; figures and reporting statistics are under
`../results/connectivity_experiment/analysis_v2/`. The build report is in
`build_connectivity/compile_report.json`. The final PDF has embedded fonts,
no unresolved references, and four visually reviewed pages.

The [result and reproduction note](../docs/30_connectivity_results_and_reproduction.md)
contains evaluation and analysis commands. To build the PDF after generating
the verified inputs, run Tectonic against `connectivity.tex`, then copy
`build_connectivity/connectivity.pdf` to `UAV_connectivity_repair_IEEE.pdf`.
The [exact change note](../docs/31_exact_connectivity_changes.md) and
[delivery audit](../docs/32_connectivity_delivery_audit.md) explain all scope
limits and checks. Current claims apply at the simulator's one second samples.

## Earlier Arrival Reward Report

The positive result gate passed. An eight page IEEE conference style manuscript
reports the completed four treatment, five seed comparison on the received
Barcelona radio map. It is a local research draft, not an accepted or submitted
IEEE publication.

## Files and Provenance

- `UAV_reward_repair_IEEE.pdf`: compiled deliverable.
- `main.tex`: editable manuscript using the IEEEtran conference class.
- `thesis_comparison.tex`: comparison appendix with page specific TFM sources,
  covering the environment, objective, evaluation, and PPO parameters.
- `results_macros.tex`, `results_table.tex`, `metrics_table.tex`: generated
  numbers and tables from the validated statistics, never hand edited numbers.
- `../results/controlled_experiment/analysis_v1/`: figure PDF/PNG files and
  source statistics.

The authors are Guillem Moreno Garcia and Evgenii Vinogradov, in the order
requested by the user, with Universitat Politècnica de Catalunya as their
shared affiliation. Select a venue's exact template and page limit before
any submission. The authorship update is recorded in note 23.

## Rebuild

From the project root, regenerate the analysis and manuscript tables:

```powershell
python scripts/analyze_controlled_experiment.py
python scripts/build_paper_tables.py
python scripts/check_thesis_citations.py
```

Then compile from `paper/` with an installed TeX distribution:

```powershell
tectonic -X compile main.tex --outdir build
Copy-Item -LiteralPath build/main.pdf -Destination UAV_reward_repair_IEEE.pdf
```

The validated local build uses Tectonic 0.17.0 and IEEEtran 1.8b. Tectonic may
need network access for its package cache on the first build. The local Codex
LaTeX compile helper can also locate the bundled executable. The final build
report is retained in `build/compile_report.json`; render inspection and the
machine readable PDF check are under `../outputs/paper_review_final/`.

## Interpretation and Limits

**Historical v1 connectivity addendum:** [Note 27](../docs/27_connectivity_objective_audit.md)
audits 4,400 exactly replayed flights. The results establish improved arrival,
not completion of the full joint connectivity objective. Reward replacement
alone gives 100% standard arrival, but 92.2% arrival without any sampled RSS
outage, a mean capacity deficit fraction of 26.6%, and 20.2% arrivals with
nonempty buffers. The reward caps delay cost and has no direct interference
cost; recorded feasibility has no packet latency or minimum capacity condition.
The earlier v1 PDF should be read with this addendum and the new connectivity
report above. It is preserved unchanged. Frozen results and policies are unchanged.

Reward replacement alone reaches 100% mission success on both test splits.
Adding training termination gives 99.7% standard success but 36.1% longer route
success. The deterministic reference achieves 100% and is faster. All negative
and positive arms are retained. The paper explicitly states the repaired
common observation/action interface, physical proxies, static load pattern,
private dataset dependency, and unavailable original simulator.

The practical positive gate justified writing this paper; it does not establish
novelty, external validity, or publication acceptance. Raw shaping invariance
does not remove the effects of reward normalization and clipping during PPO.

## Original TFM Citations and Complete Comparison

Every TFM citation in the manuscript has a printed page locator. For example,
`\cite[p.~12, Eqs.~(13)--(14)]{thesis}` identifies the original reward
definitions, and `\cite[p.~15, Table~3]{thesis}` identifies their numerical
settings. These appear as citations such as `[1, p. 12, Eqs. (13)–(14)]`.
Add two to the printed number to find the PDF viewer page. Source equation
numbers belong to the thesis, independently of this manuscript's numbering.

[Note 25](../docs/25_exact_changes_from_tfm.md) contains the complete comparison,
definition index, all 42 observation features, every PPO setting, event ordering,
and explicit unknowns. Only reward and training termination vary within our
experiment; all other changes from the written thesis are shared. Notes 18
and 20 remain frozen historical protocol files, with their citation mapping
supplied by note 25. [Note 26](../docs/26_tfm_traceability_revision.md) records
the citation and manuscript checks.

The manuscript and reproduction package are complete for the frozen study.
The next research decision is direct original simulator replication or a new
independently designed test of traffic and geographic generalization. The full
audit is in `../docs/23_manuscript_and_final_audit.md`.
