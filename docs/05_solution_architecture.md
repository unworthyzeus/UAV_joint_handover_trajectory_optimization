# Proposed Solution Architecture

## Principle

Do not begin by replacing PPO with a more complicated model. First repair the task definition and build a deterministic benchmark. Then test whether learning adds value in stochastic or partially observed conditions.

## Layer 1: Deterministic Planner

Construct a time expanded or motion feasible graph over the urban grid. A node represents position, time, and serving cell at the required resolution. An edge represents a feasible movement and optional handover. Edge attributes keep time, energy, delay, interference, outage risk, and handover cost separate.

Run shortest path or A* for simple baselines and a minimum weight graph method for the joint deterministic benchmark. Im et al. show that a related joint trajectory and handover problem can be converted to a polynomial time minimum weight path problem: [paper record](https://doaj.org/article/00fb7cc137a444a9a898201e1ecc318c).

This planner provides:

1. A guaranteed mission completing reference when a feasible path exists.
2. A lower bound or strong benchmark for travel and handover cost.
3. Demonstrations or waypoints for the learned controller.
4. A fallback when the policy proposes unsafe behavior.

## Layer 2: Mixed Action Controller

Use continuous acceleration and heading for the initial motion interface. Use a masked categorical head for stay or handover decisions and an optional masked resource head. The heads may share an encoder but should expose separate action distributions and diagnostics. Reconsider heading as a bounded turn rate after the simulator dynamics and control interval are recovered.

Candidate selection should keep only base stations that are observable, geographically relevant, and protocol feasible. The current serving cell must always remain a valid stay action unless the environment has declared a radio failure.

The executable `MixedAction` class is an unmasked audit interface over all 87
base stations and 12 resource groups. It documents the inherited cardinality;
it is not yet the candidate based controller described above.

Candidate algorithms after the environment is validated:

1. Continuous PPO with separate masked categorical network actions.
2. Soft Actor Critic for continuous flight plus a discrete network head.
3. P DQN, Hybrid MPO, or another native mixed action actor critic.
4. Constrained policy optimization or a Lagrangian actor critic for explicit limits.

## Layer 3: Multiobjective Evaluation

Train a small set of clearly defined preferences or a preference conditioned policy. Keep success and safety fixed. Sweep only secondary objective preferences. Present a Pareto front rather than choosing a single undocumented reward vector.

## Required Ablations

1. Legacy formulation and PPO.
2. State repair only.
3. Reward and termination repair only.
4. Action masks only.
5. Continuous motion only.
6. All formulation repairs with PPO.
7. All repairs with the selected mixed action method.

This sequence distinguishes an algorithm improvement from an environment correction.
