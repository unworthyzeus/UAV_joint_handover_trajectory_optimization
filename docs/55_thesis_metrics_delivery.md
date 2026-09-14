# Thesis Metrics and V2.2 Delivery Verification

Date: 14 September 2026.

## Work and Purpose

The user requested missing thesis metrics, an attempt to improve performance,
and a clear presentation primarily in the README. We added passive
measurements to unchanged initial flights and evaluated a separately declared
lookahead supervisor. The single paper includes the source consistency audit,
new results, service tradeoffs and every fixed policy seed. The README keeps
source quantities separate when their physical meaning or aggregation differs.

## Verified Artifacts

- All 33 source/protocol files in five experiment freezes are unchanged.
- All 20 released weights are unchanged, totaling 2,741,480 bytes. V2.2 reuses
  five full V2 policies and adds no newly trained network.
- All 23,000 new final episodes and their sample arrays replay exactly.
- All 4,000 initial V1.5/full V2 episodes preserve every original field while
  adding the missing measurements. These are not independent new flights.
- The 94 implementation tests pass. The new tests cover the metric formulas,
  station exclusion, source energy diagnostic, state preservation during
  planning and passive instrumentation.
- A custom route from (1000, 1000) to (1800, 1300), policy seed 2101, completes
  in 40 s through the documented evaluator. This is a usage check, not a new
  statistical performance sample or selection criterion.
- Initial statistics, three initial figure PDFs and all old result records
  remain intact. No private HDF5 is included in Git.

The [machine readable delivery audit](../results/thesis_metrics_v22/analysis/delivery_validation.json)
checks the new README tables against the saved statistics, recovered means
and CDF medians. It independently recomputes sampled SNR, remaining energy
and handover frequency from all 27,000 episode records and arrays, checks
padding and successful mission constraints, and verifies the exact replay
file hashes. It also records the current paper hash and visual review.

The [paper audit](../results/reward_comparison/analysis_v15/paper_audit.json)
retains source hashes, printed page citation locators, embedded font checks,
text bounds, final compiler diagnostics and the review of rendered pages.
The location is historical; its scope is explicitly the current unified paper.
Earlier delivery snapshots retain their original commit scope.

## Execution Record and Reproduction

The final evaluation started serially, then resumed in three independent
workers to reduce elapsed time. Completed runs were reused and replayed;
one unfinished run restarted through the same frozen evaluator. No batch
size, controller parameter, route or source changed. The orchestration hash
and this execution note are stored in the
[replay audit](../results/thesis_metrics_v22/replay_audit.json).

From the repository root, after compilation and visual review:

```powershell
python scripts/audit_metric_interpretation.py
python scripts/audit_v2_reward_paper.py
python scripts/audit_thesis_metrics_delivery.py
```

The metric recovery and controller setup commands are in
[note 54](54_thesis_metrics_reproduction.md). The declared scientific source
and selected horizon are frozen in
[`configs/frozen_thesis_metrics_v22.json`](../configs/frozen_thesis_metrics_v22.json).
The [result note](53_v22_guard_results.md) includes every candidate and all
fresh completion and service outcomes; no further tuning followed those tests.

## Limits and Next Decision

The new measurements do not settle physical uplink calibration, the original
energy recurrence or the original handover normalization. Source SNR figures
exceed the bound implied by its stated equation and the same map; this does
not identify the coding cause. The supervisor uses more known map computation,
and its results do not show an isolated reward effect or a new learning method.

Further work needs independent routes, maps or traffic and declared component
ablations. Existing evaluation routes must not be used to tune another
candidate. All mission failures and unsuccessful reward candidates remain
visible in the completed record.
