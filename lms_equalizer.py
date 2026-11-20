"""Educational, symbol-spaced, training-mode complex LMS FIR equalizer.

Only NumPy is required. Works with real BPSK and complex QPSK.
The equalizer is trained on known symbols, then its weights are frozen for
out-of-sample BER/EVM testing (no ground-truth leakage into test adaptation).
"""

from dataclasses import dataclass
from typing import Optional
import numpy as np

CHANNELS = {
    "mild": np.array([0.90, 0.65, -0.35], dtype=float),
    "severe": np.array([0.65, 0.90, -0.55, 0.30], dtype=float),
    "flat": np.array([1.00], dtype=float),
}


def modulate(bits, scheme="BPSK"):
    """Map bit array to unit-average-energy BPSK or Gray-like quadrant QPSK.

    QPSK maps consecutive bits independently to I and Q signs; its nearest
    quadrant hard decision preserves the original bit ordering.
    """
    bits = np.asarray(bits, dtype=np.int8)
    scheme = scheme.upper()
    if np.any((bits != 0) & (bits != 1)):
        raise ValueError("bits must contain only zeros and ones")
    if scheme == "BPSK":
        return (1 - 2 * bits).astype(float)
    if scheme == "QPSK":
        if len(bits) % 2:
            raise ValueError("QPSK requires an even number of bits")
        return ((1 - 2 * bits[0::2]) + 1j * (1 - 2 * bits[1::2])) / np.sqrt(2)
    raise ValueError("scheme must be 'BPSK' or 'QPSK'")


def demodulate(symbols, scheme="BPSK"):
    """Hard-decision bits for coherent, phase-aligned BPSK or QPSK."""
    symbols = np.asarray(symbols)
    scheme = scheme.upper()
    if scheme == "BPSK":
        return (np.real(symbols) < 0).astype(np.int8)
    if scheme == "QPSK":
        bits = np.empty(2 * len(symbols), dtype=np.int8)
        bits[0::2] = (np.real(symbols) < 0).astype(np.int8)
        bits[1::2] = (np.imag(symbols) < 0).astype(np.int8)
        return bits
    raise ValueError("scheme must be 'BPSK' or 'QPSK'")


def add_awgn(clean_signal, snr_db, rng):
    """Return signal + complex/real AWGN at measured receive signal-power SNR."""
    x = np.asarray(clean_signal)
    noise_power = np.mean(np.abs(x) ** 2) / (10 ** (snr_db / 10))
    if np.iscomplexobj(x):
        noise = np.sqrt(noise_power / 2) * (
            rng.standard_normal(len(x)) + 1j * rng.standard_normal(len(x))
        )
    else:
        noise = np.sqrt(noise_power) * rng.standard_normal(len(x))
    return x + noise


@dataclass
class LMSOutput:
    output: np.ndarray
    error: np.ndarray
    weights: np.ndarray
    weights_history: Optional[np.ndarray]


def lms_equalizer(received, desired, mu=0.018, num_taps=9,
                  train_stop=None, track_weights=False):
    r"""Train an LMS equalizer, optionally freezing weights after train_stop.

    Define x[n] = [r[n], r[n-1], ..., r[n-M+1]]^T,
    y[n] = w[n]^H x[n], e[n] = d[n] - y[n],
    w[n+1] = w[n] + mu * x[n] * conj(e[n]).

    Samples n < M-1 have no full input window; their output/error are zero.
    During n >= train_stop, desired is used ONLY to compute diagnostic error;
    weights are not adapted. Avoid using diagnostic test error as receiver data.
    """
    r, d = np.asarray(received), np.asarray(desired)
    if r.ndim != 1 or d.ndim != 1 or len(r) != len(d):
        raise ValueError("received and desired must be matching 1-D arrays")
    if not 1 <= num_taps <= len(r):
        raise ValueError("num_taps must be between 1 and the signal length")
    if not (np.isfinite(mu) and mu > 0):
        raise ValueError("mu must be a finite positive number")
    if train_stop is None:
        train_stop = len(r)
    if not num_taps <= train_stop <= len(r):
        raise ValueError("train_stop must be from num_taps through signal length")
    dtype = np.result_type(r.dtype, d.dtype, np.float64)
    weights = np.zeros(num_taps, dtype=dtype)
    out = np.zeros(len(r), dtype=dtype)
    err = np.zeros(len(r), dtype=dtype)
    history = np.zeros((train_stop, num_taps), dtype=dtype) if track_weights else None

    for n in range(num_taps - 1, len(r)):
        x = r[n - num_taps + 1 : n + 1][::-1]
        out[n] = np.vdot(weights, x)  # conjugate(w) dot x
        err[n] = d[n] - out[n]
        if n < train_stop:
            weights += mu * x * np.conj(err[n])
            if history is not None:
                history[n] = weights
    return LMSOutput(out, err, weights.copy(), history)


