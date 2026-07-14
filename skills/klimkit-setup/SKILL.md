---
name: klimkit-setup
description: Set up Klimkit's docs-first repo context for agent work. Use when adding the `docs/work/` journal layout, `docs/agents/` state files, repo skill pointers, config state, or onboarding instructions to a project that should use Klimkit workflows.
---

# Klimkit Setup

Use this when a repository needs the Klimkit evidence layout and skill routing made explicit. Keep the setup small and reviewable.

## Setup Workflow

1. Resolve the operator name before creating or migrating files:
   - Check the current request and `${XDG_CONFIG_HOME:-~/.config}/klimkit/config.toml`.
   - Check git identity (`git config user.name`) as a fallback candidate.
   - If there is no single clear match, ask the user to choose or provide a name. The
     operator name is used for attribution in work `LOG.md` entries.
2. Ask the user to choose an agent personality, offering two or three options plus a custom name and one-sentence description:
   - `Steady Operator`: Direct, careful, evidence-first, and conservative with scope.
   - `Product Engineer`: Pragmatic, user-facing, and focused on shipping inspectable behavior.
   - `Research Scribe`: Methodical, source-backed, and explicit about assumptions and decisions.
3. Read existing repo instructions: `AGENTS.md`, `CONTEXT.md`, `CONTEXT-MAP.md`, `docs/adr/`, `README.md`, and any existing `docs/work/` or legacy `.klimkit` files.
4. Create the docs-first evidence layout only when meaningful work is starting:
   - `docs/work/README.md` — the one-page work-journal convention described in [references/artifact-workflow.md](references/artifact-workflow.md).
   - `docs/work/.gitignore` — ignoring `**/.local/`.
   - `docs/agents/memory.md`, `docs/agents/log.md`, `docs/agents/reflection.md`.
5. If the repo has a legacy `.klimkit/` evidence tree, offer to migrate it into `docs/work/` (one work folder per legacy task, authorship recovered into `LOG.md` files) instead of leaving two layouts side by side.
6. Write the selected operator and agent personality to `${XDG_CONFIG_HOME:-~/.config}/klimkit/config.toml`.
7. Add a short repo instruction block only if the repo lacks one. Prefer updating existing `AGENTS.md` over inventing a second instruction file; add a `CLAUDE.md → AGENTS.md` symlink so Claude Code loads the same instructions. The block should cover the work-log rules: journal live, keep phase `LOG.md` updated, preserve every human message verbatim in exactly one note, never bulk-load `docs/work/`.
8. Add or update lightweight context docs when useful:
   - `docs/agents/domain.md` for project language and invariants.
9. Recommend relevant Klimkit skills by name in the repo instructions: `klimkit-implement`, `klimkit-diagnose`, `klimkit-tdd`, `klimkit-walkthrough`, `klimkit-report-server`, and `klimkit-create-worktree`.
10. Verify that new docs do not expose secrets, machine-local paths, private repo names, or local runtime state.

## Boundaries

- Do not copy `~/.codex` files into the repository.
- Do not set up deprecated Klimkit runtime services, notification hooks, dashboards, machine-sync scripts, or browser IDE profiles as part of skills-first setup.
- Do not commit tokens, runtime DBs, or anything under a `.local/` folder.
- Keep setup docs stable and human-editable; work evidence belongs in `docs/work/<NNN-DDMMYY-slug>/`.
- Do not store mutable operator state inside installed skill folders. Skill updates may replace those files.

Read [references/artifact-workflow.md](references/artifact-workflow.md) before creating or migrating evidence files.
Read [references/state-config.md](references/state-config.md) before saving operator defaults, report-server settings, or other mutable configuration.
