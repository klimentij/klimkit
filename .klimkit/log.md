# Project Log

Timestamped audit trail. Entries describe actions, not preferences.

## Log
2026-05-08T09:58:05Z: Implemented the 02-better-wf-and-tabs workflow, reports daemon, Tab Browser drag ordering, browser QA proof report, and live Tailscale reports URL verification.
2026-05-08T10:31:48Z: Updated the 02-better-wf-and-tabs proof report and shared workflow guidance to use full-width media and MP4 report videos for easier browser inspection.
2026-05-11T10:03:46Z: Integrated the external quality-rule guidance into the shared Codex AGENTS pack, excluding token-budget rules, and added validation coverage against duplicate raw rule blocks.
2026-05-11T10:15:05Z: Wrote the acceptance checklist for `03-reflection-workflow` covering reflection intake, append-only ledger behavior, fresh-context reflection, validation tests, and `kk apply`.
2026-05-11T10:22:09Z: Implemented the shared Codex Reflection Gate with a fresh-context reflector agent, append-only reflection ledger guidance, validation tests, and live pack projection.
2026-05-11T10:32:51Z: Prepared `v0.1.4` release metadata for the shared Codex quality and Reflection Gate workflow changes.

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
- 2026-05-05T00:00:00Z: Added the v1 fork-first operator repo decision to the open-source readiness review.
- 2026-05-06T00:41:20Z: Implemented Switchboard tmux-wrapped copy commands, manual tab archiving, clickable archive catalog checkboxes, and task proof for `15-h-more-polish`.
- 2026-05-06T00:54:33Z: Formatted Switchboard Telegram attention messages, suppressed subagent completion Telegram notifications, and projected the updated Codex Stop hook with `kk apply --skip-services`.
- 2026-05-06T03:41:35Z: Changed code-server user settings projection to seed defaults without overwriting local preferences during `kk pull` or autosync.
- 2026-05-06T03:59:40Z: Added the managed code-server profile capture/sync flow, captured ODev code-server settings and extensions, hid archived Switchboard tabs from the tab bar, and updated the README install path to fork-first local install.
- 2026-05-06T04:22:37Z: Fixed Switchboard completion summaries that start with `What changed:`, explicit Tailscale Serve permission skips, and full done-message Telegram notification coverage.
- 2026-05-06T04:32:26Z: Strengthened the done-message Telegram path from rollout parsing to notification delivery and documented Switchboard Chrome/PWA usage plus keyboard shortcuts.
- 2026-05-06T04:42:33Z: Added configurable Switchboard loaded-tab retention with a default of five most-recently-used code-server tabs and documented the per-tab RAM tradeoff.
- 2026-05-06T05:03:27Z: Documented the `v0.1.0` operator-preview release status in README before creating the GitHub release.
- 2026-05-06T05:07:35Z: Removed the legacy upstream auto-clone path from `install.sh`, documented checkout-local installation, and added installer proof for the fork-first flow.
- 2026-05-06T05:15:27Z: Corrected the installer proof search transcript to avoid self-matching its own recorded command.
- 2026-05-07T02:55:37Z: Implemented final polish for `17-h-final-polish`, including softer fork guidance, README screenshots, Switchboard catalog archive behavior, and v0.1.1 version metadata.
- 2026-05-07T03:40:15Z: Implemented the Codex pack checklister workflow, refactored shared `AGENTS.md`, and wrote the high-level `20-a` pack improvement summary.
- 2026-05-07T03:40:15Z: Added README guidance for the Codex harness workflow, parallel Switchboard agent worktrees, and the generic `examples/create-worktree.sh` helper.
- 2026-05-07T04:18:00Z: Prepared `v0.1.2` release metadata for the Codex pack workflow and parallel worktree documentation.
- 2026-05-07T04:26:00Z: Collected 3/3 final reviewer passes for the Codex pack workflow and worktree documentation release task.
- 2026-05-08T05:30:23Z: Wrote the one-page plan for `02-better-wf-and-tabs` covering harness QA reports and Switchboard tab browser ordering.
- 2026-05-08T09:06:48Z: Wrote the acceptance checklist for `02-better-wf-and-tabs` covering harness QA reports, Tab Browser drag/drop, daemon reports index, gitignore behavior, automated tests, browser QA, and final report proof.
- 2026-05-14T09:40:01Z: Wrote the better reflection format analysis for `03-reflection-workflow`, including naming options, pros and cons, and compressed rewrites of the current reflection entry.
- 2026-05-14T09:48:12Z: Revised the reflection format analysis toward a timestamped cross-task reflection log with four fixed sections per session.
- 2026-05-14T10:49:32Z: Implemented and projected the timestamped cross-task Reflection Log harness update, with validation and release preparation for `v0.1.5`.
- 2026-05-14T10:52:43Z: Published GitHub release `v0.1.5` as the latest release for the timestamped Reflection Log harness update.
- 2026-05-14T11:48:29Z: Prepared the generic best-practice harness update and `mattpocock/skills` comparison for review without applying, committing, or releasing.
- 2026-05-14T12:04:52Z: Prepared `v0.1.6` release metadata for the generic best-practice harness update.
- 2026-05-14T12:08:45Z: Published GitHub release `v0.1.6` as the latest release for the generic best-practice harness update.
- 2026-05-16T04:43:51Z: Wrote the acceptance checklist for PR #1 team workflow fixes under `.klimkit/tasks/05-team-workflow-fixes/`.
- 2026-05-16T11:10:00Z: Flattened PR #1 proof evidence back to the solo `.klimkit/` layout and removed contributor operator-scoped `.klimkit` artifacts from the public repo.
- 2026-05-16T11:11:00Z: Recorded the durable preference that this repository remains in the solo flat `.klimkit/` artifact layout while team workflow stays optional product functionality.
