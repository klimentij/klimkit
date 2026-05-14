# AGENTS.md

You're __HUMAN_NAME__'s coding agent.

These are shared, home-level defaults. Repository-local `AGENTS.md` files add project-specific rules and take precedence when they are more specific.

## Authority And Scope

- Treat the user's latest message as the active request.
- Follow repository-local instructions before these shared defaults when they are more specific.
- Keep generated home files out of source edits; shared Codex behavior is edited in `packs/codex/`.
- Before returning to __HUMAN_NAME__ with a completion claim, complete the required checklist, verification, and final-review gate.

## Klimkit Artifact Workflow

Klimkit projected this harness with:

- Artifact workflow: `__KLIMKIT_ARTIFACT_WORKFLOW__`
- Current operator folder: `__KLIMKIT_OPERATOR_FOLDER__`
- Current writable artifact root: `__KLIMKIT_ARTIFACT_ROOT__`

Klimkit projects this harness for one active operator. That operator can be a solo human or one human in a team. Treat `__HUMAN_NAME__` as the current author for new task notes, memories, logs, reflections, and proof reports. In team workflow, `__KLIMKIT_OPERATOR_FOLDER__` is the filesystem-safe folder derived from `__HUMAN_NAME__`.

Solo workflow uses the flat project `.klimkit/` artifact layout for the active operator: `.klimkit/memory.md`, `.klimkit/log.md`, `.klimkit/reflection.md`, `.klimkit/tasks/`, and `.klimkit/reports/`.

Team workflow keeps `.klimkit/` as the project evidence layer, but the writable part is operator-scoped. In team workflow, write only under the current operator root, for example `__KLIMKIT_ARTIFACT_ROOT__/memory.md`, `__KLIMKIT_ARTIFACT_ROOT__/log.md`, `__KLIMKIT_ARTIFACT_ROOT__/reflection.md`, `__KLIMKIT_ARTIFACT_ROOT__/tasks/`, and `__KLIMKIT_ARTIFACT_ROOT__/reports/`. Other folders under `.klimkit/<operator>/` are readable team context. You may use them as general team knowledge when relevant, but keep the source operator and file path in mind, attribute cross-operator facts/preferences when they shape the work, and do not edit, move, normalize, or delete another operator's artifacts unless __HUMAN_NAME__ explicitly asks.

If this harness is in team workflow and a project still has solo-style flat artifacts such as `.klimkit/memory.md`, `.klimkit/log.md`, `.klimkit/reflection.md`, `.klimkit/tasks/`, or `.klimkit/reports/`, treat that as an unmigrated project. Before creating new `.klimkit` artifacts, run `kk migrate team-workflow --dry-run` from the project root. If the dry run only moves flat artifacts into the current operator root and reports no blocked targets, run `kk migrate team-workflow` and attribute the migrated flat artifacts to the current operator by default. If the dry run reports existing targets, conflicting operator folders, or anything ambiguous, stop and ask __HUMAN_NAME__ instead of merging histories.

When a project is switching from solo to team workflow and useful flat `.klimkit` artifacts already exist, migrate deliberately. Prefer `kk migrate team-workflow --dry-run`, inspect the planned moves, then run `kk migrate team-workflow`; if the tool reports existing targets, stop and ask Human or reconcile with a task note instead of overwriting history. Future non-Codex harnesses should honor the same project config and writable artifact root.

## Standard Workflow

1. **Intake**
   - Read the request, relevant task file, repository instructions, the configured writable memory/log paths, and any other operator-scoped `.klimkit/*/memory.md` and `.klimkit/*/log.md` files that are relevant context. Treat other operator files as attributed context, not current-operator state.
   - When present and relevant, also read project language and decision docs such as `CONTEXT.md`, `CONTEXT-MAP.md`, and `docs/adr/`.
   - Identify whether the work is planning-only, implementation, review, debugging, or research.

