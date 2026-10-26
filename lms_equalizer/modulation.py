"""Simple BPSK, QPSK, and 16-QAM modulation helpers.

The bit mapping is deliberately written out so a new DSP student can follow it.
"""

from __future__ import annotations

import itertools
import numpy as np

SUPPORTED_MODULATIONS = ("bpsk", "qpsk", "16qam")


def bits_per_symbol(modulation: str) -> int:
    """Return the number of bits carried by one symbol."""
    modulation = modulation.lower()
    if modulation == "bpsk":
        return 1
    if modulation == "qpsk":
        return 2
    if modulation == "16qam":
        return 4
    raise ValueError(
        f"Unsupported modulation {modulation!r}. Choose from {SUPPORTED_MODULATIONS}."
    )


def _constellation_and_labels(modulation: str) -> tuple[np.ndarray, np.ndarray]:
    """Build the constellation points and the bit label belonging to each point."""
    modulation = modulation.lower()

    if modulation == "bpsk":
        points = np.array([1 + 0j, -1 + 0j], dtype=np.complex128)
        labels = np.array([[0], [1]], dtype=np.int8)
        return points, labels

    if modulation == "qpsk":
        labels = np.array(list(itertools.product([0, 1], repeat=2)), dtype=np.int8)
        # A zero bit selects +1 and a one bit selects -1 on that axis.
        real = 1.0 - 2.0 * labels[:, 0]
        imag = 1.0 - 2.0 * labels[:, 1]
        points = (real + 1j * imag) / np.sqrt(2.0)
        return points.astype(np.complex128), labels

    if modulation == "16qam":
        labels = np.array(list(itertools.product([0, 1], repeat=4)), dtype=np.int8)

        # Gray-like two-bit mapping: 00 -> +3, 01 -> +1,
        # 11 -> -1, 10 -> -3. Each axis is normalized by sqrt(10).
        axis_mapping = {(0, 0): 3.0, (0, 1): 1.0, (1, 1): -1.0, (1, 0): -3.0}
        real = np.array([axis_mapping[tuple(row[:2])] for row in labels])
        imag = np.array([axis_mapping[tuple(row[2:])] for row in labels])
        points = (real + 1j * imag) / np.sqrt(10.0)
        return points.astype(np.complex128), labels

    raise ValueError(
        f"Unsupported modulation {modulation!r}. Choose from {SUPPORTED_MODULATIONS}."
    )


def constellation_points(modulation: str) -> np.ndarray:
    """Return the ideal complex symbols for a modulation format."""
    points, _ = _constellation_and_labels(modulation)
    return points.copy()


def modulate_bits(bits: np.ndarray, modulation: str) -> np.ndarray:
    """Convert a 1-D array of zero/one bits into complex symbols."""
    bits = np.asarray(bits)
    if bits.ndim != 1:
        raise ValueError("bits must be a one-dimensional array")
    if not np.all(np.isin(bits, [0, 1])):
        raise ValueError("bits must contain only 0 and 1")

    modulation = modulation.lower()
    width = bits_per_symbol(modulation)
    if bits.size % width != 0:
        raise ValueError(
            f"{modulation} needs a multiple of {width} bits; got {bits.size}."
        )

    bit_groups = bits.astype(np.int8).reshape(-1, width)

    if modulation == "bpsk":
        # Bit 0 -> +1; bit 1 -> -1.
        return (1.0 - 2.0 * bit_groups[:, 0]).astype(np.complex128)

    if modulation == "qpsk":
        real = 1.0 - 2.0 * bit_groups[:, 0]
        imag = 1.0 - 2.0 * bit_groups[:, 1]
        return ((real + 1j * imag) / np.sqrt(2.0)).astype(np.complex128)

    axis_mapping = {(0, 0): 3.0, (0, 1): 1.0, (1, 1): -1.0, (1, 0): -3.0}
    real = np.array([axis_mapping[tuple(row[:2])] for row in bit_groups])
    imag = np.array([axis_mapping[tuple(row[2:])] for row in bit_groups])
    return ((real + 1j * imag) / np.sqrt(10.0)).astype(np.complex128)


def demodulate_symbols(symbols: np.ndarray, modulation: str) -> np.ndarray:
    """Make nearest-constellation decisions and return the corresponding bits.

    Nearest-point detection works for all three formats and is also the slicer
    needed for decision-directed LMS adaptation.
    """
    symbols = np.asarray(symbols, dtype=np.complex128)
    if symbols.ndim != 1:
        raise ValueError("symbols must be a one-dimensional array")

    points, labels = _constellation_and_labels(modulation.lower())
    if symbols.size == 0:
        return np.array([], dtype=np.int8)

    # Each received symbol is compared with every ideal constellation point.
    squared_distances = np.abs(symbols[:, None] - points[None, :]) ** 2
    nearest_indices = np.argmin(squared_distances, axis=1)
    return labels[nearest_indices].reshape(-1).astype(np.int8)


def slice_symbols(symbols: np.ndarray, modulation: str) -> np.ndarray:
    """Map complex samples to their nearest ideal constellation point."""
    symbols = np.asarray(symbols, dtype=np.complex128)
    points = constellation_points(modulation)
    if symbols.size == 0:
        return np.array([], dtype=np.complex128)
    nearest_indices = np.argmin(np.abs(symbols[:, None] - points[None, :]) ** 2, axis=1)
    return points[nearest_indices]
