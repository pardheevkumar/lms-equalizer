# LMS Linear Equalizer Simulator (Python)

A student-friendly, end-to-end simulation of a **Least Mean Squares (LMS) linear equalizer** for a digital communication receiver. The project follows the AVD612 course brief: model a communication subsystem in Python, explain its mathematics, and test it with multiple signal formats and parameter settings.

> **Important for your viva:** do not memorize results only. Be ready to explain the channel model, why intersymbol interference (ISI) occurs, what each equalizer tap does, why the LMS error is calculated, and how changing the step size affects convergence.

Requires Python 3.10 or newer.

## What the simulator does

1. Creates random data bits and modulates them using **BPSK, QPSK, or 16-QAM**.
2. Sends the symbols through a configurable multipath FIR channel and adds complex AWGN at a chosen SNR.
3. Uses a known training portion of the packet to learn the equalizer weights with LMS.
4. Tests the learned equalizer on later symbols that were not used as training targets.
5. Compares the received signal before and after equalization using **bit error rate (BER)** and **normalized error-vector magnitude (EVM)**.
6. Saves figures and numeric results, including an optional BER-versus-SNR sweep.

The default example is reproducible: QPSK, 20 dB SNR, 12,000 symbols, 9 taps, `mu = 0.01`, 60% training, and random seed 7. On the included channel, this run should show lower BER/EVM after equalization. Exact metrics are written to `results/metrics.json` whenever you run it.

## 1. Install and run (Windows)

Open PowerShell in the folder containing this README.

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python run_simulation.py
```

If PowerShell blocks environment activation, you can run the interpreter directly instead:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe run_simulation.py
```

On Linux/macOS, activate the environment with `source .venv/bin/activate` after creating it with `python3 -m venv .venv`.

## 2. Useful commands

Run BPSK at 15 dB, using seven equalizer taps:

```bash
python run_simulation.py --modulation bpsk --snr-db 15 --num-taps 7 --mu 0.008
```

Run 16-QAM with a smaller LMS step size:

```bash
python run_simulation.py --modulation 16qam --snr-db 25 --mu 0.003
```

Try a different decision delay (must be smaller than the tap count):

```bash
python run_simulation.py --num-taps 9 --decision-delay 2
```

Use more symbols for a smoother experiment:

```bash
python run_simulation.py --num-symbols 30000 --sweep-symbols 10000
```

Try decision-directed adaptation after the known training region:

```bash
python run_simulation.py --decision-directed
```

Skip the longer SNR sweep when you only need the single experiment:

```bash
python run_simulation.py --skip-snr-sweep
```

Show every supported argument:

```bash
python run_simulation.py --help
```

## 3. Understand the folders

| File/folder | Purpose |
|---|---|
| `run_simulation.py` | Command-line entry point; reads settings and runs experiments |
| `lms_equalizer/modulation.py` | Bit-to-symbol mapping, constellation points, symbol decisions |
| `lms_equalizer/channel.py` | Multipath FIR channel and complex additive white Gaussian noise |
| `lms_equalizer/equalizer.py` | The LMS update loop, normal equalization, optional decision-directed updates |
| `lms_equalizer/simulation.py` | Connects the transmitter, channel, training, test data, BER, and EVM together |
| `lms_equalizer/plotting.py` | Creates figures, CSV, and JSON metrics |
| `tests/` | Automated checks that should pass before committing changes |
| `docs/MATHEMATICAL_NOTES.md` | Equations and plain-language explanation for study/viva |
| `docs/TEST_PLAN.md` | Suggested parameter and signal experiments |
| `report/main.tex` | IEEEtran report scaffold; replace prompts with your team's explanation |
| `presentation/outline.md` | Suggested 10-minute presentation plan |
| `AI_LOG.md` | Required record of AI-assisted work and how you verified it |

## 4. LMS in plain language

The multipath channel makes the current received sample contain a mixture of the current transmitted symbol and delayed symbols. Those delayed pieces cause **intersymbol interference (ISI)**.

The equalizer is an FIR filter with adjustable weights. Each output is compared with the known training symbol. If the output is wrong, LMS nudges the weights in a direction expected to reduce the squared error next time.

