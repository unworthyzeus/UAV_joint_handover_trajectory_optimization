"""Verify reward fidelity and that the V1.5 intervention changes no V2 transition."""
import ast
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest
import torch

from uav_joint_optimization.connectivity_env import ConnectivityBatch, ConnectivityConfig
from uav_joint_optimization.original_reward_env import RewardComparisonBatch, original_reward
from uav_joint_optimization import connectivity_ppo, reward_comparison_ppo


class FlatRadio:
    limits = np.array([5000., 3500.], dtype=np.float32)
    positions = np.zeros((6, 2), dtype=np.float32)
    values = [-40, -44, -48, -52, -56, -60]
    path, stride = "synthetic_test", 1

    def query(self, positions):
        return np.tile(np.array(self.values, dtype=np.float32), (len(positions), 1))


ROUTES = [{"id": "short", "start": [1000., 1000.], "goal": [1100., 1000.], "load_phase": 0}]


def test_original_reward_matches_independent_source_examples():
    # RD=1/2, RI=1/2, Rh=1/101; source equal policy + approach bonus.
    value = original_reward(100., 99., .1, 1e-5, 1, -40., 25., False, False)
    assert value == pytest.approx(.35/2 + .30/2 + .35/101 + 12)
    assert original_reward(100., 100., 0., 0., 0, -40., 0., False, False) == pytest.approx(1)
    assert original_reward(100., 99., 0., 0., 0, -96., 25., False, False) == pytest.approx(3)
    assert original_reward(100., 99., 0., 0., 0, -40., 100., True, False) == pytest.approx(-7)
    assert original_reward(100., 99., 0., 0., 0, -40., 25., False, True) == pytest.approx(-10)


@pytest.mark.parametrize("reward", ["original", "full", "arrival"])
@pytest.mark.parametrize("mode", ["normal", "overflow", "outage", "energy", "timeout", "boundary"])
def test_all_nonreward_state_and_records_match_v2(reward, mode):
    radio = FlatRadio()
    cfg = ConnectivityConfig()
    if mode == "overflow":
        cfg = replace(cfg, offered_bps=1e12)
    elif mode == "outage":
        radio.values = [-128]*6
    elif mode == "energy":
        cfg = replace(cfg, battery_j=1)
    elif mode == "timeout":
        cfg = replace(cfg, horizon=1)
    elif mode == "boundary":
        cfg = replace(cfg, safety_filter=False)
    reference = ConnectivityBatch(radio, 1, ROUTES, "arrival" if reward == "arrival" else "full", cfg)
    changed = RewardComparisonBatch(radio, 1, ROUTES, reward, cfg)
    if mode == "boundary":
        for env in (reference, changed):
            env.pos[:] = [4999., 1000.]
            env.goal[:] = [5100., 1000.]
            env.vel[:] = [25., 0.]
            env.observe()
    for _ in range(cfg.horizon):
        motion, choice = reference.controller("straight_radio")
        expected, actual = reference.step(motion, choice), changed.step(motion, choice)
        for key, value in reference.__dict__.items():
            if isinstance(value, np.ndarray) and key != "return_sum":
                assert np.array_equal(value, changed.__dict__[key]), key
        assert np.array_equal(expected[0], actual[0])
        assert np.array_equal(expected[1], actual[1])
        assert np.array_equal(expected[3], actual[3])
        if reward != "original":
            assert np.array_equal(expected[2], actual[2])
        clean = lambda rows: [{k:v for k,v in row.items() if k != "raw_return"} for row in rows]
        assert clean(expected[4]) == clean(actual[4])
        if actual[3].all():
            assert actual[4][0]["raw_return"] == changed.return_sum[0]
            after = changed.step(motion, choice)
            assert after[2][0] == 0 and not after[3][0] and not after[4]
            break
    else:
        pytest.fail("Missing terminal")


def test_original_reward_keeps_v2_arrival_and_reset():
    env = RewardComparisonBatch(FlatRadio(), 1, ROUTES, "original")
    env.pos[:] = env.goal
    env.observe()
    _, _, reward, done, rows = env.step(np.zeros((1,2)), np.array([0]))
    assert done[0] and rows[0]["success"] and reward[0] <= 1
    env.reset(done)
    assert not env.done[0] and env.return_sum[0] == 0


def test_ppo_syntax_is_identical_except_adapter_import_and_module_docstring():
    def substantive(module):
        tree = ast.parse(Path(module.__file__).read_text())
        tree.body = [node for node in tree.body if not
                     (isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str))
                     and not (isinstance(node, ast.ImportFrom) and node.module in {"connectivity_env", "original_reward_env"})]
        return ast.dump(tree, include_attributes=False)
    assert substantive(connectivity_ppo) == substantive(reward_comparison_ppo)


def test_small_full_training_exactly_matches_frozen_v2_and_original_repeats(tmp_path):
    cfg = connectivity_ppo.PPOConfig(environments=4, rollout=8, minibatch=16, epochs=2, steps=64, threads=1)
    ecfg = replace(ConnectivityConfig(), horizon=10)
    models = []
    for module, arm, name in [(connectivity_ppo,"full","old"), (reward_comparison_ppo,"full","full"),
                               (reward_comparison_ppo,"original","a"), (reward_comparison_ppo,"original","b")]:
        models.append(module.train(FlatRadio(), ROUTES, ROUTES, arm, True, 7, tmp_path/name, cfg, ecfg, 0))
    for a,b in ((models[0],models[1]), (models[2],models[3])):
        assert all(torch.equal(value,b.state_dict()[key]) for key,value in a.state_dict().items())
    assert any(not torch.equal(value,models[2].state_dict()[key]) for key,value in models[0].state_dict().items())
