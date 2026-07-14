# LOG — 001-040526-tui-ux-multi-harness-more

Klimkit's first major hardening pass: collapsing config into one repo-local TOML,
making the Codex pack harness-agnostic, and iterating Switchboard's tab/notification
UX and multi-machine (Mac client + dev-vm server) code-server routing to production
readiness.

> Migrated 2026-07-15 from `.klimkit/tasks/01-tui-ux-multi-harness-more/`; predates the
> phase convention — artifacts are flat numbered files. Authorship below is recovered
> from the old `-h-` (human) / `-a-` (agent) file names.

- **2026-05-04** (human) [001-initial-task.md](001-initial-task.md) — original ask: single TOML config with comments, repo-local (non-git-tracked) state, harness-agnostic pack prep for future Claude Code support, near-100% test coverage incl. Codex smoke tests, and a `tasks/` folder convention with log/memory files.
- **2026-05-04** (agent) [002-critical-repo-review.md](002-critical-repo-review.md) — ultra-deep critical review of the repo (config sprawl, hardcoded Codex assumptions, hygiene) before planning, incl. running the existing 69-test suite.
- **2026-05-04** (agent) [003-implementation-plan-with-clarifications.md](003-implementation-plan-with-clarifications.md) — full implementation plan for local-first config, docs, and harness-agnostic packs, plus clarification questions for Klim.
- **2026-05-04** (agent) [004-review-and-plan-checklist.md](004-review-and-plan-checklist.md) — tracking checklist covering clarified decisions and full scope before implementation.
- **2026-05-04** (human) [005-start.md](005-start.md) — clarification answers, go-ahead to implement fully, with security/subagent review and 3x final-reviewer gate required.
- **2026-05-04** (agent) [005-results-and-proof.md](005-results-and-proof.md) — delivered repo-local config, harness registry, README/SECURITY/CONTRIBUTING/CI, and 90 passing tests (76% coverage).
- **2026-05-04** (agent) [006-status-report.md](006-status-report.md) — status snapshot after push: commits, completed scope, verification, and 3/3 final-reviewer PASS gates.
- **2026-05-04** (human) [007-autosync-and-live-apply.md](007-autosync-and-live-apply.md) — chat follow-up: `kk` should restart services and report what changed; add default-on daemon autosync from `origin/main` every 5s with a Telegram summary.
- **2026-05-04** (agent) [008-autosync-implementation-plan.md](008-autosync-implementation-plan.md) — plan for daemon autosync (fetch/fast-forward/apply/restart/notify) and deferred-restart apply flow.
- **2026-05-04** (agent) [009-autosync-results-and-proof.md](009-autosync-results-and-proof.md) — autosync shipped and verified: 100 tests passing, generated config carries `auto_sync*` defaults, Telegram summary sent.
- **2026-05-04** (human) [010-more-polish.md](010-more-polish.md) — Switchboard UX asks: drop dialog logo, only show manually created tabs, simplify statuses, fix client code-server iframe pointing at the wrong VM (`image.png`).
- **2026-05-04** (agent) [011-more-polish-implementation-plan.md](011-more-polish-implementation-plan.md) — plan for manual-tab-only rendering, status normalization, deep links, notification cleanup, and pack/README polish.
- **2026-05-04** (human) [012-bug.md](012-bug.md) — bug report: Mac client-only install's code-server iframe loads the central dev-vm instead of the Mac's own Tailscale Serve URL.
- **2026-05-04** (agent) [013-client-code-server-bug.md](013-client-code-server-bug.md) — root-caused missing/incorrect client DNS resolution; fixed Tailscale lookup, Serve config, and iframe URL derivation, with live verification.
- **2026-05-04 to 05-05** (agent) [014-open-source-readiness-review.md](014-open-source-readiness-review.md) — OSS-launch readiness review (7/10 trusted-operator, 5/10 polished OSS); blocking findings incl. mutable-main installs, later resolved to fork-first.
- **2026-05-06** (human) [015-more-polish.md](015-more-polish.md) — asks: tmux-wrapped per-tab commands, archive instead of close, batch-archive checkboxes, unformatted Telegram notifications (`image-1.png`), code-server settings reset on pull.
- **2026-05-06** (agent) [016-more-polish-proof.md](016-more-polish-proof.md), [016-switchboard-archive-dialog-proof.png](016-switchboard-archive-dialog-proof.png), [016-switchboard-archived-hidden-tabbar-proof.png](016-switchboard-archived-hidden-tabbar-proof.png) — shipped tmux-wrapped commands, archive/unarchive UX, HTML Telegram formatting, subagent-notification suppression, with QA screenshots.
- **2026-05-07** (human) [017-final-polish.md](017-final-polish.md) — softer fork guidance, move screenshots into `assets/`, add an Archived column to the catalog, unarchive-on-open behavior.
- **2026-05-07** (agent) [018-final-polish-proof.md](018-final-polish-proof.md) — delivered fork-soft install guidance, README screenshots, catalog archive column/behavior, v0.1.1 metadata; 136 tests passing.
- **2026-05-07** (human) [019-pack-impr.md](019-pack-impr.md) — requests a `checklister` subagent, non-overlapping `AGENTS.md` sections, mandatory 3x parallel final-reviewer gate, and a generic worktree helper for README.
- **2026-05-07** (agent) [020-pack-improvement-summary.md](020-pack-improvement-summary.md) — shipped `checklister` subagent, refactored pack workflow sections, worktree helper under `examples/`, and v0.1.2 release metadata.
