# Missing Asset Search

Search completed 15 July 2026.

## Direct Answer

The primary missing dataset is Marina's processed Barcelona radio environment, not the original public building footprints alone. For exact reproduction, the project needs the deterministic received signal strength values at 100 m altitude over a 5,000 by 3,500 metre grid with 1 metre spacing, together with the 133 base station records and the strongest sector selected for each station.

The implied final array contains approximately:

`133 x 5,000 x 3,500 = 2,327,500,000` signal strength values.

That is about 9.31 GB as raw float32 or 18.62 GB as raw float64 before metadata and indexing. No plausible local file of this scale was found. The largest local MAT file was 2.18 MB and the largest local ZIP was 58.79 MB.

Exact baseline reproduction also requires code, metadata, routes, seeds, checkpoints, and logs. These form one reproducibility bundle and should be requested together.

## Asset Register

### Critical data and environment assets

| ID | Required asset | Status | Why it matters |
| --- | --- | --- | --- |
| D1 | Final Barcelona RSS database at 100 m and 2.1 GHz | Missing | This is the observation and radio evaluation surface used by every baseline and learned controller. |
| D2 | Database schema, dimensions, axis order, units, missing value convention, station identifiers, and checksum | Missing | A numerical file cannot be interpreted or validated safely without these details. |
| D3 | MATLAB ray tracing generation scripts | Missing | Needed to regenerate D1 and determine whether the thesis equations match the implementation. |
| D4 | Processed Barcelona STL or equivalent scene | Missing | Needed to reproduce Marina's exact crop rather than merely use the same global source. |
| D5 | Crop bounds, coordinate reference system, projection, local origin, axis orientation, and grid indexing | Missing | Needed to align building geometry, base stations, routes, and RSS cells. |
| D6 | Base station snapshot used on 20 May 2024 | Missing | Needed to recover the exact 133 sites, 43 shared site decisions, operators, frequencies, sectors, and identifiers. |
| D7 | Sector and propagation configuration | Partial in thesis | Headline settings are documented, but exact arrays, antenna patterns, heights, azimuths, materials, loss thresholds, and numerical options are missing. |
| D8 | Resource occupancy and traffic realizations, generation logic, and seeds | Missing | They affect interference, rate, delay, reward, and comparison fairness. |

### Critical source and configuration assets

| ID | Required asset | Status | Why it matters |
| --- | --- | --- | --- |
| C1 | `JointHandoverTrajectoryOptimization` source at the thesis commit | Missing | The printed repository is unavailable, so environment transitions, rewards, termination, and metrics cannot be verified. |
| C2 | Exact Python, MATLAB, toolbox, Stable Baselines3, Gym, PyTorch, NumPy, and dependency versions | Missing | Library defaults and API behavior can change training results. |
| C3 | Full PPO policy architecture, initialization, optimizer settings, observation preprocessing, and normalization state | Missing | Table 4 does not fully determine the trained model. |
| C4 | Greedy baseline, resource allocation, A3 handover, environment, evaluation, and plotting implementations | Missing | These are required to reproduce every reported comparison. |
| C5 | Handover timing and counter semantics | Missing or ambiguous | The thesis does not fully specify time to trigger, reset, candidate switching, or event ordering. |
| C6 | Clarification of timestep and physical units | Ambiguous | Table 3 gives 0.1 s while prose also refers to 1 ms. Energy, interference, and rate expressions contain unit ambiguities that must be checked against code. |

### Critical experiment artifacts

| ID | Required asset | Status | Why it matters |
| --- | --- | --- | --- |
| E1 | Exact start and goal coordinates for every route | Missing | Figures show approximate positions only; pixels are not valid scenario definitions. |
| E2 | Training, validation, and test route splits | Missing | Needed to prevent test leakage and make generalization claims. |
| E3 | Python, NumPy, PyTorch, environment, occupancy, traffic, and route seeds | Missing | Needed for repeatability and paired comparisons. |
| E4 | PPO checkpoints for the equal, delay, interference, and handover objectives | Missing | Needed to evaluate the reported policies without uncertain retraining. |
| E5 | Observation and reward normalization statistics | Missing | A checkpoint may be unusable or behave differently without them. |
| E6 | Training logs, monitor files, TensorBoard events, and tuning records | Missing | Needed to audit stability, convergence, sample efficiency, and model selection. |
| E7 | Raw per episode trajectories, handover events, radio metrics, energy, delay, and terminal states behind Figures 5 through 10 | Missing | Plotted images do not support exact numerical reproduction or statistical analysis. |
| E8 | Figure generation and metric aggregation scripts | Missing | Needed to reproduce reported plots and detect averaging or unit errors. |
| E9 | Hardware, wall time, and runtime records | Missing | Useful for an honest efficiency comparison, though not required to run the environment. |
| E10 | Provenance, redistribution permission, and checksums for received private assets | Missing | Needed for lawful reuse and a defensible research record. |

