# V1.5 Original Reward on V2: Results

Date: 13 September 2026. All results below use the new route seeds 53012 and 53013.

## Outcome

The primary comparison does not establish improved completion from reward replacement.

Standard full minus original completion: **+0.0 percentage points**, 95% interval **[-2.8, 2.7]**. Longer completion: **+1.5 points [-2.9, 6.1]**. Neither interval establishes improved completion; this is not evidence of equivalence.

The full reward produces fewer handovers and faster completion on paired successful routes, but higher delay, slightly higher proxy energy and lower SINR. The original reward is not an ineffective navigation controller when it shares the V2 prior and filter. No overall learned superiority claim is supported.

## Joint Success

| Controller | Standard | Longer | Episodes per split |
| --- | ---: | ---: | ---: |
| PPO original (V1.5) | 95.7 | 85.8 | 1,000 |
| PPO full (V2) | 95.7 | 87.3 | 1,000 |
| PPO arrival (V2) | 94.9 | 85.1 | 1,000 |
| Goal RSS | 94.0 | 84.5 | 200 |
| Goal radio | 96.5 | 88.5 | 200 |
| Joint one step | 96.0 | 90.5 | 200 |
| Joint three steps | 92.0 | 90.5 | 200 |

## First Failure Counts

| Controller | Standard RSS / buffer / timeout | Longer RSS / buffer / timeout |
| --- | ---: | ---: |
| PPO original (V1.5) | 40 / 3 / 0 | 136 / 6 / 0 |
| PPO full (V2) | 34 / 9 / 0 | 112 / 15 / 0 |
| PPO arrival (V2) | 51 / 0 / 0 | 147 / 0 / 2 |
| Goal RSS | 12 / 0 / 0 | 31 / 0 / 0 |
| Goal radio | 7 / 0 / 0 | 21 / 2 / 0 |
| Joint one step | 8 / 0 / 0 | 18 / 0 / 1 |
| Joint three steps | 4 / 0 / 12 | 11 / 0 / 8 |

No energy or boundary failures occurred. All reported successes satisfy sampled RSS, queue, time, position and speed criteria.

## Matched Successful Flights

The comparison uses 925 standard and 781 longer successful seed/route pairs. Failure rates remain unconditional above.

| Split | Metric | Original | Full | Full minus original | 95% interval |
| --- | --- | ---: | ---: | ---: | --- |
| Standard | Flight time (s) | 31.252 | 28.112 | -3.139 | [-3.509, -2.808] |
| Standard | Accumulated radio cost | 7.094 | 5.309 | -1.785 | [-2.194, -1.389] |
| Standard | Delay proxy (s) | 1.942 | 5.827 | +3.886 | [2.731, 5.066] |
| Standard | Handovers | 6.843 | 0.443 | -6.400 | [-8.501, -4.366] |
| Standard | Interference (microW) | 0.753 | 0.748 | -0.004 | [-0.017, 0.009] |
| Standard | Energy proxy (kJ) | 7.651 | 7.788 | +0.137 | [0.115, 0.157] |
| Standard | SINR (dB) | -8.322 | -9.305 | -0.983 | [-1.483, -0.488] |
| Standard | Path length (m) | 547.596 | 551.204 | +3.608 | [2.947, 4.273] |
| Standard | Network overrides | 0.107 | 0.478 | +0.371 | [0.243, 0.504] |
| Standard | Motion overrides | 0.008 | 0.016 | +0.009 | [-0.004, 0.028] |
| Longer | Flight time (s) | 65.394 | 60.145 | -5.250 | [-5.815, -4.804] |
| Longer | Accumulated radio cost | 16.800 | 13.803 | -2.997 | [-3.765, -2.257] |
| Longer | Delay proxy (s) | 2.857 | 6.818 | +3.961 | [2.657, 5.145] |
| Longer | Handovers | 15.826 | 1.528 | -14.298 | [-19.543, -9.101] |
| Longer | Interference (microW) | 0.794 | 0.791 | -0.003 | [-0.015, 0.009] |
| Longer | Energy proxy (kJ) | 18.523 | 18.957 | +0.434 | [0.394, 0.476] |
| Longer | SINR (dB) | -8.773 | -9.957 | -1.184 | [-1.652, -0.712] |
| Longer | Path length (m) | 1345.958 | 1349.568 | +3.610 | [2.896, 4.321] |
| Longer | Network overrides | 0.467 | 1.757 | +1.289 | [0.882, 1.637] |
| Longer | Motion overrides | 0.024 | 0.044 | +0.019 | [-0.010, 0.062] |

## All Seeds

| Arm | Seed | Standard (%) | Longer (%) |
| --- | ---: | ---: | ---: |
| PPO original (V1.5) | 2101 | 96.5 | 85.5 |
| PPO original (V1.5) | 2102 | 98.0 | 89.0 |
| PPO original (V1.5) | 2103 | 95.0 | 85.0 |
| PPO original (V1.5) | 2104 | 94.0 | 85.5 |
| PPO original (V1.5) | 2105 | 95.0 | 84.0 |
| PPO full (V2) | 2101 | 97.0 | 86.5 |
| PPO full (V2) | 2102 | 95.0 | 87.5 |
| PPO full (V2) | 2103 | 95.5 | 85.5 |
| PPO full (V2) | 2104 | 95.5 | 87.5 |
| PPO full (V2) | 2105 | 95.5 | 89.5 |
| PPO arrival (V2) | 2101 | 95.5 | 83.5 |
| PPO arrival (V2) | 2102 | 96.5 | 84.5 |
| PPO arrival (V2) | 2103 | 94.0 | 86.5 |
| PPO arrival (V2) | 2104 | 93.5 | 82.5 |
| PPO arrival (V2) | 2105 | 95.0 | 88.5 |

## What Changed and Why

The user requested the original written reward with every other V2 component unchanged. Five new policies were trained with seeds 2101-2105 and 524,288 interactions each. All ten original final V2 weights were reused without selection and fixed by hash before the new run. The new 400 test routes are disjoint from prior saved routes; training and validation routes remain exactly V2.

The wrapper changes only reward and accumulated raw return. The original formula retains the source equal weights, approach bonus, penalties and energy override [TFM, printed p. 12, Eqs. (13)-(14), Sec. 5.2; p. 15, Table 3]. Its 100 m/s reward threshold cannot activate under the shared 25 m/s cap; its RSS equality penalty is retained. Arrival termination, constraints and controller remain V2.

The source freeze and analysis were declared in [note 36](36_v15_reward_comparison_protocol.md). The primary standard contrast uses 5,000 crossed seed/route bootstrap draws, seed 63000. Longer and other contrasts are secondary. Intervals are not adjusted for multiple secondary comparisons. Five training seeds limit uncertainty inference.

## Verification, Limits and Next Decision

The implementation passed 73 tests, including transition identity and exact small PPO training equivalence. The final delivery audit records the exact replay and published checkpoint manifest. No implementation or hyperparameter was retuned after these results. Software checks do not validate the physical assumptions.

The navigation prior and prospective filter are shared aids; the contrast does not isolate their effects or explain the original simulator. One map, static load, sampled connectivity, proxy service and energy remain limitations. Outstanding queue at arrival is allowed. A lower radio aggregate is not uniformly better service.

The result closes the requested comparison, including its null primary finding. The next research decision is independent evaluation and separately frozen component ablations, not rewriting the reward until the present test looks favorable. See the [setup guide](35_dataset_and_model_setup.md) for released checkpoints and commands.
