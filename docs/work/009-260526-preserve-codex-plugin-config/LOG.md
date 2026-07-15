# LOG — 009-260526-preserve-codex-plugin-config

Fixed `kk apply` clobbering VM-local Codex plugin/connector config (e.g. a connected Slack
plugin) by making config projection merge-preserve local tables instead of overwriting
`~/.codex/config.toml` wholesale.

> Migrated 2026-07-15 from `.klimkit/tasks/09-preserve-codex-plugin-config/`; predates the
> phase convention — artifacts are flat numbered files. Authorship below is recovered from
> the old `-h-`(human) / `-a-`(agent) file names.

- **05-26** [001-260526-checklist-and-implementation](001-260526-checklist-and-implementation/) — checklist plus merge-preservation implementation in `src/klimkit/install.py`, with regression tests and a `0600` file-mode fix (agent).
