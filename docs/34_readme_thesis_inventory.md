# Complete Thesis Difference Inventory in the README

Date: 13 September 2026.

## What Was Done

Expanded the root [README](../README.md#complete-inventory-of-differences-from-the-original-thesis)
with the complete documented comparison requested in the conversation. The
inventory is directly readable in the README, with twelve linked categories:

1. Implementation, data and geometry.
2. Motion, arrival and connectivity endpoints.
3. Observations and every feature index.
4. Handover, resources and action timing.
5. Radio, traffic, queues and energy.
6. Reward functions and terminal handling.
7. Residual motion and the safety filter.
8. PPO and all numerical settings.
9. Deterministic reference controllers.
10. Training, validation, tests and budgets.
11. Metrics, statistics and verification.
12. Event ordering, retained values and limits.

The inventory incorporates the complete implementation tables from
[note 25](25_exact_changes_from_tfm.md), all 31 final v2 difference rows from
[note 31](31_exact_connectivity_changes.md), and the detailed final reference
and protocol settings from [note 28](28_connectivity_experiment_protocol.md).
It includes the 42 and 156 feature layouts, every published original PPO
parameter, our additional numerical choices, exact split counts and seeds,
reward formulas, controller priors, filter behavior and claim boundaries.

The README also has a prominent entry link, an internal table of contents,
the original printed page convention and links to the verified definition
index. The quick reproduction paragraph now distinguishes the 34 original v1
tests from the complete 51 test suite, and the structure table includes v2.
Repository text remains English under the project AGENTS.md instructions.

## Why It Was Done

The user requested that the exhaustive conversational list be saved as Markdown,
including directly in the repository README. Keeping only links to separate
notes would not provide that complete reading experience. The new inventory
makes the scope of the reimplementation visible at the repository entry point.

## Result and Evidence Boundary

The README explicitly distinguishes the written original TFM, the initial v1
foundation and the final v2 changes. It also separates retained parameters from
new modeling choices and original details that are unspecified. In particular,
the five outage allowance belongs to our v1, not the original written C2 or
the final v2 controller. The 200 kbit/s traffic and one second step remain
declared surrogate choices. V2 resource and residual control are not described
as independently ablated reward improvements.

This is documentation work only. No simulator, policy, scenario, statistic,
experiment freeze, dataset or paper was modified, and no new training or
evaluation was performed. The 51 tests and historical replay counts are
previously recorded evidence, not new simulation runs for this revision.

## Validation

Validation passed across all four documentation files:

- 63 local links and their Markdown section anchors resolve.
- All 27 Markdown tables have consistent column counts; code fences are balanced.
- All 144 v1 implementation table rows and headers from sections 1–7 of note 25
  are preserved, including its 17 reference/evaluation comparison rows.
- All 31 final v2 change rows are included exactly once in the inventory.
- The inventory has twelve linked categories and both complete observation layouts.
- All six v1 and seven v2 frozen source/protocol hashes match.
- Git whitespace checks pass, and the scoped diff contains only documentation.

No unit tests or simulations were rerun for this documentation revision.

These checks establish inventory completeness relative to the existing reviewed
records, not independent verification of every statement against unavailable
original source code. Printed page citations retain the source locators already
reviewed in notes 25 and 31; no new interpretation of the thesis is introduced.

## Remaining Work and Next Decision

The requested list is now in the README. The source simulator, exact map version
and physical validation limitations remain unchanged. Future implementation
changes need a new experiment and an updated comparison; this inventory must
not silently reclassify historical v1 rules as final v2 behavior. Any future
shortened README should preserve a direct route to this complete inventory and
retain the scope distinctions, source locators and negative results.
