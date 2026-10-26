"""A small, reproducible multipath + AWGN channel model."""

from __future__ import annotations

import numpy as np

DEFAULT_CHANNEL_TAPS = np.array(
    [0.90 + 0.00j, 0.35 + 0.15j, 0.15 - 0.10j], dtype=np.complex128
)


def apply_multipath_channel(
    transmitted_symbols: np.ndarray,
    channel_taps: np.ndarray | list[complex] = DEFAULT_CHANNEL_TAPS,
    snr_db: float | None = 20.0,
    rng: np.random.Generator | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Apply a causal FIR channel and optional complex AWGN.

    Returns
    -------
    received_symbols:
        Samples observed by the receiver (same length as the input).
    noiseless_output:
        Channel output before noise, useful for debugging and measurements.

    ``snr_db=None`` turns noise off, which is handy in unit tests.
    """
    transmitted_symbols = np.asarray(transmitted_symbols, dtype=np.complex128)
    channel_taps = np.asarray(channel_taps, dtype=np.complex128)

    if transmitted_symbols.ndim != 1:
        raise ValueError("transmitted_symbols must be one-dimensional")
    if channel_taps.ndim != 1 or channel_taps.size == 0:
        raise ValueError("channel_taps must be a non-empty one-dimensional array")
    if transmitted_symbols.size == 0:
        return transmitted_symbols.copy(), transmitted_symbols.copy()
    if snr_db is not None and not np.isfinite(snr_db):
        raise ValueError("snr_db must be a finite number or None")

    # np.convolve(..., 'full') includes the channel's tail. The simulator keeps
    # the original packet length, as a simple packet receiver usually would.
    noiseless_output = np.convolve(transmitted_symbols, channel_taps, mode="full")[
        : transmitted_symbols.size
    ]

    if snr_db is None:
        return noiseless_output.copy(), noiseless_output

    if rng is None:
        rng = np.random.default_rng()

    signal_power = float(np.mean(np.abs(noiseless_output) ** 2))
    noise_power = signal_power / (10.0 ** (snr_db / 10.0))
    # For complex noise, split the total variance equally between I and Q.
    noise = np.sqrt(noise_power / 2.0) * (
        rng.standard_normal(noiseless_output.size)
        + 1j * rng.standard_normal(noiseless_output.size)
    )
    return noiseless_output + noise, noiseless_output
