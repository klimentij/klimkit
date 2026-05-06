# Project Memory

Durable preferences, corrections, and process rules. Add dated one-sentence memories.

## Memories

- 2026-05-04: Defer shared harness pack extraction; keep `packs/codex/` as a clean hand-authored pack until another harness exists.
- 2026-05-04: `kk apply` must make managed service changes live by restarting what Klimkit manages and reporting restarted services plus live URLs.
- 2026-05-04: Klimkit daemon autosync should be default-on for all VMs, check `origin/main` every 5 seconds by default, apply updates, restart managed services, and send a concise Telegram summary when configured.
- 2026-05-04: Switchboard client tabs must open the selected machine's own Tailscale Serve code-server URL, never fall back to the central Switchboard server's code-server.
- 2026-05-04: Shared Codex hooks must stay compatible with macOS `/bin/bash` 3.2 and fail open so hook issues never block Codex turns.
- 2026-05-04: Harness pack human references should use `__HUMAN_NAME__` and project from `[operator].human_name`, defaulting to `Human`.
- 2026-05-05: For v1 public users, strongly prefer a fork-first operator repo model where users autosync their own fork and review upstream harness-pack changes selectively with agents.
- 2026-05-06: Telegram completion notifications should be sent only for main Codex agents, not spawned subagents.
- 2026-05-06: `kk apply` and `kk pull` should seed code-server `User` defaults without overwriting local preferences such as theme, extension settings, or trusted folders.
