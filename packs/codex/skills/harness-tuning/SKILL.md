---
name: harness-tuning
description: Tune __HUMAN_NAME__'s shared Codex home-level harness pack safely through the Klimkit repo, not by editing generated files in ~/.codex directly.
---

# Harness Tuning

Use this skill when __HUMAN_NAME__ asks to change shared Codex behavior, subagents, skills, hooks, model defaults, or other home-level harness files.

Current projected artifact workflow: `__KLIMKIT_ARTIFACT_WORKFLOW__`; operator folder: `__KLIMKIT_OPERATOR_FOLDER__`; writable artifact root: `__KLIMKIT_ARTIFACT_ROOT__`.

This skill runs as one active operator. In team workflow, use other operators' `.klimkit/<operator>/` files as readable team context with attribution, and write tuning notes, memories, logs, reflection, task proof, and reports only under the current operator root.

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
3. When integrating external advice, synthesize it into the existing pack instead of pasting template blocks; check `AGENTS.md`, subagents, skills, and tests for duplicate or conflicting guidance.
4. For UI-impacting workflow changes, require proof reports under the configured writable reports directory (solo `.klimkit/reports/`, team `__KLIMKIT_REPORTS_PATH__/`) with Git-tracked HTML plus screenshot/video evidence, display media as full-width sections, prefer MP4 report videos for Chrome/PWA scrubbing, and include the Tailscale-served report URL in the final handoff when available.
5. Make the smallest source-pack edit that solves the request.
6. Run `uv run python -m unittest tests.test_codex_pack_validation -q`.
7. Run broader tests when hooks, config parsing, or Klimkit install/apply behavior changed.
8. Run `kk preview` for machine-affecting projection changes when useful.
9. Run `kk apply` to make changes live on the current VM when the user wants the current VM updated now.
10. Before final reviewers on non-trivial implementation work, run the Reflection Gate: append a full-timestamped cross-task Reflection Log session to the configured writable reflection file (solo `.klimkit/reflection.md`, team `__KLIMKIT_REFLECTION_PATH__`), using `Observations`, `Derived Pattern`, `Insight`, and `Next Probe` by default with up to ten named sections when useful; preserve older reflection formats by appending a normalized entry when relevant; reconsider the result; and rerun impacted checks if reflection exposes a gap.
11. Commit and push when the change should autosync to other Klimkit machines.

## Safety Note

The default pack is tuned for a dedicated VM or external sandbox where yolo-mode Codex is acceptable. Before broadening permissions, check that the VM has minimal secrets, minimal cloud credentials, and only the network/file access needed for the work.
