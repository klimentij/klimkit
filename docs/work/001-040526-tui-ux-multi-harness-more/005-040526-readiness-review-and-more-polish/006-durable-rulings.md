# Durable rulings — readiness-review-and-more-polish

> Migrated 2026-07-15 from the retired project memory file (`.klimkit/memory.md` →
> `docs/agents/memory.md`); each ruling is dated as originally recorded.

- **2026-05-04** — Harness pack human references should use `__HUMAN_NAME__` and project from `[operator].human_name`, defaulting to `Human`.
- **2026-05-05** — For v1 public users, strongly prefer a fork-first operator repo model where users autosync their own fork and review upstream harness-pack changes selectively with agents.
- **2026-05-06** — Telegram completion notifications should be sent only for main Codex agents, not spawned subagents.
- **2026-05-06** — `kk apply` and `kk pull` should preserve local code-server preferences only when `[code_server] managed_profile = false`.
- **2026-05-06** — code-server preferences should sync through Klimkit's managed profile by default; use `kk code-server capture` after tuning the source VM.
