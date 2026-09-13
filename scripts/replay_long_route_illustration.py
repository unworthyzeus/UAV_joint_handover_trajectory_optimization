"""Recover dense traces for an outcome independent long route illustration."""
import json

import numpy as np
import torch

from run_reward_comparison import (ROOT, SPLITS, PPOConfig, ConnectivityConfig,
                                   RadioMap, checkpoint_path, digest, load_policy, verify)
from uav_joint_optimization.original_reward_env import RewardComparisonBatch

BASE = ROOT / "results/reward_comparison/confirmatory_v15"
OUT = ROOT / "results/reward_comparison/analysis_v15/long_route_illustration.json"
SELECTION = ROOT / "configs/long_route_illustration_v15.json"
COLUMNS = ["time_s", "x_m", "y_m", "speed_mps", "operator_station_index", "station_id", "rbg",
           "rss_dbm", "sinr_db", "queue_bits", "capacity_bps", "delay_proxy_s", "interference_w",
           "energy_proxy_j", "handovers", "resource_changes", "network_interventions", "motion_interventions"]


def main():
    frozen = verify()
    selection = json.loads(SELECTION.read_text())
    scenarios = json.loads(SPLITS.read_text())[selection["split"]]
    index = min(range(len(scenarios)), key=lambda i: (
        -float(np.linalg.norm(np.array(scenarios[i]["goal"]) - scenarios[i]["start"])), scenarios[i]["id"]))
    assert index == selection["scenario_index"]
    assert scenarios[index]["id"] == selection["scenario_id"]
    assert np.isclose(np.linalg.norm(np.array(scenarios[index]["goal"]) - scenarios[index]["start"]),
                      selection["distance_m"], rtol=0, atol=1e-9)
    dataset = ROOT / "dataset/Barcelona_dataset_January.h5"
    assert digest(dataset) == frozen["dataset_sha256"]
    manifest = json.loads((BASE / "checkpoint_manifest.json").read_text())
    torch.set_num_threads(PPOConfig().threads)
    print("Loading the unchanged native radio map", flush=True)
    radio = RadioMap(dataset)
    cfg = ConnectivityConfig(**frozen["environment"])
    output = {"selection": selection, "selection_sha256": digest(SELECTION),
              "scenario": scenarios[index], "columns": COLUMNS, "environment": frozen["environment"],
              "dataset_sha256": frozen["dataset_sha256"], "scenario_file_sha256": digest(SPLITS),
              "statistics_sha256": digest(OUT.parent / "statistics.json"),
              "station_ids": radio.station_ids.tolist(), "station_positions_m": radio.positions.tolist(),
              "source_sha256": digest(__file__), "arms": {}}
    for arm in selection["arms"]:
        seed = selection["model_seed"] if arm != "straight_radio" else None
        checkpoint = checkpoint_path(arm, seed, BASE) if seed else None
        if checkpoint:
            assert digest(checkpoint) == manifest["checkpoints"][checkpoint.relative_to(ROOT).as_posix()]
        policy = load_policy(checkpoint, arm, seed) if checkpoint else None
        relative = f"{arm}_seed_{seed}/{selection['split']}.json" if seed else f"{arm}_{selection['split']}.json"
        saved = json.loads((BASE / relative).read_text())
        env = RewardComparisonBatch(radio, len(scenarios), scenarios, arm if seed else "full", cfg)
        obs, mask = env.observe()
        records, trace = [], []

        def capture():
            rss, interference, sinr, rate = env.radio_state()
            k = int(env.serving[index])
            delay = np.minimum(cfg.horizon * cfg.dt_s, env.buffer / np.maximum(rate, 1.))
            trace.append([float(env.t[index] * cfg.dt_s), *env.pos[index].tolist(),
                          float(np.linalg.norm(env.vel[index])), k, int(radio.station_ids[k]),
                          int(env.rbg[index]), float(rss[index, k]), float(sinr[index]),
                          float(env.buffer[index]), float(rate[index]), float(delay[index]),
                          float(interference[index]), float(env.energy[index]), int(env.handovers[index]),
                          int(env.resource_changes[index]), int(env.network_interventions[index]),
                          int(env.motion_interventions[index])])

        capture()
        for _ in range(cfg.horizon):
            was_active = not env.done[index]
            if policy is None:
                motion, network = env.controller(arm)
            else:
                with torch.no_grad():
                    latent, network_tensor, _, _ = policy.action(torch.from_numpy(obs), torch.from_numpy(mask), True)
                motion, network = env.decode_residual(torch.tanh(latent).numpy()), network_tensor.numpy()
            obs, mask, _, _, completed = env.step(motion, network)
            records.extend(completed)
            if was_active:
                capture()
            if env.done.all():
                break
        records.sort(key=lambda row: row["lane"])
        assert records == saved["episodes"], f"Exact replay mismatch for {arm}"
        episode = records[index]
        a = np.asarray(trace)
        col = {name: a[:, i] for i, name in enumerate(COLUMNS)}
        assert len(trace) == int(episode["time_s"] / cfg.dt_s) + 1
        assert int(np.count_nonzero(np.diff(col["station_id"]))) == episode["handovers"]
        assert col["handovers"][-1] == episode["handovers"]
        assert col["energy_proxy_j"][-1] == episode["energy_proxy_j"]
        assert col["queue_bits"][-1] == episode["final_buffer_bits"]
        assert col["rss_dbm"][1:].min() == episode["minimum_rss_dbm"]
        for column, metric in (("delay_proxy_s", "delay_proxy_mean_s"),
                               ("interference_w", "interference_mean_w"), ("sinr_db", "sinr_mean_db")):
            np.testing.assert_allclose(col[column][1:].mean(), episode[metric], rtol=1e-6, atol=1e-12)
        output["arms"][arm] = {"episode": episode, "trace": trace, "exact_episode_matches": len(records),
            "record_path": (BASE / relative).relative_to(ROOT).as_posix(), "record_sha256": digest(BASE / relative),
            "checkpoint_path": checkpoint.relative_to(ROOT).as_posix() if checkpoint else None,
            "checkpoint_sha256": digest(checkpoint) if checkpoint else None}
        print(f"{arm}: all {len(records)} episodes match exactly; selected route {episode['outcome']}, "
              f"{episode['handovers']} handovers, {episode['time_s']:.0f} s", flush=True)
    output["exact_episode_matches"] = sum(row["exact_episode_matches"] for row in output["arms"].values())
    OUT.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
