"""Behavioral checks for a reward only V2.1 intervention."""
import ast
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest

from uav_joint_optimization.connectivity_env import ConnectivityBatch, ConnectivityConfig
from uav_joint_optimization.service_reward_env import ServiceRewardBatch, ServiceRewardConfig, service_cost
from uav_joint_optimization import connectivity_ppo, service_reward_ppo


class Radio:
    limits = np.array([5000., 3500.], dtype=np.float32)
    positions = np.zeros((6, 2), dtype=np.float32)
    values = [-40, -44, -48, -52, -56, -60]
    path, stride = 'synthetic_service_check', 1

    def query(self, positions):
        return np.tile(np.array(self.values, dtype=np.float32), (len(positions), 1))


ROUTES = [{'id': 'short', 'start': [1000., 1000.], 'goal': [1100., 1000.], 'load_phase': 0}]


@pytest.mark.parametrize('mode', ['normal', 'overflow', 'outage', 'energy', 'timeout', 'boundary'])
@pytest.mark.parametrize('reward', ['service', 'full'])
def test_transitions_filter_and_nonreward_records_identical(mode, reward):
    radio = Radio()
    cfg = ServiceRewardConfig(service_rss_weight=.25, service_failure_penalty=100)
    if mode == 'overflow':
        cfg = replace(cfg, offered_bps=1e12)
    elif mode == 'outage':
        radio.values = [-128]*6
    elif mode == 'energy':
        cfg = replace(cfg, battery_j=1)
    elif mode == 'timeout':
        cfg = replace(cfg, horizon=1)
    elif mode == 'boundary':
        cfg = replace(cfg, safety_filter=False)
    base_cfg = ConnectivityConfig(**{k:getattr(cfg,k) for k in ConnectivityConfig.__dataclass_fields__})
    base = ConnectivityBatch(radio, 1, ROUTES, 'full', base_cfg)
    candidate = ServiceRewardBatch(radio, 1, ROUTES, reward, cfg)
    if mode == 'boundary':
        for env in (base,candidate):
            env.pos[:] = [4999., 1000.]; env.goal[:] = [5100., 1000.]
            env.vel[:] = [25., 0.]; env.observe()
    for _ in range(cfg.horizon):
        motion, network = base.controller('straight_radio')
        a, b = base.step(motion,network), candidate.step(motion,network)
        for k,v in base.__dict__.items():
            if isinstance(v,np.ndarray) and k != 'return_sum':
                assert np.array_equal(v,candidate.__dict__[k]),k
        clean=lambda rows:[{k:v for k,v in r.items() if k!='raw_return'} for r in rows]
        assert clean(a[4]) == clean(b[4])
        if reward == 'full':
            assert np.array_equal(a[2],b[2])
        assert np.isfinite(b[2]).all()
        if b[3].all():
            assert b[4][0]['raw_return'] == candidate.return_sum[0]
            dead=candidate.step(motion,network)
            assert dead[2][0] == 0 and not dead[3][0] and not dead[4]
            break
    else:
        pytest.fail('Missing terminal')


def test_delay_queue_and_signal_sensitivity_without_new_constraints():
    c=ServiceRewardConfig(service_rss_weight=.1)
    delays=np.array([0.,1.,6.,10.,200.])
    cost=service_cost(delays,0,0,0,-40,c)
    assert np.all(np.diff(cost)>0)
    old=.35*10*delays/(1+10*delays)
    assert cost[3]-cost[2] > 10*(old[3]-old[2])
    assert service_cost(1.,1.,0,0,-90,c)>service_cost(1.,.5,0,0,-90,c)
    assert service_cost(1.,.5,0,0,-95,c)>service_cost(1.,.5,0,0,-40,c)
    assert c.rss_min_dbm == -96 and c.offered_bps == 200000 and c.buffer_bits == 1280000


def test_ppo_estimator_unchanged():
    def canonical(module):
        tree=ast.parse(Path(module.__file__).read_text())
        tree.body=[n for n in tree.body if not
                   (isinstance(n,ast.Expr) and isinstance(n.value,ast.Constant) and isinstance(n.value.value,str))
                   and not (isinstance(n,ast.ImportFrom) and n.module in {'connectivity_env','service_reward_env'})]
        return ast.dump(tree,include_attributes=False)
    assert canonical(connectivity_ppo)==canonical(service_reward_ppo)


def test_terminal_arrival_and_queue_remain_allowed():
    env=ServiceRewardBatch(Radio(),1,ROUTES)
    env.pos[:]=env.goal; env.observe()
    _,_,reward,done,rows=env.step(np.zeros((1,2)),np.array([0]))
    assert done[0] and rows[0]['success'] and np.isfinite(reward[0])
    env.reset(done)
    assert not env.done[0] and env.return_sum[0] == 0
