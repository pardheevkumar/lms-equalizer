# Suggested 10-minute presentation outline

The course brief suggests about 10 minutes and asks for an introduction, informal explanation, mathematical model/derivation, and test results. Use this as a plan, not as a substitute for rehearsing or understanding the code. Divide speaking time among all three team members if applicable.

| Slide | Time | Include | Presenter should be able to explain |
|---|---:|---|---|
| 1. Title and team | 0:20 | Project title, course, names | What subsystem was selected? |
| 2. Problem: ISI | 0:50 | Why a multipath channel distorts received symbols | What happens when delayed copies arrive? |
| 3. Where the equalizer sits | 0:45 | Transmitter → channel + AWGN → LMS equalizer → detector | What is input/output of this block? |
| 4. Intuition: tap-delay line | 0:55 | Current/past samples and adjustable tap weights | What does a tap do? |
| 5. Mathematical model | 1:10 | Channel equation and equalizer output | Define every symbol and index |
| 6. LMS derivation/update | 1:20 | Error, MSE goal, weight update, step size | Explain why the update uses the conjugated error |
| 7. Software design | 0:55 | Module diagram or the five main Python modules | How are responsibilities separated and tested? |
| 8. Learning curve + constellation | 1:10 | Insert generated `learning_curve.png` and `constellation_comparison.png` | What evidence shows convergence/recovery? |
| 9. BER/EVM and parameter study | 1:30 | Insert `ber_vs_snr.png`; compare mu/taps/training length | What changed and what did not work? |
| 10. Limits and conclusion | 0:55 | Key finding, limitations, next steps | What would you add for a more realistic receiver? |

## Figure/data checklist

- Use figures produced by your own final Git revision.
- State the modulation, SNR, tap count, step size, and training fraction next to each result.
- For BER, state how many bits were measured; zero errors in a finite run is not proof of zero true BER.
- Include at least one comparison showing a parameter change, not just one successful plot.
- Practise explaining the update loop in `lms_equalizer/equalizer.py` without reading the slide.
