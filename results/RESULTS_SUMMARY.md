# Results summary from the bundled default run

These values were produced on 26 October 2026 by running `python run_simulation.py` with the default seed and parameters. Re-run the code and use the values from your own final run in the report and slides.

## Default single-run settings

| Setting | Value |
|---|---:|
| Modulation | QPSK |
| SNR | 20 dB |
| Transmitted symbols | 12,000 |
| Training-region boundary | 7,200 symbols (60%) |
| LMS taps | 9 |
| Step size `mu` | 0.01 |
| Decision delay | 4 symbols (center tap by default) |
| Test target bits measured | 9,592 |

## Default measured performance

| Metric | Before equalization | After LMS equalization |
|---|---:|---:|
| BER | 0.00385738 | 0 observed errors |
| Normalized RMS EVM | 0.44541 | 0.13583 |

The BER result after LMS is zero errors in this finite test packet, **not proof that the true BER is exactly zero**. EVM fell by about 69.5% in this run, but that is one channel/seed/parameter combination rather than a universal guarantee.

## SNR sweep (7,000 symbols per point)

| SNR (dB) | BER before LMS | BER after LMS |
|---:|---:|---:|
| 0 | 0.2101 | 0.2082 |
| 5 | 0.1018 | 0.07135 |
| 10 | 0.03398 | 0.003040 |
| 15 | 0.01574 | 0 observed errors |
| 20 | 0.005722 | 0 observed errors |
| 25 | 0 observed errors | 0 observed errors |
| 30 | 0 observed errors | 0 observed errors |

There are 5,592 measured test bits at each SNR point in this sweep. The plot uses a visual floor for zero-error points so they can appear on a logarithmic axis; the stored CSV keeps the actual measured BER values.

## Additional checks performed

- BPSK at 15 dB with 7 taps and `mu=0.008`: BER remained zero before/after for that random test sample, while EVM improved from 0.4704 to 0.2303.
- 16-QAM at 25 dB with 9 taps and `mu=0.003`: BER changed from 0.1446 to zero observed errors; EVM improved from 0.4342 to 0.08819.
- QPSK decision-directed adaptation at 10 dB with 7 taps and `mu=0.005`: BER changed from 0.04081 to 0.005955; EVM improved from 0.5344 to 0.3597.

These extra cases are smoke checks, not a complete parameter study. For the course submission, add the results of your own comparisons of step size, tap count, training length and decision delay, including any unsuccessful settings.
