# Data and Sources

## Local Sources

| Path | Role |
| --- | --- |
| `references/proposals/I2R_proposal_UAV.pdf` | Canonical two page I2R proposal |
| `sources/UAV_Bermudez_Granados_2026_MSc_thesis.pdf` | Marina's complete 2026 baseline thesis |
| `references/pages/Marina_Bermudez_2026_UPCommons.url` | Official source shortcut |

## Missing Research Assets

Update, 12 September 2026: `dataset/Barcelona_dataset_January.h5` has been
received and inspected. It contains the radio map, grid coordinates, and station
metadata. See `17_received_dataset_assessment.md` for the checksum, complete
scan results, and remaining provenance questions. The historical missing asset
list below predates receipt; the original code and experiment artifacts remain
unavailable in this project.

The exhaustive public and local search is documented in
[`16_missing_asset_search.md`](16_missing_asset_search.md). The project still
needs:

1. The exact legacy source repository.
2. The final deterministic Barcelona RSS database, its schema, and generation
   scripts.
3. The processed Barcelona geometry, coordinate transform, and exact May 2024
   base station snapshot.
4. Resource and traffic generation logic and seeds.
5. Original route pairs, scenario splits, seeds, checkpoints, normalization
   statistics, logs, raw results, and plotting scripts.
6. Exact software environments and clarification of ambiguous timing and
   physical units.

## Provenance Rules

1. Store untouched received assets under `data/raw/` or `external/`.
2. Record source, date, license, version, and SHA256 hash.
3. Put transformations under scripts and derived outputs under `data/processed/`.
4. Never overwrite the original channel database.
5. Keep coordinate transforms and unit conversions explicit and tested.

## Source Availability Note

The thesis is open through UPCommons. Its printed GitHub project URL was checked
on 15 July 2026 and returned 404. The UPC deposit contains only the thesis PDF.
No public fork, mirror, release, web archive, or related research upload was
found. The original 3D GloBFP geometry source is public, and UPSim offers a
promising Barcelona geometry substitute, but neither contains Marina's exact
RSS database or experiment artifacts. These date dependent statements should
be rechecked when reproduction resumes.
