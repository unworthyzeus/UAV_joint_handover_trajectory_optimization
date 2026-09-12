"""Behavioral checks for strict thesis constraints and communication control."""
from dataclasses import replace

import numpy as np
import pytest
import torch

from uav_joint_optimization.connectivity_env import ConnectivityBatch, ConnectivityConfig
from uav_joint_optimization.connectivity_ppo import HybridPolicy


class FlatRadio:
    limits = np.array([5000., 3500.], dtype=np.float32)
    positions = np.zeros((6, 2), dtype=np.float32)
    values = [-40, -44, -48, -52, -56, -60]

    def query(self, positions):
        return np.tile(np.array(self.values, dtype=np.float32), (len(positions), 1))


def make_env(radio=None, **config):
    routes = [{"id": "unit", "start": [1000., 1000.], "goal": [1100., 1000.], "load_phase": 0}]
    config.setdefault("safety_filter", False)
    return ConnectivityBatch(radio or FlatRadio(), 1, routes, config=replace(ConnectivityConfig(), **config))


def test_rss_equality_is_allowed_and_any_lower_value_fails():
    class WeakRadio(FlatRadio):
        values = [-96] * 6
    env = make_env(WeakRadio(), offered_bps=0)
    _, _, _, done, _ = env.step(np.zeros((1, 2)), np.array([0]))
    assert not done[0]
    env.radio.values = [-97] * 6
    _, _, _, done, rows = env.step(np.zeros((1, 2)), np.array([0]))
    assert done[0] and not rows[0]["success"]
    assert rows[0]["outcome"] == "connectivity"
    assert rows[0]["outage_s"] == 1


def test_bad_initial_rss_cannot_be_erased_by_motion():
    class InitiallyWeak(FlatRadio):
        values = [-97] * 6
    env = make_env(InitiallyWeak(), offered_bps=0)
    env.radio.values = [-40] * 6
    _, _, _, done, rows = env.step(np.zeros((1, 2)), np.array([0]))
    assert done[0] and rows[0]["outcome"] == "connectivity"


def test_buffer_violation_overrides_arrival():
    env = make_env(offered_bps=1e12)
    env.pos[:] = env.goal
    env.observe()
    _, _, _, done, rows = env.step(np.zeros((1, 2)), np.array([0]))
    assert done[0] and rows[0]["arrival_at_endpoint"] and not rows[0]["success"]
    assert rows[0]["outcome"] == "buffer" and rows[0]["dropped_bits"] > 0


def test_user_did_not_request_empty_queue_as_an_arrival_condition():
    env = make_env()
    rate = env.radio_state()[3][0]
    env.cfg = replace(env.cfg, offered_bps=float(rate + 1000))
    env.pos[:] = env.goal
    env.observe()
    _, _, _, done, rows = env.step(np.zeros((1, 2)), np.array([0]))
    assert done[0] and rows[0]["success"] and rows[0]["final_buffer_bits"] > 0


def test_all_three_original_radio_costs_change_reward_without_one_second_plateau():
    env = make_env()
    base = env.communication_cost(np.array([2.]), np.array([1e-6]), np.array([0]))[0]
    assert env.communication_cost(np.array([3.]), np.array([1e-6]), np.array([0]))[0] > base
    assert env.communication_cost(np.array([2.]), np.array([2e-6]), np.array([0]))[0] > base
    assert env.communication_cost(np.array([2.]), np.array([1e-6]), np.array([1]))[0] > base


def test_masks_only_offer_free_resources_and_allow_stay():
    env = make_env()
    assert env.action_mask.shape == (1, 61) and env.action_mask[0, 0]
    for choice in np.flatnonzero(env.action_mask[0, 1:]) + 1:
        station, group = env.option_station[0, choice], env.option_rbg[0, choice]
        assert (group - (7 * station + env.phase[0])) % 12 >= 6
    policy = HybridPolicy(env.observe()[0].shape[1])
    obs, mask = env.observe()
    latent, choice, logp, _ = policy.action(torch.from_numpy(obs), torch.from_numpy(mask))
    score, _, _ = policy.score(torch.from_numpy(obs), torch.from_numpy(mask), latent, choice)
    assert mask[0, choice.item()] and torch.allclose(logp, score)


def test_all_option_radio_predictions_agree_with_executed_radio():
    env = make_env()
    rss, interference, rate = env.options_at(env.pos)
    for choice in np.flatnonzero(env.action_mask[0]):
        station = env.option_station[0, choice]
        group = env.option_rbg[0, choice]
        env.serving[0], env.rbg[0] = station, group
        actual_rss, actual_i, _, actual_rate = env.radio_state()
        assert actual_rss[0, station] == rss[0, choice]
        assert actual_i[0] == pytest.approx(interference[0, choice], rel=1e-5)
        assert actual_rate[0] == pytest.approx(rate[0, choice], rel=1e-5)


