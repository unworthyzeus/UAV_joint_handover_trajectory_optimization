# TFM Comparison and Citation Revision

Date: 12 September 2026.

## What Was Done and Why

At the user's request, audited the written TFM against the executed source and
made the full set of differences explicit. Created note 25 with a source
definition index, comparison tables, exact observation layout, PPO settings,
event ordering, evaluation semantics, retained constants, and unknown source
details. This prevents the result from being read as a change to only the
reward in the original simulator.

Added 56 pinpoint TFM citations to the IEEE manuscript and its comparison
appendix. Each citation includes a printed page; sections, equations, tables,
and figures are included where relevant. Printed page numbers are two less
than the PDF viewer counter. The body distinguishes source equation numbers
from its own equations and cites the numerical parameter tables separately.

The manuscript is now eight pages including the comparison appendix. It keeps
Guillem Moreno Garcia and Evgenii Vinogradov as authors. The environment and
PPO comparison tables distinguish shared reconstruction choices from the two
factorial treatments. References follow their first citation order.

## Source Review and Corrections

Reviewed source definitions visually and in extracted text: printed pp. 6–7
for the radio map; pp. 9–12 for movement, radio/queue/energy equations,
constraints, state/actions, reward and termination; pp. 13–16 for PPO, greedy
control and parameters; and pp. 19–21 for navigation and conclusions. The
complete methods and result text was available for checking contextual claims.

Updated the earlier diagnosis, radio audit, dataset assessment, abstract
diagnostic, and relevant historical source notes with page locators. Removed
the earlier diagnostic's unsupported inference that its 4–5 m trace proved
physical noncompletion; Table 3 gives a 10 m position tolerance. The current
notes already preserve that distinction, and note 25 makes it explicit again.

The energy and interference models are labeled replacements, not simply unit
fixes. Unreported architecture, normalization, splits, and event ordering are
marked not specified. We do not infer them from Stable Baselines defaults.
The configured value coefficient and local half MSE convention are both
disclosed, as is the common raw reward used by the evaluator for all policies.

## Checks and Result

- `python scripts/check_thesis_citations.py` confirms 56 TFM citations have
  page locators and all six frozen source/protocol hashes still match.
- `results/tables/tfm_traceability_audit.json` lists every citation location
  and its locator, with an explicit distinction between automated structural
  checks and manual semantic source review.
- The LaTeX build succeeds. References resolve, and the rendered comparison
  tables and body citations are legible. The final PDF remains at the same
  deliverable path; its checksum and font/page audit are refreshed.
- Scientific parameter values, frozen scenarios, checkpoints, evaluation
  records, and experiment source remain unchanged. No policy was retrained or
  selected again, and the previous test results were not used for tuning.
- `AGENTS.md` now retains the user's requirement to provide original TFM page
  locators in future citations. Notes 18 and 20 are not retroactively modified
  because their content is part of the recorded experiment freeze.

The complete comparison and page specific citation request are fulfilled.
The result remains evidence for reward replacement inside the declared shared
model, not an independently reproduced fix to the original saved policy.

## Risks, Remaining Work, and Next Decision

Page references establish what the original text says, not what its absent code
executed. A structural citation checker cannot automatically establish semantic
support; the reviewed definition index remains necessary. Independent reviewers
should use that index when assessing the modeling assumptions and comparability.

No work remains for this documentation request. Recover the original simulator
to resolve unknowns, or define a new separately frozen experiment for any
implementation change. A later venue submission may require adapting the
appendix layout or page count to its instructions.