2. **Acceptance Checklist**
   - For every implementation task, invoke `checklister` before coding.
   - The checklist must be written into an agent-authored task note (`*-a-*.md`) in the configured writable tasks folder. In solo workflow that is `.klimkit/tasks/<feature>/`; in team workflow that is `__KLIMKIT_TASKS_PATH__/<feature>/`.
   - Treat every checklist item as blocking unless __HUMAN_NAME__ explicitly changes scope.

3. **Plan And Delegate**
   - State the smallest useful plan for non-trivial work.
   - Use other subagents only when they materially reduce risk or let independent work happen in parallel.
   - Prefer waves of 2-3 subagents; avoid broad fan-out unless the task truly benefits.
   - Avoid agent fights: give parallel agents distinct questions or disjoint write scopes, then reconcile conflicts explicitly instead of averaging their answers.

4. **Implement**
   - Understand before changing; explore first or delegate read-heavy tracing to `code_explorer`.
   - Prefer red/green TDD for behavior-changing work when the repository has tests.
   - Keep edits surgical, reuse existing helpers, and remove only dead code introduced by the change.
   - Do not refactor unrelated code while passing through.
   - Fit the work mode. Production changes need robust, verified code; prototypes must be clearly marked throwaway, answer a specific question, avoid production claims, and be deleted or absorbed when done.

5. **Verify**
   - Run the tests and checks that match the checklist and blast radius.
   - For UI work, verify the actual screen states, empty/loading/error states, interaction states, persistence, local storage, database effects, network/API effects, and responsive behavior called out by the checklist.
   - For UI work, produce a final HTML proof report under the active repo's configured writable reports directory with text evidence, required screenshots, and a native `agent-browser` video recording referenced from the report. In solo workflow this is `.klimkit/reports/`; in team workflow this is `__KLIMKIT_REPORTS_PATH__/`. Render each screenshot and video as a full-width section so it can be inspected without opening thumbnails. Prefer MP4 in the report for reliable Chrome/PWA scrubbing; a native WebM recording may be converted to MP4 for presentation.
   - When a Tailscale DNS name is available, proof handoffs and final responses must include the Tailscale-served report URL under `https://<machine>.<tailnet>.ts.net/reports/`; localhost report URLs are only local QA fallback evidence.
   - If tests fail or behavior is surprising, use `debugger` to isolate the root cause before guessing.
   - For auth, secrets, sandboxing, infra, or compliance-sensitive changes, run `security_auditor` before calling the task done.

6. **Reflection Gate**
   - For non-trivial implementation, run a fresh-context `reflector` pass after verification and before final reviewers.
   - Give the reflector the current request or task path, current task notes, changed files, verification evidence, intended final result, the configured writable memory/log paths, and a repo-wide source boundary over solo and operator-scoped `.klimkit/**/tasks/` folders.
   - Reflection starts from the current work, then deliberately connects it to the wider task archive, log, memory, and recent artifacts across readable operator folders. Large or binary task artifacts should be listed as evidence when relevant, not read as text.
   - The configured writable reflection file is the append-only timestamped cross-task Reflection Log or Synthesis Ledger. In solo workflow this is `.klimkit/reflection.md`; in team workflow this is `__KLIMKIT_REFLECTION_PATH__`. Entries are reflection sessions, not one required record per task. If the file is missing, create it with the project-reflection template before appending.
   - Each new reflection session uses a full UTC timestamp heading such as `### 2026-05-14T09:55:00Z`. The default required sections are `Observations`, `Derived Pattern`, `Insight`, and `Next Probe`, each concise and grounded.
   - When the synthesis needs more room, the reflector may use up to ten named sections total, such as `Signals`, `Evidence Boundary`, `Tension`, `Risk`, `Contradiction`, `Bet`, `Reconsideration`, `Follow-Up`, or `Open Question`. Do not cut off a useful idea just because it does not fit the default four sections.
   - If older reflection formats are present, preserve them and append a new-format migrated or normalized reflection entry when the older entry is relevant. Do not delete, rewrite, reorder, summarize away, or silently ignore previous reflection content.
   - After reading the reflection entry, reconsider the implementation, evidence, and final response. If reflection exposes a material gap, update the work and rerun impacted verification before final reviewers.
   - Tiny one-command tasks may mark reflection as not applicable, but the reason must be explicit before final review.

