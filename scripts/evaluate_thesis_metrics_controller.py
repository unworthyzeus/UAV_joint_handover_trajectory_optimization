"""Run a declared controller and report the added thesis motivated metrics."""
import argparse
import json
from pathlib import Path

import numpy as np
import torch

import run_thesis_metrics_study as study


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--controller', required=True, choices=['guard', 'full', 'original', 'service',
        'straight_radio', 'joint_mpc', 'joint_lookahead'])
    parser.add_argument('--seed', type=int, choices=study.SEEDS, default=2101)
    parser.add_argument('--split', choices=['test', 'longer_test'], default='test')
    parser.add_argument('--start', nargs=2, type=float)
    parser.add_argument('--goal', nargs=2, type=float)
    parser.add_argument('--load-phase', type=int, choices=range(12), default=0)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if (args.start is None) != (args.goal is None):
        parser.error('Supply both start and goal.')
    if any(args.output.with_suffix(s).exists() for s in ('.json', '.npz')):
        raise FileExistsError(args.output)
    study.verify_history(); frozen = study.verify_new(); torch.set_num_threads(2)
    if args.start is not None:
        for x, y in (args.start, args.goal):
            if not (0 <= x <= 5000 and 0 <= y <= 3500):
                parser.error('Coordinates must be within the 5000 by 3500 m map.')
        routes = [{'id': 'custom', 'start': args.start, 'goal': args.goal, 'load_phase': args.load_phase}]
    else:
        routes = json.loads(study.SCENARIOS.read_text())[args.split]
    radio = study.RadioMap(study.ROOT/'dataset/Barcelona_dataset_January.h5')
    seed = args.seed if args.controller in ('guard', 'full', 'original', 'service') else None
    horizon = frozen['selected_horizon'] if args.controller == 'guard' else None
    if args.controller == 'guard' and horizon is None:
        parser.error('No guard passed the declared development gate.')
    records, arrays, seconds = study.evaluate(args.controller, seed, radio, routes, horizon)
    study.save(args.output.with_suffix('.json'), {'controller': args.controller, 'seed': seed,
        'guard_horizon': horizon, 'runtime_seconds': seconds, 'episodes': records, 'summary': study.summarize(records)})
    np.savez_compressed(args.output.with_suffix('.npz'), **arrays)
    print(json.dumps(study.summarize(records), indent=2))


if __name__ == '__main__':
    main()
