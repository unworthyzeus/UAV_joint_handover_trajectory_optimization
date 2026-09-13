# Confirmed Identity of the Original Thesis Dataset

Date: 13 September 2026.

## Confirmation and Work

The researcher who supplied the dataset explicitly confirmed in the project
conversation: "its the same dataset", and requested that this be clear in
the paper and README. We therefore identify the supplied Barcelona HDF5 as
the same dataset used in the original master's thesis.

Updated the current paper's abstract, introduction, shared physical model
and limitations, together with the root README, paper guide and dataset
setup guide. Removed the current claim that exact thesis dataset identity
is unverified. The confirmation is recorded here as supplied provenance;
it is not presented as a new comparison with a separately obtained file.

## Dataset Record

| Property | Value |
| --- | --- |
| File | `dataset/Barcelona_dataset_January.h5` |
| Relationship to the thesis | Same Barcelona ray tracing dataset |
| Size | 2,327,593,160 bytes |
| SHA256 | `d4630dd3a6c45419e12d0b60dd08473c4ffa4062ca4fab1decabecf2b992ea0d` |
| Dataset station count | 133 sites |
| Selected operator | Operator 1, 87 sites |
| Carrier and altitude | 2.1 GHz; 100 m |
| Dataset handling | Raw HDF5 unchanged and excluded from Git |

The thesis describes channel generation in printed pp. 6-7, Sec. 3.1 and
Table 2, and selects Operator 1 in printed p. 14, Sec. 6.1. Those passages
describe the source dataset; the present confirmation establishes the
identity of the file supplied for this study.

## Result and Scientific Scope

Dataset identity is no longer an unresolved difference from the thesis.
The reward comparison, numeric results and primary conclusion do not change:
V1.5 and full V2 use the same file they used before this clarification.

The original simulator and trained policies remain unavailable. Shared
dataset identity does not imply identical dynamics, observations, traffic,
service arithmetic, energy model, control aids, PPO settings or evaluation
routes. The provisional interpretation of the -128 sentinel remains a
separate implementation assumption; the confirmation does not supply its
generator convention. All other documented model limitations remain.

## Verification and Preserved History

Rebuilt and visually inspected all seven pages of the current IEEE PDF.
The audit confirms 35 thesis citations with page locators, 20 embedded fonts,
no unresolved references or overfull boxes, and no text outside page bounds.
Current paper sources no longer contain the previous dataset identity caveat.
All 20 frozen source/protocol hashes and 15 checkpoint hashes match. Figures,
raw records and statistics remain unchanged. Recomputed the HDF5 checksum
and confirmed the unchanged 2,327,593,160 byte study file recorded above.
No retraining or new evaluation was performed for this provenance correction.

Frozen protocols, archived papers and contemporaneous historical notes keep
their original text and hashes. Their earlier uncertainty about dataset
identity is superseded by this confirmation; it is not the current position.
The next research decision still concerns the unavailable original simulator
and independent control ablations, rather than dataset identity.
