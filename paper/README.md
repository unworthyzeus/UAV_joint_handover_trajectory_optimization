# Current IEEE Research Paper

[UAV_joint_reward_connectivity_IEEE.pdf](UAV_joint_reward_connectivity_IEEE.pdf)
is the current paper, **Reward Design under Shared Connectivity Constraints
for Cellular UAV Control**, by Guillem Moreno Garcia and Evgenii Vinogradov.
It contains the V2/V1.5 original reward comparison and a separately declared
V2.1 service reward followup. It is an IEEE format research draft, not an
accepted publication.

The study uses **the same Barcelona ray tracing dataset as the original
thesis**, confirmed by the researcher who supplied it. The private HDF5 is
preserved unchanged. The environment, controllers and experimental protocol
are our implementation; the original simulator and trained policies remain
unavailable. See the [dataset provenance update](../docs/43_confirmed_thesis_dataset_identity.md).

The initial primary standard comparison is null: original and full both achieve 95.7%
joint success, difference 0.0 percentage points [-2.8, 2.7]. Longer completion
is 85.8% versus 87.3%, difference +1.5 points [-2.9, 6.1]. Full trades fewer
handovers and shorter flights for higher communication delay. The paper retains
all failures and does not claim overall PPO or reward superiority.

The initial comparison tables use route seeds 53012 and 53013. The V2.1
followup tables use new 54012/54013 routes and report its own completion and
service results. Those samples are not pooled. The earlier arrival study is
absent from the final paper. All twenty final weights are included in Git;
the private map is still required separately. See the
[initial setup guide](../docs/35_dataset_and_model_setup.md),
[V2.1 setup](../docs/49_service_reward_models_and_reproduction.md),
[initial checkpoint manifest](../models/checkpoint_manifest.json) and
[V2.1 manifest](../models/service_reward_manifest.json).

The V2.1 candidate does not satisfy the requested completion first priority:
its fresh success is 95.48% versus full V2's 96.92% on standard routes and
88.60% versus 91.84% on longer routes. Its complete paired intervals, service
metrics and failures are in [note 48](../docs/48_service_reward_results.md).
The paper retains this unsuccessful improvement attempt as part of the
evidence rather than promoting the candidate as the main model.

## Sources and Generated Artifacts

- `unified.tex`: main file, source requirements and shared V2 model.
- `v15_front.tex`: abstract and introduction.
- `v15_protocol.tex`: original reward and controlled experimental design.
- `v15_findings.tex`: results, limits, conclusion and appendices.
- `v15_macros.tex` and `v15_*_table.tex`: generated from verified fresh results.
- `v21_followup.tex`, `v21_abstract.tex`, `v21_conclusion.tex` and `v21_seed_table.tex`: generated from the separate V2.1 analysis.
- `../results/reward_comparison/analysis_v15/`: statistics, three figures and paper audit.
- `../results/service_reward_v21/`: pilot outcomes, final weights, fresh records, analysis and exact replay.

The trajectory illustration now uses the longest of the 200 declared longer
test routes: 1,784.7 m, selected by geometry without filtering on outcomes.
It includes all 87 station markers, a route zoom, handover locations, and
eight time series for RSS, SINR, queue, capacity, handovers, delay, energy and
interference. See the [reporting revision](../docs/41_long_route_figure_revision.md)
for selection, exact replay checks and retained limitations.

The source retains printed page locators for each original thesis citation.
The [protocol](../docs/36_v15_reward_comparison_protocol.md),
[results](../docs/37_v15_reward_results.md), and
[delivery note](../docs/38_v2_paper_and_model_release.md) explain the evidence.

## Build and Verify

From the repository root, generate reporting artifacts from saved results:

```powershell
python scripts/analyze_reward_comparison.py
python scripts/build_reward_comparison_report.py
python scripts/analyze_service_reward_study.py
python scripts/build_service_reward_report.py
```

The report builder uses committed verified dense traces for the long route
figures and does not require the private map. To recover those traces from
the unchanged simulator and checkpoints, with the private dataset available:

```powershell
python scripts/replay_long_route_illustration.py
python scripts/build_long_route_figures.py
```

The replay verifies all 600 original longer batch episode records for the
three illustrated controllers. It does not add new independent evaluation
episodes. Compilation alone uses the committed figures and requires no dataset.
With Tectonic installed, compile from `paper/`:

```powershell
tectonic -X compile unified.tex --outdir build_unified
Copy-Item -LiteralPath build_unified/unified.pdf -Destination UAV_joint_reward_connectivity_IEEE.pdf
```

The delivered build uses the LaTeX plugin compile helper. Its structured report
is retained at `build_unified/compile_report.json`. After a new helper build,
retain that new report and run from the repository root:

```powershell
python scripts/audit_v2_reward_paper.py
```

The audit requires PyMuPDF and Pillow in addition to experiment dependencies.
It checks all four source freezes, twenty checkpoint hashes, 7,600 initial
and 18,000 followup exact replays,
printed page citations, embedded fonts, final pass references, text bounds and
absence of the historical arrival study. Rendered pages require separate visual
review; a prior build report alone cannot validate a changed PDF.

## Archived Manuscripts

The prior consolidated source and PDF have a `20260912` suffix. Earlier
standalone drafts also remain as historical artifacts. They are superseded by
the current PDF above and must not be combined with the new test results.
