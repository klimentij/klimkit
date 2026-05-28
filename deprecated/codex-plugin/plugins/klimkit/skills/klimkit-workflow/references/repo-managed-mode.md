# Repo-Managed Mode

Use this reference when a user asks how the public plugin relates to the full Klimkit repo.

## Plugin Boundary

Installing the Klimkit plugin loads bundled skills. It does not rewrite `~/.codex/AGENTS.md`, `~/.codex/config.toml`, local subagent TOML, Stop hooks, connector state, code-server settings, services, Tailscale Serve, Switchboard, or Telegram notifications.

## `kk apply` Boundary

The repo-managed path is for users who want Klimkit to project and manage machine-level files:

- `packs/codex/AGENTS.md` to `~/.codex/AGENTS.md`
- `packs/codex/config.toml` to `~/.codex/config.toml`
- `packs/codex/agents/` to `~/.codex/agents/`
- `packs/codex/skills/` to `~/.codex/skills/`
- `packs/codex/hooks/` to `~/.codex/hooks/`
- code-server, Switchboard, report serving, Tailscale Serve, and service manager files

Use `harness-tuning` for changes to that source pack. Preserve VM-local plugin, connector, MCP, project trust, and hook trust state; do not copy those tables into public plugin files.

Autosync and Telegram notifications are opt-in machine automation. Do not imply the public plugin enables either one.
