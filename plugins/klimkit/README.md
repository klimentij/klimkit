# Klimkit Codex Plugin

Klimkit packages the reusable part of the repo-managed Codex harness as a public Codex plugin.

## Installed Surfaces

- `skills/` contains the installable Codex skills.
- `skills/klimkit-workflow/` is the plugin-first workflow entry point for project evidence, checklist-driven implementation, verification, reflection, and final review.
- `reference/` carries public-safe reference material from the Klimkit harness pack: `AGENTS.md`, subagent TOML, config defaults, and the Stop notification hook.

Codex plugins install bundled skills directly. Home-level `AGENTS.md`, `config.toml`, subagent TOML, and notification hooks are still machine-level Codex configuration. Use the repo-managed `kk apply` path when you want Klimkit to project those files into `~/.codex/` and manage code-server, Switchboard, Tailscale Serve, or service restart behavior.

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
