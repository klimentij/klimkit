# Klimkit Skill State And Config

Installed skills should be treated as immutable package content. Do not write operator preferences, report-server ports, tokens, or run state into `skills/`, `~/.codex/skills/`, or an installed skill cache. Skill updates may replace those files.

## Storage Locations

Use this precedence when a Klimkit skill needs configuration:

1. Current user request.
2. Project-local operator config: `.klimkit/<operator>/config.toml`.
3. User-global defaults: `${XDG_CONFIG_HOME:-~/.config}/klimkit/config.toml`.
4. Ask the user.

Project-local evidence belongs under `.klimkit/<operator>/`. User-global defaults are for machine/user preferences that should apply across projects. Runtime logs, sockets, and non-portable state belong under `${XDG_STATE_HOME:-~/.local/state}/klimkit/` when they are not part of a repository proof trail.

## Operator Discovery

When setup starts, inspect these sources in order:

1. Current repo `.klimkit/<operator>/config.toml`.
2. Current repo `.klimkit/<operator>/` folders that are not reserved names.
3. Home Klimkit repo operator config or folders, usually under `~/klimkit/.klimkit/`.
4. User-global defaults.

If the sources point to exactly one operator, use it and tell the user what was inferred. If there are several candidates, ask the user to choose from them or provide a different operator name. If the user chooses a new operator name, create that operator skeleton in the current repo and, when the home Klimkit repo exists, in the home repo too.

## Global Defaults Example

```toml
[defaults]
operator = "Klim"
artifact_layout = "operator-scoped"

[agent]
personality_name = "Steady Operator"
personality_description = "Direct, careful, evidence-first, and conservative with scope."

[reports]
host = "127.0.0.1"
port = 8765
tailnet_url = ""
```

`klimkit-setup` should still ask for the operator name when discovery is ambiguous. If a global default exists, offer it as the default answer instead of silently choosing it when repo-local folders suggest another operator.

## Safety

- Never commit the global config file or machine-local runtime state.
- Keep secrets out of `.klimkit/<operator>/config.toml`; use environment variables or the user's secret manager.
- Keep shared project decisions in tracked docs or task notes, not in the installed skill package.
