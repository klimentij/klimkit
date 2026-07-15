# LOG — 004-040526-bug-fixes

> Migrated 2026-07-15 from `.klimkit/tasks/01-tui-ux-multi-harness-more/`; predates the
> phase convention — authorship below is recovered from the old `-h-` (human) / `-a-`
> (agent) file names.

- **2026-05-04** (human) [001-bug.md](001-bug.md) — bug report: Mac client-only install's code-server iframe loads the central dev-vm instead of the Mac's own Tailscale Serve URL (`image.png`).
- **2026-05-04** (agent) [002-client-code-server-bug.md](002-client-code-server-bug.md) — root-caused missing/incorrect client DNS resolution; fixed Tailscale lookup, Serve config, and iframe URL derivation, with live verification.
- **2026-07-15** (agent) [003-durable-rulings.md](003-durable-rulings.md) — migrated 2 durable rulings from the retired `docs/agents/memory.md` during `docs/agents` dissolution.
