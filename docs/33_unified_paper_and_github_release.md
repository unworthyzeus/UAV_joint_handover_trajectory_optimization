# Unified Paper and GitHub Release

Date: 12 September 2026.

## What Was Done and Why

The user requested a GitHub push and then asked to put everything into a single
paper and push it. Created `paper/unified.tex` and `unified_appendices.tex`,
compiled as `paper/UAV_joint_reward_connectivity_IEEE.pdf`, with requested
authors Guillem Moreno Garcia and Evgenii Vinogradov. Updated the repository,
documentation index, status and paper guide to make this the current paper.
The original two sources and PDFs remain unchanged historical records.

The consolidation is a coherent scientific narrative with one abstract,
introduction, shared model description, interpretation, conclusion and
bibliography. Study I is the frozen reward/termination comparison v1; Study II
is the separately frozen strict connectivity comparison v2. The connectivity
audit explains the transition between them. The manuscript includes the methods,
splits, principal results, paired uncertainty, failed designs, and five figures.
Four appendices contain the original model/PPO comparison, every executed v2
change, both complete observation layouts, development outcomes and artifact map.

## Result and Interpretation

The final paper has 15 pages: ten pages of main text, figures and references,
followed by five pages of appendices. It contains 104 original TFM citations
with printed page locators; the PDF viewer offset remains plus two.

The scientific results are unchanged. Study I supports repairing the written
reward within its reimplementation: standard arrival rises from 21.4% to 100%
with reward replacement alone, while termination alone gives 0%. That arrival
criterion did not establish maintained connectivity. Study II makes strict
sampled RSS and buffer constraints part of success and restores every radio
cost. Full PPO achieves 96.6% standard and 89.7% longer joint success; its
weighted radio cost improves while delay rises. The learned completion effect
is uncertain. Goal radio reaches 98.0% and 92.5% and provides the positive
deterministic result. The paper retains all these limits.

The revision adds no experiment, checkpoint selection or statistical estimate.
Generated tables and macros still use the existing statistics. It explicitly
discloses the earlier SINR percentage reporting correction and distinguishes
all surrogate choices from original thesis definitions.

## Validation

- All 51 tests passed again; the CPU run emitted the existing optional CUDA warning.
- All six v1 and seven v2 frozen source/protocol hashes still match.
- The previous exact replays remain 4,400 audit flights and 5,600 final v2 flights;
  consolidation does not claim to have rerun those simulations.
- Tectonic compiled the final PDF with no unresolved references, missing glyphs
  or overfull boxes. All 29 fonts are embedded, with no Type 3 fonts.
- Every rendered page was reviewed for layout; the final main page has balanced
  columns, and figures, equations and multipage tables remain legible.
- The structural citation audit found 104 pinpoint TFM citations. Semantic
  support follows the previously reviewed definition index in notes 25 and 31;
  the structural check alone does not establish semantic support.
- `results/tables/unified_paper_audit.json` records PDF, manuscript, statistics
  and frozen source checks. `paper/build_unified/compile_report.json` records
  the final build.

## GitHub Release Scope and Exact Bytes

The requested destination is the existing `origin`, branch `main`, at
<https://github.com/unworthyzeus/UAV_joint_handover_trajectory_optimization>.
The release includes project code, tests, configuration, research notes, raw
evaluation records, statistical analysis, source snapshots, figures, TeX and
the consolidated PDF. Earlier separate PDFs remain historical records.

The private 2.33 GB HDF5 and trained checkpoint binaries are excluded by
`.gitignore`; scratch renders and build intermediates are also excluded.
The user authorized publishing the repository work, not redistribution of the
private dataset. Reproduction therefore still requires authorized data access
and either retraining or obtaining local checkpoint binaries separately.

Git was configured with `core.autocrlf=true`. Some frozen files use LF, others
CRLF, and one has mixed line endings. Automatic normalization would invalidate
their byte hashes. Added `.gitattributes` rules disabling text conversion for
the 13 frozen source/protocol files and recorded results, including all source
snapshots. TeX files likewise retain their exact bytes for the source audit.
These attributes do not modify experimental contents. The staged blobs are
checked against the freeze manifests before the commit is pushed.
The two initial reward diagnostic records retain their already committed Git
normalization. The historical appendix's final blank line is also retained;
its whitespace check exception avoids rewriting the archived source.

## Remaining Work, Risks and Next Decision

No research work remains for this consolidation. The source simulator, exact
dataset version identity, independent maps, dynamic load, switching interruption
and continuous physical connectivity remain unverified. The two studies have
different endpoints and controller architectures; their success rates are not
a causal comparison across versions. This is an IEEE format research draft,
not an accepted or submitted publication. A future submission requires a venue
and its page limit; shortening this complete draft must preserve the negative
results and source traceability. New scientific claims require a new protocol
and independent evaluation rather than editing either frozen experiment.
