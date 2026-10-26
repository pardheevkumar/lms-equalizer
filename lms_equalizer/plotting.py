"""Plots and result files for the LMS equalizer experiment."""

from __future__ import annotations

import csv
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from .modulation import constellation_points
from .simulation import SimulationResult


def _moving_average(values: np.ndarray, window: int = 100) -> np.ndarray:
    if values.size == 0:
        return values
    window = max(1, min(window, values.size))
    return np.convolve(values, np.ones(window) / window, mode="valid")


def save_main_results(result: SimulationResult, output_dir: str | Path) -> None:
    """Write four clear figures and a machine-readable metrics JSON file."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1) Show how the distorted constellation changes after equalization.
    rng = np.random.default_rng(123)
    max_points = 1200
    if result.raw_test.size > max_points:
        chosen = np.sort(rng.choice(result.raw_test.size, max_points, replace=False))
        raw_plot = result.raw_test[chosen]
        equalized_plot = result.equalized_test[chosen]
    else:
        raw_plot = result.raw_test
        equalized_plot = result.equalized_test
    ideal = constellation_points(result.modulation)

    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5))
    axes[0].scatter(raw_plot.real, raw_plot.imag, s=9, alpha=0.45, label="Received")
    axes[0].set_title("Before equalization")
    axes[1].scatter(equalized_plot.real, equalized_plot.imag, s=9, alpha=0.45, label="Equalized")
    axes[1].scatter(ideal.real, ideal.imag, marker="x", s=65, label="Ideal symbols")
    axes[1].set_title("After LMS equalization")
    for axis in axes:
        axis.set_xlabel("In-phase (I)")
        axis.set_ylabel("Quadrature (Q)")
        axis.grid(True, alpha=0.25)
        axis.set_aspect("equal", adjustable="datalim")
        axis.legend(loc="best")
    fig.suptitle(f"{result.modulation.upper()} constellation, SNR = {result.snr_db:g} dB")
    fig.tight_layout()
    fig.savefig(output_dir / "constellation_comparison.png", dpi=160)
    plt.close(fig)

    # 2) Plot the falling training error. The moving average makes the trend clear.
    mse = _moving_average(np.asarray(result.training_mse), window=100)
    fig, axis = plt.subplots(figsize=(8, 4.5))
    if mse.size:
        axis.plot(10 * np.log10(np.maximum(mse, 1e-12)))
    axis.set_title("LMS training learning curve")
    axis.set_xlabel("Training update (moving-average index)")
    axis.set_ylabel("Mean-square error (dB)")
    axis.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(output_dir / "learning_curve.png", dpi=160)
    plt.close(fig)

    # 3) Compare the known transmitted symbols with the aligned receiver outputs.
    count = min(160, result.target_indices.size)
    target = result.transmitted[result.target_indices[:count]]
    raw = result.raw_test[:count]
    equalized = result.equalized_test[:count]
    fig, axis = plt.subplots(figsize=(10, 4.5))
    axis.plot(np.arange(count), target.real, label="Transmitted target (I)", linewidth=1.4)
    axis.plot(np.arange(count), raw.real, label="Received at target time (I)", alpha=0.7)
    axis.plot(np.arange(count), equalized.real, label="Equalizer output (I)", alpha=0.8)
    axis.set_title("Symbol recovery: first test symbols")
    axis.set_xlabel("Test symbol number")
    axis.set_ylabel("In-phase amplitude")
    axis.grid(True, alpha=0.25)
    axis.legend(loc="best")
    fig.tight_layout()
    fig.savefig(output_dir / "symbol_recovery.png", dpi=160)
    plt.close(fig)

    metrics = {
        "modulation": result.modulation,
        "snr_db": result.snr_db,
        "num_symbols": int(result.transmitted.size),
        "training_symbols": int(result.training_end),
        "num_taps": result.equalizer.num_taps,
        "step_size_mu": result.equalizer.step_size,
        "decision_delay": result.equalizer.decision_delay,
        "ber_before_equalization": result.ber_before,
        "ber_after_equalization": result.ber_after,
        "evm_before_equalization": result.evm_before,
        "evm_after_equalization": result.evm_after,
        "final_equalizer_weights": [
            {"real": float(weight.real), "imag": float(weight.imag)}
            for weight in result.equalizer.weights
        ],
    }
    (output_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")


def save_snr_sweep(rows: list[dict[str, float]], output_dir: str | Path) -> None:
    """Save SNR sweep measurements and plot BER versus SNR."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    if not rows:
        return

    csv_path = output_dir / "snr_sweep.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    snr = np.array([row["snr_db"] for row in rows])
    ber_before = np.array([row["ber_before"] for row in rows])
    ber_after = np.array([row["ber_after"] for row in rows])
    # A semilog plot cannot display exact zeros. Use half an error per measured
    # test bit as each point's plotting floor, without changing stored BER values.
    bit_counts = np.array([row["num_test_bits"] for row in rows], dtype=float)
    plotting_floor = 0.5 / bit_counts
    fig, axis = plt.subplots(figsize=(7.5, 4.5))
    axis.semilogy(snr, np.maximum(ber_before, plotting_floor), "o-", label="Without equalizer")
    axis.semilogy(snr, np.maximum(ber_after, plotting_floor), "s-", label="With LMS equalizer")
    axis.set_title("BER versus SNR")
    axis.set_xlabel("SNR (dB)")
    axis.set_ylabel("Bit error rate (BER)")
    axis.grid(True, which="both", alpha=0.3)
    axis.legend(loc="best")
    fig.tight_layout()
    fig.savefig(output_dir / "ber_vs_snr.png", dpi=160)
    plt.close(fig)
