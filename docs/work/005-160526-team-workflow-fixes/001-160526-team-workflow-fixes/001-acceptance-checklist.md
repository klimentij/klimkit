# Team Workflow Fixes Acceptance Checklist

Task: implement fixes to Dominik's PR #1 `Add team artifact workflow` on branch `review/pr-1-dominik`.
Created by: checklister
Attribution: this fix task is repo evidence in this repo's solo flat `.klimkit/` layout. Contributor operator-scoped `.klimkit` evidence was reviewed as PR context and then removed from the public repo per Klim's scope correction.

## Acceptance Checklist

### Scope And Planning

- [x] A short implementation plan is written or updated under `.klimkit/tasks/05-team-workflow-fixes/` before production edits, covering the migration hardening, report discovery/serving hardening, CLI follow-up command rendering, Codex pack token fix, tests, adversarial QA, proof report, reflection, and final review sequence.
- [x] The implementation stays on branch `review/pr-1-dominik` and limits production edits to the PR #1 team artifact workflow surfaces needed for the four review findings and their verification.
- [x] Existing repo evidence is kept in the solo flat `.klimkit/` layout, with no committed `.klimkit/<operator>/` folders in this repository.
- [x] New task proof for this fix is written under `.klimkit/tasks/05-team-workflow-fixes/` and `.klimkit/reports/05-team-workflow-fixes/`.
- [x] The fix preserves the product ideology that `solo` is the default solo-builder workflow; team support remains optional, light, and explicitly selected rather than becoming Klimkit's primary operating mode.

### Migration Hardening

- [x] `operator_folder_from_human_name` and/or config validation rejects or safely remaps any `human_name` whose sanitized folder would collide with flat artifact names or reserved `.klimkit` names, including at least `memory.md`, `log.md`, `reflection.md`, `tasks`, `reports`, `local`, `state`, `backups`, and `logs`.
- [x] `kk migrate team-workflow --dry-run` fails loudly before planning moves when the sanitized operator folder is reserved, hidden, empty, `.` / `..`, or otherwise resolves to a path that could overlap the flat artifact sources.
- [x] `kk migrate team-workflow` performs no partial migration when the operator folder is invalid, a target already exists, a target is inside a source artifact directory, or any planned move is blocked.
- [x] Migration applies all blocker checks before moving any artifact and writes `workflow = "team"` only after the migration is safe and complete.
- [x] Migration still moves only trackable evidence artifacts: `memory.md`, `log.md`, `reflection.md`, `tasks/`, and `reports/`.
- [x] Migration still does not move or track `.klimkit/local/`, `.klimkit/state/`, `.klimkit/backups/`, `.klimkit/logs/`, secrets, runtime databases, service logs, or generated state.
- [x] A project-local migration from a non-Klimkit repo with `.klimkit/` still targets that project and does not rewrite the active harness config when it is only a project evidence migration.
- [x] An explicit migration with `--repo` and `--human-name` still works without an existing config file and does not create or rewrite an unrelated config file.
- [x] Existing passing migration behavior for a normal human name such as `Alice Example` remains unchanged, producing `.klimkit/Alice-Example/`.

### Dry-Run Follow-Up Command

- [x] The `Next` command printed after `kk migrate team-workflow --dry-run` preserves an explicit global `--config` argument when one was supplied.
- [x] The printed follow-up command preserves explicit `--repo` and `--human-name` arguments when they were supplied.
- [x] Paths and names containing spaces, quotes, shell metacharacters, or non-default config locations are shell-quoted safely in the printed follow-up command.
- [x] The printed follow-up command omits optional flags only when they were not needed for the dry-run context.
- [x] Regression tests prove the printed command can be copied into a POSIX shell and resolves to the same config path, repo path, and human name as the dry run.

### Switchboard Report Discovery And Serving

- [x] Switchboard discovers flat solo reports only under each configured repo root's `.klimkit/reports/**/*.html`.
- [x] Switchboard discovers team-scoped reports only under valid operator directories shaped as `.klimkit/<operator>/reports/**/*.html`.
- [x] Switchboard does not index flat artifact directories as operators, including `.klimkit/tasks/reports`, `.klimkit/local/reports`, `.klimkit/state/reports`, `.klimkit/backups/reports`, `.klimkit/logs/reports`, or nested report-looking directories under flat artifacts.
- [x] Switchboard ignores or warns on non-directory, unreadable, missing, duplicate, and reserved report roots without crashing the daemon.
- [x] Switchboard rejects symlinked operator directories or symlinked `reports` directories that resolve outside the configured repo root's `.klimkit` tree.
- [x] Switchboard does not serve report HTML, screenshots, videos, or other assets through symlinks that escape the owning `.klimkit/reports` or `.klimkit/<operator>/reports` directory.
- [x] Report asset resolution continues to reject path traversal, absolute paths, backslashes, empty segments, `.` / `..` segments, unknown root IDs, unknown owner directories, and reserved owner names with 404 or 403 behavior.
- [x] Valid flat solo report links and valid team-scoped report links still serve with the correct content type and preserve relative media references.
- [x] `GET /reports/` and `HEAD /reports/` continue to work outside the `/switchboard/` base path without breaking existing Switchboard routes.
- [x] Report media serving still supports video MIME types, byte ranges, valid `206` partial content responses, and invalid range `416` responses where existing behavior already supports them.
- [x] Report routes use the same auth boundary as Switchboard: loopback tokenless access remains allowed, and token-protected deployments require the configured token or valid auth cookie.

