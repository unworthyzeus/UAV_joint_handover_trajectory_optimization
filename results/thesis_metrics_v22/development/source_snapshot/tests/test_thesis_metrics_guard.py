"""Source formulas, passive instrumentation and guarded action invariants."""
import numpy as np
import pytest

from uav_joint_optimization.connectivity_env import ConnectivityBatch, ConnectivityConfig
from uav_joint_optimization.connectivity_guard import guarded_action, strongest_feasible_network
from uav_joint_optimization.thesis_metrics import ThesisMetrics, radio_measurements, literal_energy_update


class Radio:
    limits = np.array([5000., 3500.], dtype=np.float32)
    positions = np.zeros((6, 2), dtype=np.float32)
    def query(self, positions):
        return np.tile(np.array([-40, -44, -48, -52, -56, -128], dtype=np.float32), (len(positions), 1))


def environment():
    routes = [{'id': 'unit', 'start': [1000., 1000.], 'goal': [1100., 1000.], 'load_phase': 0}]
    return ConnectivityBatch(Radio(), 1, routes, config=ConnectivityConfig())


def test_source_snr_and_neighbor_power_exclusion():
    snr, power, literal = radio_measurements(np.array([[-40., -40., -128.]]), np.array([0]))
    assert snr[0] == pytest.approx(63.41)
    assert power[0] == pytest.approx(.1)
    assert literal[0] == -168
    assert np.isnan(radio_measurements(np.array([[-128., -40.]]), np.array([0]))[0][0])


def test_literal_energy_is_not_physical_consumption():
    assert literal_energy_update(1000., 0.) == 1000.1
    assert np.all(literal_energy_update(1000., np.arange(26)) > 1000.)


@pytest.mark.parametrize('horizon', [3, 5, 8])
def test_guard_does_not_mutate_state_and_obeys_current_mask(horizon):
    env = environment()
    prior = {k: v.copy() for k, v in env.__dict__.items() if isinstance(v, np.ndarray)}
    motion, choice = guarded_action(env, env.reference_motion(), horizon)
    for k, value in prior.items():
        np.testing.assert_array_equal(getattr(env, k), value)
    assert env.action_mask[0, choice[0]]
    assert np.isfinite(motion).all()
    assert env.action_mask[0, strongest_feasible_network(env, motion)[0]]


def test_passive_metrics_preserve_episode_and_only_record_executed_steps():
    env = environment(); reference = environment(); metrics = ThesisMetrics(env)
    for _ in range(200):
        active = ~env.done.copy()
        motion, network = env.controller('straight_radio')
        _, _, _, _, completed = env.step(motion, network)
        _, _, _, _, baseline = reference.step(motion, network)
        metrics.record(active, completed)
        if completed:
            for key, value in baseline[0].items():
                assert completed[0][key] == value
            assert completed[0]['metric_samples'] == completed[0]['time_s']
            assert completed[0]['remaining_energy_kj'] == pytest.approx(100 - completed[0]['energy_proxy_j']/1000)
            assert completed[0]['snr_mean_db'] == pytest.approx(63.41)
            count = metrics.counts.copy()
            metrics.record(~env.done, [])
            np.testing.assert_array_equal(metrics.counts, count)
            break
    assert env.done.all()
