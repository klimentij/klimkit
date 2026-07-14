# LOG — 014-280526-root-skills-library

Building Klimkit's first root `skills/` package in Vercel Agent Skills format as the
primary distribution surface, deprecating the legacy runtime/plugin projection.

> Migrated 2026-07-15 from `.klimkit/tasks/14-root-skills-library/`; predates the phase
> convention — artifacts are flat numbered files. Authorship below is recovered from the
> old `-h-`(human) / `-a-`(agent) file names.

- **2026-05-28** (human) [001-request.md](001-request.md) — Klim asks for a first reviewable root `skills/` package; scope amendments add operator config storage (`.klimkit/<operator>/config.toml`), drop tracker/board/triage/control-plane skills, and deprecate everything outside root `skills/`.
- **2026-05-28** (agent) [002-acceptance-checklist.md](002-acceptance-checklist.md) — Blocking checklist: first-wave skill scope, operator/personality setup behavior, config storage locations, legacy deprecation, and validation requirements.
- **2026-05-28** (agent) [003-implementation-proof.md](003-implementation-proof.md) — Added 7 root skills (workflow, setup, diagnose, tdd, report-server, walkthrough, worktree-stack), moved the legacy runtime under `deprecated/`, documented scope changes (operator subfolders, dropped tracker skills), and ran quick_validate/unittest/`npx skills add --list`/privacy greps.
