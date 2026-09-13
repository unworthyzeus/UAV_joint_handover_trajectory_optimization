# README: Current Findings and Differences from the Thesis

Date: 13 September 2026.

## Work and Reason

The user requested a clear README account of what differs from the original
thesis, the general results, and the conclusions after observing similar
completion rates for V1.5 and V2. The previous README already retained the
detailed implementation inventory, but the implications for the original
diagnosis needed a more prominent explanation.

Reorganized the opening around the current conclusion, twelve main areas of
change from the thesis, the controlled V1.5 versus full V2 contrast, general
results, failure counts, and six explicit conclusions. Preserved the complete
lower level specification, source page locators, dataset placement, model
instructions, reproduction commands and brief historical note.

The difference table distinguishes shared changes from the reward intervention.
It covers executable/data provenance, navigation, observations, constraint
enforcement, arrival, network actions, physical dynamics, radio/traffic/energy
proxies, reward, PPO, split design and evaluation. Source claims use printed
page and section/equation/table locators from the verified definition index.
Missing original implementation details remain unknown rather than proven
absent.

## Results and Conclusions Made Explicit

- Both original reward V1.5 and full V2 reach 95.7% standard joint success.
  Full minus original is 0.0 percentage points, 95% interval [-2.8, 2.7].
  Longer success is 87.3% versus 85.8%, difference +1.5 points [-2.9, 6.1].
  Neither interval establishes improved completion or proves equivalence.
- On the 925 standard and 781 longer common successful pairs, V2 reduces
  handovers and flight time while increasing delay and proxy energy and
  reducing SINR. Interference differences remain inconclusive. The README
  gives both arm means for both splits, rather than treating every metric
  as similar because completion rates are similar.
- RSS failures decrease in the observed counts while buffer failures
  increase. Both types and the total failure counts remain visible beside
  unconditional completion and conditional service results.
- The early interpretation that reward was the main cause of the original
  thesis's wandering was too strong. The source itself considers reward,
  motion implementation and training difficulty [TFM, printed p. 19,
  Sec. 7.2]. The current comparison cannot identify their causal contributions.
- V1.5 has all V2 control aids and physical assumptions. It is not the
  original thesis agent. Shared guidance, observations, stopping rules,
  masks and filtering could compensate for reward deficiencies, but those
  effects have not been separately measured.
- No overall reward or PPO superiority is established. The defensible
  contribution is a reproducible comparison with explicit joint outcomes,
  uncertainty, failures, tradeoffs, released weights and source traceability.

## Verification

Checked the README's completion percentages, primary intervals, every new
paired mean, reported percentage changes and failure counts against
`results/reward_comparison/analysis_v15/statistics.json`. Checked local links,
heading anchors, Markdown table structure and code fences. All 20 frozen
source/protocol hashes remain unchanged. The paper, checkpoints, raw records,
statistics and model code are unchanged; this update does not rerun training
or simulation and does not claim new experiment tests.

The check covered 14 completion percentages, 28 paired means, 12 failure
counts, two success intervals, 61 local links and 15 Markdown tables across
the edited documentation. The README retains one brief historical note.

## Remaining Work, Risks and Next Decision

The earlier 73 passing experiment tests and 7600 exact replays establish
computational consistency, not the validity of physical approximations.
One city, sampled connectivity, static load, idealized service, uncalibrated
energy and unavailable original code still limit inference. The additional
600 exact matches used for the long route illustration repeat existing
observations and do not enlarge the independent sample.

No new experiment was performed for this documentation request. Explaining
the source behavior requires the original implementation or a separately
declared reconstruction, and controlled ablations of navigation guidance,
observations, termination and filtering. Generalization requires independent
maps and traffic. Existing test routes must not become tuning data for those
future claims.
