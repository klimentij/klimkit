# Reflection Workflow Acceptance Checklist

Human request: implement Klim's requested reflection workflow standard into the shared Codex harness pack.
Context source: `/home/ubuntu/klimkipedia/.klimkit/reflection.md`.
Created by: checklister.

## Acceptance Checklist

### Scope And Source Control

- [ ] The implementation reads `/home/ubuntu/klimkipedia/.klimkit/reflection.md` and records the relevant source boundary in the task proof or implementation notes.
- [ ] Shared Codex behavior is edited only through source pack files under `packs/codex/`; no generated files under `~/.codex/` are edited directly.
- [ ] The final implementation keeps the existing memory/log/task responsibilities distinct: log records actions, memory records durable rules, and reflection records non-obvious synthesis.

### Main Workflow Contract

- [ ] `packs/codex/AGENTS.md` adds an explicit reflection step after verification and before the three `final_reviewer` subagents.
- [ ] The reflection step requires the main agent to draft or know the intended final result, run reflection, read the reflection output, reconsider the result, and update code/docs/tests/final response when the reflection exposes a material gap.
- [ ] If reflection changes the result or evidence, the workflow requires rerunning the impacted verification before final reviewers are called.
- [ ] Final reviewers are instructed to receive the reflection entry or reflection proof along with the original request, checklist, changed files, verification evidence, and exact draft response.

### Reflection Inputs And Output

- [ ] The workflow requires reflection to consider the current task folder first, then the repo's text task archive under `.klimkit/tasks/`, `.klimkit/log.md`, and `.klimkit/memory.md`.
- [ ] Reflection instructions explicitly handle large or binary task artifacts by listing them as evidence when relevant rather than trying to read screenshots/videos as text.
- [ ] `.klimkit/reflection.md` is treated as the repo-level reflection ledger; if missing, the workflow requires creating it with a short project-reflection heading before appending.
- [ ] Reflection writes are append-only: each pass adds a dated entry with task reference, source-read summary, synthesis, risks or contradictions, and any candidate memory/log/task follow-ups.
- [ ] Reflection instructions prohibit replacing prior reflection entries or turning reflection into a chronological action log.

### Subagent Or Isolation Mechanism

- [ ] The implementation provides a fresh/noise-free reflection mechanism, preferably a dedicated read-only reflecting subagent under `packs/codex/agents/`, or records an explicit equivalent isolation decision in the implementation proof.
- [ ] If a new reflecting subagent is added, its TOML parses, has required `name`, `description`, and `developer_instructions`, and instructs append-only reflection against `.klimkit/reflection.md`.
- [ ] If no new subagent is added, `packs/codex/AGENTS.md` still names the exact command/workflow mechanism that gives the reflection pass fresh context.

### Checklister Requirements

- [ ] `packs/codex/agents/checklister.toml` requires implementation checklists to include reflection intake and reflection-write checks when a task is non-trivial.
- [ ] Checklister guidance requires checklist items to verify `.klimkit/reflection.md` is read when present, created when missing and meaningful, and appended before final review when the task can produce cross-task learning.
- [ ] Checklister guidance keeps reflection requirements observable and scoped so tiny one-command tasks can explicitly mark reflection as not applicable.

### Validation And Apply

- [ ] `tests/test_codex_pack_validation.py` includes assertions for the new reflection workflow in `packs/codex/AGENTS.md`.
- [ ] `tests/test_codex_pack_validation.py` includes assertions that checklister instructions mention `.klimkit/reflection.md`, reflection reads/writes, append-only behavior, and placement before final review.
- [ ] If a reflecting subagent is added, pack validation covers its required fields and key instructions; if not, validation covers the documented fresh-context alternative.
- [ ] `uv run python -m unittest tests.test_codex_pack_validation -q` passes.
- [ ] `uv run python -m unittest discover -s tests -q` passes, or any unrelated failure is recorded with evidence and impact.
- [ ] `kk apply` completes successfully after pack changes, and projected files under `~/.codex/` show the new reflection workflow is live on this VM.

### Completion Gate

- [ ] `.klimkit/log.md` receives an ISO-timestamped entry for the implemented reflection workflow.
- [ ] The implementation proof records changed files, exact validation commands, `kk apply` result, and any skipped or unavailable checks.
- [ ] Before the user-facing completion response, the main agent runs reflection, reconciles any findings, then runs three parallel `final_reviewer` subagents.
- [ ] All three final reviewers return READY FOR USER before the completion claim is sent.
