# Joint Handover and Trajectory Optimization in 5G Connected UAVs

Research workspace for the non THz n3cat UAV proposal. Updated 12 September 2026.

## Consolidated IEEE Paper

Read [the single paper covering both studies](paper/UAV_joint_reward_connectivity_IEEE.pdf),
authored by Guillem Moreno Garcia and Evgenii Vinogradov. Its 15 pages include
the reward experiment, connectivity audit and correction, all principal results,
trajectory figures, splits, failed development designs, and detailed thesis
comparisons with 104 printed page citations. The
[paper guide](paper/README.md) explains the build; [note 33](docs/33_unified_paper_and_github_release.md)
records the consolidation and GitHub release scope. Earlier PDFs remain historical records.

## Latest Result: Connectivity Constraints

The v2 study corrects the connectivity omission. A successful mission now has
to satisfy the thesis's RSS and buffer constraints at every simulated sample,
as well as arrive and stop. The full reward restores delay, interference and
handover costs, with available resource choices and a shared safety filter.
No new packet deadline or empty queue arrival requirement was added.

| Controller | Standard joint success | Longer joint success |
| --- | ---: | ---: |
| PPO with arrival cost and strict constraints | 96.9% | 86.3% |
| PPO with full radio cost and strict constraints | 96.6% | 89.7% |
| Goal directed controller with radio selection | 98.0% | 92.5% |

Full PPO reduces weighted radio cost on paired successful routes by 24.5% and
14.7%, but increases delay and does not establish a completion advantage.
The radio selection reference improves longer completion over strongest RSS
selection by 5.5 points, 95% interval [1.5, 9.5]. All four deterministic
references and every learned seed are retained in the complete results.

Read [the results and commands](docs/30_connectivity_results_and_reproduction.md),
[every connectivity change with thesis pages](docs/31_exact_connectivity_changes.md),
or [the consolidated IEEE paper](paper/UAV_joint_reward_connectivity_IEEE.pdf).
There are 51 passing tests and 5,600 exact replayed final evaluations. The
dataset and both experiment freezes are unchanged. The one second surrogate
sampling does not establish physical continuity between samples.

## Earlier Arrival Reward Study

Reward replacement restored mission completion in a documented reimplementation
on the received Barcelona radio map. Twenty PPO policies were trained using
four treatments and five seeds, with 524,288 interactions per policy. Each
policy evaluated the same 200 standard and 200 longer test routes.

| Training treatment | Standard mission success | Longer mission success |
| --- | ---: | ---: |
| Legacy reward | 21.4% | 0.0% |
| Termination change only | 0.0% | 0.0% |
| Reward replacement only | 100.0% | 100.0% |
| Reward and termination changes | 99.7% | 36.1% |
| Deterministic reference | 100.0% | 100.0% |

Standard routes span 200–1000 m; longer routes span 1000–1800 m. Safe arrival
requires distance at most 10 m and speed at most 2 m/s within 200 s. Every
evaluation stops at safe arrival, including policies trained with continuing
episodes. The primary combined versus legacy gain is 78.3 percentage points,
with a paired crossed bootstrap 95% interval of [66.2, 89.5]. The prespecified
positive result gate passed.

Reward replacement is the essential tested intervention. Adding termination
was less reliable on longer routes. The deterministic reference completed all
routes and was faster; these results do not establish a learning advantage
over classical control.

## Scope

This is a validated reimplementation of the written reward structure, not a
reproduction of Marina Bermúdez Granados's original simulator or policy. All
treatments share repaired observations, continuous flight actions, masked
handover choices, and explicit radio and energy proxies. The experiment does
not isolate observation repair or prove the exact cause of the original
policy's behavior. Original code, checkpoints, collision scene, and exact
dataset version confirmation remain unavailable.

The received 2.33 GB map is preserved at
`dataset/Barcelona_dataset_January.h5` and excluded from Git. It has not been
published. Study I's historical recorded feasible success checks buffer overflow and outage:
reward replacement alone achieved 98.7% standard and 96.0% longer feasible
success. Mission success alone is not a complete safety claim.

The [connectivity audit](docs/27_connectivity_objective_audit.md) showed why
Study I did not establish the full joint objective. In 1,000 standard
reward replacement flights, arrival is 100%, but only 92.2% have no sampled RSS
outage; capacity falls below offered traffic for a mean 26.6% of flight time,
and 20.2% arrive with data still queued. Short capacity deficits can be buffered
and are not themselves disconnections. Study II repairs the sampled RSS and
buffer endpoint; it still does not establish service between samples or a
packet latency guarantee. The audit exactly replayed 4,400 frozen episodes
without changing training or original results.

## Read and Reproduce

- [Confirmed results and every seed](docs/21_confirmed_results.md)
- [Everything changed from the original TFM, with precise source pages](docs/25_exact_changes_from_tfm.md)
- [Reproduction commands and artifact map](docs/22_reproduction_guide.md)
- [IEEE manuscript and build instructions](paper/README.md)
- [Documentation index](docs/README.md)
- [Current task status](docs/12_task_status.md)

The complete experiment has 34 passing tests, saved checkpoints and raw records,
and an exact replay of all 200 standard episodes for the first reward replacement
seed. Start with:

```powershell
python -m pytest tests -q
python scripts/analyze_controlled_experiment.py
python scripts/evaluate_checkpoint.py --checkpoint results/controlled_experiment/confirmatory_v1/reward_only_seed_1101/checkpoint.pt --split test
```

Use the recorded dependencies in `requirements-experiments.txt` and obtain the
private map separately from its owner. The analysis verifies frozen source
hashes; use a new experiment label for new training, preserving the completed
comparison.

## Structure

| Path | Purpose |
| --- | --- |
| `docs/` | Dataset audit, design, validation, pilots, results, risks, and logbook |
| `src/uav_joint_optimization/` | Environment, hybrid PPO, and earlier audit utilities |
| `scripts/` | Training, analysis, checkpoint replay, diagnostics, and paper tables |
| `configs/` | Frozen source hashes, settings, route coordinates, and seeds |
| `results/controlled_experiment/` | Pilots, twenty final policies, episodes, statistics, and figures |
| `paper/` | IEEE source, generated tables, compiled PDF, and build guide |
| `sources/` | Research PDFs, including the original thesis |

Earlier notes numbered 01–16 document the predata investigation and proposals.
Their historical blocked status and hypotheses are superseded by notes 17–23.
The old hand written reward diagnostic is not trained evidence and its distance
trace does not satisfy the current meaning of a failed mission; see its revised
limitations in `docs/11_initial_reward_diagnostic.md`.

The next research decision is to repeat the reward ablation in the recovered
original simulator, then test independent traffic and geographic conditions.

The baseline thesis is preserved at
`sources/UAV_Bermudez_Granados_2026_MSc_thesis.pdf`, with the official
[UPCommons record](https://upcommons.upc.edu/entities/publication/a8ce08c2-c238-4145-a5ab-5d39b12c6553).
