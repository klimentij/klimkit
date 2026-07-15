# LOG — 001-240526-checklist-and-implementation

- **2026-05-24** (agent) [001-acceptance-checklist.md](001-acceptance-checklist.md) — blocking checklist for the deep link: use the raw hook `session_id` (not `turn_id`/rollout filename), omit the link when absent, keep Switchboard/code-server links intact, and gate on tests/release/reflection/final-review.
- **2026-05-24** (agent) [002-implementation-proof.md](002-implementation-proof.md) — implemented the link in `packs/codex/hooks/stop-notify.sh`, added hook test coverage, verified projection on the VM, pushed commit `2e91197`, and published release `v0.1.11`.
- **2026-07-15** (agent) [003-reflection-archive.md](003-reflection-archive.md) — migrated the 2026-05-24 reflection session verbatim from the retired `docs/agents/reflection.md` during `docs/agents` dissolution.
