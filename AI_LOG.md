# AI assistance log — AVD612 LMS Equalizer

The project instructions expressly encourage AI as an **aide**, require that each team member understand the output, and require an updated AI interaction log at **each Git commit**, recording prompts and how the AI-generated output was checked. This log is provided to help meet those requirements **truthfully**. The team must add any missing conversations and entries for subsequent work.

## Initial package-generation session (2026-11-18)

**Tool:** OpenAI ChatGPT (GPT-6).

**Student request, summarized from this conversation:** Asked what outcomes the instructor expects for an assigned LMS Equalizer course project, considered BPSK plus QPSK and notebook versus Python module organization, and finally asked: **“Then complete the total project by urself and give a downloadable copy.”**

**AI-generated/helped deliverables:** `lms_equalizer.py`, `experiments.py`, `LMS_Equalizer.ipynb`, `tests/test_lms.py`, README and documentation, nine plots plus JSON/CSV data, a draft IEEEtran LaTeX report with bibliography and compiled PDF, an editable Beamer presentation and compiled PDF. The algorithm and prose should be understood, checked, and revised by the team.

**Checks performed during this session (automated, not an instructor/team verification):**

- Executed Python's unit-test suite with BPSK/QPSK roundtrip, unit power, complex LMS one-step update, frozen weights and absence of test-label updates, AWGN special case, repeatable held-out metrics and noiseless identity channel.
- Ran `python experiments.py` to compute BER, RMS EVM, learning-rate/filter-length sweeps, and nine PNG graphs from the actual simulator.
- Executed all Jupyter notebook cells using `jupyter nbconvert --execute --inplace`; saved completed outputs in the notebook.
- Compiled IEEEtran `.tex` to PDF using `pdflatex` and `bibtex.original` (the local `bibtex` symlink was broken); confirmed the resulting report is within the six-page limit.
- Compiled Beamer slides to PDF and confirmed 11 slides; inspected previews for layout.
- Tested equalizer weights remain unchanged if known test labels are altered, preventing ground-truth leakage into inference.

**Remaining independent checks for the student team:** Explain each equation without prompting, inspect the QPSK conjugate update, change a parameter and reproduce the plots, verify all citations and assumptions, rewrite the report in your own words, fill team details, practice a live demonstration, and review exact testing outcome on your own computers. Confirm no teammate is represented as having done work they did not do.

**Git commit ID:** _None yet — this ZIP is not a Git repository and has no fabricated commits._

---

## Template to append for EVERY future commit

**Date & actual Git commit ID:**

**Human task/change and team member(s):**

**Exact AI tool and prompt(s) used (or “No AI used”):**

**AI output retained/modified/rejected:**

**Human verification (tests run, results checked, citations inspected):**

**Files modified and reason:**

---

> Example of an honest entry: “Used ChatGPT to suggest edge-case tests for complex QPSK LMS. Adapted them manually, ran `python -m unittest discover -s tests -v`, reviewed conjugate-gradient reasoning and made commit abc123.” Do not copy this example unless it actually occurred.
