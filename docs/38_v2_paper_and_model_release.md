# V2 Paper and Final Model Release

Date: 13 September 2026.

## Work and Reason

The user requested a V2 focused repository and paper, with the original written
reward evaluated on every other component of V2. The later clarification
removes historical V1 entirely from the final paper and limits its README
presence to a short provenance note. The full historical inventory remains
archived in note 39; prior source freezes and results are preserved.

Added V1.5 as an original reward adapter that delegates all transitions,
observations, filters and terminal rules to V2. Its PPO is identical except
for the environment import. A new protocol and 400 fresh test routes were
frozen before training and evaluation. Five original reward policies were
trained from scratch; all ten V2 policies were reused without seed selection.
The current comparison contains 7,600 final evaluations, all replayed exactly.

## Result and Interpretation

Both original and full reward achieve 95.7% standard joint success. The primary
full minus original difference is 0.0 percentage points [-2.8, 2.7]. Longer
success is 87.3% versus 85.8%, difference +1.5 points [-2.9, 6.1]. The null
primary result is retained. Full reduces handovers, weighted cost and flight
time on common successful routes, but increases delay and proxy energy and
reduces SINR. This is not a general reward improvement or PPO superiority claim.
Note 37 contains every seed, failure and paired metric.

## Paper and Documentation

The current `paper/unified.tex` now builds the V2 paper with V1.5 as its reward
control, using generated tables and figures from the fresh comparison.
Historical V1 appears nowhere in the final manuscript. The current PDF remains
`paper/UAV_joint_reward_connectivity_IEEE.pdf` for stable links. Authors remain
Guillem Moreno Garcia and Evgenii Vinogradov.

The earlier consolidated PDF and source are preserved as
`paper/UAV_joint_reward_connectivity_IEEE_20260912.pdf` and
`paper/unified_20260912.tex`. Its original audit is retained with the same date
suffix. Historical scripts and manuscripts are not current reproduction entry
points. Current build instructions are in `paper/README.md`.

The README has been rewritten around V2: mission criteria, complete observation
layout, actions, filtering, reward definitions, PPO settings, data/model choices,
new splits, exact source pages, results, limitations and setup commands. The
setup guide and documentation index now identify current weights and fresh
test routes rather than implying weights require separate restoration.

## Model Publication

The user explicitly authorized including trained weights. Git now includes
exactly 15 final `checkpoint.pt` files: five V1.5 original, five V2 full and five
V2 arrival. The [manifest](../models/checkpoint_manifest.json) lists paths,
seeds, sizes, SHA256, dimensions and training steps. Total size is 2,054,910
bytes, about 2.05 MB. Every file contains policy tensors and configuration
metadata; no raw radio map is embedded. All five seeds per arm are retained.

Narrow ignore exceptions include only those final paths. Other training and
development checkpoints remain excluded. The HDF5 remains private and ignored.
Binary attributes preserve checkpoint bytes, and explicit attributes protect
all seven newly frozen source/protocol files alongside the earlier thirteen.

## Validation and Remaining Scope

The 73 test suite passes. It includes source formula examples, reward invariant
state transitions across every failure mode, arrival/reset semantics, PPO
syntax identity, exact small full reward training equivalence and repeatable
original reward training. The new 7,600 episode replay matches every record.
The new source freeze, two old freezes and all reused weights remain unchanged.

The final CLI smoke checks load both an original reward checkpoint and a full
reward checkpoint and produce complete custom flight outputs. These are usage
checks, not additional confirmatory evidence. After snapshots were created,
default pytest discovery also found their archived test copy. A `pytest.ini`
now limits default discovery to `tests/`, preserving all snapshot bytes and
making the documented `python -m pytest -q` command run the intended suite.

The paper audit checks source citations, generated numbers, embedded fonts,
unresolved references, page bounds and absence of historical V1 material.
The final six page PDF has 35 pinpoint TFM citations and 18 embedded fonts,
with no unresolved final pass references, overfull boxes or out of page text.
All six rendered pages were visually reviewed, including the detailed paired
table, sample route figure, every seed and observation layout. The two custom
CLI smoke flights completed successfully and are excluded from study counts.
Its machine readable record and visual review status are in
`results/reward_comparison/analysis_v15/paper_audit.json`.
The delivery checks also verify Markdown links, exact staged checkpoint bytes,
no tracked private dataset, and the remote commit after publication.

The requested comparison is complete, including its null primary finding.
Software checks do not verify map version, sentinel meaning, dynamic traffic,
uplink calibration, real packet delay, switching interruption, obstacle safety,
energy calibration or connectivity between samples. The navigation prior and
filter are shared aids. The next research decision is independent evaluation
and separately frozen component ablations, not tuning on these test results.
