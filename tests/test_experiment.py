"""Meaningful environment and estimator checks before learned experiments."""
from dataclasses import replace

import numpy as np
import pytest
import torch

from uav_joint_optimization.experiment_env import EnvironmentConfig, RadioMap, UAVBatch, make_scenarios
from uav_joint_optimization.experiment_ppo import HybridPolicy, gae


class FlatRadio:
    limits = np.array([5000., 3500.], dtype=np.float32)
    positions = np.array([[100., 100.], [200., 200.], [300., 300.], [400., 400.], [500., 500.], [600., 600.]], dtype=np.float32)

    def query(self, positions):
        return np.tile(np.array([-40., -44., -48., -52., -56., -60.]), (len(positions), 1)).astype(np.float32)


def route():
    return [{"id": "unit", "start": [1000., 1000.], "goal": [1100., 1000.], "load_phase": 0}]


def test_double_integrator_and_acceleration_speed_constraints():
    env = UAVBatch(FlatRadio(), 1, route())
    env.step(np.array([[1., 0.]]), np.array([0]))
    assert env.pos[0] == pytest.approx([1002.5, 1000.])
    assert env.vel[0] == pytest.approx([5., 0.])
    for _ in range(7):
        old = env.vel.copy()
        env.step(np.array([[1., 1.]]), np.array([0]))
        assert np.linalg.norm(env.vel[0]) <= 25.00001
        assert np.linalg.norm(env.vel[0]-old[0]) <= 5.00001


def test_arrival_requires_low_speed_and_common_evaluation_termination():
    env = UAVBatch(FlatRadio(), 1, route(), evaluation=True)
    env.pos[:] = env.goal - [5., 0.]
    env.vel[:] = [5., 0.]
    env.observe()
    _, _, _, done, _ = env.step(np.zeros((1, 2)), np.array([0]))
    assert not done[0]
    _, _, _, done, rows = env.step(np.array([[1., 0.]]), np.array([0]))
    # At exact goal, the radial basis defaults to +x, so explicitly test a fresh rest state.
    env = UAVBatch(FlatRadio(), 1, route(), evaluation=True)
    env.pos[:] = env.goal; env.observe()
    _, _, _, done, rows = env.step(np.zeros((1, 2)), np.array([0]))
    assert done[0] and rows[0]["success"]


def test_success_reward_is_paid_only_once_in_continuing_arm():
    env = UAVBatch(FlatRadio(), 1, route(), reward="fixed")
    env.pos[:] = env.goal; env.observe()
    _, _, first, done, _ = env.step(np.zeros((1, 2)), np.array([0]))
    _, _, second, _, _ = env.step(np.zeros((1, 2)), np.array([0]))
    assert not done[0]
    assert first[0] - second[0] == pytest.approx(20.)


def test_potential_telescopes_with_zero_terminal_value():
    gamma = .99
    potentials = np.array([-9., -7., -8., -3., 0.])
    shaping = gamma * potentials[1:] - potentials[:-1]
    assert np.dot(gamma ** np.arange(4), shaping) == pytest.approx(-potentials[0])


def test_finite_horizon_is_a_terminal_failure_and_gae_does_not_bootstrap():
    env = UAVBatch(FlatRadio(), 1, route(), reward="fixed", config=replace(EnvironmentConfig(), horizon=1))
    _, _, reward, done, rows = env.step(np.zeros((1, 2)), np.array([0]))
    assert done[0] and not rows[0]["success"] and rows[0]["outcome"] == "timeout"
    assert reward[0] < -19.
    adv, returns = gae(np.array([[2.]], dtype=np.float32), np.array([[.5]], dtype=np.float32),
                       np.array([[True]]), np.array([100.]), .99, .95)
    assert returns[0, 0] == pytest.approx(2.)


def test_masked_handover_never_samples_an_invalid_action_and_logprob_matches():
    policy = HybridPolicy(8)
    obs = torch.zeros((100, 8))
    mask = torch.tensor([[True, False, True, False, False]]).repeat(100, 1)
    latent, choice, old, _ = policy.action(obs, mask)
    new, _, _ = policy.score(obs, mask, latent, choice)
    assert torch.all(mask[torch.arange(100), choice])
    assert torch.allclose(old, new)


