"""Train and evaluate the declared reimplementation, retaining every run."""
import argparse
import json
import sys
from dataclasses import asdict, replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from uav_joint_optimization.experiment_env import RadioMap, EnvironmentConfig, make_scenarios
from uav_joint_optimization.experiment_ppo import PPOConfig, evaluate, summarize, train

ARMS = {"legacy": ("legacy", False), "terminal_only": ("legacy", True),
        "reward_only": ("fixed", False), "fixed": ("fixed", True)}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--phase", choices=["pilot", "confirmatory", "baseline"], required=True)
    p.add_argument("--arms", nargs="+", choices=list(ARMS), default=["legacy", "fixed"])
    p.add_argument("--seeds", nargs="+", type=int, default=[41])
    p.add_argument("--steps", type=int, default=524288)
    p.add_argument("--stride", type=int, default=1)
    p.add_argument("--label", default="v1")
    args = p.parse_args()
    result_root = ROOT / "results" / "controlled_experiment" / f"{args.phase}_{args.label}"
    result_root.mkdir(parents=True, exist_ok=True)
    train_routes = make_scenarios(4096, 42000)
    validation = make_scenarios(64, 42001)
    test = make_scenarios(200, 42012)
    longer = make_scenarios(200, 42013, 1000, 1800)
    split_path = ROOT / "configs" / "controlled_scenarios.json"
    split_path.write_text(json.dumps({"training": train_routes, "validation": validation,
        "test": test, "longer_test": longer}, indent=2)+"\n", encoding="utf-8")
    print("Loading original radio map", flush=True)
    radio = RadioMap(ROOT / "dataset" / "Barcelona_dataset_January.h5", args.stride)
    cfg = EnvironmentConfig()
    ppo = replace(PPOConfig(), steps=args.steps)
    if args.phase == "baseline":
        for name, routes in [("validation", validation)]:
            rows = evaluate(None, radio, routes, cfg, result_root / f"pd_{name}", pd=True)
            print(name, json.dumps(summarize(rows)), flush=True)
        return
    (result_root / "run_manifest.json").write_text(json.dumps({"arguments": vars(args),
        "environment": asdict(cfg), "ppo": asdict(ppo)}, indent=2)+"\n", encoding="utf-8")
    if args.phase == "confirmatory":
        for name, routes in [("test", test), ("longer_test", longer)]:
            rows = evaluate(None, radio, routes, cfg, result_root / f"pd_{name}", pd=True)
            print("pd", name, json.dumps(summarize(rows)), flush=True)
    for seed in args.seeds:
        for arm in args.arms:
            out = result_root / f"{arm}_seed_{seed}"
            if (out / "checkpoint.pt").exists():
                raise FileExistsError(f"Refusing to overwrite trained run {out}")
            reward, terminal = ARMS[arm]
            policy = train(radio, train_routes, validation, reward, terminal, seed, out, ppo, cfg,
                           validation_every=16 if args.phase == "pilot" else 0)
            if args.phase == "confirmatory":
                for name, routes in [("test", test), ("longer_test", longer)]:
                    rows = evaluate(policy, radio, routes, cfg, out / name)
                    print(arm, seed, name, json.dumps(summarize(rows)), flush=True)


if __name__ == "__main__":
    main()
