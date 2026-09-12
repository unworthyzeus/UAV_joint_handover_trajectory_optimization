# Connectivity Repair Development Log

Date: 12 September 2026. All observations below use development routes only.
The final test routes were not evaluated before the freeze recorded in
`configs/frozen_connectivity_v2.json`.

## What Changed and Why

The user required the thesis's communication requirements rather than new
application deadlines. We implemented strict sampled RSS and buffer constraints,
restored the delay/interference/handover learning costs, and restored available
RBG choices. See note 28 for source pages and final definitions.

The first development version exposed that merely adding the cost does not
solve navigation or guarantee future feasible association. We added a shared
model based safety filter that changes an unsafe proposal when an alternative
is found. It does not waive constraints or guarantee a route exists. We then
added a destination braking prior with learned residual motion and trained
across the full evaluated length range. These are explicitly additional design
changes, common to both final learned reward arms.

## Retained Development Runs

| Design | Pilot seed and budget per arm | Arrival arm standard / longer joint success | Full arm standard / longer joint success |
| --- | --- | ---: | ---: |
| Direct motion, no filter, short training lengths | 51; 524,288 | 89.1% / 59.4% | 92.2% / 34.4% |
| Direct motion, safety filter, short training lengths | 52; 1,048,576 | 92.2% / 78.1% | 98.4% / 75.0% |
| Residual motion, safety filter, 200–1800 m training lengths | 53; 524,288 | 96.9% / 84.4% | 98.4% / 87.5% |

Standard validation contains 64 routes and longer validation 32. These are
single seed pilot estimates, not final results or independent confirmations.
The resource action mask initially removed the current station/group pair as
a duplicate of stay. The second design keeps that pair legal, allowing stable
selection of a group without an artificial alternating mask. No numerical
communication threshold was relaxed during these revisions.

The final pilot's full objective reduced standard handovers to a mean 0.40
per successful mission, but its delay proxy rose to 4.64 s, versus 7.92
handovers and 1.24 s for the arrival arm. These means use different successful
subsets. This is a warning about the original reciprocal weights and learned
tradeoff, not evidence that every communication quantity improves. Final
comparisons must use matched successful pairs and include completion rates.

The longer route problem in the first two pilots included extrapolation beyond
the training range. The final training routes span the entire tested range;
longer final routes therefore test new coordinate pairs, not unseen lengths.
This change is explicit and must not be described as improved extrapolation.

## Deterministic Reference Development

The nominal straight RSS controller under initial strict checks completed
95.3% / 71.9% of standard/longer validation routes. Resource and prospective
association control completed 96.9% / 90.6%. The first local joint search
completed 95.3% / 81.3% and sometimes preferred stationary low cost states.

A first step progress preference removed the observed stationary trap from the
one step controller on validation. With the shared safety filter, its joint
success was 98.4% / 87.5%. It still had RSS failures. The filtered prospective
radio reference completed 96.9% / 93.8%.

A three step local lookahead reference initially postponed motion at every
replan despite forecasting future progress, completing 70.3% / 53.1%. Applying
the progress preference to the first predicted step, rather than only the end
of the prediction horizon, improved it to 93.8% / 87.5%. Three standard routes
still timed out. These failures are retained. The final comparison includes
all four references, not only whichever wins a test metric.

The lookahead reference's successful validation flights had lower delay and
normalized communication cost, but lower completion than some simpler
controllers. This cannot be presented as unconditional superiority.

## Freeze Decision and Verification

Selected the final residual design and 524,288 interactions per learned policy
because the pilot already performs basic mission control at that budget; this
does not establish convergence. Final seeds are 2101–2105. No development
checkpoint is carried into final training, and no final checkpoint is selected
using its test performance.

The full suite has 51 passing tests, including 17 new checks. They cover strict
RSS inequality semantics, initial coverage, immediate violation failure,
overflow precedence over arrival, permitted outstanding queues at arrival,
all three radio costs, resource masks and power arithmetic, action projection,
filter behavior, lookahead state isolation, and repeatable PPO training that
changes parameters. Original v1 source hashes still match.

Six pilot policies are retained under `results/connectivity_experiment/`.
Every development result directory retains its source hashes and snapshots.
The first development snapshots were captured before further source revision;
later runs capture them automatically at launch. Final artifacts use a separate
freeze manifest and result directory. No original dataset or v1 experiment
artifact was overwritten.

## Risks and Next Decision

The final study preserves a one second surrogate step, static load pattern,
uncalibrated energy and downlink service models, instantaneous handovers and
resource changes, and prospective map access in the filter. It is a repair
of the sampled objective and controller, not proof of real continuous
connectivity. Strict constraint violations remain possible when the finite
control candidates or policy cannot find a feasible continuation.

Run the frozen five seed comparison, retain all failures and individual
communication metrics, and distinguish improvement in the weighted objective
from improvement in every component. The user did not request new latency,
packet delivery, or throughput constraints, so none should be introduced to
make the final result appear better or worse.
