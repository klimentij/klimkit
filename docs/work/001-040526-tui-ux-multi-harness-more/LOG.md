# LOG — 001-040526-tui-ux-multi-harness-more

Klimkit's first major hardening pass: collapsing config into one repo-local TOML,
making the Codex pack harness-agnostic, and iterating Switchboard's tab/notification
UX and multi-machine (Mac client + dev-vm server) code-server routing to production
readiness.

> Migrated 2026-07-15 from `.klimkit/tasks/01-tui-ux-multi-harness-more/`; predates the
> phase convention — artifacts were flat numbered files, now split into phases below.
> Authorship in each phase `LOG.md` is recovered from the old `-h-` (human) / `-a-`
> (agent) file names.

- **05-04..05-04** [001-040526-initial-task-and-build](001-040526-initial-task-and-build/) — repo-local TOML config, harness-agnostic pack prep, README/SECURITY/CONTRIBUTING/CI, 90 passing tests (joint).
- **05-04..05-04** [002-040526-autosync](002-040526-autosync/) — default-on daemon autosync from `origin/main` with fetch/apply/restart and Telegram summaries (joint).
- **05-04..05-04** [003-040526-more-polish](003-040526-more-polish/) — Switchboard UX asks and plan: manual-tab-only rendering, status normalization, deep links (joint).
- **05-04..05-04** [004-040526-bug-fixes](004-040526-bug-fixes/) — root-caused and fixed the Mac client code-server iframe pointing at the wrong VM (joint).
- **05-04..05-06** [005-040526-readiness-review-and-more-polish](005-040526-readiness-review-and-more-polish/) — OSS-launch readiness review plus a second polish round: tmux-wrapped commands, archive/unarchive UX, HTML Telegram formatting (joint).
- **05-07..05-07** [006-070526-final-polish](006-070526-final-polish/) — softer fork guidance, README screenshots, catalog Archived column, v0.1.1 release (joint).
- **05-07..05-07** [007-070526-pack-improvement](007-070526-pack-improvement/) — `checklister` subagent, refactored pack workflow, worktree helper, v0.1.2 release (joint).
