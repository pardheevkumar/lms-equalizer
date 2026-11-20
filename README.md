# LMS Adaptive Equalizer — AVD612 course project

**BPSK + QPSK | Python + Jupyter | training-based complex LMS | IEEEtran report | Beamer slides**

This is a **complete, runnable educational simulator** for a point-to-point digital communication subsystem. It follows the requirements listed in the provided `2026_CourseProject.pdf`: a Python model, mathematical justification, testing with different inputs and parameters, report (maximum six pages in IEEEtran), and a 10-minute presentation. The course instructions also require **a private team GitHub repository, a real commit history, an updated AI interaction log, and instructor push access**. Those account-side steps must be completed by the team; this ZIP does **not** pretend that they are already done.

> **Before submission:** the supplied report is an **AI-assisted technical draft**. The course explicitly requires you to understand and write the report in your own words (rather than submit an entirely AI-written report). All three teammates should read, check, independently revise, and explain the simulation, figures, conclusions and code; replace all title-page placeholders.

## Project files

```text
LMS_Equalizer_Project/
├── LMS_Equalizer.ipynb                 # executed Jupyter notebook, math + code + graphs
├── lms_equalizer.py                   # standalone BPSK/QPSK modem + complex LMS routine
├── experiments.py                     # completely regenerates plots, metrics and CSV
├── requirements.txt                   # Python packages
├── README.md
├── AI_LOG.md                           # initial transparent log + future-entry template
├── GIT_WORKFLOW.md                     # private GitHub and grading instructions
├── tests/
│   └── test_lms.py                   # automated algorithm/unit tests
├── results/
│   ├── simulation_graphs/             # nine computed PNG figures
│   ├── metrics.json                   # all main settings/measurements
│   └── ber_vs_snr.csv                 # three-seed BER sweep
├── report/
│   ├── IEEE_Report.tex                # editable IEEEtran LaTeX draft
│   ├── references.bib                 # BibTeX references
│   └── IEEE_Report.pdf                # compiled report (3–4 pages; <= 6)
├── presentation/
│   ├── LMS_Presentation.tex           # editable Beamer presentation
│   └── LMS_Presentation.pdf           # compiled 11-slide presentation
└── docs/
    ├── THEORY_NOTES.md                # LMS math in simple language
    ├── VIVA_QA.md                     # viva questions with clear answers
    ├── TEAM_HANDOFF.md                # 3-member presentation, course handoff
    └── EXPERIMENT_GUIDE.md            # plots, limitations, interpretation
```

## 1. Installation

