"""Evaluate a saved or custom route with V2.2 or the frozen V2.3 candidate."""
import argparse
import json
from pathlib import Path

import numpy as np

import run_signal_guard_study as study


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--controller', choices=['v22', 'signal'], default='v22')
    parser.add_argument('--seed', type=int, choices=study.old.SEEDS, default=2101)
    parser.add_argument('--split', choices=['test', 'longer_test'], default='test')
    parser.add_argument('--scenario-index', type=int, default=0)
    parser.add_argument('--start', type=float, nargs=2)
    parser.add_argument('--goal', type=float, nargs=2)
    parser.add_argument('--load-phase', type=int, choices=range(12), default=0)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    if bool(args.start) != bool(args.goal):
        parser.error('--start and --goal must be given together.')
    if args.output.with_suffix('.json').exists() or args.output.with_suffix('.npz').exists():
        raise FileExistsError('Use a new output prefix to preserve existing records.')
    study.verify_history(); frozen = study.verify_frozen()
    dataset = study.ROOT/'dataset/Barcelona_dataset_January.h5'
    assert study.old.sha(dataset) == frozen['dataset_sha256']
    if args.start:
        points = np.asarray([args.start, args.goal])
        if not np.isfinite(points).all() or np.any(points < 0) or np.any(points > [5000., 3500.]):
            parser.error('Coordinates must be finite and inside the 5000 by 3500 m map.')
        route = {'id': 'custom', 'start': args.start, 'goal': args.goal, 'load_phase': args.load_phase}
    else:
        routes = json.loads(study.TEST_ROUTES.read_text())[args.split]
        if not 0 <= args.scenario_index < len(routes):
            parser.error('Scenario index is outside the saved split.')
        route = routes[args.scenario_index]
    study.initialize()
    allowance = frozen['selected_allowance_m'] if args.controller == 'signal' else None
    records, arrays, seconds = study.evaluate(args.seed, [route], allowance)
    prefix = args.output.resolve()
    study.old.save(prefix.with_suffix('.json'), {
        'scope': 'Single route demonstration; use the full study runner for exact original batch replay.',
        'controller': args.controller, 'seed': args.seed, 'allowance_m': allowance,
        'route': route, 'runtime_seconds': seconds, 'episodes': records,
        'checkpoint_sha256': study.old.sha(study.old.checkpoint('full', args.seed)),
        'dataset_sha256': frozen['dataset_sha256'], 'frozen_source_hashes': frozen['source_hashes'],
        'wrapper_sha256': study.old.sha(__file__), 'new_training': False})
    np.savez_compressed(prefix.with_suffix('.npz'), **arrays)
    print(json.dumps({'output': str(prefix.with_suffix('.json')), 'episode': records[0]}, indent=2))


if __name__ == '__main__':
    main()