### Codex Pack Projection Fix

- [x] The hard-coded `Human` in `packs/codex/AGENTS.md` migration-conflict guidance is replaced with `__HUMAN_NAME__`.
- [x] Pack projection for a configured human name proves the generated `~/.codex/AGENTS.md` text names that human in the conflict guidance instead of `Human`.
- [x] Legitimate generic terms such as `Human-authored files use -h-` and default config examples using `human_name = "Human"` remain intact if they are not the review finding.
- [x] Static pack validation prevents reintroducing an untemplated `ask Human` or equivalent hard-coded operator reference in projected workflow guidance.

### Solo Default And Optional Team Ideology

- [x] `default_config()`, `parse_config()` fallback behavior, `render_config()`, setup output, README examples, and existing install tests all prove `[operator] workflow = "solo"` remains the default.
- [x] A fresh setup with no explicit workflow continues to write flat `.klimkit/memory.md`, `.klimkit/log.md`, `.klimkit/reflection.md`, `.klimkit/tasks/`, and `.klimkit/reports/` guidance for existing solo users.
- [x] Team workflow behavior is activated only by explicit `workflow = "team"` or an intentional migration command; report discovery support for team-scoped evidence does not change where solo agents write artifacts.
- [x] README and harness docs describe team artifacts as optional team support and do not present team workflow as the recommended default for a solo builder.
- [x] Docs continue to state that `.klimkit/` is project evidence while machine-local config, state, backups, logs, secrets, and service state remain ignored/local.

### Automated Tests

- [x] `uv run python -m unittest tests.test_klimkit_install -q` passes with new coverage for reserved sanitized operator names, no partial migration on invalid targets, normal-name migration compatibility, and solo default behavior.
- [x] `uv run python -m unittest tests.test_klimkit_cli -q` passes with new coverage for dry-run `Next` command preservation and quoting of `--config`, `--repo`, and `--human-name`.
- [x] `uv run python -m unittest tests.test_switchboard -q` passes with new coverage for excluding `.klimkit/tasks/reports`, excluding reserved artifact pseudo-owners, rejecting symlink escape in discovery and serving, and preserving valid flat/team report serving.
- [x] `uv run python -m unittest tests.test_codex_pack_validation -q` passes with new coverage for the `__HUMAN_NAME__` replacement and no hard-coded `ask Human` guidance.
- [x] `uv run python -m unittest tests.test_docs_static -q` passes with README/docs assertions for solo default, optional team workflow, migration safety, and report discovery boundaries.
- [x] `uv run python -m unittest discover -s tests -q` passes before final review.
- [x] `git diff --check` passes before final review.

### Manual And Adversarial QA

- [x] Manual migration QA uses temporary repos or worktrees only and does not run destructive migration commands against the live repo `.klimkit/` evidence.
- [x] Manual migration QA shows `--dry-run` and real migration behavior for a normal operator name, a reserved sanitized name such as `tasks`, a dotted filename-like name such as `memory.md`, an existing target conflict, and a project path containing spaces.
- [x] Manual CLI QA captures the exact dry-run `Next` commands for cases with explicit `--config`, explicit `--repo`, explicit `--human-name`, and shell-quoting-sensitive values.
- [x] Manual report QA starts a local Switchboard/Klimkit server with controlled temporary report roots containing valid flat reports, valid team reports, `.klimkit/tasks/reports`, reserved pseudo-owner report dirs, and symlink escape attempts.
- [x] Manual HTTP QA verifies `/reports/`, a valid flat report, a valid team report, valid media, traversal attempts, symlink escape attempts, and unauthorized token-protected access with observable status codes.
- [x] Manual QA records the current live repo remains in solo flat `.klimkit/` layout after the fix.

### Browser QA And Evidence Capture