For the complex baseband convention used in this code:

\[
\begin{aligned}
\mathbf{x}[n] &= [r[n], r[n-1], \ldots, r[n-M+1]]^T,\\
y[n] &= \mathbf{w}^H[n]\mathbf{x}[n],\\
e[n] &= d[n]-y[n],\\
\mathbf{w}[n+1] &= \mathbf{w}[n]+\mu\mathbf{x}[n]e^*[n].
\end{aligned}
\]

- `M` is the number of equalizer taps.
- `mu` (step size) controls how much the weights change after each error.
- `d[n]` is the known training symbol aligned to the chosen decision delay.
- `e[n]` is the difference between the desired symbol and the equalizer output.
- `*` means complex conjugate; `H` means conjugate transpose.

A larger step size may converge faster but can also oscillate or diverge. A very small step size is often stable but learns more slowly. The best value depends on the signal power, channel, number of taps, and modulation; do not assume one value is optimal for every experiment.

## 5. Outputs

After a run, open the `results/` folder:

- `constellation_comparison.png` — samples before/after LMS, with ideal constellation points.
- `learning_curve.png` — moving-average training error in dB.
- `symbol_recovery.png` — transmitted target, raw received signal, and equalizer output aligned in time.
- `ber_vs_snr.png` — BER before/after equalization at several SNR values (unless skipped).
- `metrics.json` — experiment parameters, BER/EVM values, and final tap weights.
- `snr_sweep.csv` — measured SNR sweep values.

**How to read the figures:** a tighter constellation around the ideal points is generally better; a falling learning curve indicates adaptation; lower BER and EVM indicate better symbol recovery. In some channels, settings, or random runs LMS may not improve performance. Report such results honestly and investigate the step size, training length, tap count, and decision delay.

## 6. Run the tests

```bash
python -m unittest discover -s tests -v
```

The tests check BPSK/QPSK/16-QAM modulation round trips, a noiseless identity channel, LMS recovery with a known training sequence, improvement on the default multipath example, decision-directed mode, and invalid parameter handling.

## 7. Git and course submission checklist

The course brief expects the code to be maintained in a **private GitHub repository**, with a meaningful commit history and an AI log updated alongside commits. The zip of this project is not a substitute for your team's own Git history.

From the project folder:

```bash
git init
git add README.md requirements.txt .gitignore AI_LOG.md
git commit -m "Add project setup and initial AI-use log"
# Before each following commit, update AI_LOG.md with the work and checks.
git add lms_equalizer/modulation.py lms_equalizer/channel.py AI_LOG.md
git commit -m "Add modulation and multipath channel models"
git add lms_equalizer/equalizer.py lms_equalizer/simulation.py AI_LOG.md
git commit -m "Implement trained LMS equalizer and metrics"
git add lms_equalizer/plotting.py run_simulation.py tests/ AI_LOG.md
git commit -m "Add simulation plots, command-line runner, and tests"
git add docs/ report/ presentation/ AI_LOG.md results/ README.md
git commit -m "Add study notes and course deliverable scaffolds"
```

Before each commit, update `AI_LOG.md` to describe the relevant AI-assisted work, the checks you ran, and any changes you made yourself. Give the instructor the repository access required by the course.

## References for further study

- GNU Radio, [Linear Equalizer](https://wiki.gnuradio.org/index.php/Linear_Equalizer) — training-based and decision-directed linear equalization.
- GNU Radio, [Adaptive Algorithm](https://wiki.gnuradio.org/index.php?title=Adaptive_Algorithm) — LMS/NLMS/CMA algorithm settings and step-size discussion.
- Simon Haykin, *Adaptive Filter Theory*, 5th ed., Pearson, 2014 — adaptive filtering and LMS.
- John G. Proakis and Masoud Salehi, *Digital Communications*, 5th ed., McGraw-Hill, 2008 — communication channels, ISI, and equalization.

This is an educational symbol-spaced model. It is not a complete receiver with timing recovery, carrier recovery, pulse shaping, or an over-the-air RF front end.
