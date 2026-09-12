# Received Dataset and Reward Diagnosis

Date: 12 September 2026.

## What Was Done

Opened `dataset/Barcelona_dataset_January.h5` in read only mode, inspected every
dataset and attribute, and scanned all 2,327,500,000 radio values. Computed a
SHA256 checksum, a complete value histogram, and per operator best RSS and
candidate counts across all 17,500,000 horizontal grid locations. The source
file was not moved or modified. No training or simulator replay was performed.

The numerical results are saved in
`results/tables/dataset_intake_audit_20260912.json`. The scan used Python 3.12,
h5py 3.16.0, and NumPy. For each station slice, it accumulated the histogram
and, for each operator owning that station, updated a pointwise maximum and
the number of RSS entries strictly greater than -96 dBm.

## Why

The user supplied the previously missing radio dataset and asked whether the
reward diagnosis still holds. Examining the actual radio surface can test
whether inevitable geographic RSS outages offer an alternative explanation,
although it cannot establish the cause of a trained policy's behavior.

## Results

The file matches the thesis's headline environment specifications [TFM,
printed pp. 6–7, Sec. 3.1, Table 2; add two for PDF pages]:

| Item | Observed value |
| --- | --- |
| File size | 2,327,593,160 bytes, about 2.33 GB |
| SHA256 | `d4630dd3a6c45419e12d0b60dd08473c4ffa4062ca4fab1decabecf2b992ea0d` |
| Radio array | `measurements/rss_dBm`, shape `(133, 5000, 3500)` |
| Storage | Signed int8, contiguous, uncompressed |
| Frequency attribute | 2.1 GHz |
| Height | 100 m |
| Grid resolution attribute | 1 m |
| Operators and station counts | Telefonica 87, Orange 59, Vodafone 41 |
| Other metadata | Station IDs, coordinates, operator membership, and 46 dBm transmit powers |
| Overall stored RSS range | -128 to -25 dBm |
| Entries equal to -128 | 646,403,855, or 27.77245% of all link entries |
| Other stored values | -110 to -25 dBm |

This updates the earlier rough storage estimate: int8 values require about
2.33 GB, whereas the previous missing asset search assumed float32 or float64.

For the 87 station operator used in the thesis [TFM, printed p. 14, Sec. 6.1], every grid point has at least
38 stations strictly above -96 dBm. The median is 63 and the maximum is 77.
The strongest station's RSS ranges from -51 to -25 dBm over the full grid.
Both other operators also have full coverage under this particular threshold.
These are exact full grid summaries, not estimates from a spatial sample.

Consequently, the stored map does not contain an unavoidable geographic
coverage hole under the thesis's RSS threshold [TFM, printed p. 15, Table 3] when an arbitrary suitable
station can be selected. This is not proof of a feasible complete flight under
A3 handover rules, resource occupancy, SINR requirements, flight dynamics, or
deadlines. The number of above threshold stations is not a count of immediately
admissible handover actions.

## Assessment of the Reward Hypothesis

Reward and observation design remain the leading explanation to test. The
written reward awards a fixed +12 on every approach step, without a matching
retreat cost, while the stated formulation has no arrival reward or success
termination. Reward can therefore accumulate through repeated approach or
unnecessarily slow progress. The listed observations omit velocity despite
acceleration control and the intended requirement to stop at the destination.
The source definitions are [TFM, printed p. 12, Sec. 5.2, Eqs. (13)–(14)]
for observations, reward, and continued arrival; [printed p. 15, Table 3] for
the bonus; and [printed p. 9, Sec. 3.2] for motion and stopping intention.

The radio data itself does not contain the original reward, movement,
termination, scheduling, or policy implementation. No original environment
code, checkpoint, or trajectory log was found in this project during intake.
Therefore, neither reward as the sole cause nor a successful correction has
been established. The complete RSS coverage weakens one alternative explanation,
but does not supply a causal ablation.

The older reward diagnostic remains an abstract incentive illustration. Its
handcrafted traces are not dynamically validated, and its nominal never arrive
trace is only 4 to 5 metres from the goal, within the thesis's listed 10 metre
position tolerance. Its supplied success labels must not be treated as outcomes
of the original arrival test. A subsequent physical replay must use the real
position and speed criteria and stay outside the success region when testing
noncompletion.

## Risks and Remaining Work

1. Confirm the supplied file's provenance and whether it is the exact version
   used for the final thesis experiments. Matching dimensions and metadata do
   not prove version identity.
2. Confirm the meaning of -128. Its concentration at the int8 minimum and the
   gap to -110 suggest a sentinel or clipped floor, but this is an inference.
   Confirm missing ray handling and quantization with the generator or author.
3. Use the stored coordinate vectors when indexing. They span 0 to 5000 with
   5000 samples and 0 to 3500 with 3500 samples, giving actual spacings of
   approximately 1.00020004 and 1.00028580 m despite the 1 m attribute. The
   array shape supports `(station, x, y)`; compare with the original loader.
4. Promote stored integers before radio arithmetic, convert dBm to linear
   power before aggregation, and verify the link direction and interference
   model. RSS coverage alone says nothing conclusive about SINR or throughput.
5. Recover the original environment, route definitions, seeds, checkpoints,
   logs, and training configuration. Channel inspection is now possible;
   exact baseline reproduction is still incomplete.

## Next Experiment

After recovering or explicitly validating a reimplementation of the environment,
hold the channel map, routes, seeds, PPO settings, training budget, and common
evaluation success criterion fixed. Compare the original formulation, a change
to reward and success termination, a change to observations, and both changes.
Use a deterministic controller to establish route feasibility first. Report
mission success and failure separately, then time, energy, and radio metrics
conditional on success. This distinguishes reward effects from observability
effects and provides an actual test of the proposed explanation.
