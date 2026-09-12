# Exact Changes in the Connectivity Repair

Date: 12 September 2026. This note supplements the complete original TFM versus
v1 comparison in [note 25](25_exact_changes_from_tfm.md). It describes the final
v2 design, not the earlier pilot versions preserved in note 29.

Original locators refer to printed TFM pages; add two for the PDF viewer page.
The source is Marina Bermúdez Granados's 2026 master's thesis. An original
written definition is not evidence that its unavailable implementation enforced
that definition exactly.

## User Scope

The user selected the same requirements as the thesis. We therefore did not
introduce the proposed 2 s packet deadline, a minimum throughput requirement,
or mandatory delivery of the remaining queue before arrival. The source
defines delay as queue/service rate [TFM, printed p. 9, Eq. (4)] and optimizes
delay, interference and handovers [TFM, printed p. 10, Eq. (11)]. Its written
communication constraints are minimum RSS and bounded queue [TFM, printed
p. 11, Eq. (12), C2 and C4].

## Executed Differences

| Item | v1 executed behavior | Final v2 executed behavior | Original source relationship |
| --- | --- | --- | --- |
| Minimum RSS | RSS ≤ −96 dBm counts as outage. | RSS < −96 dBm counts as violation; equality is allowed. | Follow C2's ≥ inequality [TFM, p. 11, Eq. (12)] and the numeric minimum [p. 15, Table 3]. |
| Initial RSS | Strongest station selected at reset; no separate persistent initial violation flag. | Check the initial serving RSS and preserve any violation until failure. | Include the initial modeled sample in C2 [TFM, p. 11]. |
| Failure rule | Five consecutive sampled outages terminate a flight. | Any single sampled RSS violation terminates a failed joint mission. | Enforce the written C2 at modeled samples [TFM, p. 11], rather than reproduce the source's soft reward penalty [p. 12, Eq. (14)]. |
| Buffer overflow | Count lost bits, clip queue, continue flight; disqualify only the subsequent feasible label. | Any overflow ends failure; clipping cannot erase it. | Enforce C4 at the sampled queue update [TFM, p. 11, Eq. (12)]. Source removal of a direct dump penalty is described on pp. 20–21, Sec. 7.3. |
| Joint success | Arrival is primary; recorded feasibility permits up to 5% RSS outage and zero drops. | Arrival plus no prior sampled RSS violation, no overflow, and no physical failure. No additional permissive feasibility label. | Combine source communication constraints [TFM, p. 11] with explicit destination completion. |
| Event precedence | Some physical failures override arrival; overflow does not. | RSS, overflow, boundary and energy failure override simultaneous arrival. | New explicit ordering; original source ordering is unspecified [TFM, p. 12, Sec. 5.2]. |
| Outstanding queue at arrival | Allowed. | Still allowed and reported. | The source does not specify an empty queue arrival test [TFM, pp. 9–12, Secs. 3.2–5.2]. We do not claim all generated data has been delivered. |
| Delay cost | `0.05 * min(D, 1)` inside fixed reward. | `0.35 * 10D / (1 + 10D)` in full arm. No flat reward plateau at one second. | One minus original reciprocal utility [TFM, p. 12, Eq. (13)] with equal configuration values [p. 15, Table 3]. Smooth saturation remains. |
| Interference cost | Absent from fixed reward, although measured. | Restore `0.30 * 100000I / (1 + 100000I)`. | Same reciprocal utility scales and weights [TFM, pp. 12, 15]. I remains our downlink proxy. |
| Handover cost | `0.05 * H`. | `0.35 * 100H / (1 + 100H)`. | Restore normalized source utility [TFM, p. 12, Eq. (13); p. 15, Table 3]. |
| Positive per step radio utility | Present in reimplemented legacy reward, removed in v1 fixed reward. | Subtract communication cost, so simply staying active does not earn that utility bonus. | Changes the positive reciprocal reward structure [TFM, p. 12, Eqs. (13)–(14)] while preserving the three normalized tradeoff components. |
| Learning comparison | Four reward/termination arms; direct acceleration learning. | Two arms: arrival base only versus arrival base minus all three radio costs. Both use strict failure, termination and the same new controller architecture. | A new controlled comparison; neither arm is the source's trained policy. |
| Network decision timing | Every five seconds, with observed outage exception. | Every modeled second. | Source describes choices each environment step [TFM, pp. 9, 12, Secs. 3.3.1, 5.2]; a five second interval was our prior assumption. |
| Network action | Stay plus four strongest candidate stations: five categorical choices. | Stay plus five candidate station slots by 12 groups: 61 choices. | Restores resource choice from the source's BS/RBG action [TFM, p. 12, Sec. 5.2]. |
| Station candidate selection | Serving plus strongest four, stable RSS ordering. | Retained. Duplicate serving station slots are masked. | Restricted candidate interface is ours; source lists full BS/RBG choices [TFM, p. 12]. |
| A3 condition | Candidate RSS > serving RSS + 3 dB. | Retained; prospective filter cannot bypass it. | Follow the inequality, not the reversed nearby prose [TFM, p. 9, Eq. (3); p. 15, Table 3]. |
| Resource allocation | Deterministic first free RBG at reset and handover. | That initialization remains; the controller can choose any currently free RBG, including within the same station. | Source allows RBG requests with fallback [TFM, p. 9, Sec. 3.3.1]. The exact masking implementation is ours. |
| Repeating a resource choice | No learned resource choice. | Current serving station/group pair remains a valid pair action; explicit stay also remains. | Avoid a new artificial alternating action mask; this is an implementation decision. |
| Resource change count | Not independently reported. | Count every station/group change, including same station RBG changes. | Diagnostic addition. Same station resource changes are not counted as handovers. |
| Switching interruption | Not modeled. | Still not modeled; no extra RBG switching cost. | Source does not provide a calibrated interruption duration [TFM, p. 9, Sec. 3.3.1; p. 15, Table 3]. This remains a limitation, not a verified original behavior. |
| Continuous action | Two direct radial/lateral acceleration commands. | Projected reference command plus two bounded learned residuals of scale 0.5, followed by physical projection. | New controller prior; differs from original discrete acceleration and heading [TFM, p. 12, Sec. 5.2; p. 15, Table 3]. |
| Safety filter | None. | Predict the next sample; repair unsafe network choice if possible, otherwise try local motion/network alternatives; still fail if unresolved. | New model based constraint handling component; original source describes reward penalties [TFM, p. 12, Eq. (14)]. |
| Prospective radio access | Learned policy observes current candidates. | PPO still observes current options. Its shared filter and model based references query the known map at predicted positions. | New information/control architecture, not reproduced source logic. |
| Observation | 42 features. | 156 features, detailed below. | Original source has six listed state elements [TFM, p. 12, Sec. 5.2]. Both are reimplementations with repaired state. |
| PPO network head | Five categorical logits. | 61 categorical logits; continuous and value heads retained. | Original architecture details are not sufficiently specified [TFM, p. 13, Sec. 5.3]. |
| Training route lengths | 200–1000 m. | 200–1800 m; longer tests lie within this range. | New study design; original route distribution and independent splits are not documented [TFM, pp. 15–16, Secs. 6.2–6.3]. |
| Final route identities | Seeds 42012 and 42013. | Fresh seeds 52012 and 52013. Exact pairs are disjoint from v1 and other v2 splits. | Our explicit split protocol; same map remains shared. |
| Training seeds | 1101–1105. | 2101–2105. | New repeated experiment; original seed list is unspecified [TFM, pp. 15–16]. |
| Final budget | 524,288 interactions each; 20 policies. | Same interactions per policy; 10 policies. | Our PPO budget remains different from 300 episodes and 2,000 maximum steps in the source [TFM, p. 16, Table 4]. |
| Deterministic references | Destination braking and strongest admissible RSS. | Four nominal control laws with the same filter: Goal RSS, Goal radio, one step joint search, and three step joint search. | New references, not a recreation of the thesis's discrete constant velocity greedy controller [TFM, pp. 13–14, Sec. 5.4]. |
| Secondary comparison | Success conditioned summaries and selected matched comparisons. | Explicit intersections of successful route/seed pairs for radio comparisons, with counts and crossed bootstrap intervals. | Source does not report a matching conditional joint success protocol [TFM, pp. 16–20, Sec. 7]. |

