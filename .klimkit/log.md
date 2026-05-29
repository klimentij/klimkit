# Project Log

Timestamped audit trail. Entries describe actions, not preferences.

## Log
2026-05-29T09:07:28Z: Folded the old `klimkit-workflow` skill into `klimkit-implement`, moved its artifact workflow reference, and removed the separate workflow skill from the root package.
2026-05-29T09:06:04Z: Extracted the deprecated checklister, code explorer, security auditor, reflector, and final reviewer subagent roles into root skills and added `klimkit-implement` as the skills-first implementation workflow.
2026-05-29T05:28:29Z: Updated the Klimkit grill-me skill to write an auditable Question Triage grid with up to 10 considered questions, importance estimates, and the reason the current question was chosen.
2026-05-29T05:27:20Z: Refined the Klimkit grill-me skill so it restores Matt-style human grilling while preparing a priority-ranked question list from repo and web context, then reranking after each answer.
2026-05-29T05:22:00Z: Added the Klimkit-adapted grill-me skill to the root skills package with question-by-question decision tracking in operator-scoped task notes.
2026-05-28T13:50:42Z: Added the Docker fresh-machine Codex smoke test approach to project memory after verifying it is useful for testing Klimkit skills through mounted auth, Vercel Skills CLI install, and `codex exec` setup proof.
2026-05-28T10:27:00Z: Removed tracker, board, triage, and control-plane skills from the root package; moved legacy runtime/plugin sources under `deprecated/`; rewrote README and CI around the seven-skill first wave.
2026-05-28T10:07:00Z: Updated the root Klimkit skills so skills-first setup asks for an operator name, defaults evidence to `.klimkit/<operator>/`, documents XDG/global config conventions, and passes skill, unit, CLI, smoke, privacy, and diff checks without subagents.
2026-05-28T09:40:01Z: Added the first root `skills/` Klimkit library package, made Vercel Skills CLI the primary README path, marked the old runtime as deprecated, and verified the 10-skill package with skills CLI listing plus local validation.
2026-05-28T09:24:57Z: Created the sanitized request note and blocking acceptance checklist for `14-root-skills-library`, covering root Vercel-compatible skill packaging, first-wave skill scope, privacy boundaries, validation, reflection, and final review.
2026-05-28T02:34:07Z: Wrote the deep Symphony/Matt/Klimkit skill-first control-plane analysis and one-page executive brief for `13-symphony-skills-control-plane-research`, keeping private candidate-skill material summarized only at a neutral pattern level.
2026-05-28T02:30:55Z: Created the sanitized request note and blocking acceptance checklist for `13-symphony-skills-control-plane-research`, covering planning-only scope, Symphony/Matt/Klimkit source intake, private candidate-skill privacy boundaries, analysis artifacts, verification, reflection, and final review.
2026-05-28T02:18:04Z: Copied Matt Pocock's upstream `skills/` snapshot into `third_party/mattpocock-skills/` with MIT license attribution and wrote the `12-matt-skills-merge-plan` analysis for merging Matt's composable skills with Klimkit workflow gates and skills.sh packaging.
2026-05-27T08:39:25Z: Reworked the Klimkit plugin skills toward skill-creator guidance, removed the plugin root harness reference bundle, added skill-owned workflow references and OpenAI skill metadata, and verified validators plus focused/full unit suites on `codex-plugin-skill-cleanup`.
2026-05-27T08:32:17Z: Wrote the acceptance checklist for `11-plugin-skill-cleanup`, covering Klimkit plugin skill structure, skill-owned workflow references, UI metadata, root reference cleanup, validation, proof, reflection, and final review.
2026-05-27T08:12:45Z: Published `codex-plugin-first` through PR #2, merged it to `main` at `f8b8700c7a325daed15a2cbda69ce2f58407d361`, created latest release `v0.1.15`, installed and upgraded the Klimkit Codex plugin on this VM, repointed its marketplace to released `main`, and verified cache version `0.1.15`.
2026-05-27T08:01:33Z: Updated the codex-plugin-first acceptance checklist with blocking publish, release, live plugin install, upgrade, home/cache proof, reflection, and final-review criteria.
2026-05-27T05:17:44Z: Added the public Klimkit Codex plugin package and marketplace, repositioned README around plugin-first Codex app usage, and verified plugin/docs/static coverage plus full unittest discovery on `codex-plugin-first`.
2026-05-27T04:44:14Z: Disabled Klimkit autosync by default, set the local machine config to `auto_sync = false`, restarted `klimkit.service`, and verified the install/supervisor/default-off behavior with unit tests.
2026-05-24T05:59:00Z: Added Codex app thread deep links to Telegram stop notifications, verified local projection and tests, pushed commit `2e9119759bf886c149df4f64531cb70dfb5e6d3e`, published latest release `v0.1.11`, and recorded the VM verification boundary.
2026-05-22T04:08:45Z: Pushed Klimkit marketing asset commit `f1eb323` to `origin/main`, created latest GitHub release `v0.1.9`, and verified the live GitHub README and Tailscale proof report.
2026-05-22T04:03:14Z: Reworked README image optimization to higher-quality JPEGs, restored rejected noisy PNG edits, verified local README rendering, and prepared the marketing hygiene changes for GitHub main publication.
2026-05-22T03:04:00Z: Added Klimkit README marketing hygiene, optimized README images, GitHub topics, a public-safe 7.5 hour run proof moment, a draft Show HN post, and browser proof evidence.
2026-05-22T02:59:45Z: Expanded the Symphony reflection with Klimkipedia raw/index/search analysis, Klim's agentic-engineering trajectory, and a GitHub-first orchestration strategy for Klimkit.
2026-05-21T10:12:05Z: Created the `07-symphony-reflection` research task comparing OpenAI Symphony with Klimkit and evaluating GitHub Issues versus Linear for future orchestration.
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
- 2026-05-16T11:49:55Z: Added a repository-local `AGENTS.md` reminder to create and mark a latest GitHub release after every commit to `main`.
- 2026-05-20T03:43:31Z: Implemented secondary direct code-server Tailscale links across Telegram notifications, added the `grill-me` Codex pack skill, verified projection, and ran the full test suite.
- 2026-05-20T04:08:00Z: Added runtime stop-hook Telegram payload tests after final review found the broken embedded Python quoting path, fixed the projected hook, and reran the full suite.
- 2026-05-26T04:14:27Z: Implemented Codex config projection preservation for VM-local plugin/connector tables, verified Slack stayed enabled after `kk apply --skip-services`, and ran focused plus full unit suites.
- 2026-05-26T04:23:02Z: Fixed the Codex config preservation security review finding by projecting `~/.codex/config.toml` and its update backups with `0600`, then reran focused, supervisor, full unit, diff, and live apply checks.
