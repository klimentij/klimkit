# LOG — 005-160526-team-workflow-fixes

Hardened Dominik's PR #1 "Add team artifact workflow": migration collision safety, Switchboard
report discovery/serving, CLI dry-run command quoting, and a stale hard-coded `Human` string in
the projected Codex pack — while flattening this repo's own evidence back to the solo layout.

> Migrated 2026-07-15 from `.klimkit/tasks/05-team-workflow-fixes/` and
> `.klimkit/reports/05-team-workflow-fixes/`; predates the phase convention — artifacts are flat
> numbered files. Authorship below is recovered from the old `-h-`(human) / `-a-`(agent) file names
> (all four artifacts here were agent-authored).

- **2026-05-16** (agent) [001-acceptance-checklist.md](001-acceptance-checklist.md) — checklist for hardening PR #1's team workflow: migration preflight/collision safety, Switchboard report discovery/serving, dry-run command quoting, Codex pack `__HUMAN_NAME__` fix.
- **2026-05-16** (agent) [002-implementation-plan.md](002-implementation-plan.md) — five-step plan: migration preflight hardening, Switchboard hardening, CLI follow-up command repair, Codex pack wording fix, then verification/proof.
- **2026-05-16** (agent) [003-implementation-proof.md](003-implementation-proof.md) — implemented all four fixes, ran the full suite (169 tests) plus adversarial CLI/HTTP QA and browser screenshots, flattened this repo's evidence back to the solo `.klimkit/` layout; two final-review rounds.
- **2026-05-16** (agent) [004-proof-report.html](004-proof-report.html) — self-contained story-style HTML proof report of the reports UI and reserved-name rejection; its `assets/*.png` and `assets/reports-flow.mp4` references were never committed (heavy-artifact policy) and no longer resolve.
