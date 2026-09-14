# Thesis Metrics and V2.2 Model Usage

Date: 14 September 2026.

## Dataset and Model

The README contains the main comparisons. Notes 51, 52 and 53 record the
declared protocol, source metric recovery and fresh controller results.
The dataset is the same unchanged dataset as in the original thesis:

```text
dataset/Barcelona_dataset_January.h5
```

Expected size: 2,327,593,160 bytes. SHA256:

```text
d4630dd3a6c45419e12d0b60dd08473c4ffa4062ca4fab1decabecf2b992ea0d
```

V2.2 adds a finite lookahead supervisor to the five existing full V2 policies.
It does not introduce a newly trained network or additional weights. The
selected horizon is five steps. The same twenty published checkpoints still
cover all studies; V2.2 uses this subset, with seeds 2101-2105:

```text
results/connectivity_experiment/confirmatory_v2/full_seed_2101/checkpoint.pt
```

The architecture, observations, physical transitions, A3 rule and mission
constraints remain V2. The supervisor changes action selection and performs
additional map queries. Its measured wall time depends on machine resources
and concurrent jobs; it is not a demonstrated real time deployment controller.

## Evaluate a Saved or Custom Route

Use the same Python 3.12 environment and experiment dependencies as note 35.
From the repository root:

```powershell
python scripts/evaluate_thesis_metrics_controller.py --controller guard --seed 2101 --split test --output outputs/v22_standard_01
python scripts/evaluate_thesis_metrics_controller.py --controller guard --seed 2101 --start 1000 1000 --goal 1800 1300 --output outputs/v22_custom_01
```

Available controllers are `guard`, `full`, `original`, `service`,
`straight_radio`, `joint_mpc` and `joint_lookahead`. Learned controllers reuse
one of the five declared policy seeds. Fresh saved splits are `test` and
`longer_test`, each with 500 routes. Coordinates are local meters within
the 5000 by 3500 m map. Supply both start and goal for a custom route.

Outputs are a JSON containing episode outcomes and added metrics, plus a
compressed NPZ containing per step samples and their counts. Existing output
prefixes are rejected. A route can fail; all failures remain recorded.

## Reproduce the Study

Choose a new label and use it throughout to preserve delivered results:

```powershell
python scripts/run_thesis_metrics_study.py --phase development --label local_v22_01
python scripts/run_thesis_metrics_study.py --phase freeze --label local_v22_01
python scripts/run_thesis_metrics_study.py --phase evaluate --label local_v22_01
python scripts/run_thesis_metrics_study.py --phase replay --label local_v22_01
python scripts/analyze_thesis_metrics_study.py --label local_v22_01
```

The source freeze, selected horizon and scenario hashes must match during
every phase. A reproduction repeats the declared selection procedure and
uses the same route seeds. It is not new independent evidence. Further
controller tuning needs a new declared protocol and unused evaluation routes.

The delivered evaluation began serially and then used three worker processes
to run independent jobs through the unchanged frozen evaluator. Its 500 route
batch size and controller computations stayed fixed. Completed records were
retained and replayed; an unfinished run was restarted. The supplementary
orchestrator is `scripts/finish_thesis_metrics_parallel.py`, and its hash and
execution note are retained in `results/thesis_metrics_v22/replay_audit.json`.
The serial commands above remain the portable reproduction path.

## Metric Files and Interpretation

- `confirmatory/`: all fresh outcomes and per step arrays.
- `initial_replay/`: additional measurements on the 4,000 unchanged initial
  V1.5/full V2 episodes, with exact original field comparisons.
- `development/`: all three guard candidates and both references.
- `analysis/statistics.json`: fresh completion, failures and paired intervals.
- `analysis/initial_recovered_metrics.json`: initial matched means and pooled
  sample CDF medians, kept separate from fresh routes.
- `map_metric_bounds.json`: dataset hash and possible Eq. (8) SNR bound.

The `.npz` arrays contain valid executed samples followed by NaN padding;
`counts` identifies the executed length for each route. Missing serving paths
also yield NaN SNR and an explicit missing signal count in JSON. Other RSS
sentinels contribute zero linear power to the neighbor sum. The raw integer
RSS sum diagnostic retains the sentinel values and is not a power in dBm.
The literal source energy score is not energy and has no physical unit.

The source labels Eq. (9) uplink, but a physical uplink model is still not
calibrated. Remaining energy in kJ uses the declared V2 accounting, and
handover frequency has an explicit seconds denominator instead of guessed
source normalization. Every positive or negative performance conclusion must
refer to the defined metric, controller, route set and common success subset.
