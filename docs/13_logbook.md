# Logbook

## 2026-07-15: Workspace Bootstrap and Baseline Audit

### What Was Done

1. Created a sibling research repository modeled on the existing atmospheric monitoring workspace.
2. Preserved the proposal and Marina's thesis with source provenance.
3. Extracted and visually reviewed the proposal and relevant thesis pages.
4. Audited the state, action, reward, termination, metrics, and printed physical equations.
5. Searched the local workspace and Downloads folder for the code and channel database.
6. Checked the printed GitHub source URL and public repository list.
7. Drafted a mission first constrained formulation and controlled evaluation protocol.
8. Implemented and validated an executable reward alignment diagnostic.
9. Added unit explicit radio calculations, a mixed action interface, and
   mission first episode metrics.
10. Completed an expanded asset hunt across local workspaces, 39 ZIP archives,
    101 GZip files, public Git hosting, web archives, research repositories,
    UPC bundles, 3D GloBFP releases, UPSim, and Spanish government data sources.
11. Found the public upstream building geometry and a strong Barcelona geometry
    substitute, but no exact RSS database, source repository, station snapshot,
    routes, seeds, checkpoints, logs, or raw figure data.

### Why

The proposal begins with baseline diagnosis. Training another policy before recovering and validating the environment would compound unknowns and could repeat the same objective error.

### Result

The main failure is objective misalignment: the legacy controller could improve its measured radio rewards without completing the mission. Missing velocity, goal, candidate radio information, success termination, and success metrics reinforced that problem.

The 22 unit tests and compilation checks pass. In the handcrafted diagnostic,
the never arrive trace scores 79.65 versus 69.95 for direct arrival under the
legacy discounted return. The corrected mission first audit reverses the order,
21.05 versus -18.17.

### Remaining Work

1. Obtain the legacy code and channel database.
2. Verify printed equations against implementation.
3. Reproduce original metrics.
4. Implement deterministic graph baselines.
5. Integrate and train the mixed action controller.

### Risks

The current causal diagnosis is strongly supported by the thesis but still needs code level verification. Printed equations may not match the unavailable implementation.

### Next Step

Request the missing source and channel assets, then validate the environment
and reproduce the legacy baseline before any training claim.

The full missing asset register, search coverage, evidence, and limitations are
in `docs/16_missing_asset_search.md`.

## 2026-09-12: Received Data, Controlled Training, and IEEE Draft

### What Was Done and Why

1. Inspected the complete received HDF5 radio map, recorded its SHA256 and
   schema, and scanned its values and selected operator coverage.
2. Revisited the thesis reward diagnosis and corrected the interpretation of
   the old hand written distance trace, which entered the current goal radius.
3. Built an explicit shared environment and native hybrid PPO with continuous
   acceleration, observed goal and velocity, and masked categorical handovers.
4. Corrected a common network timing issue during validation. Retired the
   exploratory route sets before training and preserved their records.
5. Ran six pilots, froze sources, routes, five final seeds, four treatments,
   the equal interaction budget, and a practical positive result gate.
6. Trained twenty final policies and evaluated 8000 learned episodes plus
   400 deterministic reference episodes on shared standard and longer routes.
7. Computed paired uncertainty, retained every seed and negative arm, verified
   the complete frozen comparison, and replayed one checkpoint exactly.
8. Created the IEEE manuscript only after the positive gate passed, generated
   its tables from statistics, and visually reviewed the compiled six page PDF.

The purpose was to test the reward hypothesis with the newly available data,
while explicitly separating this reimplementation from unavailable source code.

### Result

Legacy standard/longer mission success is 21.4%/0.0%; termination only is
0.0%/0.0%; reward replacement alone is 100.0%/100.0%; the combined treatment is
99.7%/36.1%. The primary combined minus legacy gain is 78.3 percentage points,
with a 95% crossed bootstrap interval [66.2, 89.5]. The deterministic reference
completes 100% in both splits and is faster. Reward replacement alone has
98.7% standard and 96.0% longer recorded feasible success.

