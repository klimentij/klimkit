---
name: klimkit-workflow
description: Use Klimkit's Codex workflow for implementation tasks that need inspectable task notes, verification evidence, reflection, and final review.
---

# Klimkit Workflow

Use this skill when the user asks for Klimkit, asks for a checklist/proof-driven implementation, or wants Codex work to leave durable project evidence.

## Default Path

- Prefer the Codex app for day-to-day multi-machine interaction, remote follow-up, and live thread control.
- Use this plugin for reusable workflow guidance and skills.
- Use the full Klimkit repo-managed path only when the user needs machine orchestration, code-server profile projection, Switchboard, Tailscale Serve, Stop hooks, or home-level Codex config/subagent projection.

## Working Rules

1. Read the repository instructions, relevant task notes, memory/log files, and nearby tests before editing.
2. For implementation work, create or update an agent-authored acceptance checklist under `.klimkit/tasks/<feature>/`.
3. Keep edits scoped to the request and reuse existing project conventions.
4. Run verification that matches the blast radius. For UI work, include actual screen evidence and a proof report under `.klimkit/reports/`.
5. Record meaningful verification and skipped checks in a task proof note.
6. For non-trivial work, append a timestamped reflection session to `.klimkit/reflection.md` after verification and before final review.
7. Run final review before claiming completion. Use the repository's local instructions for the required reviewer count.

## Repo-Managed Harness Reference

This plugin includes public-safe reference material from Klimkit's repo-managed harness in `reference/`:

- `reference/AGENTS.md`
- `reference/agents/`
- `reference/config.toml`
- `reference/hooks/stop-notify.sh`

Those files document the repo-managed harness. They are not automatically projected into `~/.codex/` by installing the plugin. For that, clone Klimkit and use `kk apply`.
