# LOG — 008-260526-codex-stop-thread-deeplink

Added a `codex://threads/<session_id>` deep link to Codex Telegram stop notifications so
Klim can jump straight into the originating Codex app thread.

> Migrated 2026-07-15 from `.klimkit/tasks/08-codex-stop-thread-deeplink/`; predates the
> phase convention — artifacts are flat numbered files. Authorship below is recovered from
> the old `-h-`(human) / `-a-`(agent) file names.

- **2026-05-24** (agent) [001-acceptance-checklist.md](001-acceptance-checklist.md) — blocking checklist for the deep link: use the raw hook `session_id` (not `turn_id`/rollout filename), omit the link when absent, keep Switchboard/code-server links intact, and gate on tests/release/reflection/final-review.
- **2026-05-24** (agent) [002-implementation-proof.md](002-implementation-proof.md) — implemented the link in `packs/codex/hooks/stop-notify.sh`, added hook test coverage, verified projection on the VM, pushed commit `2e91197`, and published release `v0.1.11`.
