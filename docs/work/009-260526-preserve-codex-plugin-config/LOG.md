# LOG — 009-260526-preserve-codex-plugin-config

Fixed `kk apply` clobbering VM-local Codex plugin/connector config (e.g. a connected Slack
plugin) by making config projection merge-preserve local tables instead of overwriting
`~/.codex/config.toml` wholesale.

> Migrated 2026-07-15 from `.klimkit/tasks/09-preserve-codex-plugin-config/`; predates the
> phase convention — artifacts are flat numbered files. Authorship below is recovered from
> the old `-h-`(human) / `-a-`(agent) file names.

- **2026-05-26** (agent) [001-acceptance-checklist.md](001-acceptance-checklist.md) — checklist for preserving machine-local Codex plugin/connector stanzas across `kk apply`/autosync, with deterministic pack-vs-local precedence and no secrets leaking into the source-controlled pack.
- **2026-05-26** (agent) [002-proof.md](002-proof.md) — implemented table-level config merge preservation in `src/klimkit/install.py`, added regression tests for local Slack-style plugin/runtime tables, and tightened `config.toml`/backup file mode to `0600` after a security review finding.
