"""Bounded V2.1 development, frozen fresh evaluation and exact replay."""
import argparse
from dataclasses import asdict, replace
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
import torch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from uav_joint_optimization.experiment_env import RadioMap,make_scenarios
from uav_joint_optimization.connectivity_env import ConnectivityConfig
from uav_joint_optimization.service_reward_env import ServiceRewardConfig
from uav_joint_optimization import service_reward_ppo as learner
from uav_joint_optimization import reward_comparison_ppo as old_learner

BASE=ROOT/'results/service_reward_v21'
FREEZE=ROOT/'configs/frozen_service_reward_v21.json'
SPLITS=ROOT/'configs/service_reward_scenarios_v21.json'
SEEDS=[2101,2102,2103,2104,2105]
CANDIDATES={
    'full_control': ServiceRewardConfig(),
    'service': ServiceRewardConfig(),
    'reliability': ServiceRewardConfig(service_rss_weight=.10,service_failure_penalty=60),
    'reliability_strong': ServiceRewardConfig(service_queue_weight=.40,service_rss_weight=.25,service_failure_penalty=100),
}
SOURCES=['src/uav_joint_optimization/service_reward_env.py',
         'src/uav_joint_optimization/service_reward_ppo.py',
         'scripts/run_service_reward_study.py','scripts/analyze_service_reward_study.py',
         'tests/test_service_reward.py','docs/46_service_reward_development_protocol.md']


def digest(path):
    with Path(path).open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()


