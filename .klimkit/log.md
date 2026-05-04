# Project Log

Timestamped audit trail. Entries describe actions, not preferences.

## Log

- 2026-05-04T08:09:50Z: Implemented the local-first single-config, Codex harness projection, docs, validation, and proof pass for `01-tui-ux-multi-harness-more`.
- 2026-05-04T09:04:00Z: Updated `kk apply` and `kk pull` reporting so managed service restarts and live URLs are explicit after applying changes.
- 2026-05-04T09:16:00Z: Added default-on daemon autosync from `origin/main`, deferred apply/restart orchestration, and Telegram autosync summaries.
- 2026-05-04T09:25:00Z: Fixed final-review blocker by wiring `kk apply --defer-service-restart` through `cmd_apply` and adding a CLI regression test.
- 2026-05-04T11:31:00Z: Implemented Switchboard manual-tab polish, notification cleanup, Codex harness tuning docs, README/security/contribution polish, and browser QA screenshots for `10-h-more-polish`.
- 2026-05-04T12:11:00Z: Fixed `12-h-bug` so Switchboard client tabs resolve selected client machines to their own Tailscale Serve code-server URLs and verified the live Mac tab iframe URL.
- 2026-05-04T12:27:30Z: Fixed the Codex stop notification hook to be macOS Bash 3 compatible and fail open when optional hook dependencies are unavailable.
- 2026-05-04T12:56:00Z: Implemented Switchboard client attention Telegram fanout, fixed local/server machine identity merging for status updates, added harness human-name templating, and verified multi-machine status transitions with browser screenshots.
- 2026-05-04T12:57:00Z: Wrote the open-source readiness review for `01-tui-ux-multi-harness-more` with launch blockers, preparedness level, and QA evidence.
- 2026-05-04T13:08:00Z: Recaptured the `NEW` status QA screenshot so both `odev` and `MacBook-Air-8.local` tabs are visibly in `NEW` state after final-review feedback.
