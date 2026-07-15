# LOG — 001-260526-checklist-and-implementation

- **2026-05-26** (agent) [001-acceptance-checklist.md](001-acceptance-checklist.md) — checklist for preserving machine-local Codex plugin/connector stanzas across `kk apply`/autosync, with deterministic pack-vs-local precedence and no secrets leaking into the source-controlled pack.
- **2026-05-26** (agent) [002-proof.md](002-proof.md) — implemented table-level config merge preservation in `src/klimkit/install.py`, added regression tests for local Slack-style plugin/runtime tables, and tightened `config.toml`/backup file mode to `0600` after a security review finding.
- **2026-07-15** (agent) [003-reflection-archive.md](003-reflection-archive.md) — migrated the two 2026-05-26 reflection sessions verbatim from the retired `docs/agents/reflection.md` during `docs/agents` dissolution.