The reward hypothesis has positive evidence under the shared model. The earlier
assumption that success termination must also improve learning was too strong.
All evaluation still ends at first safe arrival, regardless of training rule.
The suite has 34 passing tests; checkpoint replay matches all 200 raw standard
episode records. Sources, logs, checkpoints, results, notes, and paper are local.

### Remaining Work, Risks, and Next Decision

The requested implementation, tests, documentation, and conditional paper are
complete. Original simulator replication remains dependent on external source
and experiment artifacts. The current map uses one city, frequency, altitude,
and static background resource pattern, with uncalibrated energy and downlink
communication proxies. It does not model obstacle safety.

Do not infer a validated fix to Marina's exact saved policy or superiority to
classical control. Recover the source for direct ablation, or design a new
independent traffic and geography experiment. Preserve the completed freeze;
do not tune against its test results or silently replace its policies.

## 2026-09-12: Exact TFM Comparison and Pinpoint Citations

At the user's request, compared the full executed environment, reward,
observation/action interface, radio and energy proxies, PPO parameters,
reference controller, split protocol, and evaluation with the written TFM.
Note 25 records all choices and original printed pages, equations, tables,
and sections. Unknown source implementation details remain explicitly unknown.

Added 56 manuscript citations with printed page locators and expanded the
IEEE draft to eight pages with comparison tables. Note 26 records the source
review and verification. The six frozen experiment files, policies, scenarios,
and results remain unchanged. Original simulator recovery remains the next
research decision; the requested comparison and citation revision are complete.

## 2026-09-12: Connectivity Objective Audit

The user questioned whether nearly straight routes indicate loss of the
connectivity objective. Inspected the frozen implementation and original TFM
definitions, then exactly replayed 4,400 existing flights with service and
final queue diagnostics. All six frozen source hashes matched.

Note 27 records the result: connectivity is represented but its criteria are
permissive. Reward replacement alone yields 100% standard arrival, 92.2%
arrival without any sampled RSS outage, mean capacity below offered traffic
for 26.6% of flight time, and 20.2% arrivals with remaining queued data. Brief
capacity deficits can be buffered; these fractions are not disconnection rates.
The existing positive completion study does not solve the full joint objective.

Added a reproducible audit script, raw and aggregate diagnostic outputs, and
README scope annotations. No original result, checkpoint, scenario, frozen
protocol, or IEEE PDF was changed. The paper README links the addendum.
Remaining work is a new study with declared service requirements, explicit
joint feasibility, and controls that isolate routing and network contributions.

## 2026-09-12: Strict Connectivity Repair Completed

The user requested the fix and selected the same requirements as the thesis,
declining new packet deadline and empty queue arrival conditions. Implemented
strict sampled RSS and buffer failure, all three source radio costs, available
RBG actions, a shared prospective filter, and residual flight control. Notes
28–32 record the protocol, all six development policies, exact changes, final
results, and delivery audit.

Ten final policies were trained after a new freeze and evaluated with four
deterministic references on fresh route pairs. Full PPO reaches 96.6% standard
and 89.7% longer joint success. Its weighted radio cost improves while delay
worsens; completion differences are uncertain, so the strong learned claim
gate is not met. Goal radio reaches 98.0% and 92.5%, and improves longer
completion over Goal RSS by 5.5 points [1.5, 9.5].

All 51 tests pass and all 5,600 final evaluations replay exactly. Both source
freezes and the received dataset are unchanged. Delivered a new four page IEEE
report with 24 pinpoint source citations and retained the earlier v1 PDF.
The reporting copy removes an inappropriate unused percentage field for
logarithmic SINR; absolute results and the frozen estimator remain unchanged.
The work corrects the modeled joint objective, not the unavailable original
simulator or continuity between the one second samples.

## 2026-09-12: Consolidated Paper and Requested GitHub Release

