"""Freeze, train and evaluate the original reward under the unchanged V2 system."""
import argparse
import hashlib
import json
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from uav_joint_optimization.experiment_env import RadioMap, make_scenarios
from uav_joint_optimization.connectivity_env import ConnectivityConfig
from uav_joint_optimization.reward_comparison_ppo import PPOConfig, HybridPolicy, train, evaluate, summarize

FREEZE = ROOT / "configs/frozen_reward_comparison_v15.json"
SPLITS = ROOT / "configs/reward_comparison_scenarios_v15.json"
V2 = ROOT / "results/connectivity_experiment/confirmatory_v2"
SEEDS = [2101, 2102, 2103, 2104, 2105]
ARMS = ["original", "full", "arrival"]
CONTROLLERS = ["straight_rss", "straight_radio", "joint_mpc", "joint_lookahead"]
SOURCES = ["src/uav_joint_optimization/original_reward_env.py",
           "src/uav_joint_optimization/reward_comparison_ppo.py",
           "scripts/run_reward_comparison.py", "scripts/analyze_reward_comparison.py",
           "configs/reward_comparison_scenarios_v15.json",
           "docs/36_v15_reward_comparison_protocol.md", "tests/test_reward_comparison.py"]


def digest(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def verify_old():
    for name in ("frozen_comparison_v1.json", "frozen_connectivity_v2.json"):
        manifest = json.loads((ROOT / "configs" / name).read_text())
        for path, expected in manifest["source_hashes"].items():
            assert digest(ROOT / path) == expected, path


def checkpoint_path(arm, seed, base):
    return (base if arm == "original" else V2) / f"{arm}_seed_{seed}/checkpoint.pt"


def load_policy(path, arm, seed):
    checkpoint = torch.load(path, map_location="cpu", weights_only=False)
    metadata = checkpoint["metadata"]
    assert metadata["seed"] == seed and metadata["reward"] == arm
    assert metadata["terminate_success"] is True
    assert metadata["environment"] == asdict(ConnectivityConfig())
    assert metadata["ppo"] == asdict(PPOConfig())
    assert checkpoint["steps"] == PPOConfig().steps and checkpoint["obs_dim"] == 156
    policy = HybridPolicy(checkpoint["obs_dim"], checkpoint["hidden"])
    policy.load_state_dict(checkpoint["policy"])
    policy.eval()
    return policy


def verify():
    verify_old()
    frozen = json.loads(FREEZE.read_text())
    for path, expected in frozen["source_hashes"].items():
        assert digest(ROOT / path) == expected, path
    for path, expected in frozen["reused_checkpoint_hashes"].items():
        assert digest(ROOT / path) == expected, path
    assert frozen["environment"] == asdict(ConnectivityConfig())
    assert frozen["ppo"] == asdict(PPOConfig())
    return frozen


def freeze():
    verify_old()
    if FREEZE.exists() or SPLITS.exists():
        raise FileExistsError("Freeze or saved new scenarios already exist")
    v2 = json.loads((ROOT / "configs/connectivity_scenarios_v2.json").read_text())
    v1 = json.loads((ROOT / "configs/controlled_scenarios.json").read_text())
    routes = {key: v2[key] for key in ("training", "validation", "validation_longer")}
    routes.update(test=make_scenarios(200, 53012), longer_test=make_scenarios(200, 53013, 1000, 1800))
    seen = {tuple(r["start"] + r["goal"]) for pool in (v1, v2) for split in pool.values() for r in split}
    for split in ("test", "longer_test"):
        for row in routes[split]:
            key = tuple(row["start"] + row["goal"])
            assert key not in seen
            seen.add(key)
    hashes = {}
    for arm in ("full", "arrival"):
        for seed in SEEDS:
            path = checkpoint_path(arm, seed, None)
            load_policy(path, arm, seed)
            hashes[path.relative_to(ROOT).as_posix()] = digest(path)
    map_hash = digest(ROOT / "dataset/Barcelona_dataset_January.h5")
    assert map_hash == json.loads((ROOT / "configs/frozen_comparison_v1.json").read_text())["dataset_sha256"]
    save(SPLITS, routes)
    save(FREEZE, {"frozen_utc": datetime.now(timezone.utc).isoformat(), "study": "v15_reward_on_v2",
                  "seeds": SEEDS, "arms": ARMS, "controllers": CONTROLLERS,
                  "environment": asdict(ConnectivityConfig()), "ppo": asdict(PPOConfig()),
                  "source_hashes": {p: digest(ROOT / p) for p in SOURCES},
                  "reused_checkpoint_hashes": hashes, "dataset_sha256": map_hash,
                  "primary_contrast": "full_minus_original_test", "bootstrap_seed": 63000,
                  "bootstrap_draws": 5000, "new_test_seeds": [53012, 53013]})
    print("Frozen new source, reused weights and fresh tests before training/evaluation.", flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", required=True, choices=["freeze", "train", "evaluate", "replay"])
    parser.add_argument("--label", default="v15")
    args = parser.parse_args()
    torch.set_num_threads(PPOConfig().threads)
    if args.phase == "freeze":
        freeze()
        return
    frozen = verify()
    assert digest(ROOT / "dataset/Barcelona_dataset_January.h5") == frozen["dataset_sha256"]
    routes = json.loads(SPLITS.read_text())
    base = ROOT / "results/reward_comparison" / f"confirmatory_{args.label}"
    base.mkdir(parents=True, exist_ok=True)
    if args.phase == "train":
        for relative in SOURCES:
            destination = base / "source_snapshot" / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes((ROOT / relative).read_bytes())
        save(base / "source_hashes.json", frozen["source_hashes"])
    print("Loading unchanged native radio map", flush=True)
    radio = RadioMap(ROOT / "dataset/Barcelona_dataset_January.h5")
    if args.phase == "train":
        for seed in SEEDS:
            folder = base / f"original_seed_{seed}"
            if (folder / "checkpoint.pt").exists():
                load_policy(folder / "checkpoint.pt", "original", seed)
                assert (folder / "summary.json").exists(), "Incomplete run; use a fresh label"
                print(f"Verified completed original seed {seed}; retained unchanged.", flush=True)
                continue
            if folder.exists():
                raise FileExistsError(f"Partial run exists: {folder}; use a fresh label")
            train(radio, routes["training"], routes["validation"], "original", True,
                  seed, folder, PPOConfig(), ConnectivityConfig(), validation_every=0)
        save(base / "checkpoint_manifest.json", {
            "completed_utc": datetime.now(timezone.utc).isoformat(),
            "checkpoints": {checkpoint_path(arm, seed, base).relative_to(ROOT).as_posix():
                            digest(checkpoint_path(arm, seed, base)) for arm in ARMS for seed in SEEDS}})
        return
    checkpoint_manifest = json.loads((base / "checkpoint_manifest.json").read_text())
    for path, expected in checkpoint_manifest["checkpoints"].items():
        assert digest(ROOT / path) == expected, path
    replay = args.phase == "replay"
    destination = ROOT / "results/reward_comparison" / f"replay_{args.label}" if replay else base
    matches = 0
    for arm in ARMS + CONTROLLERS:
        for seed in SEEDS if arm in ARMS else [None]:
            policy = load_policy(checkpoint_path(arm, seed, base), arm, seed) if seed else None
            for split in ("test", "longer_test"):
                relative = f"{arm}_seed_{seed}/{split}" if seed else f"{arm}_{split}"
                prefix = destination / relative
                if prefix.with_suffix(".json").exists():
                    raise FileExistsError(prefix)
                rows = evaluate(policy, radio, routes[split], ConnectivityConfig(), prefix,
                                pd=False if seed else arm, reward=arm if seed else "full")
                if replay:
                    original = json.loads((base / relative).with_suffix(".json").read_text())["episodes"]
                    assert rows == original, relative
                    matches += len(rows)
                print(relative, json.dumps(summarize(rows)), flush=True)
    if replay:
        assert matches == 7600
        save(destination / "audit.json", {"exact_episode_matches": matches,
             "checked_utc": datetime.now(timezone.utc).isoformat(),
             "source_hashes": frozen["source_hashes"], "checkpoint_hashes": checkpoint_manifest["checkpoints"]})


if __name__ == "__main__":
    main()
