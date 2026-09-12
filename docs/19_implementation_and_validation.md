# Implementation and Validation

Date: 12 September 2026.

## What Was Done and Why

Implemented a vectorized environment in `experiment_env.py`, native hybrid
Gaussian and categorical PPO in `experiment_ppo.py`, an experiment runner,
and tests for dynamics, arrival, potential telescoping, terminal bootstrap,
masked action likelihoods, deterministic route completion, and identical
physical trajectories under different reward treatments. These checks precede
policy training to avoid confusing environment errors with learning failures.

## Initial Results

The original 22 tests plus eight new experiment tests passed. A deterministic
controller completed 61 of 64 validation missions with the first radio interface.
Inspection showed that a five second network interval could defer an available
handover until after five outage samples had already ended the episode. The
updated common mask therefore also permits a request on an observed RSS outage.
This is an environment correction made before training, not a reward treatment.

The raw backlog/service delay proxy became extremely large during zero service.
The experiment now censors that proxy at the mission deadline, explicitly in
the model and documentation. It does not claim empirical packet latency.

Exploratory deterministic results are retained under
`results/controlled_experiment/baseline_v1/`. Its route seeds 42002 and 42003
were viewed during feasibility inspection and retired. Final test seeds 42012
and 42013 replace them before any training. All development uses validation
seed 42001. This change prevents silent reuse of inspected routes as untouched
tests.

## Initial Remaining Work and Risks

Run the updated deterministic check and pilot PPO. The implementation is a
documented reconstruction, and passing unit tests does not establish full
equivalence to the unavailable original simulator. The original airframe,
traffic, and handover timing are unknown. PPO uses a latent Gaussian policy
whose samples pass through tanh and an acceleration norm limit; likelihood
ratios are calculated consistently in latent action space. The entropy bonus
uses latent Gaussian entropy and masked categorical entropy.

## Initial Next Decision

Verify deterministic mission completion after the common interface correction,
then use separate pilot seeds to set an equal training budget for all arms.

## Final Validation and Outcome

The completed suite has 34 passing tests. Additional checks exercise multi
episode GAE resets, native radio axes and coordinate spacing, emergency network
mask behavior, and an actual PPO update repeated with the same seed. The common
environment source, PPO source, runner, scenarios, and protocol notes were
hashed before the final comparison. Analysis verified every frozen hash and
the configurations, budgets, seed identities, and paired route identities.

The corrected deterministic controller completed all 64 validation missions.
Six pilots preceded twenty final runs. The full results are in note 21;
reward replacement alone completed all standard and longer test missions.
The combined change completed 99.7% and 36.1%, respectively.

Loading `reward_only_seed_1101/checkpoint.pt` and evaluating its 200 standard
routes produced exactly the same raw episode records as the saved evaluation.
Replay outputs are retained under `outputs/replay_seed_1101.json` and `.csv`.
The replay uses deterministic action evaluation and first safe arrival
termination for every treatment. Checkpoints support inference replay, not a
bitwise resumption of optimizer and environment state.

The separate dynamics based reward witness uses the actual radio map and
motion equations. On a 1000 m route, a 2 m/s flight that remains 601 m away at
the deadline receives more legacy reward than a controller that arrives in
46 s. Reward replacement reverses that ranking. The arriving controller drops
83,856 bits, so this is an incentive counterexample about mission completion,
not evidence that both trajectories satisfy every recorded feasibility check.
Its raw metrics are in `results/tables/physical_reward_audit.json`.

The shaping telescoping identity applies before reward normalization and
clipping. These training transformations can change the effective objective;
the ablation tests the complete documented recipe rather than separately
estimating each transformation's effect. Passing tests and replay establishes
properties of this implementation, not equivalence to unavailable source code.

No further implementation work is needed for this frozen study. The next
decision is whether to recover the original simulator for direct replication
or preregister a new experiment on independent traffic and geographic splits.
