"""End-to-end link simulation used by the command-line runner."""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from .channel import DEFAULT_CHANNEL_TAPS, apply_multipath_channel
from .equalizer import LMSLinearEqualizer
from .modulation import (
    bits_per_symbol,
    constellation_points,
    demodulate_symbols,
    modulate_bits,
)


@dataclass
class SimulationResult:
    modulation: str
    snr_db: float
    bits: np.ndarray
    transmitted: np.ndarray
    received: np.ndarray
    noiseless_received: np.ndarray
    equalizer: LMSLinearEqualizer
    training_end: int
    training_mse: np.ndarray
    sample_indices: np.ndarray
    target_indices: np.ndarray
    equalized_test: np.ndarray
    raw_test: np.ndarray
    ber_before: float
    ber_after: float
    evm_before: float
    evm_after: float


def bit_error_rate(reference_bits: np.ndarray, detected_bits: np.ndarray) -> float:
    """Calculate the fraction of bits that were detected incorrectly."""
    reference_bits = np.asarray(reference_bits, dtype=np.int8)
    detected_bits = np.asarray(detected_bits, dtype=np.int8)
    if reference_bits.shape != detected_bits.shape:
        raise ValueError("reference_bits and detected_bits must have the same shape")
    if reference_bits.size == 0:
        return float("nan")
    return float(np.mean(reference_bits != detected_bits))


def normalized_evm(reference: np.ndarray, estimate: np.ndarray) -> float:
    """Return normalized RMS error-vector magnitude (lower is better)."""
    reference = np.asarray(reference, dtype=np.complex128)
    estimate = np.asarray(estimate, dtype=np.complex128)
    if reference.shape != estimate.shape:
        raise ValueError("reference and estimate must have the same shape")
    if reference.size == 0:
        return float("nan")
    reference_power = float(np.mean(np.abs(reference) ** 2))
    if reference_power == 0:
        return float("nan")
    return float(np.sqrt(np.mean(np.abs(estimate - reference) ** 2) / reference_power))


def run_simulation(
    modulation: str = "qpsk",
    snr_db: float = 20.0,
    num_symbols: int = 12000,
    num_taps: int = 9,
    step_size: float = 0.01,
    train_fraction: float = 0.60,
    decision_delay: int | None = None,
    decision_directed: bool = False,
    seed: int = 7,
    channel_taps: np.ndarray | list[complex] = DEFAULT_CHANNEL_TAPS,
) -> SimulationResult:
    """Create symbols, pass them through the channel, train, and measure BER."""
    modulation = modulation.lower()
    bps = bits_per_symbol(modulation)  # Also validates modulation name.
    if not isinstance(num_symbols, int) or num_symbols < 100:
        raise ValueError("num_symbols must be an integer of at least 100")
    if not 0.20 <= train_fraction <= 0.90:
        raise ValueError("train_fraction must be between 0.20 and 0.90")
    if not np.isfinite(snr_db):
        raise ValueError("snr_db must be finite")

    rng = np.random.default_rng(seed)
    bits = rng.integers(0, 2, size=num_symbols * bps, dtype=np.int8)
    transmitted = modulate_bits(bits, modulation)
    received, noiseless_received = apply_multipath_channel(
        transmitted, channel_taps=channel_taps, snr_db=snr_db, rng=rng
    )

    training_end = int(num_symbols * train_fraction)
    equalizer = LMSLinearEqualizer(
        num_taps=num_taps,
        step_size=step_size,
        decision_delay=decision_delay,
    )
    if training_end <= max(equalizer.num_taps - 1, equalizer.decision_delay):
        raise ValueError(
            "The training region is too short for this tap count and decision delay. "
            "Increase --num-symbols or --train-fraction, or reduce --num-taps."
        )
    training_mse = equalizer.train(received, transmitted, training_end=training_end)

    # Evaluate only symbols whose target is at or after the training boundary.
    # This avoids scoring any target symbol that was used to train the filter.
    test_start = max(training_end + equalizer.decision_delay,
                     equalizer.num_taps - 1,
                     equalizer.decision_delay)

    if decision_directed:
        equalized_test, sample_indices = equalizer.decision_directed_adapt(
            received,
            constellation=constellation_points(modulation),
            start_sample=test_start,
        )
    else:
        equalized_test, sample_indices = equalizer.equalize(
            received, start_sample=test_start
        )

    target_indices = sample_indices - equalizer.decision_delay
    if target_indices.size == 0:
        raise ValueError("No test symbols remain; increase num_symbols or reduce training")

    # A fair un-equalized baseline uses the received sample at the same symbol
    # time as the target. The LMS output may use a wider window and decision delay.
    raw_test = received[target_indices]
    reference_bits = bits.reshape(num_symbols, bps)[target_indices].reshape(-1)
    detected_before = demodulate_symbols(raw_test, modulation)
    detected_after = demodulate_symbols(equalized_test, modulation)

    reference_symbols = transmitted[target_indices]
    return SimulationResult(
        modulation=modulation,
        snr_db=float(snr_db),
        bits=bits,
        transmitted=transmitted,
        received=received,
        noiseless_received=noiseless_received,
        equalizer=equalizer,
        training_end=training_end,
        training_mse=training_mse,
        sample_indices=sample_indices,
        target_indices=target_indices,
        equalized_test=equalized_test,
        raw_test=raw_test,
        ber_before=bit_error_rate(reference_bits, detected_before),
        ber_after=bit_error_rate(reference_bits, detected_after),
        evm_before=normalized_evm(reference_symbols, raw_test),
        evm_after=normalized_evm(reference_symbols, equalized_test),
    )


def run_snr_sweep(
    snr_values: list[float] | np.ndarray,
    modulation: str = "qpsk",
    num_symbols: int = 7000,
    num_taps: int = 9,
    step_size: float = 0.01,
    train_fraction: float = 0.60,
    decision_delay: int | None = None,
    seed: int = 100,
) -> list[dict[str, float]]:
    """Repeat the experiment across SNR values for a BER-performance plot."""
    rows: list[dict[str, float]] = []
    for index, snr_db in enumerate(snr_values):
        result = run_simulation(
            modulation=modulation,
            snr_db=float(snr_db),
            num_symbols=num_symbols,
            num_taps=num_taps,
            step_size=step_size,
            train_fraction=train_fraction,
            decision_delay=decision_delay,
            decision_directed=False,
            seed=seed + index,
        )
        rows.append(
            {
                "snr_db": float(snr_db),
                "ber_before": result.ber_before,
                "ber_after": result.ber_after,
                "evm_before": result.evm_before,
                "evm_after": result.evm_after,
                "num_test_bits": int(result.target_indices.size * bits_per_symbol(modulation)),
            }
        )
    return rows
