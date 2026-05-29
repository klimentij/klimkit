# Sanitized Human Request

Create a first reviewable version of Klimkit's root `skills/` package using the current Vercel/Agent Skills format and the prior public-safe planning note. Check official Vercel skills documentation, the public skills CLI repository, and public Vercel skill examples before authoring the package.

The first wave should add root `skills/<skill-name>/SKILL.md` packages for workflow, setup, diagnose, TDD, issue slicing, triage, report-server, walkthrough, worktree-stack, and GitHub control-plane workflows. The skills must be public-safe: do not copy private source text or private identifiers, and only summarize private candidate patterns at a neutral level.

Keep scope limited to the root skills package and validation/docs needed to review it. Do not change plugin package files or production runtime code unless a small validation or documentation change is necessary and explicitly recorded.

## Scope Amendments

- Klim approved project-local `.klimkit/<operator>/config.toml` plus optional user-global `${XDG_CONFIG_HOME:-~/.config}/klimkit/config.toml`.
- Setup should infer or ask for the operator name, create operator folders in the current repo and home Klimkit repo when a new operator is chosen, and save an agent personality preference.
- Tracker, board, triage, and control-plane skills are removed from this first version. They may be revisited in a later phase.
- Everything except root `skills/` is deprecated; legacy runtime and plugin sources should be reachable under `deprecated/`.
