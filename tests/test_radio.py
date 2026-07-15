import math

import pytest

from uav_joint_optimization.radio import (
    dbm_to_mw,
    mw_to_dbm,
    shannon_rate_bps,
    sinr_db,
    sum_powers_dbm,
)


def test_dbm_round_trip() -> None:
    assert dbm_to_mw(0.0) == pytest.approx(1.0)
    assert mw_to_dbm(dbm_to_mw(-96.0)) == pytest.approx(-96.0)


def test_powers_are_summed_in_linear_units() -> None:
    assert sum_powers_dbm([0.0, 0.0]) == pytest.approx(3.0102999566)


def test_sinr_includes_noise_and_interference() -> None:
    value = sinr_db(signal_dbm=0.0, interference_dbm=[-10.0], noise_dbm=-10.0)
    assert value == pytest.approx(10.0 * math.log10(5.0))


def test_shannon_rate_uses_linear_sinr_and_multiplies_bandwidth() -> None:
    assert shannon_rate_bps(1.0, 0.0) == pytest.approx(1.0)
    assert shannon_rate_bps(1_000_000.0, 10.0) == pytest.approx(
        1_000_000.0 * math.log2(11.0)
    )


def test_invalid_power_and_bandwidth_are_rejected() -> None:
    with pytest.raises(ValueError):
        mw_to_dbm(0.0)
    with pytest.raises(ValueError):
        shannon_rate_bps(0.0, 0.0)

