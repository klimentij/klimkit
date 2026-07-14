# LOG — 001-150726-adoption-and-migration

- **2026-07-15 ~00:50** (human) — Klim directed adopting the conversation-be docs/work
  convention as Klimkit's new default, sanitized of any Sellify mentions, with the old
  `.klimkit/` tree migrated into it in this repo and everything shipped as one PR:
  [001-klim-directive.md](001-klim-directive.md).
- **2026-07-15 ~01:00** (agent) — Inspected PR #3680's `docs/work/README.md`,
  `docs/work/.gitignore`, `AGENTS.md` work-log section, phase/work `LOG.md` examples,
  and the convention-design note; mapped every `.klimkit` reference in this repo
  (skills, README, CONTRIBUTING, SECURITY, tests, smoke script, report server).
- **2026-07-15 ~01:05** (agent) — Migrated all 17 `.klimkit/tasks/<NN-slug>/` folders to
  `docs/work/<NNN-DDMMYY-slug>/` via `git mv` (dates from first-commit history), stripped
  `-h-`/`-a-` authorship markers to plain `NNN-` prefixes, merged the two
  `.klimkit/reports/` HTMLs into their work folders, and moved
  `memory.md`/`log.md`/`reflection.md` to `docs/agents/`.
- **2026-07-15 ~01:10** (agent) — Four Sonnet sub-agents authored per-folder `LOG.md`
  files for the migrated work folders, recovering authorship from the staged rename map
  and dates from `docs/agents/log.md`; one stale filename reference fixed, one report's
  never-committed `assets/` media documented as expected loss.
- **2026-07-15 ~01:15** (agent) — Created the sanitized generic convention
  (`docs/work/README.md`, `docs/work/.gitignore`), rewrote `AGENTS.md` with the work-log
  and agent-state sections, added the `CLAUDE.md → AGENTS.md` symlink, and updated all
  skills (setup, implement, checklister, grill-me, tdd, diagnose, walkthrough, reflector,
  report-server + serve script), README, CONTRIBUTING, SECURITY, `.gitignore`, unit
  tests, and the fresh-Codex smoke test to make docs/work the default instead of
  `.klimkit`.
