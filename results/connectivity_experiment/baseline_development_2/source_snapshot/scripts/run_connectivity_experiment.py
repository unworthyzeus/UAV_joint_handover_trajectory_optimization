"""Development, freeze, and independent tests for the connectivity repair."""
import argparse
import hashlib
import json
import sys
from dataclasses import asdict, replace
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from uav_joint_optimization.experiment_env import RadioMap, make_scenarios
from uav_joint_optimization.connectivity_env import ConnectivityConfig
from uav_joint_optimization.connectivity_ppo import PPOConfig, train, evaluate, summarize

SPLITS = ROOT / "configs/connectivity_scenarios_v2.json"
FREEZE = ROOT / "configs/frozen_connectivity_v2.json"
SOURCES = ["src/uav_joint_optimization/connectivity_env.py", "src/uav_joint_optimization/connectivity_ppo.py",
           "scripts/run_connectivity_experiment.py", "configs/connectivity_scenarios_v2.json",
           "docs/28_connectivity_experiment_protocol.md"]


def verify_v1():
    frozen = json.loads((ROOT / "configs/frozen_comparison_v1.json").read_text())
    for name, expected in frozen["source_hashes"].items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected, name


def splits():
    if not SPLITS.exists():
        spec = {"training": make_scenarios(4096, 52000), "validation": make_scenarios(64, 52001),
                "validation_longer": make_scenarios(32, 52002, 1000, 1800),
                "test": make_scenarios(200, 52012), "longer_test": make_scenarios(200, 52013, 1000, 1800)}
        original = json.loads((ROOT / "configs/controlled_scenarios.json").read_text())
        seen = {tuple(s["start"] + s["goal"]) for routes in original.values() for s in routes}
        for routes in spec.values():
            for s in routes:
                key = tuple(s["start"] + s["goal"])
                assert key not in seen
                seen.add(key)
        SPLITS.write_text(json.dumps(spec, indent=2) + "\n", encoding="utf-8")
    return json.loads(SPLITS.read_text())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=["baseline", "pilot", "freeze", "confirmatory"], required=True)
    parser.add_argument("--label", default="v2")
    parser.add_argument("--seeds", nargs="+", type=int, default=[51])
    parser.add_argument("--arms", nargs="+", choices=["arrival", "full"], default=["arrival", "full"])
    parser.add_argument("--steps", type=int, default=524288)
    args = parser.parse_args()
    verify_v1()
    scenarios = splits()
    cfg, ppo = ConnectivityConfig(), replace(PPOConfig(), steps=args.steps)
    if args.phase == "freeze":
        if FREEZE.exists():
            raise FileExistsError(FREEZE)
        FREEZE.write_text(json.dumps({"frozen_utc": datetime.now(timezone.utc).isoformat(),
            "seeds": args.seeds, "arms": args.arms, "environment": asdict(cfg), "ppo": asdict(ppo),
            "source_hashes": {n: hashlib.sha256((ROOT / n).read_bytes()).hexdigest() for n in SOURCES}}, indent=2) + "\n", encoding="utf-8")
        print("Frozen before test evaluation.")
        return
    if args.phase == "confirmatory":
        frozen = json.loads(FREEZE.read_text())
        assert args.seeds == frozen["seeds"] and args.arms == frozen["arms"]
        assert asdict(cfg) == frozen["environment"] and asdict(ppo) == frozen["ppo"]
        for n, expected in frozen["source_hashes"].items():
            assert hashlib.sha256((ROOT / n).read_bytes()).hexdigest() == expected, n
    output = ROOT / "results/connectivity_experiment" / f"{args.phase}_{args.label}"
    output.mkdir(parents=True, exist_ok=True)
    snapshot = {n: hashlib.sha256((ROOT / n).read_bytes()).hexdigest() for n in SOURCES}
    (output / "source_hashes.json").write_text(json.dumps(snapshot, indent=2) + "\n", encoding="utf-8")
    for n in SOURCES:
        destination = output / "source_snapshot" / n
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes((ROOT / n).read_bytes())
    print("Loading the unchanged native radio map", flush=True)
    radio = RadioMap(ROOT / "dataset/Barcelona_dataset_January.h5")
    eval_splits = ["test", "longer_test"] if args.phase == "confirmatory" else ["validation", "validation_longer"]
    if args.phase in {"baseline", "confirmatory"}:
        for controller in ("straight_rss", "straight_radio", "joint_mpc"):
            for split in eval_splits:
                prefix = output / f"{controller}_{split}"
                if prefix.with_suffix(".json").exists():
                    raise FileExistsError(prefix)
                rows = evaluate(None, radio, scenarios[split], cfg, prefix, pd=controller)
                print(controller, split, json.dumps(summarize(rows)), flush=True)
        if args.phase == "baseline":
            return
    for seed in args.seeds:
        for arm in args.arms:
            folder = output / f"{arm}_seed_{seed}"
            if (folder / "checkpoint.pt").exists():
                raise FileExistsError(folder)
            policy = train(radio, scenarios["training"], scenarios["validation"], arm, True, seed, folder,
                           ppo, cfg, validation_every=16 if args.phase == "pilot" else 0)
            for split in eval_splits:
                rows = evaluate(policy, radio, scenarios[split], cfg, folder / split)
                print(arm, seed, split, json.dumps(summarize(rows)), flush=True)


if __name__ == "__main__":
    main()
