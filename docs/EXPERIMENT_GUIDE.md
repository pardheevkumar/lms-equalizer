# Experiment-by-experiment guide

All figures in `results/simulation_graphs/` are computed from real calls to `simulate()` and `lms_equalizer()`. Main setting: `mild` 3-tap FIR channel, 12 dB measured received signal-power SNR, 9-tap LMS, $\mu=0.018$, delay 2, 2,500 training time samples, and 9,000 held-out reference symbols. The seed is 2026 unless specified.

| Plot | What it demonstrates | What to say in the viva |
|---|---|---|
| `01_mse_convergence` | 90-sample running training squared error, BPSK and QPSK | We do not expect a zero error floor because AWGN and finite-length inverse filtering remain. |
| `02_qpsk_constellation` | raw vs equalized QPSK constellation | The four clusters become more concentrated near the ideal symbols. |
| `03_bpsk_waveforms` | desired vs raw aligned vs equalized BPSK | LMS output tracks BPSK symbols better than raw ISI-distorted samples. |
| `04_stepsize_sweep` | $\mu=0.004,0.012,0.03,0.07$ | Larger $\mu$ can adapt quickly but produce a larger residual MSE and BER. |
| `05_filter_length_sweep` | 3/5/9/13/17 taps | Nine taps are a reasonable demonstration choice here, not a universal optimum. |
| `06_ber_vs_snr` | 0/4/8/12/16/20 dB, mean over 3 seeds | LMS is better over much of the simulated range; it is not guaranteed for every low-SNR setting. |
| `07_effective_impulse_response` | $h * \mathrm{conj}(\mathbf w)$ | Combined channel/equalizer impulse tends to concentrate energy near intended decision delay. |
| `08_coefficient_trajectories` | weight evolution over training | Coefficients begin at zero and adapt over hundreds of training symbols. |
| `09_channel_comparison` | flat, mild, severe channel cases | Equalization matters when there is ISI; different channels may need different settings. |

## Reading the results properly

- **SNR is not Eb/N0.** It is computed from the average noiseless sample power *after the channel* divided by added AWGN power.
- **Avoid test-label leakage.** For sample indices `n >= train_stop`, the reference test symbols are used only to calculate offline diagnostic error/BER, never to update weights. Actual first tested reference symbol is `s[n_train]`.
- **BER estimates are random.** Finite numbers of transmitted bits and different seeds change measured BER. In `06_ber_vs_snr` each point averages three seeded trials.
- **Raw unequalized BER can be non-monotonic.** With the selected dispersive channel the interference itself sometimes flips the hard decision. Some added noise can randomly flip such an incorrect sign back, so raw BER need not be a monotonic textbook AWGN curve. The true message is the comparison of two receivers with identical channel/noise conditions for each trial.
- **QPSK complex LMS:** the filter output is $\mathbf w^H\mathbf x$ and update is $\mu\mathbf x e^*$; forgetting the conjugate would be mathematically wrong.
- **No eye diagram in this version.** A legitimate eye diagram requires pulse shaping and oversampled samples. Use the waveforms and constellations provided instead.

## Further meaningful tests (optional extensions)

- Replace `CHANNELS["mild"]` with a measured or textbook FIR impulse response, rerun experiments, and explain differences.
- Compare multiple independent random seeds and report variance/confidence intervals.
- Add pilot overhead or an optional decision-directed mode with caution about error propagation.
- Add symbol-rate complex channel taps and inspect QPSK phase adaptation.
- Implement NLMS as a separate method for comparison, but do not change the project's primary LMS title.