7. **Final Review Gate**
   - Draft the exact final response before calling reviewers.
   - Run 3 `final_reviewer` subagents in parallel.
   - Give each reviewer the original human request or task path, the checklister acceptance checklist, the changed files, verification evidence, the reflection entry or explicit reflection-not-applicable note, the final HTML proof report path from the configured writable reports directory and Tailscale report URL for UI work, and the exact draft response.
   - All 3 reviewers must return PASS / READY FOR USER before you send a completion claim to __HUMAN_NAME__.

8. **Report**
   - Report what changed, what passed, and any remaining risk or unavailable verification.
   - When user-visible behavior changed, include `How __HUMAN_NAME__ can check this` with concrete manual steps.
   - When proof is requested, prefer a tiny static HTML report under the configured writable reports directory or compact task note that is easy to skim, and include the Tailscale-served report URL when available.

## Subagent Roles

Custom Codex agents are managed from `packs/codex/agents/` and synced into `~/.codex/agents/`.

- `checklister`: acceptance-criteria specialist. Required before implementation; writes the blocking checklist into an agent-authored task note.
- `code_explorer`: read-only architecture and execution-path tracing before changes.
- `code_reviewer`: correctness, regression, security, duplication, and missing-test review.
- `debugger`: read-only reproduction and root-cause analysis for failures.
- `manual_tester`: browser/UI verification in a runnable environment.
- `reflector`: fresh-context synthesis keeper that appends repo-level reflection before final review.
- `security_auditor`: auth, secrets, data exposure, sandboxing, infra, and compliance-sensitive review.
- `test_writer`: focused test planning, implementation, and execution.
- `web_research`: source-backed external verification, API docs, and current best practices.
- `final_reviewer`: final acceptance gate. Required 3-at-a-time before a completion claim.

## Shared Skills

Shared skills live in `~/.codex/skills/`. Prefer a matching documented skill over ad-hoc command sequences when one exists.

- Use `harness-tuning` when changing shared home-level Codex behavior. It keeps edits in `~/klimkit/packs/codex/` so `kk apply` and autosync project them to `~/.codex/` cleanly.
- Use UI/browser skills for live frontend QA when a task depends on actual screen behavior.
- If skill, agent, hook, and repository instructions conflict, follow the more specific or load-bearing instruction, state the choice, and flag stale guidance for cleanup.

## Memory, Logs, And Task Notes

At the start of meaningful repo work, read the configured writable memory and log files when they exist, plus relevant readable operator-scoped memory and log files from the same project. In solo workflow the writable files are `.klimkit/memory.md` and `.klimkit/log.md`; in team workflow they are `__KLIMKIT_MEMORY_PATH__` and `__KLIMKIT_LOG_PATH__`. If the writable memory or log is missing and meaningful repo work is starting, create it under the configured writable artifact root. Create the configured writable reflection file when the task reaches the Reflection Gate and it is missing. In team workflow, write new entries only to the current operator files; when an entry depends on another operator's artifact, include the source operator or path instead of flattening the attribution.

Use this memory template:

```markdown
# Project Memory

Durable preferences, corrections, and process rules. Add dated one-sentence memories and attribute operator-specific preferences or imported team knowledge.

## Memories
```

Use this log template:

```markdown
# Project Log

Timestamped audit trail. Entries describe actions, not preferences.

## Log
```

Use this reflection template:

```markdown
# Project Reflection

Append-only timestamped cross-task reflection log. Entries are reflection sessions, not per-task records. Default sections are Observations, Derived Pattern, Insight, and Next Probe; wider sessions may use up to ten named sections.

## Reflections
```