## Public Inputs Found

These findings reduce the amount that must be requested, but none replaces the exact radio database.

| Public input | Finding | Use and limitation |
| --- | --- | --- |
| [3D GloBFP Europe v1](https://doi.org/10.5281/zenodo.11391077) | Open building footprints with height attributes under CC BY 4.0. Spain is in `Serbia_Slovakia_Slovenia_Spain_Sweden_Switzerland.rar`, about 1.4 GB, MD5 `db85367853d9bb0d954e59e0166090c8`. | Authoritative upstream geometry source. Marina's processed Barcelona crop, transform, and STL remain missing. |
| [Current Figshare 3D GloBFP release](https://doi.org/10.6084/m9.figshare.28882700.v3) | The Barcelona region is covered by `826_1.25_41.25_2.5_42.5_AN_FR_SP.zip`, 121,324,831 bytes, MD5 `03ebe7df67376b1c7d216a111b2e920c`. | Easier public geometry input, but it may differ from the version and preprocessing used in the thesis. |
| [UPSim](https://github.com/Eugenio86/UPSim) | The co supervisor's repository contains `data/Barcelona.mat`. Read only inspection found 2,992 buildings and a local footprint span of about 4,992 by 3,294 m, close to the thesis scene. | Strong candidate substitute or provenance lead. It is not confirmed as Marina's exact scene, models FR3 at 16.95 GHz rather than 2.1 GHz, and the repository currently has no license file. Permission is needed before redistribution or derivative reuse. |
| [Infoantenas](https://digital.gob.es/telecomunicaciones-infraestructuras-digitales/areas-interes/inspeccion-telecomunicaciones/niveles-exposicion/servicio-estaciones-radioelectricas) | Official individualized station query service. | Does not provide Marina's historical bulk export. The service was unavailable during this audit. |
| [Official datos.gob.es response](https://datos.gob.es/ca/solicitud-de-datos/base-de-datos-api-de-la-ubicacion-antenas-gsm) | The government states that the full SIGETEL and RENAFE station database is restricted and that only individualized Infoantenas information is public. | Confirms that the exact historical 133 site table is unlikely to be regenerated from a supported public bulk API. |
| [Public spectrum concessions register](https://avance.digital.gob.es/espectro/paginas/registro-publico-concesiones.aspx) | Public operator spectrum allocation information. | Can support a new radio model, but does not identify Marina's exact stations and sectors. |

The public geometry sources make a new Barcelona experiment possible. They do not make Marina's exact experiment reproducible because the radio map, station snapshot, preprocessing, routes, and stochastic realizations remain unknown.

## Where the Search Was Performed

### Local computer

| Location or method | Coverage | Result |
| --- | --- | --- |
| `C:\Research` | Projects, data folders, Git repositories, archives, model files, geometry files, and text content | No legacy source, channel database, checkpoint, route, or log found. |
| `C:\Users\guill\Downloads` | All likely research files and archives | Thesis, 3D GloBFP papers, and saved record pages found; no required derived assets. |
| `C:\Users\guill\Documents` | Research documents, Codex outputs, archives, and repositories | Duplicate proposal extraction only. |
| `C:\Users\guill\OneDrive`, including Documents and `Escritorio` | Synchronized files, archives, repositories, and likely data extensions | No required asset found. Unsynchronized cloud only files were not accessible. |
| `C:\Users\guill\Desktop` | Path check | The path does not exist; the OneDrive desktop was searched instead. |
| `.cache`, `.codex`, `.agents`, `.vscode`, `.cursor`, `AppData\Local\Temp`, `AppData\Roaming\Code\User`, and the pip cache | Tool caches, temporary files, editor state, and likely content | Only duplicate thesis files and rendered pages. |
| Local Git repositories | Repository names, contents, and remote URLs | No clone, fork, bundle, or relevant remote. |
| Archive inspection | 39 ZIP files, 643 text members within ZIPs, and 101 GZip files searched without bulk extraction | Zero relevant name or content matches. |
| Data extension and size audit | MAT, NPY, NPZ, H5, pickle, CSV, model, geometry, and archive formats | No file remotely large enough to be the expected RSS cube. |

The local search used filenames, extensions, Git remotes, and exact content terms including the repository URL, repository name, thesis title, author, Barcelona, ray tracing, RSS, handover, routes, seeds, checkpoints, and Stable Baselines3.

### Thesis and institutional repository

| Source | What was checked | Result |
| --- | --- | --- |
| [Official UPCommons thesis record](https://upcommons.upc.edu/entities/publication/a8ce08c2-c238-4145-a5ab-5d39b12c6553) | Record metadata, relations, downloadable files, and all repository bundles | The ORIGINAL bundle contains only `200925.pdf`, 1,836,580 bytes, MD5 `4e3e7ba4ad868bd5f112b27c204987cb`. No code or data supplement. |
| Thesis tables, equations, figures, bibliography, and appendices | Dataset specification, route coordinates, links, version details, seeds, and supplemental references | Headline parameters recovered; exact routes, schema, code, and experiment artifacts are absent. |
| I2R proposal | Tasks, expected inputs, and intended optimization target | No embedded dataset or private storage link. |

### Public code hosting

| Source | Queries and endpoints | Result |
| --- | --- | --- |
| [Printed GitHub repository](https://github.com/Nara-On/JointHandoverTrajectoryOptimization) | Web, REST, raw `README`, codeload ZIP, `git ls-remote`, branches, tags, releases, forks, and contents | All repository endpoints return 404 or repository not found. A 404 cannot distinguish private, deleted, renamed, or never published. |
| [Nara-On GitHub profile](https://github.com/Nara-On) | Public repositories, gists, recent public events, and contribution data | Five unrelated public repositories; no relevant gist or event. |
| Authenticated GitHub search | Exact name and URL; thesis title; code, repository, commit, and issue search; user scoped `handover`, `raytracing`, `3D-GloBFP`, `Barcelona`, `stable_baselines3`; distinctive PPO and action settings | Zero relevant result. |
| GitLab project API and public web search | Exact repository name, thesis title, author, and related terms | Zero relevant result. |
| Bitbucket and package or dataset host web searches | Exact repository name, title, author, and URL | No relevant public result. |

### Web archives and research repositories

| Source | Coverage | Result |
| --- | --- | --- |
| [Wayback Machine](https://web.archive.org/web/2id_/https://github.com/Nara-On/JointHandoverTrajectoryOptimization) | Exact repository, wildcard paths, raw URLs, and codeload URLs | Replay reports that the URL was not archived. |
| [Software Heritage](https://archive.softwareheritage.org/api/1/origin/search/github.com%2FNara-On%2FJointHandoverTrajectoryOptimization/?with_visit=true) | Exact GitHub origin | Empty result. |
| [Arquivo.pt](https://arquivo.pt/textsearch?maxItems=50&q=JointHandoverTrajectoryOptimization) | Exact repository name | Zero results. |
| Common Crawl | 28 indexes from `CC-MAIN-2024-10` through `CC-MAIN-2026-25`, including repository, raw, wildcard, and codeload forms | Zero captures. |
| Zenodo | Repository name, exact thesis title, author, and related dataset records | No Marina code or experiment upload. The upstream 3D GloBFP dataset was found. |
| Figshare | Repository name, thesis title, author, and 3D GloBFP records | No Marina experiment upload. A current public Barcelona geometry tile was found. |
| Hugging Face | Model and dataset APIs for the exact repository and related terms | Zero relevant result. |
| OSF and Kaggle | Exact repository name, thesis title, author, and related terms | Zero relevant public result. |
| General web search | Exact URL, repository name, title, author, distinctive parameter combinations, dataset dimensions, station counts, and thesis phrases | Results led back to the thesis or unrelated material; no exact mirror or data copy. |

### Original upstream and government sources

| Source | What was checked | Result |
| --- | --- | --- |
| Zenodo and Figshare 3D GloBFP records | Europe release, current tiles, formats, sizes, checksums, and licenses | Public geometry found, exact Marina transformation absent. |
| UPSim repository | Barcelona geometry, ray tracing reference data, routes, model parameters, artifacts, and license | Useful substitute geometry and related FR3 model found; no Marina radio map, routes, or PPO artifacts. |
| Infoantenas, datos.gob.es, transparency records, and spectrum concessions | Bulk access, API availability, historical station data, and scope | No supported public route to Marina's exact May 2024 station snapshot. |

## What Was Not Searchable

The following locations require access or credentials that were not available:

1. Marina's private, renamed, or deleted GitHub repositories.
2. Private supervisor or university storage.
3. Google Drive, SharePoint, email attachments, and other unsynchronized cloud files. A Google Drive connector was suggested but was not installed for this search.
4. Deleted local files and unmounted drives.
5. Browser binary caches and history databases were not exhaustively decoded after broad AppData scans timed out.

Absence from the searched indexes is strong evidence that no discoverable public copy exists today. It is not proof that a private or unindexed copy does not exist.

## Recommended Acquisition Order

1. Ask Marina and both supervisors for the repository export and exact commit.
2. Ask for the final RSS database with schema and checksum. This is the largest blocker.
3. Ask for the base station export and Barcelona geometry with complete coordinate metadata.
4. Ask for routes, seeds, checkpoints, normalization statistics, logs, and raw figure data.
5. Ask for the MATLAB and Python environments and written permission for any private or unlicensed assets.
6. If the exact bundle cannot be recovered, build a clearly labeled new environment from the public 3D GloBFP geometry, a documented new station source, and a regenerated channel model. Do not describe that substitute as an exact reproduction of Marina's baseline.
