"""Generate all reproducible LMS equalizer figures, tables, and JSON metrics.

Run from project root: python experiments.py
The outputs are not hand-drawn: all figures are computed from the simulator.
"""
from pathlib import Path
import csv
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from lms_equalizer import simulate

ROOT = Path(__file__).resolve().parent
FIGS = ROOT / "results" / "simulation_graphs"
FIGS.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.alpha": 0.23,
    "figure.dpi": 120, "savefig.dpi": 170,
    "axes.titleweight": "semibold", "axes.labelsize": 10,
    "legend.fontsize": 9,
})
BLUE, ORANGE, GREEN, PURPLE = "#2563eb", "#e76f51", "#188768", "#805ad5"


def save(fig, filename):
    fig.savefig(FIGS / filename, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def moving_average(arr, window=100):
    x = np.asarray(arr, dtype=float)
    if len(x) < window:
        return x
    return np.convolve(x, np.ones(window)/window, mode="valid")


def training_mse(ex):
    e = ex.lms.error
    return np.abs(e[ex.num_taps - 1 : ex.train_stop]) ** 2


def metrics(ex):
    return {"scheme": ex.modulation, "SNR_dB": float(ex.snr_db),
            "step_size": float(ex.mu), "num_taps": ex.num_taps,
            "decision_delay": ex.delay, "channel": list(map(float, np.real(ex.channel))),
            "train_symbols": ex.train_stop,
            "test_symbols": len(ex.test_indices),
            "raw_BER": float(ex.raw_ber), "LMS_BER": float(ex.equalized_ber),
            "raw_EVM_rms": float(ex.raw_evm), "LMS_EVM_rms": float(ex.equalized_evm),
            "last_500_training_MSE": float(np.mean(training_mse(ex)[-500:]))}


def generate():
    base = {scheme: simulate(scheme, snr_db=12, seed=2026,
                             track_weights=True) for scheme in ("BPSK", "QPSK")}
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.0), constrained_layout=True)
    for ax, scheme, color in zip(axes, ("BPSK", "QPSK"), (BLUE, PURPLE)):
        ex = base[scheme]
        mse = moving_average(training_mse(ex), 90)
        x = np.arange(ex.num_taps - 1 + 89, ex.num_taps - 1 + 89 + len(mse))
        ax.semilogy(x, np.maximum(mse, 1e-6), color=color, linewidth=2)
        ax.set(title=f"{scheme}: LMS adaptation", xlabel="Training iteration (sample index)",
               ylabel="90-sample running MSE")
    fig.suptitle("Training error decreases and approaches a noise/ISI floor", fontsize=13)
    save(fig, "01_mse_convergence.png")

    ex = base["QPSK"]
    truth_indices = ex.test_indices - ex.delay
    sample = np.arange(0, min(1600, len(truth_indices)))
    r = ex.received[truth_indices[sample]]
    y = ex.lms.output[ex.test_indices[sample]]
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.8), constrained_layout=True)
    for ax, z, title, color in [(axes[0], r, "Without equalization", ORANGE),
                                 (axes[1], y, "With trained LMS equalization", BLUE)]:
        ax.scatter(z.real, z.imag, s=9, alpha=0.34, color=color, edgecolors="none", rasterized=True)
        targets = np.array([1+1j, 1-1j, -1+1j, -1-1j])/np.sqrt(2)
        ax.scatter(targets.real, targets.imag, marker="x", c="black", s=80,
                   linewidths=1.5, label="Ideal QPSK symbols")
        ax.set(xlabel="In-phase (I)", ylabel="Quadrature (Q)", title=title,
               xlim=(-2.7,2.7), ylim=(-2.7,2.7), aspect="equal")
        ax.legend(loc="lower right", frameon=True, fontsize=8)
    fig.suptitle("QPSK constellations at 12 dB receive SNR", fontsize=13)
    save(fig, "02_qpsk_constellation.png")

    ex = base["BPSK"]
    sel = np.arange(ex.train_stop + 180, ex.train_stop + 230)
    truth = ex.desired[sel]
    fig, ax = plt.subplots(figsize=(10.5, 3.7), constrained_layout=True)
    ax.step(np.arange(len(sel)), truth, where="mid", label="Desired symbols", color="#1f2937", lw=1.8)
    ax.plot(ex.received[sel - ex.delay], ".-", label="Raw received (aligned)", color=ORANGE, alpha=0.67)
    ax.plot(ex.lms.output[sel], "o-", label="LMS output", color=BLUE, alpha=0.85, ms=3)
    ax.set(xlabel="Test-symbol offset", ylabel="Amplitude", title="BPSK: transmitted reference, raw received, and equalized output")
    ax.legend(loc="upper right", ncol=3, fontsize=8)
    save(fig, "03_bpsk_waveforms.png")

    fig, axes = plt.subplots(1, 2, figsize=(11, 3.9), constrained_layout=True)
    mu_values = [0.004, 0.012, 0.03, 0.07]
    mu_results = []
    for mu, col in zip(mu_values, (GREEN, BLUE, PURPLE, ORANGE)):
        ex = simulate("BPSK", snr_db=12, mu=mu, seed=2026)
        err = moving_average(training_mse(ex), 90)
        indices = np.arange(ex.num_taps - 1 + 89, ex.num_taps - 1 + 89 + len(err))
        axes[0].semilogy(indices, err, label=f"$\\mu={mu}$", color=col, lw=1.8)
        mu_results.append({"mu":mu, "test_BER":ex.equalized_ber, "test_EVM":ex.equalized_evm})
    axes[0].set(title="Learning speed versus residual training error", xlabel="Training sample index",
                ylabel="90-sample running MSE")
    axes[0].legend(fontsize=8)
    axes[1].plot(mu_values, [r["test_BER"] for r in mu_results], "o-", color=PURPLE, lw=2, ms=7)
    axes[1].set(title="Held-out BPSK BER versus step size", xlabel="Step size $\\mu$", ylabel="BER")
    fig.suptitle("Step size controls adaptation and steady-state behavior (12 dB)", fontsize=13)
    save(fig, "04_stepsize_sweep.png")

    taps = [3, 5, 9, 13, 17]
    tap_results = []
    for count in taps:
        ex = simulate("BPSK", snr_db=12, num_taps=count, delay=2, seed=2026)
        tap_results.append({"num_taps":count, "test_BER":ex.equalized_ber,
                            "test_EVM":ex.equalized_evm})
    fig, axes = plt.subplots(1, 2, figsize=(10.2, 3.65), constrained_layout=True)
    axes[0].plot(taps, [r["test_BER"] for r in tap_results], "o-", color=BLUE, lw=2)
    axes[0].set(xlabel="Number of LMS FIR taps", ylabel="Test BER", title="BER versus filter length")
    axes[1].plot(taps, [100*r["test_EVM"] for r in tap_results], "s-", color=PURPLE, lw=2)
    axes[1].set(xlabel="Number of LMS FIR taps", ylabel="RMS EVM (%)", title="EVM versus filter length")
    fig.suptitle("More taps help until estimation/adaptation cost dominates", fontsize=13)
    save(fig, "05_filter_length_sweep.png")

    snr_values = [0, 4, 8, 12, 16, 20]
    repetitions = [2026, 2027, 2028]
    ber_data = []
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4), constrained_layout=True)
    for ax, scheme in zip(axes, ("BPSK", "QPSK")):
        raw_means, eq_means = [], []
        for snr in snr_values:
            this = [simulate(scheme, snr_db=snr, n_train=2500, n_test=9000,
                             seed=s) for s in repetitions]
            raw = np.mean([r.raw_ber for r in this])
            eq = np.mean([r.equalized_ber for r in this])
            raw_means.append(raw)
            eq_means.append(eq)
            ber_data.append({"scheme":scheme, "snr_db":snr,
                             "raw_ber_mean_3_seeds":float(raw),
                             "lms_ber_mean_3_seeds":float(eq),
                             "n_seeds":3, "n_symbols_per_seed":len(this[0].test_indices),
                             "bits_per_symbol":2 if scheme=="QPSK" else 1})
        ax.semilogy(snr_values, raw_means, "s--", color=ORANGE, label="No equalizer", linewidth=1.9)
        ax.semilogy(snr_values, eq_means, "o-", color=BLUE, label="Trained LMS", linewidth=2.1)
        ax.set(xlabel="Receive SNR (dB)", ylabel="Held-out BER", title=scheme,
               xticks=snr_values, ylim=(3e-4, 0.5))
        ax.legend(loc="lower left")
    fig.suptitle("BER versus SNR (three independent deterministic trials per point)", fontsize=13)
    save(fig, "06_ber_vs_snr.png")

    fig, axes = plt.subplots(1, 2, figsize=(10.3, 4), constrained_layout=True)
    for ax, scheme in zip(axes, ("BPSK", "QPSK")):
        ex = base[scheme]
        h = ex.channel
        q = np.conjugate(ex.lms.weights)
        effective = np.convolve(h, q)
        ix = np.arange(len(effective))
        ax.stem(ix, np.abs(effective), linefmt=BLUE, markerfmt="o", basefmt=" ")
        ax.axvline(ex.delay, color=ORANGE, lw=1.6, linestyle="--", label="Desired decision delay")
        ax.set(xlabel="Combined channel/equalizer tap index", ylabel="Tap magnitude",
               title=f"{scheme}: effective impulse response", xticks=ix)
        ax.legend(loc="upper right", fontsize=8)
    fig.suptitle("Combined FIR response: $h * \\overline{w}$ (after training)", fontsize=13)
    save(fig, "07_effective_impulse_response.png")

    fig, ax = plt.subplots(figsize=(9.8, 3.9), constrained_layout=True)
    ex = base["BPSK"]
    history = ex.lms.weights_history
    for k in range(min(7, ex.num_taps)):
        ax.plot(np.real(history[ex.num_taps - 1 :, k]), lw=1.1, label=f"tap {k}")
    ax.set(xlabel="Training iterations", ylabel="Real coefficient value",
           title="BPSK LMS coefficient trajectories (first seven FIR taps)")
    ax.legend(loc="upper right", ncol=2, fontsize=8)
    save(fig, "08_coefficient_trajectories.png")

    channel_data = []
    for scheme in ["BPSK","QPSK"]:
        for channel in ["flat","mild","severe"]:
            ex = simulate(scheme, snr_db=12, channel=channel)
            channel_data.append({"scheme":scheme, "channel":channel,
                                 "raw_BER":ex.raw_ber, "LMS_BER":ex.equalized_ber,
                                 "raw_EVM":ex.raw_evm, "LMS_EVM":ex.equalized_evm})
    fig, ax = plt.subplots(figsize=(10, 3.8), constrained_layout=True)
    positions = np.arange(len(channel_data))
    w = 0.37
    ax.bar(positions-w/2, [r["raw_BER"] for r in channel_data], w,
           label="Raw received", color=ORANGE)
    ax.bar(positions+w/2, [r["LMS_BER"] for r in channel_data], w,
           label="After LMS", color=BLUE)
    ax.set(xticks=positions, xticklabels=[f"{r['scheme']}\n{r['channel']}" for r in channel_data],
           ylabel="Test BER", title="Channel sensitivity at 12 dB SNR")
    ax.legend()
    save(fig, "09_channel_comparison.png")

    result = {"configuration":{
        "description":"Symbol-rate FIR model; unit-power BPSK/QPSK; measured signal-power AWGN; training-only LMS followed by frozen-weight test",
        "main_snr_db":12, "num_taps":9, "decision_delay":2, "mu":0.018,
        "training_samples":2500, "test_samples":9000,
        "channel_irs":{k:v.tolist() for k,v in __import__('lms_equalizer').CHANNELS.items()},
        "random_seeds_for_snr":repetitions,
        "baseline":"Unequalized r[k] vs true symbol s[k]; LMS y[k+delay] vs s[k]"},
        "main_experiments":{k:metrics(v) for k,v in base.items()},
        "step_size_sweep":mu_results,
        "filter_length_sweep":tap_results,
        "ber_vs_snr":ber_data,
        "channel_sweep":channel_data}
    with open(ROOT / "results" / "metrics.json", "w", encoding="utf8") as f:
        json.dump(result, f, indent=2)
    with open(ROOT / "results" / "ber_vs_snr.csv", "w", newline="", encoding="utf8") as f:
        writer = csv.DictWriter(f, fieldnames=list(ber_data[0]))
        writer.writeheader(); writer.writerows(ber_data)
    print("Wrote 9 plots and metrics files to", ROOT / "results")
    for scheme, ex in base.items():
        print(f"{scheme}: BER raw {ex.raw_ber:.5f} -> LMS {ex.equalized_ber:.5f}; "
              f"EVM raw {ex.raw_evm:.3f} -> LMS {ex.equalized_evm:.3f}")
    return result


if __name__ == "__main__":
    generate()
