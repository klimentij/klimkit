# LOG — 010-270526-codex-plugin-first

Extracted Klimkit's Codex harness into a public, installable Codex plugin and repositioned
the Codex app plus plugin as the default README path over Switchboard/fork-and-apply.

> Migrated 2026-07-15 from `.klimkit/tasks/10-codex-plugin-first/`; predates the phase
> convention — artifacts are flat numbered files. Authorship below is recovered from the
> old `-h-`(human) / `-a-`(agent) file names.

- **2026-05-27** (agent) [001-acceptance-checklist.md](001-acceptance-checklist.md) — blocking checklist for extracting the harness into a public plugin: manifest validity, no VM-local state leakage, marketplace policy, README repositioning, and publish/release/final-review gates.
- **2026-05-27** (agent) [002-proof.md](002-proof.md) — built `plugins/klimkit` plus the repo marketplace, reworked README to plugin-first with Switchboard/`kk apply` as secondary, published via PR #2 merged to `main`, released `v0.1.15`, and verified live install/upgrade on the VM.
