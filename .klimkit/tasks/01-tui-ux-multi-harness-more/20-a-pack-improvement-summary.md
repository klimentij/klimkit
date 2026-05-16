# Pack Improvement Summary

Human task: `19-h-pack-impr.md`.

## Acceptance Checklist

- [x] Add a `checklister` subagent to the Codex pack.
- [x] Refactor `packs/codex/AGENTS.md` into clear, non-overlapping sections.
- [x] Make the workflow a dedicated section with intake, checklist, delegation, implementation, verification, final review, and reporting steps.
- [x] Require the `checklister` before implementation work.
- [x] Specify that the checklist must be written into an agent-authored `*-a-*.md` task note.
- [x] Define checklist quality for UI, persistence, database/local state, services, cross-machine behavior, and test criteria.
- [x] Require 3 parallel `final_reviewer` agents as the final workflow gate before human completion claims.
- [x] Update `final_reviewer` expectations so reviewers receive the human request/task path, checklist, evidence, and exact final response draft.
- [x] Review pack consistency across shared `AGENTS.md`, subagents, and skills touched by the workflow.
- [x] Add README documentation for the Codex harness workflow.
- [x] Add README guidance recommending a feature worktree before feature work.
- [x] Add a generic sanitized worktree helper under `examples/` and link it from README.
- [x] Add the top-level README promise that Switchboard supports 5-7 parallel agents working in separate branches/worktrees across machines.
- [x] Add automated validation for the new pack workflow and generic worktree helper.
- [x] Prepare `v0.1.2` release metadata for the requested release.

## High-Level Changes

- Added a new `checklister` subagent to the Codex pack.
- Refactored `packs/codex/AGENTS.md` around clear sections with less overlap:
  - authority and scope
  - standard workflow
  - subagent roles
  - shared skills
  - memory, logs, and task notes
  - engineering quality rules
  - completion bar
- Made checklist creation a required workflow step before implementation work.
- Defined what `checklister` must write into agent-authored task notes:
  - concrete pass/fail acceptance criteria
  - detailed UI screen/state checks when UI is involved
  - persistence, database, local state, service, and cross-machine checks when relevant
  - named automated test and manual verification expectations
- Tightened the final-review workflow so the parent agent must give each `final_reviewer`:
  - the original human request or task path
  - the checklister acceptance checklist
  - changed files
  - verification evidence
  - the exact draft response
- Updated `final_reviewer` so it verifies the draft against both the human request and every checklist item.
- Updated the `harness-tuning` skill workflow so pack edits account for the new checklist step.
- Added pack validation coverage proving the checklister agent exists and the shared workflow requires both checklister and 3 parallel final reviewers.
- Added a dedicated README explanation of the Codex harness workflow.
- Added the top-level README promise that Switchboard is meant for 5-7 parallel agents across machines and parallel branches.
- Added a generic `examples/create-worktree.sh` helper for creating feature worktrees from a synced integration branch.
- Added README guidance recommending a feature worktree before every feature and linking that helper.
- Bumped repo release metadata to `v0.1.2` for the requested release.

## Tracked Files For This Work

- `.klimkit/log.md`
- `.klimkit/memory.md`
- `.klimkit/tasks/01-tui-ux-multi-harness-more/19-h-pack-impr.md`
- `.klimkit/tasks/01-tui-ux-multi-harness-more/20-a-pack-improvement-summary.md`
- `README.md`
- `examples/create-worktree.sh`
- `packs/codex/AGENTS.md`
- `packs/codex/agents/checklister.toml`
- `packs/codex/agents/final-reviewer.toml`
- `packs/codex/skills/harness-tuning/SKILL.md`
- `pyproject.toml`
- `tests/test_docs_static.py`
- `tests/test_codex_pack_validation.py`
- `uv.lock`

## Validation

```text
$ uv run python -m unittest tests.test_codex_pack_validation -q
----------------------------------------------------------------------
Ran 6 tests in 0.009s

OK
```

```text
$ uv run python -m unittest tests.test_klimkit_install.KlimkitInstallTests.test_codex_pack_projects_human_name_template -q
----------------------------------------------------------------------
Ran 1 test in 0.006s

OK
```

```text
$ uv run python -m unittest tests.test_codex_pack_validation tests.test_klimkit_install -q
----------------------------------------------------------------------
Ran 35 tests in 0.121s

OK
```

```text
$ git diff --check
# no output
```

```text
$ uv run python -m unittest tests.test_docs_static tests.test_codex_pack_validation tests.test_klimkit_install -q
----------------------------------------------------------------------
Ran 39 tests in 0.126s

OK
```

```text
$ bash -n examples/create-worktree.sh
# no output
```

```text
$ uv run python -m unittest discover -s tests -q
----------------------------------------------------------------------
Ran 138 tests in 7.566s

OK (skipped=1)
```

```text
$ uv run kk apply --skip-services
Klimkit / apply
Local plan applied.
  actions    31
  changed    5
  live       Codex projection: /home/ubuntu/.codex
```

```text
$ ls -1 /home/ubuntu/.codex/agents | sort
checklister.toml
code-explorer.toml
code-reviewer.toml
debugger.toml
final-reviewer.toml
manual-tester.toml
security-auditor.toml
test-writer.toml
web-research.toml
```

## Review Notes

- The new checklister is intentionally `workspace-write` because its job is to write checklist notes under `.klimkit/tasks/`.
- The checklister is forbidden from production-code implementation unless explicitly asked.
- The final-review aggregation is still the parent agent's responsibility; individual `final_reviewer` agents validate the draft and evidence, then the parent collects 3/3 PASS before responding.

## Final Review Gate

- `Schrodinger`: PASS / READY FOR USER.
- `Ampere`: PASS / READY FOR USER.
- `Hegel`: PASS / READY FOR USER.
