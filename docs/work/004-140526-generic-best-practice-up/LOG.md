# LOG — 004-140526-generic-best-practice-up

Folded a viral 12-rule CLAUDE.md best-practices article (Karpathy's original 4 plus 8 more) into
the shared Codex `AGENTS.md` pack — excluding the token-budget rule — and cross-checked the
`mattpocock/skills` repo for further takeaways; released as v0.1.6.

> Migrated 2026-07-15 from `.klimkit/tasks/04-generic-best-practice-up/`; predates the phase
> convention — artifacts are flat numbered files. Authorship below is recovered from the old
> `-h-`(human) / `-a-`(agent) file names; `image.png` carried no marker and is treated as part of
> the human's original request package.

- **2026-05-14** (human) [001-in.md](001-in.md) — Klim pastes the "Karpathy's 4 CLAUDE.md rules... I added 8 more" article and asks to carefully integrate the 12 rules (minus token budget) into `AGENTS.md`, auditing all subagents/skills for duplication.
- **2026-05-14** (human) [image.png](image.png) — screenshot attached to the request, referenced inline (`![alt text](image.png)`), carrying additional no-hacks / robust-design / fail-loud guidance to integrate.
- **2026-05-14** (agent) [002-notes.md](002-notes.md) — integrated the 12-rule guidance into existing `AGENTS.md` sections, audited subagents/skills, and analyzed `mattpocock/skills` for extra Klimkit takeaways; stopped before commit/apply so Klim could review first.
- **2026-05-14** (agent) [003-release-proof.md](003-release-proof.md) — after review, projected the pack via `kk apply`, ran full validation, and published release v0.1.6 "generic agent best practices".
