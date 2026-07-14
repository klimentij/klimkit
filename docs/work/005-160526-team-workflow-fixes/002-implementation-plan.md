# Team Workflow Fixes Implementation Plan

Task: harden Dominik's PR #1 team artifact workflow while preserving Klimkit's solo-builder default.

## Plan

1. Harden migration preflight before any file move.
   - Treat team workflow as opt-in and keep `solo` as the default config/rendered guidance.
   - Reject sanitized operator folder names that collide with flat artifact names or reserved `.klimkit` runtime directories.
   - Detect source/target overlap, existing targets, and invalid roots before moving anything.

2. Harden Switchboard report discovery and serving.
   - Discover reports only from `.klimkit/reports/` and valid `.klimkit/<operator>/reports/`.
   - Exclude flat artifact directories such as `tasks`, runtime dirs, hidden dirs, invalid operator names, and symlink escapes.
   - Keep existing report auth, traversal, media range, flat report, and valid team report behavior.

3. Repair CLI dry-run follow-up commands.
   - Preserve explicit `--config`, `--repo`, and `--human-name` context.
   - Shell-quote paths and names so copied commands are safe for spaces and metacharacters.

4. Fix projected Codex wording.
   - Replace the hard-coded `Human` conflict prompt with `__HUMAN_NAME__`.
   - Add validation so the projected pack cannot reintroduce that stale operator reference.

5. Verify and prove.
   - Add focused regression tests around migration safety, CLI command rendering, report discovery/serving, docs, and pack projection.
   - Run focused suites, full unittest discovery, `git diff --check`, adversarial CLI/HTTP probes, browser QA, security review, reflection, and three parallel final reviewers.
   - Produce `.klimkit/reports/05-team-workflow-fixes/report.html` as a story-style proof report with command output, screenshots, and video evidence.
   - Keep this repository's committed evidence in the solo flat `.klimkit/` layout; do not retain contributor operator-scoped `.klimkit` artifacts in the public repo.
