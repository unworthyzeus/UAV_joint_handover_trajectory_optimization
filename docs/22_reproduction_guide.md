# Reproduction Guide

For exact dataset placement, checkpoint restoration, environment installation
and runnable examples, start with [the dataset and model setup guide](35_dataset_and_model_setup.md).
This page preserves the historical v1 reproduction workflow; the setup guide
also covers the final v2 connectivity evaluator.

## What Was Built and Why

The experiment provides a runnable native resolution radio adapter, a vectorized
flight and handover environment, a hybrid PPO implementation, frozen scenarios,
all four reward and termination treatments, raw evaluation episodes, and saved
policies. This guide connects the artifacts so that another researcher can
repeat the work rather than rely on a narrative claim.

## Environment

The tested runtime is Python 3.12 on Windows 11 with CPU PyTorch 2.4.1, NumPy
2.3.5, h5py 3.16.0, Matplotlib 3.9.0, and pytest 9.0.3. Versions are recorded in
`requirements-experiments.txt`. The machine has 16 logical processors and about
32 GiB RAM. Training sets PyTorch to two threads. No GPU, pretrained policy,
demonstrations, or imitation loss was used.

The radio adapter loads about 1.52 GB of operator 1 values into RAM. Keep the
received 2.33 GB HDF5 at `dataset/Barcelona_dataset_January.h5`. It is ignored
by Git. Its SHA256 is
`d4630dd3a6c45419e12d0b60dd08473c4ffa4062ca4fab1decabecf2b992ea0d`.
The raw dataset has not been modified or published. Obtain it separately from
the owner; the current code package alone cannot reproduce the experiment.

## Commands

Run from the project root in an environment with the recorded dependencies.

```powershell
python -m pytest tests -q
python scripts/run_controlled_experiment.py --phase baseline --label repeat
python scripts/run_controlled_experiment.py --phase pilot --arms legacy fixed --seeds 41 --steps 524288 --label repeat
python scripts/run_controlled_experiment.py --phase confirmatory --arms legacy terminal_only reward_only fixed --seeds 1101 1102 1103 1104 1105 --steps 524288 --label repeat
```

Use a fresh label: the runner refuses to overwrite an existing checkpoint.
The frozen analyzed comparison uses label `v1`. The analysis script intentionally
targets `confirmatory_v1` and verifies its frozen source and scenario hashes.
An independent repeat has its own directory and should receive its own named
analysis, rather than replacing the preserved result.

```powershell
python scripts/analyze_controlled_experiment.py
python scripts/run_physical_reward_audit.py
python scripts/evaluate_checkpoint.py --checkpoint results/controlled_experiment/confirmatory_v1/reward_only_seed_1101/checkpoint.pt --split test
python scripts/evaluate_checkpoint.py --checkpoint results/controlled_experiment/confirmatory_v1/reward_only_seed_1101/checkpoint.pt --start 1000 1000 --goal 2000 1000
```

The evaluator loads this project's trusted checkpoints and stops on the same
safe arrival criterion for every treatment, including policies trained with
continuing episodes. This makes a policy trained with `reward_only` usable in
an episodic mission evaluator without retraining. The example checkpoint is
the first declared seed, not a model selected for the best test result.

## Artifact Map

| Artifact | Contents |
| --- | --- |
| `docs/18_experiment_protocol.md` | Shared model, departures from the thesis, and design |
| `docs/19_implementation_and_validation.md` | Tests and pretraining interface corrections |
| `docs/20_pilots_and_frozen_comparison.md` | Every pilot and frozen final comparison |
| `configs/frozen_comparison_v1.json` | Configuration, seeds, practical gate, and source hashes |
| `configs/controlled_scenarios.json` | All route coordinates and split identities |
| `results/controlled_experiment/pilot_v*/` | Pilot checkpoints and validation logs |
| `results/controlled_experiment/confirmatory_v1/` | Twenty trained policies and raw paired evaluations |
| `results/controlled_experiment/analysis_v1/` | Verified statistics, per seed tables, and figures |
| `docs/21_confirmed_results.md` | Full result interpretation and every seed |
| `results/tables/physical_reward_audit.json` | Dynamics based engineering counterexample, not training |
| `paper/main.tex` and `paper/UAV_reward_repair_IEEE.pdf` | Editable IEEE manuscript and compiled deliverable |
| `paper/README.md` | Paper build commands and provenance |
| `docs/23_manuscript_and_final_audit.md` | Final scientific and artifact checks |
| `docs/25_exact_changes_from_tfm.md` | Complete source comparison with printed page, equation, and table references |
| `scripts/check_thesis_citations.py` | Verify that all manuscript TFM citations have page locators and frozen sources match |

Historical V1 checkpoints and `outputs/` are ignored by Git but retained locally. A Git clone
alone does not include these saved policies, the raw map, or replay outputs.
Archive those authorized local artifacts separately if transferring the study.

## Risks, Remaining Work, and Next Decision

Replay verifies this implementation, not equivalence to the original source.
Recorded feasible success checks the implemented RSS outage and packet overflow
conditions; it does not certify collision safety or a calibrated aircraft.
Next research should recover the original simulator and independently validate
the downlink radio, traffic, energy, and network timing assumptions.
