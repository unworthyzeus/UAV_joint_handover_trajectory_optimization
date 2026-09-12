# Manuscript and Final Audit

Date: 12 September 2026.

## What Was Done and Why

Prepared an IEEE conference style research manuscript after the frozen
comparison passed its prespecified practical positive result gate. Generated
the quantitative macros and both result tables from the verified statistics,
included all four treatments and the deterministic reference, and retained
the weaker longer route result. This makes the positive finding reviewable
without turning a reimplementation into a claim about unavailable original code.

The current deliverable is the eight page `paper/UAV_reward_repair_IEEE.pdf`,
with editable source in `paper/main.tex` and `paper/thesis_comparison.tex`.
The manuscript uses IEEEtran 1.8b and seven primary references. The initial
six page draft was expanded with source locators and comparison tables in
the revision recorded in note 26.
It is a local draft by Guillem Moreno Garcia and Evgenii Vinogradov, not an
IEEE acceptance or submission. The shared affiliation is Universitat
Politècnica de Catalunya, Barcelona, Spain.

## Scientific Result

Twenty final PPO policies each received 524,288 interactions, totaling
10,485,760. Five seeds and 200 shared routes per split yield 8000 learned test
episodes. The deterministic reference adds 400 episodes across the two splits.
Six separate pilots and the initial feasibility inspections are retained.

| Training treatment | Standard mission success | Longer mission success |
| --- | ---: | ---: |
| Legacy | 21.4% | 0.0% |
| Termination only | 0.0% | 0.0% |
| Reward replacement only | 100.0% | 100.0% |
| Both changes | 99.7% | 36.1% |
| Deterministic reference | 100.0% | 100.0% |

The primary combined minus legacy gain is 78.3 percentage points, with a
paired crossed seed and route bootstrap 95% interval of [66.2, 89.5]. The
combined treatment also meets the gate's recorded feasibility threshold.
Reward replacement alone records 98.7% standard and 96.0% longer feasible
success. Success means arriving within 10 m at no more than 2 m/s by 200 s;
recorded feasibility additionally checks packet overflow and RSS outage.

Reward repair is the essential tested change. Arrival termination alone fails,
and adding it to the replacement reward reduces longer route success. The
deterministic reference completes all routes and is faster. The paper includes
these limitations in the abstract, results, and conclusion.

## Verification Record

- The implementation validation completed with **34 passing tests**, including
  meaningful dynamics, mission, terminal reward, masking, GAE, and PPO checks.
- Analysis verifies all frozen source hashes, configuration and training
  budgets, seed identities, route pairing, and successful arrival criteria.
- All twenty final checkpoint files exist. Exact checkpoint replay reproduces
  all **200 raw standard episode records** for `reward_only_seed_1101`.
- A final SHA256 read confirms the raw map remains
  `d4630dd3a6c45419e12d0b60dd08473c4ffa4062ca4fab1decabecf2b992ea0d`.
  The map and checkpoints remain excluded from Git and retained locally.
- Tectonic 0.17.0 compiled the manuscript successfully. References resolve on
  the final pass. The current PDF has eight pages, embedded font entries, no Type 3
  fonts, and no unresolved reference markers.
- Render inspection covered every page, including equations, legends, tables,
  and the appendix pages. Float placement was adjusted to keep figures
  beside the result discussion. Minor underfull spacing warnings do not
  produce visible clipping or overlap. Current checks supersede the initial
  six page draft's layout warnings.
- `git diff --check` found no whitespace errors; Git's CRLF conversion notices
  are platform notices. Frozen source files were not changed during writing.

The machine readable final record is
`results/tables/final_artifact_audit_20260912.json`. It records the final PDF
checksum and size, frozen file checks, checkpoint count, and exact replay count.
The compile report is `paper/build/compile_report.json`. Page render images
and font checks are under `outputs/paper_review_final/`. Earlier render passes
remain as development artifacts; the named deliverable is the final PDF.

## Limits and Remaining Work

The experiment tests the written reward structure in a shared reconstructed
model. Original environment code, checkpoints, collision geometry, and exact
dataset version identity remain unverified. Repaired observations and actions
are common to all arms, so their independent contribution is not estimated.
The model uses one city, frequency, altitude, and deterministic resource load
pattern with downlink, delay, and energy proxies. It does not validate obstacle
safety or field performance.

The shaping identity holds for raw rewards; normalization and clipping can
change PPO's effective objective. The comparison tests the full declared recipe
and does not separately identify those interactions. Five seeds and tests on
the same radio map do not establish robust generalization. The freeze was a
local protocol record, not an independently registered public study.

The user's requested code, controlled tests, Markdown documentation, and
conditional IEEE paper are complete. The private dataset and ignored local
checkpoints must be obtained or transferred separately for independent replay;
a Git clone alone is insufficient. No dataset release or paper submission was
performed.

## Next Decision

Use reward replacement with evaluation ending at safe arrival as the supported
starting point for further experiments. Recover the original simulator for a
direct reward ablation, or freeze a new study using independent traffic and
geographic conditions. Preserve this study's test outcomes, including the
negative arms; any follow up needs its own label, sources, and evaluation plan.

## Authorship Update

On 12 September 2026 the user specified the authors as themselves and Genia.
The paper now lists Guillem Moreno Garcia first and Evgenii Vinogradov second.
Guillem's spelling and UPC affiliation follow the existing THz project paper.
Genia's full name and UPC affiliation were verified against the official
[N3Cat website](https://n3cat.upc.edu/), which identifies Evgenii (Genia)
Vinogradov. The shared institution is shown without inferred department titles
or email addresses.

The PDF was rebuilt and its title page reviewed; the manuscript remains six
pages. The final artifact audit now records the revised PDF checksum. This
change supplies the requested authorship metadata and does not alter the
frozen experiment, results, or scientific conclusions. No authorship work
remains for this request; venue formatting remains a later submission decision.
