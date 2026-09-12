"""Post hoc service diagnostics on frozen flights; no training or model changes.

Replay both reward replacement arms and the PD reference on both existing test
splits. Require exact agreement with every saved episode before reporting new
metrics. Capacity below offered traffic is a service deficit, not an RSS outage
or a newly declared mission failure. A buffer may absorb short deficits.
"""
from __future__ import annotations

import csv
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from uav_joint_optimization.experiment_env import EnvironmentConfig, RadioMap, UAVBatch
from uav_joint_optimization.experiment_ppo import HybridPolicy


def replay(policy, radio, scenarios, config, saved, pd=False):
    env = UAVBatch(radio, len(scenarios), scenarios, "fixed", True, config, evaluation=True)
    obs, mask = env.observe()
    deficit = np.zeros(env.n, dtype=int)
    consecutive = deficit.copy()
    longest = deficit.copy()
    delay_above_one = deficit.copy()
    max_delay = np.zeros(env.n)
    results = []
    for _ in range(config.horizon):
        active = ~env.done.copy()
        if pd:
            motion, network = env.pd_action()
        else:
            with torch.no_grad():
                latent, choice, _, _ = policy.action(torch.from_numpy(obs), torch.from_numpy(mask), True)
            motion, network = torch.tanh(latent).numpy(), choice.numpy()
        obs, mask, _, _, completed = env.step(motion, network)
        _, _, _, rate = env.radio_state()
        below = rate < config.offered_bps
        deficit += active & below
        consecutive = np.where(active, np.where(below, consecutive + 1, 0), consecutive)
        longest = np.maximum(longest, consecutive)
        delay = np.minimum(config.horizon * config.dt_s, env.buffer / np.maximum(rate, 1.))
        delay_above_one += active & (delay > 1.)
        max_delay = np.maximum(max_delay, np.where(active, delay, 0.))
        results.extend(completed)
        if env.done.all():
            break
    results.sort(key=lambda row: row["lane"])
    assert results == saved, "Replay differs from frozen episode records"
    rows = []
    for row in results:
        i = row["lane"]
        steps = int(env.t[i])
        rows.append({**row,
            "path_to_endpoint_distance_ratio": row["path_m"] / row["straight_distance_m"],
            "service_deficit_fraction": float(deficit[i] / steps),
            "longest_service_deficit_s": float(longest[i] * config.dt_s),
            "delay_above_one_s_fraction": float(delay_above_one[i] / steps),
            "max_delay_proxy_s": float(max_delay[i]),
            "final_buffer_bits": float(env.buffer[i]),
        })
    return rows


def summarize(rows):
    success = [r for r in rows if r["success"]]
    summary = {
        "episodes": len(rows), "successful_episodes": len(success),
        "success_rate": len(success) / len(rows),
        "recorded_feasible_success_rate": float(np.mean([r["recorded_feasible_success"] for r in rows])),
        "success_without_any_rss_outage_rate": sum(r["success"] and r["outage_s"] == 0 for r in rows) / len(rows),
        "success_with_nonempty_final_buffer_count": sum(r["final_buffer_bits"] > 0 for r in success),
        "successful_missions_with_any_service_deficit_count": sum(r["service_deficit_fraction"] > 0 for r in success),
    }
    for key in ("time_s", "handovers", "outage_s", "sinr_mean_db", "delay_proxy_mean_s",
                "path_to_endpoint_distance_ratio", "service_deficit_fraction",
                "longest_service_deficit_s", "delay_above_one_s_fraction", "final_buffer_bits"):
        values = [r[key] for r in success]
        summary["successful_" + key] = {
            "mean": float(np.mean(values)), "median": float(np.median(values)),
            "p95": float(np.percentile(values, 95)),
        } if values else None
    return summary


def main():
    frozen = json.loads((ROOT / "configs/frozen_comparison_v1.json").read_text())
    for name, expected in frozen["source_hashes"].items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected, name
    config = EnvironmentConfig(**frozen["environment"])
    scenarios = json.loads((ROOT / "configs/controlled_scenarios.json").read_text())
    torch.set_num_threads(2)
    radio = RadioMap(ROOT / "dataset/Barcelona_dataset_January.h5")
    base = ROOT / "results/controlled_experiment/confirmatory_v1"
    all_rows, per_run, checkpoint_hashes = [], {}, {}
    for arm in ("reward_only", "fixed", "pd"):
        for seed in (frozen["seeds"] if arm != "pd" else [None]):
            policy = None
            if arm != "pd":
                path = base / f"{arm}_seed_{seed}/checkpoint.pt"
                checkpoint_hashes[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
                checkpoint = torch.load(path, map_location="cpu", weights_only=False)
                assert checkpoint["metadata"]["environment"] == frozen["environment"]
                policy = HybridPolicy(checkpoint["obs_dim"], checkpoint["hidden"])
                policy.load_state_dict(checkpoint["policy"])
                policy.eval()
            for split in ("test", "longer_test"):
                path = base / (f"pd_{split}.json" if arm == "pd" else f"{arm}_seed_{seed}/{split}.json")
                saved = json.loads(path.read_text())["episodes"]
                rows = replay(policy, radio, scenarios[split], config, saved, arm == "pd")
                all_rows.extend({"arm": arm, "seed": seed, "split": split, **row} for row in rows)
                name = f"{arm}_{seed}_{split}"
                per_run[name] = summarize(rows)
                print(f"{name}: {len(rows)} exact episode matches", flush=True)
    output = ROOT / "results/controlled_experiment/connectivity_audit_v1"
    output.mkdir(parents=True, exist_ok=True)
    with (output / "episodes.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(all_rows[0]))
        writer.writeheader()
        writer.writerows(all_rows)
    grouped = {f"{arm}_{split}": summarize([r for r in all_rows if r["arm"] == arm and r["split"] == split])
               for arm in ("reward_only", "fixed", "pd") for split in ("test", "longer_test")}
    report = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "Post hoc descriptive audit of existing tests, not a new confirmatory experiment or policy selection",
        "exact_episode_matches": len(all_rows), "frozen_source_hashes_verified": True,
        "diagnostic_script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "dataset_sha256_from_frozen_manifest": frozen["dataset_sha256"],
        "checkpoint_sha256": checkpoint_hashes,
        "config": frozen["environment"],
        "capacity_equals_offered_traffic_sinr_db": float(10 * np.log10(2 ** (config.offered_bps / config.bandwidth_hz) - 1)),
        "aggregation": "Radio and path metrics condition on success; means weight each successful mission equally. Seeds reuse the same routes. No independence or significance claim.",
        "grouped": grouped, "per_run": per_run,
    }
    (output / "summary.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(grouped, indent=2))


if __name__ == "__main__":
    main()
