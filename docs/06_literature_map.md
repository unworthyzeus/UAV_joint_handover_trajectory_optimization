# Literature Map

Only primary papers or institutional records are used for method decisions.

| Topic | Source | Relevance |
| --- | --- | --- |
| Legacy baseline | [Bermúdez Granados, 2026](https://upcommons.upc.edu/entities/publication/a8ce08c2-c238-4145-a5ab-5d39b12c6553) | Exact inherited environment and PPO formulation |
| Deterministic joint optimization | [Im et al., 2025](https://doaj.org/article/00fb7cc137a444a9a898201e1ecc318c) | Converts a related problem to minimum weight graph search with an optimal polynomial time method |
| Joint cargo UAV planning and association | [Cherif et al., 2024](https://arxiv.org/abs/2312.02478) | Mission, energy, disconnectivity, and handover objective design |
| D3QN joint control | [Deng et al., 2023](https://www.6g-sky.net/assets/papers/A_DQN_Based_Mobility_Management_Algorithm_for_Cellular_Connected_UAVs.pdf) | Direct legacy comparison and KPI tradeoffs |
| Multiagent joint management | [Deng et al., 2026](https://www.diva-portal.org/smash/get/diva2%3A1923986/FULLTEXT01.pdf) | POMDP formulation and cooperative optimization |
| PPO | [Schulman et al., 2017](https://arxiv.org/abs/1707.06347) | Reproduction baseline, not a diagnosis by itself |
| Continuous control | [Haarnoja et al., 2018](https://proceedings.mlr.press/v80/haarnoja18b.html) | Sample efficient off policy continuous controller |
| Constrained RL | [Achiam et al., 2017](https://proceedings.mlr.press/v70/achiam17a.html) | Separates reward from safety and mission constraints |
| Mixed action control | [Xiong et al., 2018](https://arxiv.org/abs/1810.06394) | Native discrete and continuous action formulation |
| Hybrid actor critic | [Fan et al., 2019](https://www.ijcai.org/Proceedings/2019/0316.pdf) | Structured actor critic for parameterized actions |
| Hybrid MPO | [Neunert et al., 2020](https://proceedings.mlr.press/v100/neunert20a.html) | Mixed discrete and continuous control |
| Constrained mixed action RL | [Zhou et al., 2025](https://papers.neurips.cc/paper_files/paper/2025/hash/5eca2e4fe7858cbbfef4e08573cfcb25-Abstract-Conference.html) | Directly combines parameterized actions with explicit cost constraints; strong advanced candidate after simpler baselines |
| Multiobjective policy optimization | [Abdolmaleki et al., 2020](https://proceedings.mlr.press/v119/abdolmaleki20a.html) | Maintains separately scaled objectives and tradeoffs |
| Invalid action masking | [Huang and Ontañón, 2020](https://arxiv.org/abs/2006.14171) | Removes unavailable or protocol invalid network choices |
| Reward shaping | [Ng, Harada, and Russell, 1999](https://www.cs.utexas.edu/~shivaram/readings/b2hd-NgHR1999.html) | Basis for policy invariant potential shaping |
| Mission logic and URLLC planning | [Ping et al., 2026](https://arxiv.org/abs/2607.03781) | Very recent mixed integer planning alternative with explicit mission timing, handover, and communication feasibility |

## Initial Reading Conclusion

The strongest immediate baseline is deterministic graph optimization because the inherited channel map is deterministic. The strongest learning direction is a constrained mixed action controller with masks. CHPO is the closest current algorithmic match, but it should be compared with simpler Hybrid MPO and repaired PPO implementations. Learning should be justified by stochastic occupancy, uncertainty, dynamics, or the need for fast repeated decisions, not assumed necessary.

Ping et al. was submitted on 4 July 2026 and is a preprint. It is a useful formulation reference, not established comparative evidence.

## Comparison Caution

Published results use different maps, radio models, route definitions, objectives, and handover rules. Numerical gains cannot be transferred directly. Only methods run in the recovered Barcelona environment with identical scenarios are comparable.
