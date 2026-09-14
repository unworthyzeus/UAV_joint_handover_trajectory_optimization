"""Behavioral checks of signal selection, state isolation and baseline identity."""
import numpy as np
import pytest

from uav_joint_optimization.connectivity_env import ConnectivityBatch, ConnectivityConfig
from uav_joint_optimization.connectivity_guard import guarded_action
from uav_joint_optimization.signal_guard import signal_guard_action


class Radio:
    limits = np.array([5000., 3500.], dtype=np.float32)
    positions = np.zeros((6, 2), dtype=np.float32)

    def query(self, positions):
        result = np.tile(np.array([-45, -50, -60, -70, -80, -128], dtype=np.float32), (len(positions), 1))
        result[:, 0] += np.clip((positions[:, 1]-1000)/2, -10, 10)
        return result


def environment():
    routes = [{'id': str(i), 'start': [1000., 1000.], 'goal': [1500., 1000.], 'load_phase': i} for i in range(2)]
    return ConnectivityBatch(Radio(), 2, routes, config=ConnectivityConfig())


def test_zero_allowance_matches_frozen_guard_over_complete_flights():
    env = environment()
    for _ in range(env.cfg.horizon):
        proposal = env.reference_motion()
        a = guarded_action(env, proposal, 5)
        b = signal_guard_action(env, proposal, 0)
        np.testing.assert_array_equal(a[0], b[0]); np.testing.assert_array_equal(a[1], b[1])
        env.step(*a)
        if env.done.all():
            break
    assert env.ever_success.all()


@pytest.mark.parametrize('allowance', [1, 3, 6])
def test_gradient_choice_improves_predicted_signal_within_service_and_progress_caps(allowance):
    env = environment()
    env.vel[:, 0] = 20.
    before = {k: v.copy() for k, v in env.__dict__.items() if isinstance(v, np.ndarray)}
    motion, network, d = signal_guard_action(env, env.reference_motion(), allowance, diagnostics=True)
    for k, v in before.items():
        np.testing.assert_array_equal(getattr(env, k), v)
    assert np.all(env.action_mask[env.rows, network]) and np.isfinite(motion).all()
    # The smallest allowance excludes the angled primitive at this speed.
    assert np.any(d['selected'] != d['baseline']) == (allowance >= 3)
    b, s, lanes = d['baseline'], d['selected'], env.rows
    assert np.all(d['snr'][s, lanes] >= d['snr'][b, lanes])
    if allowance >= 3:
        assert np.all(d['snr'][s, lanes] > d['snr'][b, lanes])
    assert np.all(d['score'][s, lanes] <= d['score'][b, lanes]+allowance)
    assert np.all(d['delay'][s, lanes] <= d['delay'][b, lanes])
    assert np.all(d['handovers'][s, lanes] <= d['handovers'][b, lanes])
    assert not d['failed'][s, lanes].any()


def test_near_goal_and_done_lanes_keep_baseline():
    env = environment(); env.goal[:] = [1020., 1000.]; env.done[1] = True
    a = guarded_action(env, env.reference_motion(), 5)
    b = signal_guard_action(env, env.reference_motion(), 6)
    np.testing.assert_array_equal(a[0], b[0]); np.testing.assert_array_equal(a[1], b[1])


def test_invalid_allowance_rejected():
    env = environment()
    with pytest.raises(ValueError):
        signal_guard_action(env, env.reference_motion(), 2)
