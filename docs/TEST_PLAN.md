# Test Plan: LMS Equalizer

The course brief asks for testing with different input signals and parameter values. Save each run's command, seed, plot and `metrics.json`, and summarize what changed.

| Experiment | Suggested settings | What to inspect | Expected question |
|---|---|---|---|
| Baseline QPSK | Default runner | BER/EVM before vs after; learning curve | Does LMS reduce ISI in this example? |
| BPSK | `--modulation bpsk --snr-db 15` | Constellation and BER | Does the code support a one-bit symbol format? |
| 16-QAM | `--modulation 16qam --snr-db 25 --mu 0.003` | Constellation, BER and EVM | How does a denser constellation change sensitivity to noise? |
| Lower SNR | `--snr-db 5` | Scatter spread and BER | What happens when noise is stronger? |
| More training | `--train-fraction 0.75` | Training curve and test BER | Does giving LMS more known symbols help this channel? |
| Less training | `--train-fraction 0.30` | Training curve and test BER | What can happen before the equalizer has converged? |
| Step-size comparison | Repeat with `--mu 0.002`, `0.01`, `0.03` | Learning curve; watch for unstable values | How does convergence speed trade off against stability? |
| Tap-count comparison | Repeat with `--num-taps 3`, `7`, `11` | BER/EVM and training curve | How does filter length affect equalization and convergence? |
| Decision-delay comparison | Repeat with `--decision-delay 1`, `2`, or default center (keep delay below tap count) | BER/EVM and constellation | How does the desired symbol alignment affect the result? |
| Decision-directed | `--decision-directed` | BER/EVM; compare with trained-only run | Can detected symbols maintain or damage adaptation? |
| Reproducibility | Repeat the same command and seed | `metrics.json` | Why should the result match between runs? |
| SNR sweep | Default run | `ber_vs_snr.png`, `snr_sweep.csv` | How does noise affect performance, and does LMS help? |

## Interpretation cautions

- Do not claim the equalizer always improves BER. It is a finite-tap adaptive filter and depends on channel, delay, SNR, training length, and step size.
- The SNR sweep is a Monte Carlo experiment with finite samples, so adjacent points can be irregular. Increase `--sweep-symbols` for smoother estimates.
- At high SNR, a finite run may observe zero bit errors. Report the number of measured bits alongside zero BER; zero observed errors does not prove the true error probability is exactly zero.
- Run `python -m unittest discover -s tests -v` after editing the code and before committing changes.
