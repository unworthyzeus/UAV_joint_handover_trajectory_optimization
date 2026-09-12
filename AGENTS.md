# Repository Instructions

All project facing text must be written in English.

This includes Markdown documentation, paper drafts, figure labels, table captions, code comments, human readable script output, and commit messages. Another language may appear only in a direct quotation or an external filename.

When adding research work, create or update a Markdown note that records:

1. What was done.
2. Why it was done.
3. What result was obtained.
4. What remains to be done.
5. Risks or limitations.
6. The next experiment or decision.

## Scientific Rules

1. Mission completion is the primary outcome. A radio metric aggregate must never hide a failed flight.
2. Report time, energy, delay, interference, SINR, and handovers conditional on mission success, with failure rate shown separately.
3. Use identical scenario seeds, starts, destinations, channel data, and deadlines for controlled comparisons.
4. Preserve the original ray tracing database. Derived data belongs under `data/processed/` with provenance.
5. Do not call a hand written reward trace a trained result. The initial reward audit is an engineering diagnostic only.
6. Do not claim improvement over Marina's baseline until the original code and channel database have been reproduced or an explicitly reimplemented baseline has been validated.
7. Keep physical quantities and units explicit. Convert dBm to linear power before summation and convert SNR or SINR from dB before applying capacity formulas.
8. Record all random seeds and report variation across multiple runs for learned policies.
9. When citing the original TFM for a definition, parameter, method, or result,
   give its printed page number and the section, equation, table, or figure
   when available. The PDF viewer page is the printed page plus two. Use
   `docs/25_exact_changes_from_tfm.md` as the verified definition index. Clearly
   distinguish original definitions from our replacements and unspecified details.
10. Preserve the six source/protocol files hashed in
    `configs/frozen_comparison_v1.json`. Documentation additions about that
    completed experiment belong in current notes, not retroactive edits to its
    frozen protocol. A changed implementation needs a separately labeled study.
    Also preserve every source and protocol file hashed in
    `configs/frozen_connectivity_v2.json`. Notes 28–32 describe that completed
    study. Reporting corrections outside a freeze must preserve the original
    result and explicitly document what changed. V2 enforces the thesis RSS
    and buffer requirements; the user declined adding a new packet deadline
    or empty queue arrival condition.

## Implementation Rules

1. Include goal relative position, velocity, heading, remaining time, and observable radio candidates in the Markov state.
2. Terminate a successful episode when position and terminal speed tolerances are both satisfied.
3. Treat safety and minimum connectivity as constraints where possible, rather than relying only on manually balanced reward terms.
4. Keep continuous motion control separate from masked discrete handover and resource decisions.
5. Validate environment transitions, rewards, termination, and metrics before long training runs.
