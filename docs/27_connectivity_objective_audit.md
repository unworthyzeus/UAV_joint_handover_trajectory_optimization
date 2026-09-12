# Connectivity Objective Audit

Date: 12 September 2026.

## Finding

The completed study establishes improved arrival behavior under the declared
radio model. It does **not** establish a solution to the full joint objective
of completing the mission while maintaining an application adequate connection.
Connectivity is represented, but its success criteria are permissive. Treating
the reward repair as a complete fix to the original thesis would be too strong.

Nearly straight trajectories are not by themselves evidence of an error. A
straight route can be appropriate when handovers maintain adequate service.
Here, however, the constraint and service audit identifies substantive gaps
independently of the trajectory appearance.

## What Was Checked and Why

The user questioned whether restoring destination arrival had displaced the
connectivity objective. We inspected the frozen environment, observations,
actions, reward, termination, and evaluation; compared them with the original
TFM definitions; and replayed saved flights with additional service diagnostics.

The replay covers both reward replacement treatments, all five training seeds,
and both existing 200 route test splits, plus the deterministic reference on
both splits: 4,400 episodes in total. Every original episode record matched
exactly. All six frozen source hashes matched. No policy, training setting,
scenario, original result, or frozen protocol was changed.

This is a **post hoc descriptive audit of existing test results**, not new
confirmatory evidence, a new policy comparison, or permission to tune against
these routes. Ten checkpoints were replayed; the deterministic controller has
no checkpoint. The other two treatment arms were not replayed in this audit.

## Original Definition Versus Our Executed Criterion

Original source: Marina Bermúdez Granados, *Deep Reinforcement Learning-Based
Joint Handover and Trajectory Optimization for 5G-Connected UAV*, 2026.
References below identify printed
pages; add two for the PDF viewer page. The complete definition index is in
[note 25](25_exact_changes_from_tfm.md).

| Aspect | Written original TFM | Frozen reimplementation and implication |
| --- | --- | --- |
| Objective | Minimize weighted delay, interference, and handovers [TFM, printed p. 10, Eq. (11); p. 11, Eq. (12)]. | Fixed reward prioritizes arrival and time, with small delay, RSS outage, and handover costs. Direct interference cost was removed. The reward intervention changes the communication tradeoff as well as approach shaping. |
| Minimum connectivity | Serving RSS must meet the minimum at every time [TFM, printed p. 11, Eq. (12), C2]. | Outage is serving RSS at or below −96 dBm. Five consecutive sampled outage seconds end a flight. Evaluation permits an RSS outage fraction up to 5% in recorded feasible success. This is weaker than the written all time condition. |
| Enforcement in the original agent | RSS violation has a reward penalty [TFM, printed p. 12, Eq. (14); p. 15, Table 3]. | The written constraint is not evidence that the unavailable original implementation guaranteed continuous connectivity. Our comparison concerns definitions and our executable behavior. |
| Service quality | Delay is queue divided by rate [TFM, printed p. 9, Eq. (4)]; rate and noise definitions appear in Eqs. (7)–(8) [TFM, printed p. 10]. | We compute a downlink SINR capacity proxy and backlog/service delay proxy. Neither minimum capacity nor a latency deadline is a mission constraint. |
| Buffer | Queue must stay within capacity [TFM, printed p. 11, Eq. (12), C4]. The thesis describes removal of a direct data dump penalty [TFM, printed pp. 20–21, Sec. 7.3]. | Overflow is dropped and counted. It does not terminate the mission or incur a direct fixed reward penalty. Zero drops is checked only in the separate recorded feasible success label. Arrival does not require the remaining queue to be delivered. |
| Network control | Agent selects BS and RBG [TFM, printed p. 12, Sec. 5.2]; resource reassignment is described on p. 9, Sec. 3.3.1. | Agent selects stay or a masked top RSS candidate. RBG selection is deterministic. Association candidates are screened by RSS improvement, not achievable SINR. Handovers have control bits but no interruption duration. |
| Background load | At least half of resources randomly occupied [TFM, printed p. 14, Sec. 6.1; p. 15, Table 3]. | A deterministic half occupied pattern is static. Its phase rotates resource labels, rather than generating independent temporal traffic conditions. |
| Reported original difficulty | The source describes prioritizing connectivity over task completion [TFM, printed p. 21, Sec. 8]. | Our ablation repairs completion within a shared surrogate. It does not establish that the original wandering was wholly unnecessary for communication, or that our communication model reproduces the original one. |

The executed fixed reward's radio cost is

```text
0.05 * (min(delay_proxy_seconds, 1) + rss_outage_indicator + handover_indicator)
```

Thus the delay part supplies no additional penalty for worsening delay once
the proxy exceeds one second. There is no direct SINR, interference, lost bit,
or undelivered final queue term. The policy observes radio features, so this
does not show that it ignores them. It shows that the objective and feasibility
rules do not enforce the stronger service claim.

Reward normalization and clipping during PPO also mean raw coefficient
comparisons alone cannot explain learned behavior. Our evidence here is the
executed criteria and measured outcomes, not an attribution based solely on
the ratio between success and radio reward coefficients.

## Why Straight Paths Are Plausible Here

The full grid audit found at least **38 operator 1 stations above −96 dBm at
every location**, with median 63 and maximum 77. The strongest signal ranges
from −51 to −25 dBm. See [note 17](17_received_dataset_assessment.md), which
uses the original threshold [TFM, printed p. 15, Table 3].

This provides no geographic coverage hole under that RSS definition if an
arbitrary suitable station can be selected. Actual association restrictions,
motion between observations, and interference can still impair service.
Strong received signal alone is not evidence of high SINR or adequate capacity.

