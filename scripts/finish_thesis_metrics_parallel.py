"""Resume independent frozen evaluations and verify every episode and sample.

Calls the frozen evaluator unchanged, including its 500 route batch size.
Existing completed runs are verified, never overwritten or selected by outcome.
"""
from concurrent.futures import ProcessPoolExecutor, as_completed
import json

import numpy as np
import torch

import run_thesis_metrics_study as study

RADIO = None


def initialize():
    global RADIO
    torch.set_num_threads(2)
    RADIO = study.RadioMap(study.ROOT/'dataset/Barcelona_dataset_January.h5')


def run_job(job):
    arm, seed, split, routes, horizon = job
    prefix = study.BASE/'confirmatory'/(f'{arm}_seed_{seed}' if seed else arm)/split
    existed = prefix.with_suffix('.json').exists()
    records, arrays, seconds = study.evaluate(arm, seed, RADIO, routes, horizon if arm == 'guard' else None)
    if not existed:
        study.write_run(prefix, records, arrays, seconds, arm, seed, horizon if arm == 'guard' else None)
        records, arrays, _ = study.evaluate(arm, seed, RADIO, routes, horizon if arm == 'guard' else None)
    assert records == json.loads(prefix.with_suffix('.json').read_text())['episodes'], str(prefix)
    with np.load(prefix.with_suffix('.npz')) as saved:
        assert set(saved.files) == set(arrays)
        for key, value in arrays.items():
            np.testing.assert_array_equal(value, saved[key])
    return {'run': prefix.relative_to(study.BASE).as_posix(), 'episodes': len(records),
            'record_sha256': study.sha(prefix.with_suffix('.json')),
            'samples_sha256': study.sha(prefix.with_suffix('.npz')), 'existing_run_reused': existed}


def main():
    study.verify_history(); frozen = study.verify_new()
    expected = json.loads((study.ROOT/'configs/frozen_comparison_v1.json').read_text())['dataset_sha256']
    assert study.sha(study.ROOT/'dataset/Barcelona_dataset_January.h5') == expected
    routes = json.loads(study.SCENARIOS.read_text()); horizon = frozen['selected_horizon']
    arms = ['original', 'full', 'service'] + (['guard'] if horizon else [])
    settings = [(a, s) for a in arms for s in study.SEEDS]
    settings += [(a, None) for a in ('straight_radio', 'joint_mpc', 'joint_lookahead')]
    jobs = [(a, seed, split, r, horizon) for a, seed in settings for split, r in routes.items()]
    # Schedule expensive independent guard jobs first to balance worker time.
    jobs.sort(key=lambda j: j[0] != 'guard')
    checks = []
    with ProcessPoolExecutor(max_workers=3, initializer=initialize) as pool:
        for future in as_completed([pool.submit(run_job, job) for job in jobs]):
            result = future.result(); checks.append(result)
            print(json.dumps({'verified': result['run'], 'episodes': result['episodes']}), flush=True)
    checks.sort(key=lambda r: r['run'])
    study.save(study.BASE/'replay_audit.json', {'exact_episode_and_metric_matches': sum(r['episodes'] for r in checks),
        'all_sample_arrays_exact': True, 'runs': checks, 'workers': 3,
        'orchestration_sha256': study.sha(__file__),
        'execution_note': 'The serial evaluator was stopped during an unfinished run to parallelize independent jobs. '
                          'Completed runs were retained and replayed; missing runs used the frozen evaluator unchanged.'})


if __name__ == '__main__':
    main()
