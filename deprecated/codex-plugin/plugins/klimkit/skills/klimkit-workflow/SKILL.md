---
name: klimkit-workflow
description: Klimkit's evidence-first Codex workflow for implementation, debugging, review, and release tasks. Use when a user asks for Klimkit, wants checklist/proof-driven work, needs `.klimkit` task artifacts, or expects verification, reflection, and final review before handoff.
---

# Klimkit Workflow

## Default Path

- Prefer the Codex app for day-to-day multi-machine interaction, remote follow-up, and live thread control.
- Use this plugin for reusable workflow guidance and skills.
- For Git-backed plugin updates, refresh the marketplace snapshot and re-add the plugin so the local cache moves to the new version.
- Use the full Klimkit repo-managed path only when the user needs machine orchestration, code-server profile projection, Switchboard, Tailscale Serve, Stop hooks, or home-level Codex config/subagent projection.

## Workflow

1. Read the repository instructions, relevant task notes, memory/log files, and nearby tests before editing.
2. For implementation work, write an agent-authored acceptance checklist under `.klimkit/tasks/<feature>/`.
3. Keep edits scoped to the request and reuse existing project conventions.
4. Run verification that matches the blast radius. For UI work, include real screen evidence and a proof report under `.klimkit/reports/`.
5. Record meaningful verification, skipped checks, and residual risk in a task proof note.
6. For non-trivial work, append a timestamped reflection session to `.klimkit/reflection.md` after verification and before final review.
7. Run final review before claiming completion. Use the repository's local instructions for the required reviewer count.

## References

- Read `references/artifact-workflow.md` when the task needs concrete `.klimkit` task, proof, memory, log, report, or reflection layout.
- Read `references/repo-managed-mode.md` when the user asks how the plugin differs from `kk apply`, Switchboard, hooks, code-server, Tailscale Serve, or repo-managed Codex config.

Keep reference loading targeted. Do not load both references by default when the body above is enough.
