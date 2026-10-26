# AI-use log (update this as the project evolves)

The course brief asks teams to record AI-assisted work and how AI output was checked. Keep this file truthful and update it whenever AI assistance changes the code or deliverables. Do not claim a test was performed unless your team ran it.

## Entry 1 — Initial implementation and review

- **Date:** 2026-10-26
- **Tool:** OpenAI ChatGPT
- **Task/prompt summary:** Use the AVD612 course brief to implement a complete, readable Python LMS equalizer project; include tests and explain the implementation for a beginner.
- **AI-assisted work:** Initial Python modules for modulation/demodulation, multipath + AWGN channel, complex LMS equalizer, end-to-end simulation, BER/EVM metrics, plots, command-line parameters, test scaffold, and documentation.
- **Checks run by assistant in the working environment:** `python -m unittest discover -s tests -v` passed 6 tests; a default QPSK run completed and saved the plots and metrics. The actual results are in `results/metrics.json`.
- **Checks the team must repeat:** Run the tests on your own machine; run BPSK, QPSK, and 16-QAM cases; compare at least three step sizes and tap lengths; inspect plots and decide whether the parameter settings make physical sense; discuss any failures with the instructor/TA.
- **Human changes/review:** _Team members: add your names, any code changes you made, questions checked with the instructor/TA, and the commit hash._
- **Limitations to mention:** Educational symbol-spaced simulation; does not implement timing synchronization, carrier recovery, pulse shaping, or a hardware radio.

## Entry template for future changes

- **Date and commit hash:**
- **What changed:**
- **AI prompt(s) and tool(s) used:**
- **What was accepted/rejected and why:**
- **How the output was checked:**
- **Human edits and reviewer(s):**
- **Remaining issues:**


## Entry 2 — Broader tests and course materials

- **Date:** 2026-10-26
- **Tool:** OpenAI ChatGPT
- **Task/prompt summary:** Expand the simulator into a human-readable course project and add course-facing materials.
- **AI-assisted work:** Added test coverage for all modulation formats and decision-directed mode; created mathematical notes, a test plan, an IEEEtran report scaffold, a ten-minute presentation outline, and a PowerPoint starter deck using generated result plots.
- **Checks run by assistant in the working environment:** `python -m unittest discover -s tests -v` passed 8 tests; Python compile check passed; the default run and 5 extra parameter/modulation cases completed; the PowerPoint deck rendered and passed the slide overflow test; the LaTeX scaffold compiled during a smoke check.
- **LaTeX note:** The `pdflatex` smoke check succeeded. The `bibtex` executable was not available in this environment, so the bibliography references were not resolved here; run the usual LaTeX → BibTeX → LaTeX passes on a setup that includes BibTeX.
- **Human review still required:** Confirm every figure/value with a fresh run on the team's final code; add author/team details; adapt the presentation to the team's language; write the report explanations in your own words; run the experiment plan and record the results you actually observe.
- **Human changes/review:** _Team members: add your names, code edits, and commit hash after reviewing._
