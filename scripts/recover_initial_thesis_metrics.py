"""Add passive measurements to the initial comparison without changing a flight."""
import json

import torch

import run_thesis_metrics_study as study


def main():
    study.verify_history(); study.verify_new(); torch.set_num_threads(2)
    folder = study.BASE/'initial_replay'
    if folder.exists():
        raise FileExistsError(folder)
    expected = json.loads((study.ROOT/'configs/frozen_comparison_v1.json').read_text())['dataset_sha256']
    assert study.sha(study.ROOT/'dataset/Barcelona_dataset_January.h5') == expected
    radio = study.RadioMap(study.ROOT/'dataset/Barcelona_dataset_January.h5')
    routes = json.loads((study.ROOT/'configs/reward_comparison_scenarios_v15.json').read_text())
    checks = []
    for arm in ('original', 'full'):
        for seed in study.SEEDS:
            for split in ('test', 'longer_test'):
                old = study.ROOT/f'results/reward_comparison/confirmatory_v15/{arm}_seed_{seed}/{split}.json'
                source_rows = json.loads(old.read_text())['episodes']
                rows, arrays, seconds = study.evaluate(arm, seed, radio, routes[split])
                assert len(rows) == len(source_rows) == 200
                for row, source in zip(rows, source_rows):
                    assert {key: row[key] for key in source} == source
                prefix = folder/f'{arm}_seed_{seed}'/split
                study.write_run(prefix, rows, arrays, seconds, arm, seed, None)
                checks.append({'source': old.relative_to(study.ROOT).as_posix(), 'source_sha256': study.sha(old),
                               'recovered': prefix.with_suffix('.json').relative_to(study.ROOT).as_posix(),
                               'recovered_sha256': study.sha(prefix.with_suffix('.json')), 'exact_core_matches': len(rows)})
    study.save(folder/'audit.json', {'scope': 'Additional measurements on unchanged initial 53012/53013 flights; no new independent experiment.',
        'exact_core_episode_matches': sum(r['exact_core_matches'] for r in checks), 'dataset_sha256': expected,
        'script_sha256': study.sha(__file__), 'runs': checks})


if __name__ == '__main__':
    main()