def save(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')


def verify_history():
    for name in ['frozen_comparison_v1.json','frozen_connectivity_v2.json','frozen_reward_comparison_v15.json']:
        d=json.loads((ROOT/'configs'/name).read_text())
        for p,h in d['source_hashes'].items(): assert digest(ROOT/p)==h,p
        for p,h in d.get('reused_checkpoint_hashes',{}).items(): assert digest(ROOT/p)==h,p


def old_path(arm,seed):
    folder='reward_comparison/confirmatory_v15' if arm=='original' else 'connectivity_experiment/confirmatory_v2'
    return ROOT/'results'/folder/f'{arm}_seed_{seed}/checkpoint.pt'


def load(path):
    checkpoint=torch.load(path,map_location='cpu',weights_only=False)
    assert checkpoint['steps']==learner.PPOConfig().steps
    policy=learner.HybridPolicy(checkpoint['obs_dim'],checkpoint['hidden'])
    policy.load_state_dict(checkpoint['policy']); policy.eval()
    return policy


def snapshot(folder):
    hashes={p:digest(ROOT/p) for p in SOURCES}
    save(folder/'source_hashes.json',hashes)
    for p in SOURCES:
        q=folder/'source_snapshot'/p; q.parent.mkdir(parents=True,exist_ok=True); q.write_bytes((ROOT/p).read_bytes())
    return hashes


def development(radio):
    folder=BASE/'development'
    if folder.exists(): raise FileExistsError(folder)
    snapshot(folder)
    routes=json.loads((ROOT/'configs/connectivity_scenarios_v2.json').read_text())
    records={}
    for name,cfg in CANDIDATES.items():
        arm='full' if name=='full_control' else 'service'
        policy=learner.train(radio,routes['training'],routes['validation'],arm,True,2199,
                             folder/name,learner.PPOConfig(),cfg,validation_every=0)
        records[name]={}
        for split in ['validation','validation_longer']:
            records[name][split]=learner.evaluate(policy,radio,routes[split],cfg,folder/name/split,reward=arm)
        print(json.dumps({'development':name,'results':{s:learner.summarize(v) for s,v in records[name].items()}}),flush=True)
    base=records['full_control']; reports={}; eligible=[]
    for order,(name,values) in enumerate(records.items()):
        summaries={s:learner.summarize(v) for s,v in values.items()}
        count=sum(r['success'] for v in values.values() for r in v)
        delays={}; matched=[]
        for split,rows in values.items():
            pairs=[(a,b) for a,b in zip(rows,base[split]) if a['success'] and b['success']]
            assert all(a['scenario_id']==b['scenario_id'] for a,b in zip(rows,base[split]))
            delays[split]=float(np.mean([a['delay_proxy_mean_s']-b['delay_proxy_mean_s'] for a,b in pairs])) if pairs else None
            matched.extend(a for a,b in pairs)
        reports[name]={'summaries':summaries,'successes':count,'matched_delay_differences':delays,
                       'checkpoint_sha256':digest(folder/name/'checkpoint.pt')}
        minimum=sum(r['success'] for v in base.values() for r in v)
        if name!='full_control' and count>=minimum and all(v is not None and v<=0 for v in delays.values()):
            eligible.append((-count,float(np.mean([r['delay_proxy_mean_s'] for r in matched])),
                             float(np.mean([r['handovers'] for r in matched])),order,name))
    chosen=min(eligible)[-1] if eligible else None
    result={'completed_utc':datetime.now(timezone.utc).isoformat(),'pilot_seed':2199,
            'steps_per_policy':learner.PPOConfig().steps,'candidates':reports,'selected':chosen,
            'gate_passed':chosen is not None,'selection_uses_validation_only':True}
    save(folder/'selection.json',result)
    print(json.dumps({'development_gate':result['gate_passed'],'selected':chosen,'successes':{k:v['successes'] for k,v in reports.items()}}),flush=True)


def freeze():
    if FREEZE.exists() or SPLITS.exists(): raise FileExistsError('Existing final freeze')
    selection=json.loads((BASE/'development/selection.json').read_text())
    assert selection['gate_passed'] and selection['selected'] in CANDIDATES
    # Selection is made before these new routes are generated or queried.
    old=json.loads((ROOT/'configs/connectivity_scenarios_v2.json').read_text())
    routes={k:old[k] for k in ['training','validation','validation_longer']}
    routes.update(test=make_scenarios(500,54012),longer_test=make_scenarios(500,54013,1000,1800))
    seen=set()
    for file in ['controlled_scenarios.json','connectivity_scenarios_v2.json','reward_comparison_scenarios_v15.json']:
        prior=json.loads((ROOT/'configs'/file).read_text())
        seen.update(tuple(r['start']+r['goal']) for pool in prior.values() for r in pool)
    for s in ['test','longer_test']:
        for r in routes[s]:
            key=tuple(r['start']+r['goal']); assert key not in seen; seen.add(key)
    save(SPLITS,routes)
    save(FREEZE,{'frozen_utc':datetime.now(timezone.utc).isoformat(),'study':'service_reward_v21',
                 'selected':selection['selected'],'seeds':SEEDS,'ppo':asdict(learner.PPOConfig()),
                 'environment':asdict(CANDIDATES[selection['selected']]),
                 'source_hashes':{p:digest(ROOT/p) for p in SOURCES},
                 'routes_sha256':digest(SPLITS),'selection_sha256':digest(BASE/'development/selection.json'),
                 'dataset_sha256':digest(ROOT/'dataset/Barcelona_dataset_January.h5'),
                 'reused_checkpoint_hashes':{old_path(a,s).relative_to(ROOT).as_posix():digest(old_path(a,s)) for a in ['original','full'] for s in SEEDS},
                 'primary_contrast':'service_minus_full_test','bootstrap_seed':64000,'bootstrap_draws':5000})
    print('Frozen selected V2.1 candidate before final training and fresh evaluation.',flush=True)


def verify_new():
    d=json.loads(FREEZE.read_text())
    for p,h in d['source_hashes'].items(): assert digest(ROOT/p)==h,p
    for p,h in d['reused_checkpoint_hashes'].items(): assert digest(ROOT/p)==h,p
    assert digest(SPLITS)==d['routes_sha256']
    assert digest(BASE/'development/selection.json')==d['selection_sha256']
    return d


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--phase',required=True,choices=['development','freeze','train','evaluate','replay'])
    args=parser.parse_args(); verify_history(); torch.set_num_threads(2)
    if args.phase=='freeze': freeze(); return
    d=verify_new() if args.phase!='development' else None
    expected=json.loads((ROOT/'configs/frozen_comparison_v1.json').read_text())['dataset_sha256']
    assert digest(ROOT/'dataset/Barcelona_dataset_January.h5')==expected
    print('Loading unchanged native radio map',flush=True)
    radio=RadioMap(ROOT/'dataset/Barcelona_dataset_January.h5')
    if args.phase=='development': development(radio); return
    cfg=ServiceRewardConfig(**d['environment']); routes=json.loads(SPLITS.read_text())
    destination=BASE/'confirmatory'
    if args.phase=='train':
        if destination.exists(): raise FileExistsError(destination)
        snapshot(destination)
        for seed in SEEDS:
            learner.train(radio,routes['training'],routes['validation'],'service',True,seed,
                          destination/f'service_seed_{seed}',learner.PPOConfig(),cfg,validation_every=0)
        save(destination/'checkpoint_manifest.json',{'checkpoints':{
            (destination/f'service_seed_{s}/checkpoint.pt').relative_to(ROOT).as_posix():digest(destination/f'service_seed_{s}/checkpoint.pt') for s in SEEDS}})
        return
    manifest=json.loads((destination/'checkpoint_manifest.json').read_text())
    for p,h in manifest['checkpoints'].items(): assert digest(ROOT/p)==h,p
    replay=args.phase=='replay'; target=BASE/'replay' if replay else destination
    matches=0
    for arm in ['service','full','original','straight_radio','joint_mpc','joint_lookahead']:
        for seed in SEEDS if arm in ['service','full','original'] else [None]:
            policy=load(destination/f'service_seed_{seed}/checkpoint.pt' if arm=='service' else old_path(arm,seed)) if seed else None
            for split in ['test','longer_test']:
                relative=f'{arm}_seed_{seed}/{split}' if seed else f'{arm}_{split}'
                prefix=target/relative
                if prefix.with_suffix('.json').exists(): raise FileExistsError(prefix)
                if arm=='service':
                    rows=learner.evaluate(policy,radio,routes[split],cfg,prefix,reward='service')
                else:
                    rows=old_learner.evaluate(policy,radio,routes[split],ConnectivityConfig(),prefix,
                        pd=arm if seed is None else False,reward='original' if arm=='original' else 'full')
                if replay:
                    assert rows==json.loads((destination/relative).with_suffix('.json').read_text())['episodes'],relative
                    matches+=len(rows)
                print(json.dumps({'evaluation':relative,'replay':replay,'summary':learner.summarize(rows)}),flush=True)
    if replay:
        assert matches==18000
        save(target/'audit.json',{'exact_episode_matches':matches,'completed_utc':datetime.now(timezone.utc).isoformat()})


if __name__=='__main__': main()
