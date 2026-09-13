# Dataset Placement and Model Setup

Updated 13 September 2026. The examples use PowerShell and Python 3.12 on
Windows, matching the recorded CPU environment. Use `evaluate_reward_controller.py`
for the current V1.5/V2 comparison on the fresh test routes.

## What GitHub Includes

| Artifact | Included in the repository? | Needed for |
| --- | --- | --- |
| Source, scripts, saved routes and frozen configurations | Yes | Running the implementation |
| Episode records, statistics, figures and paper | Yes | Inspecting the completed results |
| `Barcelona_dataset_January.h5` | No, private file | Every simulated flight and training run |
| Final V1.5 and V2 checkpoints | Yes, all 15 declared policies | PPO evaluation without retraining |
| Deterministic controller weights | Not applicable | These controllers need the map and code, without a checkpoint |
| Virtual environments and `outputs/` | No, generated locally | Dependencies and new evaluation outputs |

The model class defines the architecture; it does not contain trained weights.
The final 15 checkpoints are included in a normal clone. Other training and
development weights remain ignored. The private map is never downloaded
automatically. Saved JSON/CSV records do not replace the map.

## 1. Work from the Repository Root

For a new clone, run from the directory where you want to keep the project:

```powershell
git clone https://github.com/unworthyzeus/UAV_joint_handover_trajectory_optimization.git
Set-Location -LiteralPath UAV_joint_handover_trajectory_optimization
```

For the existing research checkout on the author's machine:

```powershell
Set-Location -LiteralPath 'C:\Research\important_research_because_its_for_n3cat\UAV_joint_handover_trajectory_optimization'
```

The root contains `README.md`, `requirements-experiments.txt`, `scripts/` and
`configs/`. Every relative shell path below assumes this working directory.
The dataset is resolved relative to the script's repository root; relative
`--checkpoint` and `--output` arguments resolve from the shell working directory.

## 2. Place and Verify the Dataset

Create the singular `dataset` directory if absent:

```powershell
New-Item -ItemType Directory -Path dataset -Force | Out-Null
```

Put the original, uncompressed HDF5 at exactly:

```text
<repository root>/dataset/Barcelona_dataset_January.h5
```

For the existing local checkout, that is:

```text
C:\Research\important_research_because_its_for_n3cat\UAV_joint_handover_trajectory_optimization\dataset\Barcelona_dataset_January.h5
```

A different clone directory changes only the root prefix. Keep the same
relative folder and filename. The evaluators do not use `data/raw/`,
`data/processed/`, `datasets/`, a ZIP archive, or a file beside the repository.
They have no `--dataset` override. Preserve the frozen source instead of
editing its paths to accommodate another filename.

Obtain the private file separately from its owner. The repository supplies no
public dataset download. Verify these reference properties:

| Property | Expected value |
| --- | --- |
| Filename | `Barcelona_dataset_January.h5` |
| Bytes | 2,327,593,160, approximately 2.33 GB |
| SHA256 | `d4630dd3a6c45419e12d0b60dd08473c4ffa4062ca4fab1decabecf2b992ea0d` |
| RSS array | 133 × 5000 × 3500 signed 8 bit values |
| Operator used | Operator 1, 87 stations |

```powershell
Test-Path -LiteralPath dataset/Barcelona_dataset_January.h5
(Get-Item -LiteralPath dataset/Barcelona_dataset_January.h5).Length
(Get-FileHash -LiteralPath dataset/Barcelona_dataset_January.h5 -Algorithm SHA256).Hash.ToLowerInvariant()
```

The first result must be `True`; the size and hash must match the table. A
different hash means a different artifact even if its filename matches. Do not
replace the reference hash to make another dataset pass. Keep the HDF5 unchanged.

The adapter loads approximately 1.52 GB of selected RSS values into RAM, in
addition to the Python/PyTorch runtime and evaluation arrays. The recorded runs
used approximately 32 GiB system RAM. No GPU is required by these CPU evaluators.

## 3. Install the Recorded Environment

