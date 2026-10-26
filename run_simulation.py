"""Run the LMS equalizer experiment from the terminal."""

from __future__ import annotations

import argparse
from pathlib import Path
import json

from lms_equalizer.plotting import save_main_results, save_snr_sweep
from lms_equalizer.simulation import run_simulation, run_snr_sweep


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Simulate an LMS linear equalizer for a digital communication link."
    )
    parser.add_argument("--modulation", choices=["bpsk", "qpsk", "16qam"], default="qpsk")
    parser.add_argument("--snr-db", type=float, default=20.0, help="Signal-to-noise ratio in dB")
    parser.add_argument("--num-symbols", type=int, default=12000, help="Number of transmitted symbols")
    parser.add_argument("--num-taps", type=int, default=9, help="Number of adaptive filter taps")
    parser.add_argument("--decision-delay", type=int, default=None, help="Target-symbol delay; default is the center tap")
    parser.add_argument("--mu", type=float, default=0.01, help="LMS step size (smaller is usually safer)")
    parser.add_argument("--train-fraction", type=float, default=0.60, help="Fraction used for training, 0.20-0.90")
    parser.add_argument("--seed", type=int, default=7, help="Random seed for repeatable results")
    parser.add_argument("--decision-directed", action="store_true", help="Continue LMS updates using detected symbols")
    parser.add_argument("--skip-snr-sweep", action="store_true", help="Skip the additional BER-versus-SNR experiment")
    parser.add_argument("--output-dir", type=Path, default=Path("results"), help="Folder for plots and measurements")
    parser.add_argument("--sweep-symbols", type=int, default=7000, help="Symbols used at each SNR point")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    result = run_simulation(
        modulation=args.modulation,
        snr_db=args.snr_db,
        num_symbols=args.num_symbols,
        num_taps=args.num_taps,
        step_size=args.mu,
        train_fraction=args.train_fraction,
        decision_delay=args.decision_delay,
        decision_directed=args.decision_directed,
        seed=args.seed,
    )
    save_main_results(result, args.output_dir)

    print("\nLMS EQUALIZER RESULTS")
    print("--------------------")
    print(f"Modulation:               {result.modulation.upper()}")
    print(f"SNR:                      {result.snr_db:.1f} dB")
    print(f"Transmitted symbols:      {result.transmitted.size}")
    print(f"Training symbols:         {result.training_end}")
    print(f"Equalizer taps:           {result.equalizer.num_taps}")
    print(f"Step size (mu):           {result.equalizer.step_size:g}")
    print(f"Decision delay:           {result.equalizer.decision_delay}")
    print(f"BER before equalization:  {result.ber_before:.6g}")
    print(f"BER after equalization:   {result.ber_after:.6g}")
    print(f"EVM before equalization:  {result.evm_before:.6g}")
    print(f"EVM after equalization:   {result.evm_after:.6g}")
    print(f"\nPlots and metrics saved in: {args.output_dir.resolve()}")

    if not args.skip_snr_sweep:
        snr_values = [0, 5, 10, 15, 20, 25, 30]
        print("\nRunning BER-versus-SNR experiment...")
        rows = run_snr_sweep(
            snr_values=snr_values,
            modulation=args.modulation,
            num_symbols=args.sweep_symbols,
            num_taps=args.num_taps,
            step_size=args.mu,
            train_fraction=args.train_fraction,
            decision_delay=args.decision_delay,
            seed=args.seed + 100,
        )
        save_snr_sweep(rows, args.output_dir)
        print("SNR sweep:")
        for row in rows:
            print(
                f"  {row['snr_db']:>4.0f} dB: BER before={row['ber_before']:.4g}, "
                f"after={row['ber_after']:.4g}"
            )
    print("\nFinished. Open the PNG files in the results folder to view the figures.")


if __name__ == "__main__":
    main()