The deterministic reference chooses motion solely from destination and velocity,
and performs admissible handovers separately. It completes all routes. This
shows that the current arrival task can be solved with nearly straight motion;
it does not prove that its service is sufficient or that no useful detour exists.

On successful standard missions, mean path length divided by the original
start to goal distance is 1.033 for reward replacement alone, 1.024 for both
changes, and 1.001 for the reference. These are averages of per mission ratios.
The 10 m arrival tolerance means the exact destination need not be reached;
the ratio is a descriptive measure and can be less than one on individual flights.

## Measured Connectivity and Service

Each learned treatment has 1,000 evaluated episodes per split: five policies
on the same 200 routes. The reference has 200. Reused routes are not independent
new test environments. We report no significance test for this audit.

| Standard routes | Reward replacement only | Reward and termination | Deterministic reference |
| --- | ---: | ---: | ---: |
| Arrival success | 100.0% | 99.7% | 100.0% |
| Frozen recorded feasible success | 98.7% | 97.8% | 97.0% |
| Arrival with zero sampled RSS outage | 92.2% | 91.6% | 92.0% |
| Successful flights used for secondary metrics | 1,000 | 997 | 200 |
| Mean handovers per successful flight | 3.96 | 2.99 | 2.38 |
| Mean fraction of flight with capacity below offered traffic | 26.6% | 27.8% | 29.8% |
| Mean longest consecutive capacity deficit | 3.79 s | 3.43 s | 3.10 s |
| Mean fraction with delay proxy above 1 s | 20.8% | 22.0% | 22.8% |
| Mean delay proxy per successful flight | 2.58 s | 2.83 s | 3.45 s |
| Successful arrivals with nonempty final buffer | 202 / 1,000 | 197 / 997 | 62 / 200 |

The zero sampled RSS outage row is a stricter diagnostic, not a revised frozen
endpoint. It is still measured at one second resolution and does not establish
connectivity between samples. The original written C2 condition applies at
every time [TFM, printed p. 11, Eq. (12)].

Capacity deficit means the modeled instantaneous capacity is below the
configured 200,000 bit/s application arrival rate. Under the implemented
1.44 MHz Shannon formula, the corresponding SINR is approximately −9.95 dB.
It is **not the same as disconnection**: a buffer can absorb short deficits,
and later service can clear the queue. Handover control bits create additional
demand beyond this threshold. The model does not track actual packet deadlines.

Each fraction is computed within a successful flight and then averaged equally
across successful flights. The table is not a pooled fraction of all simulation
seconds. Secondary metrics for the combined treatment exclude its three failed
standard flights and must be read alongside its arrival rate.

For reward replacement alone on longer routes, arrival remains 100%, but only
77.3% of episodes arrive with zero sampled RSS outage. Capacity is below the
offered rate for a mean 29.5% of flight time; 159 of 1,000 arrivals retain queued
data. These outcomes further separate destination arrival from uninterrupted
service and completed data delivery.

The reference has worse descriptive service metrics on several measures,
while completing faster. This suggests a time versus communication tradeoff
within the surrogate, but does not establish that learned path curvature is
the cause. Speed, association choices, and flight duration also differ.

## Interpretation and Remaining Work

The positive reward ablation remains valid for its frozen completion question.
Our recorded feasible success label is inadequate as evidence of continuous,
application adequate connectivity. The full original research goal remains
unfinished. A large penalty alone would not resolve this modeling and evaluation
gap, and could restore the incentive to wait or wander without completing a mission.

A separately labeled next study should:

1. Define the application's connectivity contract before training: allowed RSS
   or service outage duration, latency and loss limits, and whether mission
   completion includes delivery of queued data. Distinguish faithful testing of
   the original C2 condition from additional application QoS requirements.
2. Count arrival with violated communication requirements as failure of the
   **joint** mission endpoint. Keep plain arrival and each violation visible.
   Use constrained control or an explicit feasibility priority rather than
   allowing radio requirements to disappear inside an aggregate return.
3. Validate achievable service and route feasibility under the radio model.
   Audit dynamic occupancy, traffic, handover interruptions, candidate quality,
   and resource control. Clearly label any new assumptions or artificial stress
   conditions; do not alter the received map to manufacture attractive curves.
4. Compare straight motion with network control, communication aware routing,
   and joint motion/network control under identical requirements and budgets.
   Isolate speed, routing, and handover contributions. A feasible route planning
   reference should establish whether detours can actually help on these maps.
5. Preserve the current study, use development scenarios for the new design,
   and freeze fresh tests before selecting the new policy. Existing test
   diagnostics must not be recycled as unseen confirmatory evidence.

No new training or stronger feasibility rule has been implemented in this audit.
Curvature is not an objective. The test is whether the controller completes the
mission while meeting declared communication requirements, and whether joint
control improves that outcome over simpler references.

## Reproduction and Artifacts

```powershell
python scripts/audit_connectivity_objective.py
```

- Script: `scripts/audit_connectivity_objective.py`.
- Per episode diagnostics: `results/controlled_experiment/connectivity_audit_v1/episodes.csv`.
- Aggregate and per seed metrics, checkpoint hashes, script hash, configuration,
  and exact replay count: `results/controlled_experiment/connectivity_audit_v1/summary.json`.
- Scope annotations: project README and paper README.

This note supplements the existing IEEE draft. The draft's original result
tables and PDF have not been revised during this audit. Its completion claims
must be read with this explicit connectivity limitation; a full joint objective
claim is not supported by the current experiment.