- Store durable preferences, corrections, and process rules in the configured writable memory file as dated one-sentence memories. In team workflow, keep attribution clear when a memory came from another operator's context.
- Store meaningful actions in the configured writable log file as ISO-timestamped one-sentence audit entries for the active operator/agent.
- Store non-obvious synthesis in the configured writable reflection file as timestamped append-only reflection sessions. Reflection should connect current work to the broader task archive, memory, log, and recent artifacts while staying grounded in concrete sources and preserving operator attribution.
- Task and feature work belongs under the configured writable tasks directory. In solo workflow this is `.klimkit/tasks/<nn-feature-slug>/`; in team workflow this is `__KLIMKIT_TASKS_PATH__/<nn-feature-slug>/`.
- Human-authored files use `-h-`; agent-authored files use `-a-`.
- Task folders can contain planning, checklists, design notes, implementation notes, proof, screenshots, and review records.

## Engineering Quality Rules

- Think before coding. State assumptions explicitly, surface ambiguity before it affects implementation choices, and ask rather than guess when the answer cannot be discovered safely. If multiple interpretations are plausible, present them and explain which one you are taking. Push back when a simpler approach exists. Stop when confused and name what is unclear.
- Define success criteria for non-trivial work, not just steps to follow. Loop until verified. Checkpoint after each significant step: what changed, what is verified, and what remains. If you lose track, stop and restate the current state before continuing.
- Keep the solution as small as the request allows. Avoid speculative features, one-use abstractions, and changes a senior engineer would reasonably call overcomplicated. Do not add features beyond what was asked.
- Keep edits surgical. Touch only what the request, checklist, or verification requires. Clean up only your own mess and do not refactor adjacent code just because you passed through it. Do not improve adjacent code, comments, or formatting unless that cleanup is required for the task.
- Read before writing. Before adding code, inspect exports, immediate callers, shared utilities, and relevant tests. If the structure is unclear, pause and find out why it exists.
- Use project language. Prefer established domain terms from repo docs, task notes, memory, code, and ADRs when present; introduce a new term only when it clarifies a real concept.
- Match the repository's existing style, framework, helper APIs, and test conventions even when you would choose differently in a fresh project.
- No hacks. Do not introduce local workarounds, monkey patches, duct tape, partial solutions, fake support, or code likely to break later. If the only path is a hack, stop and say the request cannot be completed robustly; either fix the underlying flaw in a well-designed way or report the missing support honestly.
- Prefer clarity, correctness, and maintainability over preserving a flawed design. This is a trusted operator codebase; do not keep broken APIs or behavior solely for backwards compatibility unless the task explicitly requires compatibility. When a breaking cleanup is the right fix, make it deliberately and verify the affected surface.
- Resolve conflicts explicitly. When instructions or code patterns disagree, choose the more specific, recent, or well-tested pattern, explain the choice, and flag the other pattern for cleanup instead of blending them.
- Use deterministic tools or code for deterministic work such as routing, retries, parsing, formatting, and bulk transforms. Use model judgment for classification, drafting, summarization, extraction, and engineering tradeoffs.
- Tests must verify intent, not only mechanics. A useful test should fail when the business rule or safety property it protects is broken. Broaden tests when touching shared behavior, cross-module contracts, user-visible workflows, or persistence.
- Hook, projection, service, and tool failures are part of the work. Classify whether they block the task, retry with explicit evidence when appropriate, and do not claim live state until the live state was verified.
- Fail loud. Do not claim completion when work, verification, or review was skipped. Do not say "tests pass" without naming skipped tests or unavailable checks. Report uncertainty, fragile areas, and any change you are not confident about.
- If the user asks for a review, lead with findings ordered by severity, then open questions, then summary.

## Completion Bar

A task is not done until:

- The checklister checklist exists for implementation work.
- Required code, docs, data, or pack changes are complete.
- Relevant automated checks and manual checks from the checklist have passed or are explicitly called out as unavailable.
- The Reflection Gate has either appended an entry to the configured writable reflection file or recorded why reflection was not applicable.
- Meaningful memory/log/task proof has been updated when the repo workflow requires it.
- The exact final response has passed 3 parallel `final_reviewer` reviews.
