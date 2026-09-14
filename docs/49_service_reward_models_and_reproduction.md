# V2.1 Models, Dataset and Reproduction

Date: 14 September 2026.

## Scope

V2.1 is the validation selected service reward on the same V2 simulator and
PPO architecture. Its new results are in note 48; its development and frozen
selection are in notes 46-47. V1.5 and full V2 remain the fixed controls.
The experiment changes the training reward, not physical feasibility rules,
navigation assistance, observations or the safety filter.

The dataset is the same Barcelona dataset as the original thesis. Place it
at this exact path relative to the repository root:

```text
dataset/Barcelona_dataset_January.h5
```

Its expected size is 2,327,593,160 bytes and SHA256 is:

```text
d4630dd3a6c45419e12d0b60dd08473c4ffa4062ca4fab1decabecf2b992ea0d
```

The private HDF5 is excluded from Git. V2.1 needs the same Python 3.12
environment and `requirements-experiments.txt` installation as note 35.

## Final Models

The five final V2.1 weights use the following pattern, with seeds 2101-2105:

```text
results/service_reward_v21/confirmatory/service_seed_2101/checkpoint.pt
```

`models/service_reward_manifest.json` records all five paths, byte sizes and
hashes. The initial comparison's separate `models/checkpoint_manifest.json`
continues to record the unchanged fifteen V1.5/V2 weights. Thus the release
contains twenty final policies across the two comparisons. V2.1 reuses only
the ten V1.5 original and full V2 controls, not the arrival arm.

Pilot weights remain local development artifacts. Their configurations,
logs, validation results and hashes are retained under
`results/service_reward_v21/development/`, and the declared pilots can be
regenerated. They are not final models or additional independent final seeds.

## Evaluate a Checkpoint

Use the V2.1 evaluator because its checkpoint metadata includes the new
reward coefficients. From the repository root, in PowerShell:

```powershell
python scripts/evaluate_service_reward_controller.py --checkpoint results/service_reward_v21/confirmatory/service_seed_2101/checkpoint.pt --split validation --output outputs/service_validation_01
```

For a custom route, supply both start and goal in local meters:

```powershell
python scripts/evaluate_service_reward_controller.py --checkpoint results/service_reward_v21/confirmatory/service_seed_2101/checkpoint.pt --start 1000 1000 --goal 1800 1300 --load-phase 0 --output outputs/service_custom_01
```

The map is 5000 by 3500 m. Available saved splits are `validation` (64),
`validation_longer` (32), `test` (500) and `longer_test` (500). Custom start
and goal replace the saved split. The evaluator writes a JSON and a CSV
with episode outcomes, metrics and up to four traces. An existing output
prefix is rejected rather than overwritten. A custom route can fail; the
model does not guarantee successful missions or continuous physical service.

## Repeat the Entire Study Separately

Choose a new label and use the same label in every command:

```powershell
python scripts/run_service_reward_study.py --phase development --label local_v21_01
python scripts/run_service_reward_study.py --phase freeze --label local_v21_01
python scripts/run_service_reward_study.py --phase train --label local_v21_01
python scripts/run_service_reward_study.py --phase evaluate --label local_v21_01
python scripts/run_service_reward_study.py --phase replay --label local_v21_01
python scripts/analyze_service_reward_study.py --label local_v21_01
```

The freeze phase requires the declared development gate to pass. Results
go to `results/service_reward_local_v21_01/`; new manifests and scenarios
use the same label in `configs/`. A fresh label is required for an incomplete
run because training and evaluation reject existing output folders. Final
control weights remain the published, hash verified V1.5 and full V2 models.
The source manifest and route files must match throughout each reproduction.

Do not use the delivered test routes to tune another reward and then present
them as fresh tests. A local exact reproduction is not additional independent
evidence. New scientific tuning requires a new declared protocol and new
evaluation routes. The original delivered study label must not be overwritten.

## Audit and Remaining Limits

The final source freeze is `configs/frozen_service_reward_v21.json`.
The raw records are under `results/service_reward_v21/confirmatory/`,
the statistics under `analysis/statistics.json`, and the exact replay audit
under `replay/audit.json`. The paper includes the new comparison separately
from the initial 53012/53013 result tables.

Verify the delivered documentation and artifacts from the repository root:

```powershell
python scripts/audit_metric_interpretation.py
python scripts/audit_service_delivery.py
```

These audits verify the saved results and delivery evidence; they do not
rerun training. The recorded 88 test result is retained at
`results/service_reward_v21/analysis/implementation_tests.txt`. To rerun the
implementation suite, use `python -m pytest -q`.

All twenty final weights, historical freezes and the new freeze are checked
by the delivery audit. The README values are checked against saved statistics,
and the current PDF is compiled and visually inspected. Software consistency
does not establish physical accuracy. Same map evaluation, static traffic,
proxy energy, instantaneous switching and sampled constraints still limit
conclusions; the original thesis simulator and policies remain unavailable.
