# Durable rulings — autosync

> Migrated 2026-07-15 from the retired project memory file (`.klimkit/memory.md` →
> `docs/agents/memory.md`); each ruling is dated as originally recorded.

- **2026-05-04** — `kk apply` must make managed service changes live by restarting what Klimkit manages and reporting restarted services plus live URLs.
- **2026-05-04** — Klimkit daemon autosync should be default-on for all VMs, check `origin/main` every 5 seconds by default, apply updates, restart managed services, and send a concise Telegram summary when configured.
