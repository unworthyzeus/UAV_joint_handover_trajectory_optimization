"""Evaluate a V2.1 checkpoint on saved routes or one custom mission."""
import argparse
import json
from pathlib import Path
import sys

import torch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from uav_joint_optimization.experiment_env import RadioMap
from uav_joint_optimization.service_reward_env import ServiceRewardConfig
from uav_joint_optimization.service_reward_ppo import HybridPolicy,evaluate,summarize


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--checkpoint',required=True,type=Path)
    parser.add_argument('--split',choices=['validation','validation_longer','test','longer_test'],default='validation')
    parser.add_argument('--start',nargs=2,type=float)
    parser.add_argument('--goal',nargs=2,type=float)
    parser.add_argument('--load-phase',type=int,default=0,choices=range(12))
    parser.add_argument('--output',required=True,type=Path,help='Fresh output prefix; existing outputs are not overwritten.')
    args=parser.parse_args()
    if (args.start is None)!=(args.goal is None): parser.error('Supply both --start and --goal.')
    if args.output.with_suffix('.json').exists() or args.output.with_suffix('.csv').exists():
        raise FileExistsError(args.output)
    checkpoint=torch.load(args.checkpoint,map_location='cpu',weights_only=False)
    assert checkpoint['metadata']['reward']=='service','Expected a V2.1 service reward checkpoint.'
    cfg=ServiceRewardConfig(**checkpoint['metadata']['environment'])
    policy=HybridPolicy(checkpoint['obs_dim'],checkpoint['hidden'])
    policy.load_state_dict(checkpoint['policy']); policy.eval(); torch.set_num_threads(2)
    if args.start is not None:
        for x,y in [args.start,args.goal]:
            if not (0<=x<=5000 and 0<=y<=3500): parser.error('Coordinates must stay in the 5000 by 3500 m map.')
        routes=[{'id':'custom','start':args.start,'goal':args.goal,'load_phase':args.load_phase}]
    else:
        routes=json.loads((ROOT/'configs/service_reward_scenarios_v21.json').read_text())[args.split]
    radio=RadioMap(ROOT/'dataset/Barcelona_dataset_January.h5')
    records=evaluate(policy,radio,routes,cfg,args.output,reward='service')
    print(json.dumps(summarize(records),indent=2))


if __name__=='__main__': main()