The user asked to push the work, then requested that both studies be combined
into one paper. Created the single 15 page IEEE draft with 104 pinpoint TFM
citations, all principal methods and results, five figures, and detailed
appendices. The requested authors remain Guillem Moreno Garcia and Evgenii
Vinogradov. The two previous PDFs remain historical versions; repository links
now lead to the consolidated manuscript.

All 51 tests passed again and both freezes still match. The final PDF has
embedded fonts, no unresolved references or overfull boxes, and was visually
reviewed. No new policy, simulation result or estimator was introduced.
Note 33 records the consolidation, exact source byte preservation for Git,
private dataset/checkpoint exclusions, and release scope on origin/main.

## 2026-09-13: Complete Thesis Difference Inventory in the README

The user asked to preserve the exhaustive conversational comparison in Markdown,
including directly in the root README. Added twelve navigable categories with
the original TFM definitions, v1 foundation and final v2 changes. Included both
complete feature layouts, every PPO setting, exact splits and budgets, reward
formulas, all 31 v2 difference rows, deterministic search settings, statistics,
verification, retained values and unresolved assumptions. Original printed page
locators and the PDF viewer offset remain explicit.

Note 34 records the scope and documentation validation. The documentation index
links it, and the README quick guide now distinguishes the complete 51 test
suite from the original 34 tests. This revision changes no scientific artifact
or experiment and performs no new training or simulation. The existing GitHub
publication authorization applies to this repository documentation update.

## 2026-09-13: Dataset Placement and Model Setup Guide

The user asked for explicit instructions on where to place the dataset and
other required artifacts. Added a prominent README quick start and note 35
with the exact HDF5 path, size and SHA256, Python environment commands,
checkpoint layout and version compatibility, saved split sizes, custom route
examples, output prefixes, retraining into a separate label and troubleshooting.
The documentation index and both reproduction guides now link to that guide.

Verified 67 local documentation links and anchors, table structure and code
fences, CLI help for both evaluators and the training runner, the four v2 split
sizes, the dataset checksum and the ten locally retained v2 checkpoints. All
thirteen frozen source/protocol hashes match. These checks use the existing
Python environment; no fresh dependency installation, simulation or training
was run. This revision publishes documentation only.

A fresh clone still requires the private dataset and, for PPO evaluation
without retraining, separately restored weights. The next user step is to
place those artifacts and run a custom route. The guide explains the sampled
connectivity limitation and does not imply that every custom mission succeeds.
Existing publication authorization covers this documentation update to GitHub.

## 2026-09-13: V2 Focus and the V1.5 Original Reward Control

The user requested a comparison of the original written reward against full
V2 with every other system component unchanged. A later clarification removes
historical V1 from the final paper and reduces it to a brief README note.
Added an original reward wrapper, an otherwise identical PPO implementation,
22 behavioral checks, a frozen protocol and 400 fresh test routes. Five new
original reward policies used the same training routes, seeds and budget as
all ten reused V2 policies, whose hashes were fixed before the new run.

The 7,600 new evaluations replayed exactly. Both rewards achieve 95.7% standard
joint success; full minus original is 0.0 points [-2.8, 2.7]. Longer full
success is 87.3% versus 85.8%, difference +1.5 points [-2.9, 6.1]. The null
primary finding remains explicit. Full reduces flight time, handovers and
weighted cost on common successes but increases delay and proxy energy and
reduces SINR. No tuning followed the test results.

Rewrote the current README, setup, status, index and IEEE manuscript around
V2 and V1.5. Archived the former consolidated PDF/source and mixed inventory.
Published scope is 15 final checkpoints, 2,054,910 bytes, with a manifest;
the private map and other checkpoints remain excluded. Note 38 records paper
and delivery checks. All 73 tests and three freezes pass; physical assumptions
remain unverified. Next research requires independent tests and separately
frozen component ablations, not a favorable reinterpretation of this result.
