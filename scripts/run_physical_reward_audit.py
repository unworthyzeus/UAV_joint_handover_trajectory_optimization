"""Dynamically feasible reward counterexample on the real radio map, not training."""
import json
import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from uav_joint_optimization.experiment_env import RadioMap, UAVBatch


radio = RadioMap(ROOT / "dataset" / "Barcelona_dataset_January.h5")
scenario = [{"id": "physical_diagnostic_1000m", "start": [1000., 1000.],
             "goal": [2000., 1000.], "load_phase": 0}]
results = []
for reward in ["legacy", "fixed"]:
    for controller in ["direct_stop", "slow_progress"]:
        env = UAVBatch(radio, 1, scenario, reward, reward == "fixed")
        values, path = [], [env.pos[0].tolist()]
        for _ in range(env.cfg.horizon):
            motion, network = env.pd_action()
            if controller == "slow_progress":
                _, radial, lateral, _ = env.geometry()
                acceleration = (2. * radial - env.vel) / env.cfg.dt_s
                motion = np.column_stack([(acceleration * radial).sum(axis=1),
                                          (acceleration * lateral).sum(axis=1)]) / env.cfg.max_acceleration
            _, _, step_reward, done, episodes = env.step(motion, network)
            values.append(float(step_reward[0])); path.append(env.pos[0].tolist())
            if done[0]:
                break
        row = {"reward": reward, "controller": controller, "trained_policy": False,
               "discounted_return": float(np.dot(env.cfg.gamma ** np.arange(len(values)), values)),
               "rewards": values, "path": path, "episode": episodes[0]}
        results.append(row)
        print(json.dumps({k:v for k,v in row.items() if k not in {"path", "rewards"}}), flush=True)
assert results[0]["episode"]["success"] and not results[1]["episode"]["success"]
assert results[1]["episode"]["final_distance_m"] > 10
assert results[1]["discounted_return"] > results[0]["discounted_return"]
assert results[2]["discounted_return"] > results[3]["discounted_return"]
out = ROOT / "results" / "tables" / "physical_reward_audit.json"
out.write_text(json.dumps({"type": "engineering diagnostic, not trained performance",
                          "scenario": scenario[0], "results": results}, indent=2)+"\n", encoding="utf-8")