Use Python 3.10+ on Windows, Linux or macOS. From the project folder:

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
```

To run the notebook, type `jupyter notebook` (or open the `.ipynb` in JupyterLab / VS Code), then select **Run All**. Notebook code imports the adjacent `lms_equalizer.py` and `experiments.py`, so open Jupyter from this folder. The checked-in notebook already contains outputs for quick inspection.

## 2. Regenerate the results

```bash
python -m unittest discover -s tests -v
python experiments.py
```

The first command executes the automatic tests; the second produces all nine PNG figures, `metrics.json`, and `ber_vs_snr.csv`. The outputs use fixed seeds and can be regenerated. You can also run all cells of `LMS_Equalizer.ipynb` to reproduce and display the results interactively.

## 3. What the simulation models

Bits -> **BPSK or QPSK** -> **FIR ISI channel** -> **AWGN** -> **LMS FIR equalizer** -> **hard slicer** -> **BER/EVM**.

The real channel `mild = [0.90, 0.65, -0.35]` is common to both modulation examples. QPSK uses a **complex-valued signal and weights**, with conjugate-gradient LMS. A second more-dispersive `severe` channel and a `flat` reference channel are supplied. You can replace them with your own static FIR channels.

The model is **symbol-spaced** and presumes carrier phase and symbol timing have already been synchronized. This is a deliberate simplification: synchronization is a different course subsystem. AWGN is set from the mean noiseless **received** signal power (not `Eb/N0`). No real radio, pulse shaping, fading, or oversampled eye diagram is claimed.

### Core formulas

For a $M$-tap input vector $\mathbf{x}[n]$, filter weights $\mathbf{w}[n]$, desired symbols $d[n]=s[n-D]$, and step size $\mu$:

$$y[n]=\mathbf{w}^H[n]\mathbf{x}[n],\quad e[n]=d[n]-y[n],$$

$$\boxed{\mathbf{w}[n+1]=\mathbf{w}[n]+\mu\mathbf{x}[n]e^*[n].}$$

The Wiener benchmark would satisfy $\mathbf{R}\mathbf{w}_{opt}=\mathbf{p}$ for $\mathbf{R}=E[\mathbf{x}\mathbf{x}^H]$, $\mathbf{p}=E[\mathbf{x}d^*]$. LMS estimates the gradient from each instantaneous sample instead of explicitly estimating/inverting $\mathbf{R}$.

### Test protocol: important for grading

- Train until time sample `n_train-1`; **freeze the taps** for `n>=n_train`.
- Evaluate exactly `n_test=9000` *held-out reference symbols*, starting at time sample `n_train+delay` so training target labels are not scored.
- For the raw baseline, compare **r[k]** with **s[k]**; for LMS, compare **y[k+D]** with the **same s[k]**.
- Computing `desired - output` in the test interval is **diagnostic only** and **never updates** the coefficients.
- BER counts incorrect individual bits; QPSK maps each symbol to 2 bits. EVM is a dimensionless RMS normalized by the true reference-symbol power.

## 4. Reproducible example at 12 dB receive SNR

Main settings: seed 2026, 2,500 training time samples, 9,000 held-out symbols, 9 taps, $\mu=0.018$, decision delay 2, `mild` channel.

| Modulation | Raw BER | LMS BER | Raw RMS EVM | LMS RMS EVM |
|:--|--:|--:|--:|--:|
| BPSK | 0.1549 | 0.0217 | 0.7924 | 0.4551 |
| QPSK | 0.1591 | 0.0247 | 0.7950 | 0.4592 |

These are **simulated sample estimates for the specific settings/seed**, not guaranteed real-channel performance. The SNR plot uses three seeds (2026, 2027, 2028). LMS is not guaranteed to beat an unequalized receiver at every SNR (especially in low-SNR regimes).

## 5. Experiment outcomes

1. `01_mse_convergence.png`: training error over time (BPSK and QPSK).
2. `02_qpsk_constellation.png`: before/after QPSK cloud vs ideal points.
3. `03_bpsk_waveforms.png`: desired BPSK symbols, raw aligned samples, and LMS output.
4. `04_stepsize_sweep.png`: learning-rate impact on adaptation and BER.
5. `05_filter_length_sweep.png`: changes with FIR taps (3/5/9/13/17).
6. `06_ber_vs_snr.png`: raw vs equalized BER from SNR 0–20 dB (3 seeds).
7. `07_effective_impulse_response.png`: combined channel and equalizer impulse response.
8. `08_coefficient_trajectories.png`: how seven example tap weights change during training.
9. `09_channel_comparison.png`: flat, mild and severe channel cases.

Read `docs/EXPERIMENT_GUIDE.md` for interpretation, including why the raw ISI BER curve is not always monotonic.

## 6. Report and slides

**IEEEtran report:** `report/IEEE_Report.tex` is fully editable and accompanied by `references.bib` and a compiled PDF. Its figures are generated from this repository. It has the requested introduction, informal operation, mathematical model, results, discussion and BibTeX references. **Review/rewrite it yourselves, and insert author/affiliation details before submitting to Moodle.**

**Beamer presentation:** `presentation/LMS_Presentation.tex` and its compiled PDF contain 11 slides matching the instructor's suggested 10-minute outline (title, introduction, informal explanation, math and results). Practice within the time limit; see `docs/TEAM_HANDOFF.md`.

With a LaTeX distribution installed:

```bash
cd report
pdflatex IEEE_Report.tex
bibtex IEEE_Report
pdflatex IEEE_Report.tex
pdflatex IEEE_Report.tex
# alternative if your system has a broken bibtex link: bibtex.original IEEE_Report

cd ../presentation
pdflatex LMS_Presentation.tex
pdflatex LMS_Presentation.tex
```

## 7. Git and instructor requirements

See **`GIT_WORKFLOW.md`**. A ZIP cannot supply a genuine development history or push permissions. The team needs to create a **private** GitHub repository, push the files, add meaningful future commits as work is actually improved, accurately maintain `AI_LOG.md` on every commit, and invite the instructor with **push access**. Do **not** fabricate past commits or pretend a code change happened if it did not.

## 8. Sources for learning

- S. Haykin, *Adaptive Filter Theory*, 4th ed., Prentice Hall, 2002.
- B. Widrow and S. D. Stearns, *Adaptive Signal Processing*, Prentice-Hall, 1985.
- J. G. Proakis and M. Salehi, *Digital Communications*, 5th ed., McGraw-Hill, 2007.
- [GNU Radio Linear Equalizer](https://wiki.gnuradio.org/index.php/Linear_Equalizer), [Adaptive Algorithm](https://wiki.gnuradio.org/index.php/Adaptive_Algorithm) (conceptual comparisons).

**Student integrity reminder:** This package is a starting working reference. Students should understand the symbols, mathematics, Python implementation and test methodology, check citations, revise their own paper, and be able to defend the method face to face.
