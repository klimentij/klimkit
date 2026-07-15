# Klimkit Skill State And Config

Installed skills should be treated as immutable package content. Do not write operator preferences, report-server ports, tokens, or run state into `skills/`, `~/.codex/skills/`, or an installed skill cache. Skill updates may replace those files.

## Storage Locations

Use this precedence when a Klimkit skill needs configuration:

1. Current user request.
2. Repo instructions (`AGENTS.md`) and tracked project docs.
3. User-global defaults: `${XDG_CONFIG_HOME:-~/.config}/klimkit/config.toml`.
4. Ask the user.

Project evidence belongs under `docs/work/` (see
[artifact-workflow.md](artifact-workflow.md)). User-global defaults are for machine/user
preferences that should apply across projects. Runtime logs, sockets, and non-portable
state belong under `${XDG_STATE_HOME:-~/.local/state}/klimkit/` when they are not part of
a repository proof trail.

## Operator Discovery

When setup starts, inspect these sources in order:

1. The current request.
2. User-global defaults: `${XDG_CONFIG_HOME:-~/.config}/klimkit/config.toml`.
3. Git identity (`git config user.name`).

If the sources point to exactly one operator, use it and tell the user what was inferred.
If there are several candidates, ask the user to choose from them or provide a different
operator name. The operator name is attribution metadata for `LOG.md` entries and
notifications; it no longer creates per-operator folders.

## Global Defaults Example

```toml
[defaults]
operator = "Klim"
artifact_layout = "docs-first"

[agent]
personality_name = "Steady Operator"
personality_description = "Direct, careful, evidence-first, and conservative with scope."

[reports]
host = "127.0.0.1"
port = 8765
tailnet_url = ""
```

`klimkit-setup` should still ask for the operator name when discovery is ambiguous. If a global default exists, offer it as the default answer instead of silently choosing it when other sources suggest another operator.

## Safety

- Never commit the global config file or machine-local runtime state.
- Keep secrets out of config files; use environment variables or the user's secret manager.
- Keep shared project decisions in tracked docs or work notes, not in the installed skill package.
