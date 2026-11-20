# What the three-member team needs to finish

## Submission checklist from the AVD612 course PDF

- [ ] Add all three team members and LMS equalizer to the instructor's circulated Google form, with a team name.
- [ ] Read/understand the LMS subsystem, equations, and algorithm; consult course instructor, peers and TAs.
- [ ] Make **real** Git commits to a **private** repository, update AI log at each commit, grant instructor **push** access.
- [ ] Each teammate reproduces the tests on their own computer and can discuss all plots/code.
- [ ] Replace all author/institute placeholders and **rewrite the report in your own words**, with checked citations. Keep IEEEtran document to at most **6 pages**; submit PDF to Moodle.
- [ ] Rehearse a **10-minute** presentation in which all members speak and can answer questions about any slide.
- [ ] Submit presentation slides to Moodle (may be after presentation, according to instructions).
- [ ] Back up code, figures, notebooks, report, slides, and the repository URL.

## Suggested talk allocation — 10 minutes total

| Presenter | Slides | Approx. talk share | Core points |
|---|---|---|---|
| Member 1 | 1–4 | 3 min | Explain equalizer, ISI, link and training/test procedure. |
| Member 2 | 5–8 | 4 min | Derive vector equations, Wiener objective, LMS update and complex conjugate. |
| Member 3 | 9–11 | 3 min | Explain convergence, BER, step-size, tap-count plots, conclusions/limitations. |

Adjust timings after an actual rehearsal and ensure no one relies entirely on one part.

## Instructor may ask you to demonstrate:

1. Open Jupyter and run the BPSK/QPSK example cells.
2. Show exactly where `np.vdot` and `np.conj(error)` appear.
3. Change `mu` or channel taps; explain what changes in MSE and BER.
4. Show that the weights stop adapting before test BER is measured.
5. Compare LMS to the Wiener–Hopf solution and state the meaning of `R` and `p`.
6. Show code/AI log Git commits and explain the role of each member.

## Important limits of this package

The package is not submitted to Moodle, not a GitHub repository, and not a real on-air receiver. It does not have real student names or institute details. Report/slide PDFs are artifacts to be **reviewed and edited**, not proof of student authorship.
