# Dataset Placement and Model Setup

Updated 13 September 2026. The examples use PowerShell and Python 3.12 on
Windows, matching the recorded CPU environment. Use the final v2 evaluator
for the strict sampled connectivity study.

## What GitHub Includes

| Artifact | Included in the repository? | Needed for |
| --- | --- | --- |
| Source, scripts, saved routes and frozen configurations | Yes | Running the implementation |
| Episode records, statistics, figures and paper | Yes | Inspecting the completed results |
| `Barcelona_dataset_January.h5` | No, private file | Every simulated flight and training run |
| Trained `checkpoint.pt` binaries | No, currently retained locally | PPO evaluation without retraining |
| Deterministic controller weights | Not applicable | These controllers need the map and code, without a checkpoint |
| Virtual environments and `outputs/` | No, generated locally | Dependencies and new evaluation outputs |

The model class defines the architecture; it does not contain trained weights.
Cloning does not recover ignored `.pt` files. Neither map nor weights are
downloaded automatically. Saved JSON/CSV results do not substitute for either.

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

## 4. Restore Checkpoints for the Correct Study

The ten final v2 models are `arrival` and `full`, each with seeds 2101–2105.
Each saved file is approximately 137 kB. Their original local layout is:

```text
<repository root>/
  dataset/
    Barcelona_dataset_January.h5
  results/
    connectivity_experiment/
      confirmatory_v2/
        arrival_seed_2101/
          checkpoint.pt
        full_seed_2101/
          checkpoint.pt
        ... other seeds 2102 through 2105 ...
    controlled_experiment/
      confirmatory_v1/
        reward_only_seed_1101/
          checkpoint.pt
        ... other v1 arms and seeds ...
```

Restore weights separately from the locally retained study artifacts, or
retrain into a fresh output directory as described below. The example
`full_seed_2101` is the first declared seed, not a model selected for the best
test score. You can store a checkpoint elsewhere and pass its absolute path to
`--checkpoint`. Use the complete project generated file, including its metadata.

| Study | Evaluator | Compatibility |
| --- | --- | --- |
| Final v2 | `scripts/evaluate_connectivity_controller.py` | 156 input features, 61 network options, final seeds 2101–2105 |
| Historical v1 | `scripts/evaluate_checkpoint.py` | 42 input features, five network options, final seeds 1101–1105 |

V2 checks checkpoint environment metadata against its frozen configuration.
Do not interchange versions or bypass dimension/metadata mismatches. The
architecture file alone is not a pretrained model.

## 5. Execute a Controller

All commands below run from the repository root. First try one custom flight
with the deterministic radio controller, which requires the dataset but no weights:

```powershell
.\.venv\Scripts\python.exe scripts/evaluate_connectivity_controller.py --controller straight_radio --start 1000 1000 --goal 1800 1300 --output outputs/quickstart_radio
```

Other choices are `straight_rss`, `joint_mpc` and `joint_lookahead`. To use the
example trained v2 policy, first verify that it was restored:

```powershell
Test-Path -LiteralPath results/connectivity_experiment/confirmatory_v2/full_seed_2101/checkpoint.pt
```

Evaluate its 200 standard test routes:

```powershell
.\.venv\Scripts\python.exe scripts/evaluate_connectivity_controller.py --checkpoint results/connectivity_experiment/confirmatory_v2/full_seed_2101/checkpoint.pt --split test --output outputs/quickstart_full_test
```

Or evaluate the same custom route with PPO:

```powershell
.\.venv\Scripts\python.exe scripts/evaluate_connectivity_controller.py --checkpoint results/connectivity_experiment/confirmatory_v2/full_seed_2101/checkpoint.pt --start 1000 1000 --goal 1800 1300 --output outputs/quickstart_full_custom
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

For a historical v1 checkpoint:

```powershell
.\.venv\Scripts\python.exe scripts/evaluate_checkpoint.py --checkpoint results/controlled_experiment/confirmatory_v1/reward_only_seed_1101/checkpoint.pt --split test --output outputs/quickstart_v1_test
```

V1 supports `validation`, `test` and `longer_test`. It has a different policy
interface and a more permissive communication endpoint; its arrival rate must
not be labeled as strict v2 joint success.

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

Default prefixes are `outputs/connectivity_evaluation` for v2 and
`outputs/checkpoint_evaluation` for v1. Reusing a prefix overwrites the matching
JSON and CSV. Use different names to preserve previous outputs, and keep new
checks outside the frozen result directories.

The v2 summary reports `episodes`, `success_rate`, `failure_counts` and secondary
metrics conditioned on success. A correctly executed simulation can report a
failed mission. V2 success requires arrival within 10 m, speed at most 2 m/s,
the 200 s deadline and no sampled RSS, buffer, boundary or energy failure.
Outstanding queued data at arrival is allowed. The model checks connectivity
at one second samples and does not certify physical continuity between them.

## 7. Retrain When Weights Are Unavailable

With the dataset and dependencies, reproduce the frozen design into a fresh label:

```powershell
.\.venv\Scripts\python.exe scripts/run_connectivity_experiment.py --phase confirmatory --label local_reproduction_01 --seeds 2101 2102 2103 2104 2105 --steps 524288
```

This runs four reference controllers, trains both PPO arms for five seeds,
and evaluates the final checkpoints. Outputs go under
`results/connectivity_experiment/confirmatory_local_reproduction_01/`, including
`full_seed_2101/checkpoint.pt`. Pass that new checkpoint path for later evaluation.
Choose another label if this directory already has outputs; the runner refuses
to overwrite existing reference results or checkpoints.

Do not rerun `--phase freeze`, replace hashes or alter frozen source to bypass
checks. Preserve the delivered `confirmatory_v2` results. The standard analysis
scripts read that delivered directory, not a new label automatically. Reusing
the existing test routes is a reproduction, not independent evidence for a
controller tuned on them. See [the v2 reproduction record](30_connectivity_results_and_reproduction.md).

## Troubleshooting

| Symptom | What to check |
| --- | --- |
| Script path not found | Work from the root containing `README.md` and `scripts/`. |
| HDF5 file not found | Use singular `dataset` and the exact filename inside this clone. |
| Different dataset hash | Obtain the exact reference file; a matching filename is insufficient. |
| Missing checkpoint after cloning | Weights are currently outside Git; restore, retrain or use a deterministic controller with the map. |
| Missing Python launcher | Use an installed Python 3.12 executable to create `.venv`. |
| Missing `torch`, `numpy` or `h5py` | Install requirements with the same environment executable used for evaluation. |
| Memory allocation failure | Allow for approximately 1.52 GB of selected RSS plus runtime and evaluation memory. |
| Checkpoint metadata/dimensions mismatch | Match the checkpoint study, evaluator and frozen configuration. |
| Custom endpoint argument error | Supply both coordinate pairs within the local map bounds. |
| Earlier output replaced | A reused prefix overwrites JSON/CSV; choose a new prefix per retained run. |

## Documentation Change Record

This guide and the prominent README setup section address the user's request
to document exactly where the dataset and other model artifacts belong. Both
earlier reproduction guides and the documentation index link here. The paths,
arguments, split counts and output behavior were checked against the existing
loaders, CLI parsers, frozen scenarios and writer implementation.

Validation checked 67 local documentation links and anchors, Markdown table
structure and code fences, all four saved v2 evaluation split sizes, and the
help output of both evaluators and the training runner. The dataset size and
SHA256 match the reference; all ten v2 checkpoints exist locally. Git tracks
neither the dataset nor checkpoint binaries. All six v1 and seven v2 frozen
source/protocol hashes still match. These are documentation and artifact
checks using the existing Python 3.12.10 environment; no clean environment
installation, new training or simulation was performed for this revision.

No dataset or model weights are newly published by this documentation change.
The external inputs for a fresh clone remain the private map and, unless
retraining, the chosen checkpoint. Frozen code, policies, results and paper
are preserved. The next user step is to place the artifacts, install the
recorded environment and run a custom route; new research needs a separate
protocol. This guide documents execution and does not independently validate
the physical assumptions or claim a successful mission on every input route.
