# Durable rulings — skills-library-build

> Migrated 2026-07-15 from the retired project memory file (`.klimkit/memory.md` →
> `docs/agents/memory.md`); each ruling is dated as originally recorded.

- **2026-05-29** — Klimkit should move old global `AGENTS.md` implementation workflow into root skills, with intermediate roles as inline skills and only final review preferring fresh subagents.
- **2026-05-29** — GitHub releases should have one concise paragraph of high-signal release notes that explains the essence of the change, not only generated changelog links.
- **2026-05-28** — The useful fresh-machine test for Klimkit skills is a Docker smoke that mounts only Codex auth, installs the root skills with the Vercel Skills CLI, runs `codex exec`, and verifies `klimkit-setup` creates an operator-scoped `.klimkit` skeleton.