## Exact Observation Layout

| Zero based indices | Definition |
| --- | --- |
| 0–1 | Position / map dimensions |
| 2–3 | Destination direction unit vector |
| 4 | Destination distance / 1,000 m |
| 5–6 | Radial and lateral velocity / 25 m/s |
| 7 | Speed / 25 m/s |
| 8 | Elapsed decision count / 200 |
| 9 | Queue / 1,280,000 bits |
| 10 | Consumed energy / 100,000 J |
| 11–12 | Background phase / 11 and serving RBG / 11 |
| 13 | Serving SINR in dB / 30 |
| 14–18 | Candidate RSS, transformed as `(RSS + 70) / 60` |
| 19–28 | Candidate station x/y offsets / 5,000 m |
| 29–33 | Candidate station index / 86 |
| 34–94 | `log(1 + option_capacity / 200000)` for all 61 network choices |
| 95–155 | Corresponding Boolean action masks as float features |

The earlier ever arrived feature, consecutive outage counter, and five second
decision phase are removed from the learned observation. Arrival and RSS
violation now terminate the modeled mission immediately.

## Details Retained from v1

All unchanged map, units, motion, energy, traffic, rate, noise, RBG occupancy,
PPO optimizer, and numeric limitations remain specified in note 25 and the
v2 frozen configuration. In particular, v2 does not silently switch to the
source's SNR capacity expression [TFM, p. 10, Eqs. (7)–(8)], or assert that the
downlink interference proxy is calibrated uplink interference [TFM, p. 10,
Eq. (9)]. It retains the one second surrogate step and 25 m/s speed cap rather
than the source table's 0.1 s and 100 m/s [TFM, p. 15, Table 3].

The inherited serialized `max_consecutive_outage: 5` field is unused by the
v2 step function. It does not permit five outages: v2 terminates on the first
violation. Likewise, v2 makes a network decision each step; it does not use
the old periodic gate. These compatibility fields must not be mistaken for
executed v2 logic.

Delay is still the numerical backlog/service proxy, censored at 200 s; no
actual packet deadline or latency distribution is available. Static resource
phase rotates labels rather than sampling independent traffic dynamics. The
raw radio file and its sentinel interpretation remain as previously documented.

## Artifact and Claim Boundaries

The new authoritative implementation is in `connectivity_env.py`,
`connectivity_ppo.py` and `connectivity_planner.py`. Frozen settings and source
hashes are in `configs/frozen_connectivity_v2.json`; note 28 defines the final
protocol, note 29 records every development revision, and note 30 reports final
results and reproduction commands. The original six v1 frozen files remain
unchanged.

This is a correction of the modeled joint objective and success criteria with
new control components. It is not a claim of zero failures on all routes,
improvement in every communication metric, real continuous connectivity between
samples, or a replicated fix to the unavailable original simulator.
