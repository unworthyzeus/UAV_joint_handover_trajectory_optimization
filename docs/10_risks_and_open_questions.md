# Risks and Open Questions

## Blocking Questions

1. Where is the exact source commit used by Marina?
2. Where is the Barcelona channel database and what is its schema?
3. Which routes, seeds, and checkpoints generated the thesis figures?
4. Is resource occupancy observed by the agent or intentionally hidden?
5. Does the implementation match the equations printed in the thesis?

## Scientific Risks

### Reward Repair May Explain Most of the Gain

Changing the algorithm and the environment together would make attribution impossible.

Mitigation: use the staged ablation in `docs/05_solution_architecture.md`.

### Deterministic Overfitting

A policy can memorize positions in one fixed Barcelona map.

Mitigation: hold out route pairs and spatial regions, vary traffic and occupancy, and later test map or propagation perturbations.

### Hidden Partial Observability

If candidate resource occupancy, handover timers, velocity, or traffic are hidden, the problem is a POMDP rather than the stated MDP.

Mitigation: expose observable variables, document genuinely hidden state, and test recurrent policies only when needed.

### Invalid Physical Metrics

Using dBm in arithmetic or mixing power and energy units can make impressive numerical results meaningless.

Mitigation: unit tests with reference calculations before policy training.

### Weighted Sum Collapse

One fixed reward vector can hide poor mission or tail behavior.

Mitigation: constraints, separate metrics, preference sweeps, and Pareto reporting.

### Evaluation Leakage

Repeated tuning on a small set of destination pairs can overfit the benchmark.

Mitigation: versioned train, validation, and test scenarios with test results generated once per frozen model family.

## Method Questions

1. Is a learned controller better than graph search in the deterministic setting?
2. Should resource allocation remain a policy action or a lower level optimizer?
3. What is the appropriate network decision interval relative to flight control?
4. Which constraints are strict, and which may be traded off?
5. Is the final goal one policy, a preference conditioned policy, or a Pareto set?

