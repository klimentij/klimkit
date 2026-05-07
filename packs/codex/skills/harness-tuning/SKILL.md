---
name: harness-tuning
description: Tune __HUMAN_NAME__'s shared Codex home-level harness pack safely through the Klimkit repo, not by editing generated files in ~/.codex directly.
---

# Harness Tuning

Use this skill when __HUMAN_NAME__ asks to change shared Codex behavior, subagents, skills, hooks, model defaults, or other home-level harness files.

## Ground Rules

- Work from `~/klimkit`.
- Edit source pack files under `~/klimkit/packs/codex/`.
- Do not edit generated projections in `~/.codex/` directly. They are overwritten by `kk apply`, `kk pull`, and daemon autosync.
- Keep pack files hand-authored and reviewable. Avoid generated bulk output unless the user explicitly asks for a generated artifact.
- After pack edits, run the relevant pack validation tests and then `kk apply` if the current VM should use the change immediately.
- Push committed pack changes to `main` when __HUMAN_NAME__ wants the update everywhere. Machines with autosync enabled poll `origin/main` every 5 seconds by default, fast-forward, apply projections, restart managed services, and send Telegram summaries when configured.

## Source Map

- `packs/codex/AGENTS.md` projects to `~/.codex/AGENTS.md`.
- `packs/codex/config.toml` projects to `~/.codex/config.toml`.
- `packs/codex/agents/` projects to `~/.codex/agents/`.
- `packs/codex/skills/` projects to `~/.codex/skills/`.
- `packs/codex/hooks/` projects to `~/.codex/hooks/`.

## Workflow

1. Read the existing pack file that owns the behavior.
2. For implementation work, create or update the task acceptance checklist before editing source-pack files.
3. Make the smallest source-pack edit that solves the request.
4. Run `uv run python -m unittest tests.test_codex_pack_validation -q`.
5. Run broader tests when hooks, config parsing, or Klimkit install/apply behavior changed.
6. Run `kk preview` for machine-affecting projection changes when useful.
7. Run `kk apply` to make changes live on the current VM.
8. Commit and push when the change should autosync to other Klimkit machines.

## Safety Note

The default pack is tuned for a dedicated VM or external sandbox where yolo-mode Codex is acceptable. Before broadening permissions, check that the VM has minimal secrets, minimal cloud credentials, and only the network/file access needed for the work.