@dataclass
class Experiment:
    modulation: str
    snr_db: float
    mu: float
    num_taps: int
    delay: int
    train_stop: int
    channel: np.ndarray
    symbols: np.ndarray
    received: np.ndarray
    desired: np.ndarray
    lms: LMSOutput
    test_indices: np.ndarray
    raw_ber: float
    equalized_ber: float
    raw_evm: float
    equalized_evm: float


def rms_evm(observed, reference):
    """RMS error vector magnitude, normalized by reference RMS amplitude."""
    return float(np.sqrt(np.mean(np.abs(observed - reference) ** 2) /
                         np.mean(np.abs(reference) ** 2)))


def simulate(modulation="BPSK", snr_db=10.0, mu=0.018, num_taps=9,
             delay=2, n_train=2500, n_test=9000, channel="mild",
             seed=2026, track_weights=False):
    """Reproducible symbol-rate baseband link, training-only LMS, held-out test.

    The reference is s[n-delay], so the equalizer has a causal decision delay.
    We compare to the raw channel output r[k] for the SAME reference symbol k,
    and separately score held-out equalizer output y[k+delay].
    """
    modulation = modulation.upper()
    if delay < 0 or delay >= num_taps:
        raise ValueError("delay must satisfy 0 <= delay < num_taps")
    if n_train <= num_taps or n_test < 1:
        raise ValueError("need a training interval longer than taps and test symbols")
    channel_ir = CHANNELS[channel].copy() if isinstance(channel, str) else np.asarray(channel)
    if channel_ir.ndim != 1 or len(channel_ir) < 1:
        raise ValueError("channel must be a nonempty impulse response")
    rng = np.random.default_rng(seed)
    n_symbols = n_train + n_test + delay
    bits = rng.integers(0, 2, size=n_symbols * (2 if modulation == "QPSK" else 1))
    s = modulate(bits, modulation)
    clean = np.convolve(s, channel_ir, mode="full")[:n_symbols]
    rx = add_awgn(clean, snr_db, rng)
    desired = np.zeros(n_symbols, dtype=s.dtype)
    if delay:
        desired[delay:] = s[:-delay]
    else:
        desired[:] = s
    lms = lms_equalizer(rx, desired, mu=mu, num_taps=num_taps,
                        train_stop=n_train, track_weights=track_weights)
    idx = np.arange(n_train + delay, n_symbols, dtype=int)
    symidx = idx - delay
    truth = s[symidx]
    raw = rx[symidx]
    eq = lms.output[idx]
    raw_ber = float(np.mean(demodulate(raw, modulation) != demodulate(truth, modulation)))
    eq_ber = float(np.mean(demodulate(eq, modulation) != demodulate(truth, modulation)))
    return Experiment(modulation, snr_db, mu, num_taps, delay,
                      n_train, channel_ir, s, rx, desired, lms, idx,
                      raw_ber, eq_ber, rms_evm(raw, truth), rms_evm(eq, truth))
