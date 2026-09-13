"""Evaluate released V1.5/V2 weights on fresh saved routes or a custom flight."""
import argparse
import json
from pathlib import Path

import torch

from run_reward_comparison import (ROOT, SPLITS, CONTROLLERS, RadioMap, ConnectivityConfig,
                                   load_policy, evaluate, summarize)


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--checkpoint", type=Path)
    group.add_argument("--controller", choices=CONTROLLERS)
    parser.add_argument("--split", choices=["validation", "validation_longer", "test", "longer_test"], default="test")
    parser.add_argument("--start", type=float, nargs=2)
    parser.add_argument("--goal", type=float, nargs=2)
    parser.add_argument("--output", type=Path, default=ROOT / "outputs/reward_controller_evaluation")
    args = parser.parse_args()
    if (args.start is None) != (args.goal is None):
        parser.error("Supply both --start and --goal")
    if args.start:
        for point in (args.start, args.goal):
            if not (0 <= point[0] <= 5000 and 0 <= point[1] <= 3500):
                parser.error("Coordinates must be local meters within x=0..5000, y=0..3500")
        routes = [{"id": "user_route", "start": args.start, "goal": args.goal, "load_phase": 0}]
    else:
        routes = json.loads(SPLITS.read_text())[args.split]
    policy, arm = None, "full"
    if args.checkpoint:
        # Project generated weights include configuration metadata.
        metadata = torch.load(args.checkpoint, map_location="cpu", weights_only=False)["metadata"]
        arm = metadata["reward"]
        if arm not in {"original", "full", "arrival"}:
            parser.error("Use a final V1.5/V2 checkpoint; historical V1 is incompatible")
        policy = load_policy(args.checkpoint, arm, metadata["seed"])
    torch.set_num_threads(2)
    radio = RadioMap(ROOT / "dataset/Barcelona_dataset_January.h5")
    rows = evaluate(policy, radio, routes, ConnectivityConfig(), args.output,
                    pd=args.controller or False, reward=arm)
    print(json.dumps(summarize(rows), indent=2))


if __name__ == "__main__":
    main()
