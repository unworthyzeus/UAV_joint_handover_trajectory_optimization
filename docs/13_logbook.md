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

## 2026-09-13: README Conclusions after the Controlled Reward Comparison

The user requested an explicit account of the differences from the thesis,
general results and conclusions after the similar V1.5 and V2 completion
rates. Added a prominent summary of shared system changes, a reward contrast
table, matched secondary results for both splits, first failure counts and
the revised diagnosis. The detailed implementation and setup inventory remains.

The README now states that the early attribution of the original wandering
primarily to reward was too strong. V1.5 uses the original formula inside the
V2 system; it does not reproduce the original agent. Similar completion does
not mean equivalent communication behavior: full reduces handovers and flight
time but increases delay and proxy energy on matched successful flights.
The contribution is a controlled comparison with explicit limitations, not a
demonstrated repair of the unavailable original simulator. Note 42 records
the documentation update and verification. No code, paper, weights, raw
records, statistics, frozen protocols or experiment outcomes changed.

## 2026-09-13: Thesis Dataset Identity Confirmed

The user confirmed that the supplied HDF5 is the same dataset used in the
original thesis. Updated the current paper, README and setup documentation
to state this explicitly and removed the current dataset identity caveat.
Note 43 records the confirmation and the existing file size and checksum.
Historical notes and frozen protocols retain their original text; this new
provenance confirmation supersedes their earlier uncertainty. The same data
were already used in all runs, so results and models do not change. The
original simulator and trained policies remain unavailable.

## 2026-09-13: Original Thesis Comparisons in Every README Table

Added an explicit original thesis comparison to every root README table,
including mission success, paired metrics, intervals and failure counts.
Added a reward component table and approximate readings of all five original
metric panels in printed p. 18, Fig. 6 and p. 20, Fig. 8. Source CDF medians
and bar heights retain their printed units and scaling; unavailable original
joint success, flight time and delay results are labeled as unreported.

Note 44 records the reading method and limits. Expanded the parameter
comparisons, including original target KL, rollout length, timestep and
packet size discrepancies, and the distinction between nominal training
ceilings and actual interactions. No library defaults or original output
normalizations were assumed. Existing result cells, statistics, models and
all experiment freezes are preserved. This documentation revision does not
change the null primary result or demonstrate a repair of the original agent.

## 2026-09-14: Metric Interpretation and a Completion First Improvement Attempt

The user requested more numerical source comparisons, interpretation and
preferred directions, and a better model, then clarified completion first
and service second. Expanded the README source comparison with 28 current
means, failure counts and denominators. Explained how lower delay, time,
interference and consumed energy differ from higher success, SINR and
remaining energy, and why fewer handovers can trade against service.
Unreported thesis values remain unreported; incompatible quantities retain
their original units and limitations. Note 45 records the interpretation.

Declared three reward candidates and a fresh full V2 control before running
four pilots. All used 524,288 interactions and pilot seed 2199. The service
candidate passed the declared validation gate with 91/96 missions against
90/96 for control; the stronger reliability candidates achieved 87/96 and
89/96. Preserved every pilot outcome. Froze the selected reward and source,
then trained five final models with seeds 2101-2105. The reward adapter
preserves V2 transitions, observations, navigation, filters and mission rules.
The dataset is the same unchanged private HDF5 as in the original thesis.

Evaluated 500 new standard and 500 new longer routes, separately from the
initial comparison, for 18,000 total final episodes. All 18,000 replayed
exactly. V2.1 / full V2 success is 95.48% / 96.92% standard and 88.60% /
91.84% longer. The primary difference is -1.44 percentage points with a
95% interval [-3.16, 0.32]; the longer difference is -3.24 [-5.64, -0.88].
The candidate did not improve completion. It reduces delay on common
successes, but produces more handovers and more RSS failures. V2 remains
the main model; no additional candidate or tuning followed these results.
Notes 46-48 retain the protocol, all development outcomes and final results.

Added the five final weights and a usage guide in note 49, bringing the
published total to 20 checkpoints and 2,741,480 bytes. Pilot weights stay
local with their hashes and regeneration commands retained. The single
IEEE paper now contains both separate comparisons, all final training seeds,
the existing informative route plots and the negative improvement finding.
The final eight pages were rendered and visually inspected. All 88 tests
passed, all four freezes and all checkpoint hashes match, and the initial
statistics, figures and model weights remain unchanged. The current delivery
audit is `results/service_reward_v21/analysis/delivery_validation.json`;
the prior delivery record is explicitly historical at commit `d53b293`.

The completed study does not establish a better overall model or identify
the original thesis implementation's failure. Single city sampling, five
training seeds, static traffic, proxy energy, ideal handovers and sampled
connectivity remain limitations. The next research decision is a separately
declared investigation of RSS failures and controller constraints, followed
by new evaluation routes if further tuning is undertaken. No such additional
experiment is claimed here.
