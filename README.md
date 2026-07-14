# Klimkit

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Skills: Vercel CLI](https://img.shields.io/badge/Skills-Vercel%20CLI-edfff5.svg)](https://github.com/vercel-labs/skills)
[![skills.sh](https://skills.sh/b/klimentij/klimkit)](https://skills.sh/klimentij/klimkit)
[![Agent Skills](https://img.shields.io/badge/Format-Agent%20Skills-7ef0af.svg)](https://agentskills.io/specification)

![Klimkit. Agentic engineering across machines, under control.](assets/brand/klimkit-readme-hero.jpg)

Klimkit is a skills library for agentic engineering work. Install it with the Vercel Skills CLI to give agents reusable workflows for docs-first project setup, implementation workflow, acceptance checklists, code exploration, security review, reflection, final review, plan grilling, diagnosis, TDD, walkthrough reports, local report serving, isolated worktrees, and multi-machine harness cleanup.

The old Klimkit runtime is deprecated. Switchboard, `kk`, `klimkit`, `install.sh`, the Python package, Codex pack projection, service templates, Bash helpers, autosync, Telegram notifications, and the Codex plugin prototype live under `deprecated/` for source reference and manual legacy use. New Klimkit behavior should live in root `skills/`.

## Quick Install

Install all Klimkit skills globally for Codex:

```bash
npx skills add klimentij/klimkit --skill '*' -g -a codex -y
```

List available skills:

```bash
npx skills add klimentij/klimkit --list
```

Install the main implementation workflow skill:

```bash
npx skills add klimentij/klimkit --skill klimkit-implement -g -a codex -y
```

Update installed skills:

```bash
npx skills update -g -y
```

For local review from this checkout:

```bash
npx skills add ./ --list
```

## Repo Setup

Ask your agent to use `klimkit-setup` when a repo has no Klimkit context. The setup skill resolves an operator name (used for attribution in work logs) by checking the current request, `${XDG_CONFIG_HOME:-~/.config}/klimkit/config.toml`, and git identity. If discovery is ambiguous, it asks you to choose or provide a name.

New skills-first evidence is docs-first — a git-tracked work journal plus project agent state:

```text
docs/work/<NNN-DDMMYY-slug>/           # one folder per piece of work, journaled live
docs/work/<work>/<NNN-DDMMYY-slug>/    # phase folders: one logical human+agent iteration
docs/work/<work>/<phase>/LOG.md        # timestamped beats: one-liner, who drove, file links
docs/work/README.md                    # the one-page convention
docs/agents/memory.md                  # durable preferences, corrections, process rules
docs/agents/log.md                     # timestamped action history
docs/agents/reflection.md              # append-only cross-task synthesis
```

Each work folder reads like a story: what the human asked (preserved verbatim), what the agent did, what they decided together, and why. Self-contained HTML reports are numbered artifacts inside phases; heavy media stays in gitignored `.local/` folders. See [docs/work/README.md](docs/work/README.md) for the full convention — this repo's own history under [docs/work/](docs/work/) is the first instance of it.

Setup also asks for an agent personality. It offers built-in options such as `Steady Operator`, `Product Engineer`, and `Research Scribe`, and lets you provide a custom name plus one-sentence description. User-global defaults go in `${XDG_CONFIG_HOME:-~/.config}/klimkit/config.toml`.

Installed skill folders are package content, not mutable state. Do not write operator preferences, report ports, tokens, or runtime state into installed skill directories.

## Skills

The root `skills/` package is the product:

- `klimkit-implement`: skills-first implementation workflow replacing the old global `AGENTS.md` flow.
- `klimkit-setup`: docs-first `docs/work/` + `docs/agents/` setup, operator discovery, config state, and repo context pointers.
- `klimkit-checklister`: blocking pass/fail acceptance checklists before implementation.
- `klimkit-code-explorer`: read-only execution-path tracing before edits.
- `klimkit-security-auditor`: focused auth, secrets, data exposure, sandbox, infra, DevSecOps, data-flow, and compliance review.
- `klimkit-reflector`: concise cross-task reflection after verification.
- `klimkit-final-reviewer`: fresh-context final acceptance review, designed for the final subagent gate.
- `klimkit-grill-me`: one-question-at-a-time plan interrogation with short decision tracking in the `docs/work/` journal.
- `klimkit-diagnose`: reproduce-first debugging and regression proof.
- `klimkit-tdd`: narrow red-green-refactor loops with proof.
- `klimkit-report-server`: local/Tailscale serving checks for `docs/work` proof reports.
- `klimkit-walkthrough`: static HTML walkthrough reports with media and redaction checks.
- `klimkit-create-worktree`: deterministic isolated Git worktrees for parallel agent work, including dev-from-main sync flows.
- `klimkit-codex-control`: agent-neutral control of OpenAI Codex sessions through the CLI or live desktop app-server.
- `klimkit-harness-cleanup`: two-phase inventory, recommendation, explicit approval, quarantine, cleanup, and verification for Codex and Claude Code across local and remote machines.
- `klimkit-agent-browser`: imported via Vercel Skills CLI from `vercel-labs/agent-browser`.
- `klimkit-web-design-guidelines`: imported via Vercel Skills CLI from `vercel-labs/agent-skills`.
- `klimkit-ui-ux-pro-max`: imported via Vercel Skills CLI from `nextlevelbuilder/ui-ux-pro-max-skill`.
- `klimkit-improve-codebase-architecture`: imported via Vercel Skills CLI from `mattpocock/skills`.
- `klimkit-impeccable`: imported via Vercel Skills CLI from `pbakaus/impeccable`.

Issue trackers, project boards, triage, and tracker control-plane skills are intentionally out of scope for this first skills-only version.

## Legacy Runtime

Legacy code remains available, but it is no longer the default path:

- [deprecated/runtime/install.sh](deprecated/runtime/install.sh): old installer entry point.
- [deprecated/runtime/kk](deprecated/runtime/kk): old `kk` launcher.
- [deprecated/runtime/klimkit](deprecated/runtime/klimkit): old `klimkit` launcher.
- [deprecated/runtime/src/klimkit/](deprecated/runtime/src/klimkit/): old Python package and runtime modules.
- [deprecated/runtime/src/klimkit/apps/switchboard/](deprecated/runtime/src/klimkit/apps/switchboard/): Switchboard source.
- [deprecated/runtime/src/klimkit/tools/](deprecated/runtime/src/klimkit/tools/): Bash/Python helper tools.
- [deprecated/runtime/packs/codex/](deprecated/runtime/packs/codex/): old projected Codex pack.
- [deprecated/runtime/templates/](deprecated/runtime/templates/): old service and code-server templates.
- [deprecated/runtime/examples/](deprecated/runtime/examples/): old helper scripts.
- [deprecated/runtime/tests/](deprecated/runtime/tests/): old runtime test suite.
- [deprecated/codex-plugin/plugins/klimkit/](deprecated/codex-plugin/plugins/klimkit/): old Codex plugin package.
- [deprecated/codex-plugin/agents-marketplace/](deprecated/codex-plugin/agents-marketplace/): old marketplace metadata.

To experiment with the old runtime from source:

```bash
cd deprecated/runtime
./install.sh
```

Use this only for legacy maintenance. New reusable behavior should be migrated into the owning skill as `SKILL.md`, `references/`, `scripts/`, or `assets/`.

### Legacy Switchboard Screenshots

![Klimkit Switchboard running as a Chrome PWA with code-server and Codex terminal panes.](assets/screenshots/switchboard-pwa-workspace.jpg)

![Klimkit Switchboard workspace catalog with create controls, filters, batch actions, and workspace rows.](assets/screenshots/switchboard-catalog.jpg)

## Development

Validate the root skills package:

```bash
python3 -m unittest discover -s tests -q
npx skills add ./ --list
```

Validate a single skill with Codex's local skill creator tools when available:

```bash
python3 "$HOME/.codex/skills/.system/skill-creator/scripts/quick_validate.py" skills/klimkit-implement
```

Run the fresh-machine Codex smoke test from Docker:

```bash
tests/fresh-codex-smoke/run.sh
```

The smoke test builds a small Linux container, copies only `auth.json` and `installation_id` from your Codex home into a temporary read-only mount, clones this branch, installs the root skills with the Vercel Skills CLI, runs `codex exec`, and verifies that `klimkit-setup` creates the docs-first `docs/work/` + `docs/agents/` skeleton.

## Security

Klimkit proof artifacts are meant to be inspectable, but public artifacts must not expose secrets, private repo names, customer data, private chat, tailnet internals, or local machine paths. Keep secrets in environment variables or your secret manager, not in config files or installed skill folders.

See [SECURITY.md](SECURITY.md) for the concise security notes.