def test_predicted_motion_matches_execution_and_respects_limits():
    env = make_env()
    motion = np.array([[1., .4]])
    pos, vel = env.predict_motion(motion)
    env.step(motion, np.array([0]))
    assert np.array_equal(env.pos, pos) and np.array_equal(env.vel, vel)
    assert np.linalg.norm(env.vel) <= env.cfg.max_speed


@pytest.mark.parametrize("kind", ["straight_rss", "straight_radio", "joint_mpc"])
def test_references_complete_a_feasible_flat_map_mission(kind):
    env = make_env()
    for _ in range(env.cfg.horizon):
        motion, choice = env.controller(kind)
        _, _, _, done, rows = env.step(motion, choice)
        if done[0]:
            assert rows[0]["success"]
            assert rows[0]["minimum_rss_dbm"] >= -96
            assert rows[0]["dropped_bits"] == 0
            break
    else:
        pytest.fail("Controller did not terminate")


def test_reward_treatments_share_physics_and_constraint_termination():
    full, arrival = make_env(), make_env()
    arrival.objective = "arrival"
    for _ in range(8):
        motion, choice = full.controller("straight_radio")
        f = full.step(motion, choice)
        a = arrival.step(motion, choice)
        assert np.array_equal(full.pos, arrival.pos)
        assert np.array_equal(full.buffer, arrival.buffer)
        assert np.array_equal(f[3], a[3])
        assert np.all(f[2] <= a[2])


def test_filter_repairs_unsafe_association_without_changing_safe_motion():
    class DropAhead(FlatRadio):
        def query(self, positions):
            rss = super().query(positions)
            rss[positions[:, 0] > 1001, 1] = -128
            return rss
    env = make_env(DropAhead(), safety_filter=True)
    env.serving[0] = 1
    env.rbg[0] = (7 + 6) % 12
    env.observe()
    motion = np.array([[1., 0.]], dtype=np.float32)
    expected_pos, _ = env.predict_motion(motion)
    _, _, _, done, _ = env.step(motion, np.array([0]))
    assert not done[0] and np.array_equal(env.pos, expected_pos)
    assert env.serving[0] == 0 and env.network_interventions[0] == 1


def test_filter_never_turns_unavoidable_outage_into_success():
    class NoCoverage(FlatRadio):
        values = [-128] * 6
    env = make_env(NoCoverage(), safety_filter=True)
    env.pos[:] = env.goal
    env.observe()
    _, _, _, done, rows = env.step(np.zeros((1, 2)), np.array([0]))
    assert done[0] and not rows[0]["success"] and rows[0]["outcome"] == "connectivity"


def test_small_training_is_reproducible_and_changes_parameters(tmp_path):
    from uav_joint_optimization.connectivity_ppo import PPOConfig, train
    radio = FlatRadio()
    radio.path, radio.stride = "synthetic_unit_test", 1
    routes = make_env().scenarios
    cfg = PPOConfig(environments=4, rollout=8, minibatch=16, epochs=2, steps=64, threads=1)
    env_cfg = replace(ConnectivityConfig(), horizon=10)
    first = train(radio, routes, routes, "full", True, 7, tmp_path / "a", cfg, env_cfg, 0)
    second = train(radio, routes, routes, "full", True, 7, tmp_path / "b", cfg, env_cfg, 0)
    assert all(torch.equal(v, second.state_dict()[k]) for k, v in first.state_dict().items())
    torch.manual_seed(7)
    obs, _ = ConnectivityBatch(radio, 4, routes, config=env_cfg).observe()
    initial = HybridPolicy(obs.shape[1], cfg.hidden)
    assert any(not torch.equal(v, initial.state_dict()[k]) for k, v in first.state_dict().items())


def test_lookahead_does_not_mutate_real_state_and_completes():
    env = make_env(safety_filter=True)
    for _ in range(env.cfg.horizon):
        before = {k: v.copy() for k, v in env.__dict__.items() if isinstance(v, np.ndarray)}
        motion, choice = env.controller("joint_lookahead")
        assert all(np.array_equal(v, env.__dict__[k]) for k, v in before.items())
        assert env.action_mask[env.rows, choice].all()
        _, _, _, done, rows = env.step(motion, choice)
        if done[0]:
            assert rows[0]["success"]
            break
    else:
        pytest.fail("Lookahead did not complete")


def test_zero_residual_preserves_projected_reference_motion():
    env = make_env()
    reference_pos, reference_vel = env.predict_motion(env.reference_motion())
    pos, vel = env.predict_motion(env.decode_residual(np.zeros((1, 2))))
    assert np.allclose(pos, reference_pos) and np.allclose(vel, reference_vel)
