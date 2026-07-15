# Logbook

## 2026-07-15: Workspace Bootstrap and Baseline Audit

### What Was Done

1. Created a sibling research repository modeled on the existing atmospheric monitoring workspace.
2. Preserved the proposal and Marina's thesis with source provenance.
3. Extracted and visually reviewed the proposal and relevant thesis pages.
4. Audited the state, action, reward, termination, metrics, and printed physical equations.
5. Searched the local workspace and Downloads folder for the code and channel database.
6. Checked the printed GitHub source URL and public repository list.
7. Drafted a mission first constrained formulation and controlled evaluation protocol.
8. Implemented and validated an executable reward alignment diagnostic.
9. Added unit explicit radio calculations, a mixed action interface, and
   mission first episode metrics.
10. Completed an expanded asset hunt across local workspaces, 39 ZIP archives,
    101 GZip files, public Git hosting, web archives, research repositories,
    UPC bundles, 3D GloBFP releases, UPSim, and Spanish government data sources.
11. Found the public upstream building geometry and a strong Barcelona geometry
    substitute, but no exact RSS database, source repository, station snapshot,
    routes, seeds, checkpoints, logs, or raw figure data.

### Why

The proposal begins with baseline diagnosis. Training another policy before recovering and validating the environment would compound unknowns and could repeat the same objective error.

### Result

The main failure is objective misalignment: the legacy controller could improve its measured radio rewards without completing the mission. Missing velocity, goal, candidate radio information, success termination, and success metrics reinforced that problem.

The 22 unit tests and compilation checks pass. In the handcrafted diagnostic,
the never arrive trace scores 79.65 versus 69.95 for direct arrival under the
legacy discounted return. The corrected mission first audit reverses the order,
21.05 versus -18.17.

### Remaining Work

1. Obtain the legacy code and channel database.
2. Verify printed equations against implementation.
3. Reproduce original metrics.
4. Implement deterministic graph baselines.
5. Integrate and train the mixed action controller.

### Risks

The current causal diagnosis is strongly supported by the thesis but still needs code level verification. Printed equations may not match the unavailable implementation.

### Next Step

Request the missing source and channel assets, then validate the environment
and reproduce the legacy baseline before any training claim.

The full missing asset register, search coverage, evidence, and limitations are
in `docs/16_missing_asset_search.md`.
