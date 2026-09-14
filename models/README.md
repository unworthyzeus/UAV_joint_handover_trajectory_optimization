# Released Final Checkpoints

The complete release has **20 final checkpoints, totaling 2,741,480 bytes**:
the 15 initial models below plus five V2.1 policies in the
[service reward manifest](service_reward_manifest.json). V2.2 adds no new
weights: its lookahead supervisor reuses the five full V2 policies.
See the [V2.2 usage guide](../docs/54_thesis_metrics_reproduction.md) and
[fresh results](../docs/53_v22_guard_results.md).

The [manifest](checkpoint_manifest.json) lists all 15 checkpoints used in the
initial V1.5 versus V2 reward comparison: original, full and arrival, each with
seeds 2101-2105. Files remain beside their training records under `results/`.
Every seed is included; no best model is selected by test performance.

Those initial 15 total 2,054,910 bytes. Each checkpoint has policy tensors, dimensions,
configuration metadata and final training step count. It does not contain the
radio map. The manifest records SHA256 for exact integrity verification.

Use [the setup guide](../docs/35_dataset_and_model_setup.md) for the private
dataset path, dependencies and evaluator commands. All policies require the
V2 navigation prior, residual decoding, action mask and filter implemented by
the provided evaluator; the neural network alone is not the full controller.

The original reward and full reward both reach 95.7% standard joint success
on the new tests. Full's lower handover count and flight time accompany higher
delay. Read [the complete results](../docs/37_v15_reward_results.md) before
interpreting a model as better overall. All claims concern one map and sampled
simulation, not deployment or physical connectivity guarantees.
