# Klimkit Codex Plugin

Klimkit packages the reusable Codex workflow and supporting skills as a public Codex plugin.

## Installed Surfaces

- `skills/` contains the installable Codex skills.
- `skills/klimkit-workflow/` is the plugin-first workflow entry point for project evidence, checklist-driven implementation, verification, reflection, and final review.
- Skill-owned `references/` folders carry optional details that should be loaded only when a task needs them.

Codex plugins install bundled skills directly. Home-level `AGENTS.md`, `config.toml`, subagent TOML, notification hooks, code-server profile projection, Switchboard, Tailscale Serve, autosync, and Telegram notifications are still machine-level configuration. Use the repo-managed `kk apply` path when you want Klimkit to project those files into `~/.codex/` and manage local services.

## Install

From Codex CLI:

```bash
codex plugin marketplace add klimentij/klimkit --ref main
codex plugin add klimkit@klimkit
```

Then open a new Codex thread and ask Codex to use Klimkit, or invoke one of the bundled skills directly from the plugin picker.

## Upgrade

```bash
codex plugin marketplace upgrade klimkit
codex plugin add klimkit@klimkit
```

The marketplace refresh pulls the latest Git snapshot. Re-running `codex plugin add` refreshes the installed plugin cache when the plugin version or contents changed.
