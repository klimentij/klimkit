---
name: harness-tuning
description: Safe edits to Klimkit's repo-managed Codex harness pack, including shared AGENTS guidance, model config, subagents, hooks, and bundled skills. Use when the user asks to change `packs/codex/` behavior or `kk apply` projections, not for normal plugin-only workflow use.
---

# Harness Tuning

Tune Klimkit's repo-managed Codex harness from the source pack. Do not edit generated files under `~/.codex/`; those are overwritten by `kk apply`, `kk pull`, and daemon sync.

## Ground Rules

- Work from the Klimkit repo root.
- Edit source pack files under `packs/codex/`.
- Keep pack files hand-authored and reviewable. Avoid generated bulk output unless the user explicitly asks for a generated artifact.
- After pack edits, run the relevant pack validation tests and then `kk apply` if the current VM should use the change immediately.
- Push committed pack changes to `main` only when the user wants the update published. Machines with autosync enabled apply `main`; autosync is opt-in.

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
4. For UI-impacting workflow changes, require proof reports under the configured writable reports directory (solo `.klimkit/reports/`, team `.klimkit/<operator>/reports/`) with Git-tracked HTML plus screenshot/video evidence, display media as full-width sections, prefer MP4 report videos for Chrome/PWA scrubbing, and include the Tailscale-served report URL in the final handoff when available.
5. Make the smallest source-pack edit that solves the request.
6. Run `uv run python -m unittest tests.test_codex_pack_validation -q`.
7. Run broader tests when hooks, config parsing, or Klimkit install/apply behavior changed.
8. Run `kk preview` for machine-affecting projection changes when useful.
9. Run `kk apply` to make changes live on the current VM when the user wants the current VM updated now.
10. Before final reviewers on non-trivial implementation work, run the Reflection Gate: append a full-timestamped cross-task Reflection Log session to the configured writable reflection file (solo `.klimkit/reflection.md`, team `.klimkit/<operator>/reflection.md`), using `Observations`, `Derived Pattern`, `Insight`, and `Next Probe` by default with up to ten named sections when useful; preserve older reflection formats by appending a normalized entry when relevant; reconsider the result; and rerun impacted checks if reflection exposes a gap.
11. Commit and push when the change should autosync to other Klimkit machines.

## Safety Note

The default pack is tuned for a dedicated VM or external sandbox where yolo-mode Codex is acceptable. Before broadening permissions, check that the VM has minimal secrets, minimal cloud credentials, and only the network/file access needed for the work.
