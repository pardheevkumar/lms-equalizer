# Private GitHub and Git history: what students must actually do

The instructor specifically grades real version-control history, requests a **private** GitHub repository, and requires **push access for the instructor** plus an **AI log updated at every commit**. This project ZIP cannot create that account-side history or grant external permissions.

## 1. Set up Git when your team starts working

1. Create a **private** repository on GitHub. Record the URL privately for your team.
2. Unzip this package and open a terminal within `LMS_Equalizer_Project`.
3. Run these commands (replace account/user repo URL):

```bash
git init -b main
git add .
git commit -m "Import AI-assisted LMS simulator baseline for team review"
git remote add origin https://github.com/YOUR_USER/YOUR_PRIVATE_REPO.git
git push -u origin main
```

If your Git version does not recognize `git init -b main`, use `git init` then `git branch -M main`.

4. On GitHub, invite both teammates and the instructor via repository **Settings → Collaborators** (wording varies). Ensure the instructor has **write/push** rights as specified.
5. Always work through your own understanding; never portray the initial ZIP as a student-origin development history.

## 2. Make genuine changes over time

Examples of *real* future work: replace placeholder author information; add a rigorous baseline test; test on a different channel; explain math more carefully; fix a plotting issue; perform a reproducibility check; document observations and limitations; verify citations.

For every real change:

```bash
# Edit source, tests, documentation as needed
python -m unittest discover -s tests -v
python experiments.py
# Edit AI_LOG.md: record the real prompt (or no AI), validation, changes
git add lms_equalizer.py experiments.py tests/ AI_LOG.md README.md
git commit -m "Describe what you actually changed"
git push
```

Only stage the files you really changed. If you regenerate figures/CSV/JSON, include those when needed to keep the repository consistent. Notebook output files can cause large Git diffs; decide intentionally whether to commit updated notebook outputs.

## 3. What your GitHub submission must demonstrate

- The full code and tests can be reproduced on a fresh clone.
- Each team member has reviewed the mathematical implementation.
- Commit messages describe actual work rather than fabricated stages.
- Each commit has a corresponding truthful AI-log update (or a no-AI note).
- Instructor has requested repository push access, and backups are made.
- Team form, Moodle report and slide uploads are completed by the students.
