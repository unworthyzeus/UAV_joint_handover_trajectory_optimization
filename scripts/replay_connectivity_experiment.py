"""Verify frozen evaluations exactly and retain detailed first route traces."""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from uav_joint_optimization.experiment_env import RadioMap
from uav_joint_optimization.connectivity_env import ConnectivityConfig, ConnectivityBatch
from uav_joint_optimization.connectivity_ppo import HybridPolicy


def replay(radio, scenarios, config, policy=None, controller=None):
    env = ConnectivityBatch(radio, len(scenarios), scenarios, "full", config)
    obs, mask = env.observe()
    paths = [[] for _ in range(4)]
    rows = []

    def capture(active):
        rss, interference, sinr, rate = env.radio_state()
        for i in range(4):
            if active[i]:
                paths[i].append([float(env.t[i] * config.dt_s), *env.pos[i].tolist(),
                    float(np.linalg.norm(env.vel[i])), int(env.serving[i]), int(env.rbg[i]),
                    float(rss[i, env.serving[i]]), float(env.buffer[i]), float(rate[i]),
                    float(interference[i]), float(sinr[i])])
    capture(~env.done)
    for _ in range(config.horizon):
        active = ~env.done.copy()
        if controller:
            motion, choice = env.controller(controller)
        else:
            with torch.no_grad():
                latent, network, _, _ = policy.action(torch.from_numpy(obs), torch.from_numpy(mask), True)
            motion, choice = env.decode_residual(torch.tanh(latent).numpy()), network.numpy()
        obs, mask, _, _, completed = env.step(motion, choice)
        rows.extend(completed)
        capture(active)
        if env.done.all():
            break
    rows.sort(key=lambda r: r["lane"])
    return rows, paths


def main():
    frozen = json.loads((ROOT / "configs/frozen_connectivity_v2.json").read_text())
    for n, h in frozen["source_hashes"].items():
        assert hashlib.sha256((ROOT / n).read_bytes()).hexdigest() == h, n
    cfg = ConnectivityConfig(**frozen["environment"])
    scenarios = json.loads((ROOT / "configs/connectivity_scenarios_v2.json").read_text())
    torch.set_num_threads(2)
    radio = RadioMap(ROOT / "dataset/Barcelona_dataset_January.h5")
    base = ROOT / "results/connectivity_experiment/confirmatory_v2"
    output = ROOT / "results/connectivity_experiment/replay_v2"
    output.mkdir(parents=True, exist_ok=True)
    record, total = {}, 0
    for arm in frozen["arms"] + frozen["controllers"]:
        for seed in (frozen["seeds"] if arm in frozen["arms"] else [None]):
            policy, checkpoint_hash = None, None
            if seed is not None:
                path = base / f"{arm}_seed_{seed}/checkpoint.pt"
                checkpoint_hash = hashlib.sha256(path.read_bytes()).hexdigest()
                checkpoint = torch.load(path, map_location="cpu", weights_only=False)
                policy = HybridPolicy(checkpoint["obs_dim"], checkpoint["hidden"])
                policy.load_state_dict(checkpoint["policy"])
                policy.eval()
            for split in ("test", "longer_test"):
                name = f"{arm}_seed_{seed}_{split}" if seed is not None else f"{arm}_{split}"
                path = base / (f"{arm}_seed_{seed}/{split}.json" if seed is not None else f"{arm}_{split}.json")
                expected = json.loads(path.read_text())["episodes"]
                rows, traces = replay(radio, scenarios[split], cfg, policy, arm if seed is None else None)
                assert rows == expected, f"Exact replay mismatch: {name}"
                total += len(rows)
                record[name] = {"exact_episode_matches": len(rows), "checkpoint_sha256": checkpoint_hash}
                (output / f"{name}.json").write_text(json.dumps({
                    "columns": ["time_s", "x_m", "y_m", "speed_mps", "station", "rbg", "rss_dbm",
                                "queue_bits", "rate_bps", "interference_w", "sinr_db"],
                    "traces": traces, "scenarios": scenarios[split][:4],
                    "episodes": rows[:4], "verification": record[name]}, indent=2) + "\n", encoding="utf-8")
                print(name, "exact", len(rows), flush=True)
    (output / "audit.json").write_text(json.dumps({"exact_episode_matches": total, "runs": record,
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
