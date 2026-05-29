---
name: klimkit-setup
description: Set up operator-scoped Klimkit repo context for agent work. Use when adding operator-scoped `.klimkit` task artifacts, repo skill pointers, domain docs, config state, or onboarding instructions to a project that should use Klimkit workflows.
---

# Klimkit Setup

Use this when a repository needs the Klimkit evidence layout and skill routing made explicit. Keep the setup small and reviewable.

## Setup Workflow

1. Resolve the operator name before creating or migrating files:
   - Check the current request, current repo `.klimkit/*/config.toml`, and current repo operator folders.
   - Check the home Klimkit repo when present, usually `~/klimkit/.klimkit/*/config.toml` and `~/klimkit/.klimkit/*/`.
   - Check `${XDG_CONFIG_HOME:-~/.config}/klimkit/config.toml`.
   - If there is no single clear match, ask the user to choose from inferred operator folder names or provide a different name.
2. Convert the operator name to a filesystem-safe folder, preserving a readable form where possible. Reject reserved names such as `memory.md`, `log.md`, `reflection.md`, `tasks`, `reports`, `local`, `state`, `backups`, `logs`, and `config.toml`.
3. Ask the user to choose an agent personality, offering two or three options plus a custom name and one-sentence description:
   - `Steady Operator`: Direct, careful, evidence-first, and conservative with scope.
   - `Product Engineer`: Pragmatic, user-facing, and focused on shipping inspectable behavior.
   - `Research Scribe`: Methodical, source-backed, and explicit about assumptions and decisions.
4. Read existing repo instructions: `AGENTS.md`, `CONTEXT.md`, `CONTEXT-MAP.md`, `docs/adr/`, `README.md`, and any existing `.klimkit` files.
5. Create missing operator-scoped evidence files only when meaningful work is starting:
   - `.klimkit/<operator>/config.toml`
   - `.klimkit/<operator>/memory.md`
   - `.klimkit/<operator>/log.md`
   - `.klimkit/<operator>/reflection.md`
   - `.klimkit/<operator>/tasks/`
   - `.klimkit/<operator>/reports/`
6. If the user picked a new operator name and a home Klimkit repo exists, create the same `.klimkit/<operator>/` skeleton there too.
7. Write the selected operator and agent personality to `${XDG_CONFIG_HOME:-~/.config}/klimkit/config.toml`; also write project-local operator config to `.klimkit/<operator>/config.toml`.
8. Add a short repo instruction block only if the repo lacks one. Prefer updating existing `AGENTS.md` over inventing a second instruction file.
9. Add or update lightweight context docs when useful:
   - `docs/agents/domain.md` for project language and invariants.
10. Recommend relevant Klimkit skills by name in the repo instructions: `klimkit-workflow`, `klimkit-diagnose`, `klimkit-tdd`, `klimkit-walkthrough`, `klimkit-report-server`, and `klimkit-worktree-stack`.
11. Verify that new docs do not expose secrets, machine-local paths, private repo names, or local runtime state.

## Boundaries

- Do not copy `~/.codex` files into the repository.
- Do not set up deprecated Klimkit runtime services, notification hooks, dashboards, machine-sync scripts, or browser IDE profiles as part of skills-first setup.
- Do not make `.klimkit/local/`, `.klimkit/state/`, `.klimkit/backups/`, `.klimkit/logs/`, tokens, or runtime DBs public.
- Keep setup docs stable and human-editable; task evidence belongs in `.klimkit/<operator>/tasks/`.
- Do not store mutable operator state inside installed skill folders. Skill updates may replace those files.

Read [references/artifact-workflow.md](references/artifact-workflow.md) before creating or migrating `.klimkit` evidence files.
Read [references/state-config.md](references/state-config.md) before saving operator defaults, report-server settings, or other mutable configuration.