def test_pd_controller_completes_different_routes_without_boundary_violation():
    env = UAVBatch(FlatRadio(), 32, make_scenarios(32, 18), evaluation=True)
    outcomes = []
    for _ in range(env.cfg.horizon):
        motion, network = env.pd_action()
        _, _, _, _, rows = env.step(motion, network)
        outcomes.extend(rows)
        if env.done.all():
            break
    assert len(outcomes) == 32
    assert all(row["success"] for row in outcomes)
    assert all(row["final_speed_mps"] <= 2 and row["final_distance_m"] <= 10 for row in outcomes)


def test_identical_action_sequences_have_identical_dynamics_across_reward_arms():
    scenarios = make_scenarios(8, 133)
    legacy = UAVBatch(FlatRadio(), 8, scenarios)
    fixed = UAVBatch(FlatRadio(), 8, scenarios, reward="fixed")
    rng = np.random.default_rng(9)
    for _ in range(12):
        controls = rng.uniform(-1, 1, (8, 2)); network = np.zeros(8, dtype=int)
        legacy.step(controls, network); fixed.step(controls, network)
        assert np.array_equal(legacy.pos, fixed.pos)
        assert np.array_equal(legacy.vel, fixed.vel)
        assert np.array_equal(legacy.buffer, fixed.buffer)
        assert np.array_equal(legacy.serving, fixed.serving)


def test_gae_does_not_leak_rewards_across_resets():
    rewards = np.array([[1.], [2.], [9.]], dtype=np.float32)
    values = np.zeros_like(rewards)
    done = np.array([[False], [True], [True]])
    _, returns = gae(rewards, values, done, np.array([100.]), 1., 1.)
    assert returns.ravel() == pytest.approx([3., 2., 9.])


def test_radio_lookup_uses_station_x_y_axes_and_stored_spacing(tmp_path):
    import h5py
    path = tmp_path / "radio.h5"
    expected = np.arange(18, dtype=np.int8).reshape(2, 3, 3) - 90
    with h5py.File(path, "w") as f:
        f["BS/operator_map"] = np.array([[1., 1.]])
        f["BS/id"] = np.array([11., 12.])
        f["BS/position"] = np.zeros((3, 2))
        f["grid/x"] = np.array([[0.], [2.], [4.]])
        f["grid/y"] = np.array([[0.], [3.], [6.]])
        f["measurements/rss_dBm"] = expected
    radio = RadioMap(path)
    actual = radio.query(np.array([[2., 6.], [4., 3.]]))
    assert np.array_equal(actual, np.array([expected[:, 1, 2], expected[:, 2, 1]]))
    assert actual.dtype == np.float32


def test_observed_outage_allows_emergency_handover_between_periodic_ticks():
    env = UAVBatch(FlatRadio(), 1, route())
    env.t[:] = 1
    env.serving[:] = 5
    class OutageRadio(FlatRadio):
        def query(self, positions):
            rss = super().query(positions); rss[:, 5] = -128
            return rss
    env.radio = OutageRadio()
    _, mask = env.observe()
    assert mask[0, 1]
    env.step(np.zeros((1, 2)), np.array([1]))
    assert env.serving[0] == 0


def test_training_updates_parameters_and_repeats_with_same_seed(tmp_path):
    from uav_joint_optimization.experiment_ppo import PPOConfig, train
    radio = FlatRadio(); radio.path = "synthetic_unit_test"; radio.stride = 1
    cfg = PPOConfig(environments=4, rollout=8, minibatch=16, epochs=2, steps=64, threads=1)
    env_cfg = replace(EnvironmentConfig(), horizon=10)
    scenarios = make_scenarios(8, 20)
    first = train(radio, scenarios, scenarios[:4], "fixed", True, 7, tmp_path / "first", cfg, env_cfg, 0)
    second = train(radio, scenarios, scenarios[:4], "fixed", True, 7, tmp_path / "second", cfg, env_cfg, 0)
    assert all(torch.equal(v, second.state_dict()[k]) for k,v in first.state_dict().items())
    torch.manual_seed(7)
    obs, _ = UAVBatch(radio, 4, scenarios, config=env_cfg).observe()
    initial = HybridPolicy(obs.shape[1], cfg.hidden)
    assert any(not torch.equal(v, initial.state_dict()[k]) for k,v in first.state_dict().items())