Create a Python 3.12 environment and use its executable directly. PowerShell
activation scripts and execution policy changes are unnecessary:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-experiments.txt
.\.venv\Scripts\python.exe --version
```

If `py` is unavailable but `python --version` reports Python 3.12, use
`python -m venv .venv` for the first command. The recorded packages are NumPy
2.3.5, h5py 3.16.0, PyTorch 2.4.1, Matplotlib 3.9.0 and pytest 9.0.3.
The CLI adds `src/` to its import path; an editable package install is not
required. LaTeX and PDF rendering packages belong to paper tooling and are not
needed to evaluate a controller.

## 4. Included Checkpoints and Compatibility

A normal clone contains every declared final seed 2101-2105 for three arms:

| Arm | Checkpoint directory | Meaning |
| --- | --- | --- |
| Original (V1.5) | `results/reward_comparison/confirmatory_v15/original_seed_2101/` | Original written reward on the complete V2 system |
| Full (V2) | `results/connectivity_experiment/confirmatory_v2/full_seed_2101/` | V2 arrival and full communication cost |
| Arrival (V2) | `results/connectivity_experiment/confirmatory_v2/arrival_seed_2101/` | V2 arrival reward, with the same strict connectivity constraints |

Each directory contains `checkpoint.pt`. Change the seed suffix for the other
four runs. The first seed is an example, not a selected best policy. All 15
files together occupy about 2.05 MB. The [manifest](../models/checkpoint_manifest.json)
lists exact sizes and SHA256 values. No extra download or retraining is needed
for these weights. They contain policy tensors and metadata, not the dataset.

All use 156 features, 61 network options and the same frozen V2 configuration.
The current evaluator checks dimensions, configuration, training budget and
metadata. Do not bypass a mismatch or interchange historical architectures.
You can pass an absolute checkpoint path if you store a file elsewhere.

## 5. Execute a Controller

All commands below run from the repository root. First try one custom flight
with the deterministic radio controller, which requires the dataset but no weights:

```powershell
.\.venv\Scripts\python.exe scripts/evaluate_reward_controller.py --controller straight_radio --start 1000 1000 --goal 1800 1300 --output outputs/quickstart_radio
```

Other choices are `straight_rss`, `joint_mpc` and `joint_lookahead`. To use the
included full V2 policy, first verify its path:

```powershell
Test-Path -LiteralPath results/connectivity_experiment/confirmatory_v2/full_seed_2101/checkpoint.pt
```

Evaluate its 200 standard test routes:

```powershell
.\.venv\Scripts\python.exe scripts/evaluate_reward_controller.py --checkpoint results/connectivity_experiment/confirmatory_v2/full_seed_2101/checkpoint.pt --split test --output outputs/quickstart_full_test
```

Or evaluate the same custom route with PPO:

```powershell
.\.venv\Scripts\python.exe scripts/evaluate_reward_controller.py --checkpoint results/connectivity_experiment/confirmatory_v2/full_seed_2101/checkpoint.pt --start 1000 1000 --goal 1800 1300 --output outputs/quickstart_full_custom
```

| V2 `--split` value | Route count | Role |
| --- | ---: | --- |
| `validation` | 64 | Standard development pool |
| `validation_longer` | 32 | Longer development pool |
| `test` | 200 | Standard final test pool |
| `longer_test` | 200 | Longer final test pool |

Specify either `--controller` or `--checkpoint`, never both. Custom routes
require both `--start x y` and `--goal x y`, and replace the chosen saved split.
Coordinates are local meters: `0 ≤ x ≤ 5000` and `0 ≤ y ≤ 3500`. They are not
latitude/longitude. Altitude is fixed by the map. Custom routes use background
phase zero; the CLI has no altitude or load phase argument.

The current evaluator uses new test seeds 53012 and 53013, from
`configs/reward_comparison_scenarios_v15.json`. The older
`evaluate_connectivity_controller.py` uses the prior V2 test seeds 52012 and
52013. Both use the same environment, but their test sets and aggregate numbers
are different. For the original reward control, use:

```powershell
.\.venv\Scripts\python.exe scripts/evaluate_reward_controller.py --checkpoint results/reward_comparison/confirmatory_v15/original_seed_2101/checkpoint.pt --split test --output outputs/quickstart_original_test
```

## 6. Locate and Understand the Output

`--output` takes a file prefix. For `--output outputs/quickstart_full_custom`,
the evaluator creates the parent directory if needed and writes:

```text
outputs/quickstart_full_custom.csv
outputs/quickstart_full_custom.json
```

The console prints an aggregate summary. The CSV contains one record per
route; the JSON contains the records, summary and position/speed/serving station
traces for the first four routes, or fewer when fewer routes are supplied.
These are not complete packet or radio time series for every route.

The current default prefix is `outputs/reward_controller_evaluation`. Reusing a prefix overwrites the matching
JSON and CSV. Use different names to preserve previous outputs, and keep new
checks outside the frozen result directories.

The v2 summary reports `episodes`, `success_rate`, `failure_counts` and secondary
metrics conditioned on success. A correctly executed simulation can report a
failed mission. V2 success requires arrival within 10 m, speed at most 2 m/s,
the 200 s deadline and no sampled RSS, buffer, boundary or energy failure.
Outstanding queued data at arrival is allowed. The model checks connectivity
at one second samples and does not certify physical continuity between them.

## 7. Reproduce Training and the Complete Comparison

The released checkpoints already support evaluation. To repeat the five new
original reward training runs and all 7,600 evaluations, use a fresh label:

```powershell
.\.venv\Scripts\python.exe scripts/run_reward_comparison.py --phase train --label local_reproduction_01
.\.venv\Scripts\python.exe scripts/run_reward_comparison.py --phase evaluate --label local_reproduction_01
.\.venv\Scripts\python.exe scripts/run_reward_comparison.py --phase replay --label local_reproduction_01
.\.venv\Scripts\python.exe scripts/analyze_reward_comparison.py --label local_reproduction_01
```

This trains V1.5 for all five frozen seeds with 524,288 interactions each and
reuses all ten hash fixed V2 checkpoints. New output goes under
`results/reward_comparison/confirmatory_local_reproduction_01/`, including
`original_seed_2101/checkpoint.pt`. Replay and analysis use corresponding
`replay_local_reproduction_01` and `analysis_local_reproduction_01` directories.
The training command only skips a verified complete run; an incomplete run
requires a fresh label. Evaluation refuses existing output files.

Do not rerun the freeze or alter hashes. The paper builder reads the delivered
`analysis_v15` results, not a new label automatically. Reusing these tests is
reproduction, not independent evidence for a controller tuned on them.
Independent retraining of the two V2 arms is documented in
[note 30](30_connectivity_results_and_reproduction.md); it needs no change to
the existing freezes. The comparison freeze expects the exact released V2
weights, not arbitrary newly trained replacements.

## Troubleshooting

| Symptom | What to check |
| --- | --- |
| Script path not found | Work from the root containing `README.md` and `scripts/`. |
| HDF5 file not found | Use singular `dataset` and the exact filename inside this clone. |
| Different dataset hash | Obtain the exact reference file; a matching filename is insufficient. |
| Missing checkpoint after cloning | Update the clone and check the exact published path and manifest; only the 15 declared final weights are included. |
| Missing Python launcher | Use an installed Python 3.12 executable to create `.venv`. |
| Missing `torch`, `numpy` or `h5py` | Install requirements with the same environment executable used for evaluation. |
| Memory allocation failure | Allow for approximately 1.52 GB of selected RSS plus runtime and evaluation memory. |
| Checkpoint metadata/dimensions mismatch | Match the checkpoint study, evaluator and frozen configuration. |
| Custom endpoint argument error | Supply both coordinate pairs within the local map bounds. |
| Earlier output replaced | A reused prefix overwrites JSON/CSV; choose a new prefix per retained run. |

## Documentation Change Record

The guide now covers the user authorized release of all 15 final V1.5/V2
checkpoints and the current evaluator on the fresh test routes. The dataset
path, size, checksum and environment requirements remain unchanged. The former
separate weight restoration step is unnecessary for a current clone.

The result and delivery notes record training, all 7,600 exact evaluation
replays, source integrity, checkpoint publication and paper checks. No clean
virtual environment installation is claimed; CLI and model validation used
the existing recorded Python environment. The next user step is to supply the
private map, install dependencies and run a custom flight. Physical model and
sampled connectivity limitations remain unchanged.
