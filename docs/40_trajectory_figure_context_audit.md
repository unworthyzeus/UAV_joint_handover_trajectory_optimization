# Trajectory Figure and Base Station Context Audit

Date: 13 September 2026.

This note records the inspection before the figure revision. The subsequent
[long route reporting revision](41_long_route_figure_revision.md) replaces the
paper illustration and preserves the previous figure in an archive.

## Question and Work

The user asked why the current trajectory figure lacks the gray triangles in
the original TFM, printed p. 19, Sec. 7.2, Fig. 7, and whether this indicates
missing parts of the simulated task. We inspected the complete source pages,
the HDF5 station coordinates and operator membership, the map loader, the V2
observation and transition code, the current figure builder, and the three
saved traces shown in the paper. This is an inspection of existing results,
not a new training run or evaluation protocol.

## Result

The triangles indicate base station locations. The source describes the
network topology in printed p. 6, Sec. 3.1.1 and Fig. 2, and selects the
87 stations of Operator 1 in printed p. 14, Sec. 6.1. The supplied database
contains 133 sites, of which 87 belong to Operator 1. The distribution is
consistent with the source figures; this does not establish exact dataset
version identity.

The simulator loads those 87 stations' RSS maps and coordinates in
`RadioMap` in `src/uav_joint_optimization/experiment_env.py`. V2 uses candidate
station offsets in its observation and the RSS maps for station selection,
cochannel interference, service capacity and sampled connectivity. Its step
function fails an episode on serving RSS below -96 dBm or queue overflow.
The station coordinates have not been omitted from the simulator.

The current paper figure builder, `scripts/build_reward_comparison_report.py`,
plots trajectories, start and goal but has no base station scatter layer.
Its automatic axes also zoom into the short route. No selected station lies
within the approximate displayed window, x = 4550 to 4910 m and
y = 1880 to 2095 m. Station positions need not lie inside a route's bounding
box for their radio coverage to serve it.

The first declared standard route is `53012_0000`, from
(4675.112754, 2085.719315) m to (4785.471083, 1893.080739) m, a straight
distance of **222.010320 m**. The paper shows seed 2101 for learned policies.
Direct HDF5 lookup along all initial and executed samples gives:

| Controller | Serving site ID | Handovers | RSS range (dBm) | Flight time (s) | Outcome |
| --- | ---: | ---: | ---: | ---: | --- |
| Original reward (V1.5) | 29 | 0 | -47 to -36 | 17 | Success |
| Full reward (V2) | 29 | 0 | -47 to -36 | 15 | Success |
| Goal radio | 29 | 0 | -47 to -36 | 15 | Success |

All three finish with zero queued bits in this example. Site ID 29 is at
(4386, 1854) m. The serving signal remains far above the -96 dBm threshold.
This example therefore does not demonstrate difficult handover behavior or
the need for a connectivity detour. Selection by the first declared route
avoids choosing a favorable illustration after evaluation, but does not make
that illustration representative of connectivity difficulty.

## Artifacts and Reproduction

Run `python scripts/audit_trajectory_figure_context.py` with the private HDF5
at its documented location. It reads existing records and writes:

- `results/reward_comparison/analysis_v15/figure_context_audit.json`
- `results/reward_comparison/analysis_v15/trajectory_station_context.png`

The diagnostic plot adds all selected station locations, a map overview,
local context and the serving site. It preserves the three recorded routes.
The current paper PDF, figure files used by the paper, numerical results,
checkpoints and all frozen source files remain unchanged.

## Limitations and Next Decision

The triangles represent network sites, not obstacle boundaries. Building
propagation effects enter through the supplied ray tracing RSS map; this
does not constitute collision avoidance or a building geometry simulator.
The dataset represents a 100 m altitude slice (TFM, printed pp. 7-8,
Table 2 and Figs. 3-4).

Fig. 7 in the source depicts a different and visibly much longer route;
it is not a matched comparison to our 222 m illustration. A straight path
in our example cannot establish an improvement over the source trajectories.
The controlled reward result still depends on all common V2 assumptions,
including its navigation reference and prospective feasibility filter.

A reporting revision should include station context and clearly label this
example's limited difficulty. Any additional handover illustrations need a
disclosed selection rule and must remain illustrative. A causal comparison
to the source requires its implementation or a separately declared matched
reconstruction; new control ablations require a separate protocol and fresh
evaluation. Missing plot markers alone are not evidence of absent network
modeling, and their presence would not validate the whole simulator.
