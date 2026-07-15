"""Unit explicit radio calculations for environment validation."""

from __future__ import annotations

import math
from collections.abc import Iterable


def dbm_to_mw(power_dbm: float) -> float:
    """Convert power in dBm to milliwatts."""

    if not math.isfinite(power_dbm):
        raise ValueError("power_dbm must be finite")
    return 10.0 ** (power_dbm / 10.0)


def mw_to_dbm(power_mw: float) -> float:
    """Convert strictly positive power in milliwatts to dBm."""

    if not math.isfinite(power_mw) or power_mw <= 0.0:
        raise ValueError("power_mw must be finite and positive")
    return 10.0 * math.log10(power_mw)


def sum_powers_dbm(powers_dbm: Iterable[float]) -> float:
    """Sum logarithmic powers through the linear milliwatt domain."""

    powers = tuple(powers_dbm)
    if not powers:
        raise ValueError("at least one power is required")
    return mw_to_dbm(sum(dbm_to_mw(value) for value in powers))


def sinr_linear(
    signal_dbm: float,
    interference_dbm: Iterable[float],
    noise_dbm: float,
) -> float:
    """Return linear SINR from signal, interferer, and noise powers in dBm."""

    denominator_mw = dbm_to_mw(noise_dbm) + sum(
        dbm_to_mw(value) for value in interference_dbm
    )
    return dbm_to_mw(signal_dbm) / denominator_mw


def sinr_db(
    signal_dbm: float,
    interference_dbm: Iterable[float],
    noise_dbm: float,
) -> float:
    """Return SINR in dB."""

    ratio = sinr_linear(signal_dbm, interference_dbm, noise_dbm)
    return 10.0 * math.log10(ratio)


def shannon_rate_bps(bandwidth_hz: float, sinr_db_value: float) -> float:
    """Return ideal capacity B log2(1 + SINR) in bits per second."""

    if not math.isfinite(bandwidth_hz) or bandwidth_hz <= 0.0:
        raise ValueError("bandwidth_hz must be finite and positive")
    if not math.isfinite(sinr_db_value):
        raise ValueError("sinr_db_value must be finite")
    ratio = 10.0 ** (sinr_db_value / 10.0)
    return bandwidth_hz * math.log2(1.0 + ratio)

