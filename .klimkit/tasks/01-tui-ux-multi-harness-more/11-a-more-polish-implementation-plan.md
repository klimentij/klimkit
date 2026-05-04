# More Polish Implementation Plan

Agent-authored plan for `.klimkit/tasks/01-tui-ux-multi-harness-more/10-h-more-polish.md`.

## Acceptance Criteria

- Switchboard drawer has no dialog logo, uses the full available page height, and avoids awkward empty gaps at desktop and mobile widths.
- Switchboard tab strip and catalog show only tabs manually created through `Create tab`; backend Codex/subagent sessions remain available for machine discovery, folder suggestions, notification matching, and status merging.
- Switchboard display statuses are reduced to `new`, `working`, `ask`, `done`, and `seen`; planning/sending-message states must not appear as `planning`.
- Switchboard supports stable deep links into a specific manual tab from browser/Telegram notifications.
- `[switchboard.agent] enabled` defaults to true for client-capable installs, including first VM configs, with clearer comments; client-only still needs a backend URL before apply.
- Apply/autosync/Codex Stop Telegram notifications are short, useful, emoji-formatted, and reported in CLI output when sent.
- Old Mac deep-link/Automator/Codex Focus code and notification text are removed.
- README has GitHub badges, table of contents, contribution guidance, harness/pack guidance, Chrome recommendation for Switchboard, and a visible yolo-mode security warning.
- README warnings cite current source-backed AI-agent risk material: Simon Willison's 2025 "lethal trifecta" framing and OWASP LLM Top 10 risk categories.
- Codex pack is polished: agents/skills/subagents reviewed for duplication and inconsistencies, final-reviewer requirement strengthened to 3 parallel passes, a `harness-tuning` skill is added, and default config uses GPT-5.5, xhigh, and yolo execution defaults.
- Tests and browser QA pass, with screenshots captured.
- Three parallel final reviewers all return PASS/READY before responding to Klim.

## Findings From Initial Review

- `app.js` already has manually created local workspaces in `ui.localWorkspaces`, but `materializeState()` appends all server workspaces into `ui.workspaces`, causing every Codex/subagent session to appear as a tab.
- `reconcileLocalWorkspaces()` currently removes local tabs once a matching backend session appears. That is the opposite of the new desired model; local tabs should remain the user's manual tab records and borrow status/session details from matching backend sessions.
- Status handling is split between backend raw states and frontend display labels. The low-risk path is to preserve backend states for storage/tests while normalizing only the visible UI/status filter layer.
- Stop-hook Telegram links still target code-server and include an old Mac "Quick open" trampoline. The replacement should link to Switchboard with a hash target that resolves by session/folder/machine.
- `switchboard.agent` currently defaults false on first VM because the previous model treated the central server collector as sufficient. The requested default should make agent reporting visibly on for client-capable machines, while validation still protects client-only machines without `backend_url`.
- The Codex pack has useful content but duplicates cautionary workflow guidance across `Shared Workflow` and `Behavioral guidelines`. The requested change is not to delete the caution, but to clarify that the pack itself is edited in `~/klimkit` and synced through Klimkit, not edited directly in `~/.codex`.

## Implementation Checklist

- [x] Add/maintain this plan file before code changes.
- [x] Switchboard frontend behavior
  - [x] Keep manual local tabs as the only rendered tab/catalog list.
  - [x] Merge matching backend session details into manual tabs without replacing them.
  - [x] Preserve backend sessions for machines, folder suggestions, and notification matching.
  - [x] Add URL hash deep-link parsing for `#session=...`, `#workspace=...`, and folder/machine targets.
  - [x] Normalize visible status values to `new`, `working`, `ask`, `done`, and `seen`.
  - [x] Remove logo from drawer header and tighten full-height layout.
- [x] Notifications and removed Mac flow
  - [x] Replace Stop-hook code-server/Mac quick-open links with Switchboard deep links.
  - [x] Delete `src/klimkit/apps/macos/codex-focus/`.
  - [x] Improve apply and autosync Telegram message formatting.
  - [x] Keep CLI Live section reporting Telegram send status.
- [x] Config defaults
  - [x] Default `switchboard_agent_enabled` true when the machine participates in Switchboard.
  - [x] Update rendered comments to explain local server fallback versus client reporting clearly.
  - [x] Preserve apply validation for client-only agent configs missing backend URL.
- [x] README and contribution polish
  - [x] Add badges and table of contents.
  - [x] Add contribution summary and link to `CONTRIBUTING.md`.
  - [x] Add Switchboard Chrome recommendation.
  - [x] Add harness pack tuning workflow and autosync explanation.
  - [x] Add prominent yolo/dedicated-VM warning grounded in Simon Willison and OWASP sources.
- [x] Codex pack polish
  - [x] Update `packs/codex/AGENTS.md`.
  - [x] Add `packs/codex/skills/harness-tuning/SKILL.md`.
  - [x] Set Codex default yolo config values in `packs/codex/config.toml`.
- [x] Tests and QA
  - [x] Add/adjust unit tests for install config defaults, CLI notification text, Switchboard static behavior, and Stop hook removal.
  - [x] Run targeted tests.
  - [x] Run full unittest suite.
  - [x] Run browser QA with `agent-browser`.
  - [x] Capture screenshots showing the polished drawer and current VM manual tab.
  - [x] Apply pack locally and verify generated projection paths.
- [ ] Final review gate
  - [x] Prepare draft final response and evidence summary.
  - [x] Run 3 parallel final reviewers.
  - [x] Only respond after all 3 pass.

## Source Notes

- Simon Willison, "The lethal trifecta for AI agents: private data, untrusted content, and external communication", 2025-06-16: highlights that combining private-data access, untrusted content, and external communication enables prompt-injection data theft.
- OWASP Top 10 for LLM Applications: lists Prompt Injection, Sensitive Information Disclosure, Insecure Plugin Design, and Excessive Agency as relevant risk categories for agentic systems.