- [x] Browser QA uses the `agent-browser` skill or CLI against a running local Switchboard/Klimkit server for the report index and report detail pages.
- [x] A desktop screenshot shows a populated `/reports/` index with valid flat and team-scoped reports and without any `.klimkit/tasks/reports` entry.
- [x] A desktop screenshot shows a served individual report detail page with relative media loading from the allowed reports tree.
- [x] A desktop screenshot or captured HTTP evidence shows the symlink escape or traversal attempt rejected.
- [x] A mobile-width screenshot shows `/reports/` remains readable and non-overlapping.
- [x] An empty-state screenshot shows `/reports/` when no configured root has valid report HTML.
- [x] A native `agent-browser` video recording demonstrates opening `/reports/`, opening a valid team-scoped report, returning to the index, and confirming the invalid/reserved report entry is absent.
- [x] If the native browser recording is converted to MP4 for the report, the native source recording remains in the evidence assets.

### Security-Sensitive Checks

- [x] A security-focused review is run before final review because the task touches file migration, symlink handling, path traversal, report serving, and auth boundaries.
- [x] The security review explicitly covers destructive file moves, path canonicalization, symlink escape, HTTP auth, media range handling, and exposure of ignored/local `.klimkit` state.
- [x] No test, proof report, or log records secrets from `.klimkit/local/`, environment variables, auth tokens, Telegram tokens, runtime SQLite files, or service logs.
- [x] Any new error messages reveal enough for diagnosis without exposing secret paths beyond the configured repo/report root context needed for local debugging.

### Docs And README Consistency

- [x] README sections for setup, Solo And Team Artifacts, Codex Harness Workflow, Reports, and migration remain internally consistent after the fix.
- [x] README examples and CLI help show safe migration commands, including dry-run first and explicit `--repo` / `--human-name` use for scripted migrations.
- [x] Docs state that report discovery is limited to configured repo roots and valid `.klimkit/reports` or `.klimkit/<operator>/reports` layouts.
- [x] Docs do not imply that arbitrary `.klimkit/<dir>/reports` paths, reserved artifact dirs, or symlinked directories are valid report sources.
- [x] Changelog or release notes are updated only if this PR branch already uses them for PR-facing behavior changes; otherwise the proof report documents the fix without inventing release work.

### Final HTML Proof Report

- [x] The final proof report is written to `.klimkit/reports/05-team-workflow-fixes/report.html`.
- [x] The proof report is minimal, responsive, readable without a build step, and uses relative paths for all local screenshots and videos.
- [x] The proof report includes the original request summary, this checklist path, implementation summary, changed-file list, test command results, manual/adversarial QA results, security review outcome, reflection entry reference, and final-review outcome.
- [x] The proof report displays every screenshot and video as a full-width section, not as thumbnails.
- [x] The proof report embeds an MP4 video when available for Chrome/PWA scrubbing while retaining the native `agent-browser` source recording as evidence.
- [x] The proof report explicitly states whether a Tailscale-served URL was available and, when available, gives the URL under `https://<machine>.<tailnet>.ts.net/reports/`.
- [x] The proof report HTML is Git-trackable while large screenshots and videos remain ignored local media.

### Reflection Gate

- [x] Before final review, the implementer reads `.klimkit/reflection.md` and relevant operator-scoped PR context if it informs team artifact workflow decisions.
- [x] A full UTC timestamped reflection session is appended to `.klimkit/reflection.md` after verification and before final reviewers.
- [x] The reflection session uses the default `Observations`, `Derived Pattern`, `Insight`, and `Next Probe` sections unless a wider reflection needs up to ten named sections.
- [x] The reflection preserves older formats and records the team-workflow synthesis; contributor operator-scoped `.klimkit` context is not retained in the public repo after Klim's solo-layout scope correction.
- [x] The implementer reconsiders the implementation, test evidence, manual QA, and final response after reflection and reruns impacted verification if the reflection exposes a material gap.

### Final Reviewer Gate

- [x] The exact final response draft is prepared before final review.
- [x] Three `final_reviewer` subagents are run in parallel with the original request, this checklist, changed files, automated verification evidence, manual/adversarial QA evidence, security review notes, reflection entry, proof report path, Tailscale report URL if available, and exact draft response.
- [x] All three reviewers explicitly check that solo workflow remains default and unchanged for existing users.
- [x] All three reviewers explicitly check the migration collision fix, report discovery/serving hardening, dry-run command preservation/quoting, and `__HUMAN_NAME__` pack fix.
- [x] All three reviewers verify the final HTML proof report and representative screenshot/video evidence.
- [x] All three reviewers return PASS / READY FOR USER before any completion claim is sent.
- [x] The final response reports what changed, which checks passed, the proof report path `.klimkit/reports/05-team-workflow-fixes/report.html`, the Tailscale report URL when available, and any unavailable verification or residual risk.
