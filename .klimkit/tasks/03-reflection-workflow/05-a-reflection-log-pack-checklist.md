# Reflection Log Pack Acceptance Checklist

Source request: `.klimkit/tasks/03-reflection-workflow/04-a-better-reflection-analysis.md` after `Klim:`, plus the latest instruction to continue through commit to `main`, push, and publish a new latest release.

## Acceptance Checklist

- [ ] Intake proof records that the implementer read the `Klim:` request, latest release instruction, `.klimkit/memory.md`, `.klimkit/log.md`, `.klimkit/reflection.md`, `packs/codex/AGENTS.md`, reflection-related subagents, `harness-tuning`, README release docs, and current reflection validation tests.
- [ ] Edits are made in source-controlled pack/docs/tests/task files only; generated `~/.codex/` files are not edited directly and are updated only through `kk apply`.
- [ ] `packs/codex/AGENTS.md` defines `.klimkit/reflection.md` as an append-only timestamped cross-task Reflection Log or Synthesis Ledger, where entries are reflection sessions, not one required record per task.
- [ ] Reflection entries use ISO-like timestamp headings as the primary key and keep detailed source inventories, validation transcripts, and task proof in task-local notes unless a deeper linked note is warranted.
- [ ] The shared workflow and `reflector` instructions require 3-4 default sections including `Observations`, `Derived Pattern`, `Insight`, and `Next Probe` or explicitly chosen near-synonyms.
- [ ] The shared workflow and `reflector` instructions allow optional expansion up to 10 named sections for wider, deeper, or more creative reflection sessions, without cutting off useful synthesis just because it does not fit the default four sections.
- [ ] Migration instructions require agents that encounter older reflection formats to preserve old content and add a new-format migrated or normalized entry in append-only form; old reflection content is not deleted, rewritten away, or silently ignored.
- [ ] The Reflection Gate still requires the parent agent to read the new or migrated entry after verification, record whether implementation, proof, or final response changed, rerun impacted checks when needed, and only then call final reviewers.
- [ ] `packs/codex/agents/reflector.toml`, `checklister.toml`, and `final-reviewer.toml` are updated consistently so checklist creation, reflection generation, migration expectations, reconsideration, and final-review blocking behavior all use the new format.
- [ ] `packs/codex/skills/harness-tuning/SKILL.md` and related README/Codex workflow documentation mention the new reflection log format and the required validation, projection, commit, push, and release flow where relevant.
- [ ] `.klimkit/reflection.md` keeps prior entry text intact and gains a dated new-format entry or migration entry for this task; no existing reflection content is removed.
- [ ] `tests/test_codex_pack_validation.py` or focused equivalent tests assert the timestamped cross-task log semantics, required default sections, optional expansion up to 10 sections, migration-preserves-content rule, reconsideration rule, and checklister/final-reviewer consistency.
- [ ] Tests no longer require the old reflection fields (`task reference`, `source-read summary`, `risks or contradictions`, `candidate memory/log/task follow-ups`) as the mandatory default entry shape.
- [ ] `uv run python -m unittest tests.test_codex_pack_validation -q` passes.
- [ ] `uv run python -m unittest tests.test_klimkit_install tests.test_harness_registry -q` passes because pack projection and registry behavior are in scope.
- [ ] Optional live smoke `KLIMKIT_RUN_CODEX_SMOKE=1 uv run python -m unittest tests.test_codex_smoke -q` either passes or is explicitly recorded as unavailable with the reason.
- [ ] `kk preview` is run when useful, and `kk apply` is run to project the pack; proof records projected files, service restart or skip output, and confirms live projected Codex files contain the new reflection rules.
- [ ] An agent-authored proof note under `.klimkit/tasks/03-reflection-workflow/` records changed files, validation output, projection output, reflection/reconsideration result, final reviewer outcomes, commit SHA, push target, and release tag.
- [ ] `.klimkit/log.md` receives a concise ISO-timestamped entry for the completed reflection-log harness update and release.
- [ ] UI proof is explicitly marked not applicable because this task changes harness instructions, agents, docs, tests, and release metadata only; if any UI surface changes, screenshots, native `agent-browser` video, and a `.klimkit/reports/` HTML proof report become blocking.
- [ ] The exact final response is drafted before final review, and 3 `final_reviewer` subagents run in parallel with the original request, this checklist, changed files, verification evidence, reflection/reconsideration entry, proof note, and draft response.
- [ ] All 3 final reviewers return READY FOR USER before any completion claim is sent.
- [ ] Version metadata and release docs are bumped consistently to a new latest tag, including `pyproject.toml` and README release status.
- [ ] Release notes clearly describe the timestamped reflection log format, section rules, migration behavior, validation performed, and projection status.
- [ ] The intended changes are committed on `main` with a meaningful message, pushed to the configured remote, and the remote `main` branch is verified to contain the commit.
- [ ] A new GitHub release is published for the new tag and verified as the latest visible release.
- [ ] Final handoff lists changed areas, validation commands, `kk apply` result, reflection/reconsideration result, final reviewer result, commit SHA, pushed branch/remote, release tag/URL, and any unavailable checks.
