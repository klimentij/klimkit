# LOG — 006-200526-telegram-iframe-url-and-grill-me

Added a secondary direct Tailscale code-server URL alongside the primary Switchboard link in every
Telegram notification path, and imported the external `grill-me` skill from `mattpocock/skills`
into the source-controlled Codex pack.

> Migrated 2026-07-15 from `.klimkit/tasks/06-telegram-iframe-url-and-grill-me/`; predates the
> phase convention — artifacts are flat numbered files. Authorship below is recovered from the old
> `-h-`(human) / `-a-`(agent) file names (both artifacts here were agent-authored).

- **2026-05-20** (agent) [001-acceptance-checklist.md](001-acceptance-checklist.md) — checklist for adding secondary direct code-server URLs to all Telegram notification paths (CLI, supervisor autosync, Switchboard, Codex stop-hook) and importing `grill-me`; the Final Review Gate item is left unchecked in this recovered checklist.
- **2026-05-20** (agent) [002-implementation-proof.md](002-implementation-proof.md) — implemented `build_direct_code_server_url` across CLI/supervisor/Switchboard/stop-hook, added `packs/codex/skills/grill-me/SKILL.md`, ran the full suite (173 tests), and fixed a stop-hook quoting bug that final review caught.
