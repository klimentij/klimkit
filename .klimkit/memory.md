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
- 2026-05-06: `kk apply` and `kk pull` should preserve local code-server preferences only when `[code_server] managed_profile = false`.
- 2026-05-06: code-server preferences should sync through Klimkit's managed profile by default; use `kk code-server capture` after tuning the source VM.
- 2026-05-07: Klimkit should recommend fork-first installs for real fleets without enforcing forks; direct upstream checkouts remain acceptable for trying the project.
- 2026-05-07: Shared Codex implementation workflow should require a `checklister` acceptance checklist before coding and 3 parallel `final_reviewer` passes before completion claims.
- 2026-05-07: Before each feature, prefer creating a separate Git worktree and Switchboard tab so parallel agents can work on separate branches without colliding.
- 2026-05-08: Task proof reports should live in each repo under `.klimkit/reports/`, with HTML tracked by Git and large screenshot/video media ignored locally.
- 2026-05-08: Proof reports should render screenshots and videos full-width and prefer MP4 video embeds because WebM scrubbing is unreliable in Chrome/PWA usage.
