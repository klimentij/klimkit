# AGENTS.md

You're __HUMAN_NAME__'s coding agent.

These are shared, home-level defaults. Repository-local `AGENTS.md` files add project-specific rules and take precedence when they are more specific.

## Authority And Scope

- Treat the user's latest message as the active request.
- Follow repository-local instructions before these shared defaults when they are more specific.
- Keep generated home files out of source edits; shared Codex behavior is edited in `packs/codex/`.
- Before returning to __HUMAN_NAME__ with a completion claim, complete the required checklist, verification, and final-review gate.

## Standard Workflow

1. **Intake**
   - Read the request, relevant task file, repository instructions, `.klimkit/memory.md`, and `.klimkit/log.md` when present.
   - Identify whether the work is planning-only, implementation, review, debugging, or research.

2. **Acceptance Checklist**
   - For every implementation task, invoke `checklister` before coding.
   - The checklist must be written into an agent-authored task note (`*-a-*.md`) in the relevant `.klimkit/tasks/<feature>/` folder.
   - Treat every checklist item as blocking unless __HUMAN_NAME__ explicitly changes scope.

3. **Plan And Delegate**
   - State the smallest useful plan for non-trivial work.
   - Use other subagents only when they materially reduce risk or let independent work happen in parallel.
   - Prefer waves of 2-3 subagents; avoid broad fan-out unless the task truly benefits.

4. **Implement**
   - Understand before changing; explore first or delegate read-heavy tracing to `code_explorer`.
   - Prefer red/green TDD for behavior-changing work when the repository has tests.
   - Keep edits surgical, reuse existing helpers, and remove only dead code introduced by the change.
   - Do not refactor unrelated code while passing through.

5. **Verify**
   - Run the tests and checks that match the checklist and blast radius.
   - For UI work, verify the actual screen states, empty/loading/error states, interaction states, persistence, local storage, database effects, network/API effects, and responsive behavior called out by the checklist.
   - For UI work, produce a final HTML proof report under the active repo's `.klimkit/reports/` directory with text evidence, required screenshots, and a native `agent-browser` video recording referenced from the report. Render each screenshot and video as a full-width section so it can be inspected without opening thumbnails. Prefer MP4 in the report for reliable Chrome/PWA scrubbing; a native WebM recording may be converted to MP4 for presentation.
   - When a Tailscale DNS name is available, proof handoffs and final responses must include the Tailscale-served report URL under `https://<machine>.<tailnet>.ts.net/reports/`; localhost report URLs are only local QA fallback evidence.
   - If tests fail or behavior is surprising, use `debugger` to isolate the root cause before guessing.
   - For auth, secrets, sandboxing, infra, or compliance-sensitive changes, run `security_auditor` before calling the task done.

6. **Final Review Gate**
   - Draft the exact final response before calling reviewers.
   - Run 3 `final_reviewer` subagents in parallel.
   - Give each reviewer the original human request or task path, the checklister acceptance checklist, the changed files, verification evidence, the final HTML proof report path and Tailscale report URL for UI work, and the exact draft response.
   - All 3 reviewers must return PASS / READY FOR USER before you send a completion claim to __HUMAN_NAME__.

7. **Report**
   - Report what changed, what passed, and any remaining risk or unavailable verification.
   - When user-visible behavior changed, include `How __HUMAN_NAME__ can check this` with concrete manual steps.
   - When proof is requested, prefer a tiny static HTML report under `.klimkit/reports/` or compact task note that is easy to skim, and include the Tailscale-served report URL when available.

## Subagent Roles

Custom Codex agents are managed from `packs/codex/agents/` and synced into `~/.codex/agents/`.

- `checklister`: acceptance-criteria specialist. Required before implementation; writes the blocking checklist into an agent-authored task note.
- `code_explorer`: read-only architecture and execution-path tracing before changes.
- `code_reviewer`: correctness, regression, security, duplication, and missing-test review.
- `debugger`: read-only reproduction and root-cause analysis for failures.
- `manual_tester`: browser/UI verification in a runnable environment.
- `security_auditor`: auth, secrets, data exposure, sandboxing, infra, and compliance-sensitive review.
- `test_writer`: focused test planning, implementation, and execution.
- `web_research`: source-backed external verification, API docs, and current best practices.
- `final_reviewer`: final acceptance gate. Required 3-at-a-time before a completion claim.

## Shared Skills

Shared skills live in `~/.codex/skills/`. Prefer a matching documented skill over ad-hoc command sequences when one exists.

- Use `harness-tuning` when changing shared home-level Codex behavior. It keeps edits in `~/klimkit/packs/codex/` so `kk apply` and autosync project them to `~/.codex/` cleanly.
- Use UI/browser skills for live frontend QA when a task depends on actual screen behavior.

## Memory, Logs, And Task Notes

At the start of meaningful repo work, read `.klimkit/memory.md` and `.klimkit/log.md` when they exist. If either file is missing and meaningful repo work is starting, create it under `.klimkit/`.

Use this memory template:

```markdown
# Project Memory

Durable preferences, corrections, and process rules. Add dated one-sentence memories.

## Memories
```

Use this log template:

```markdown
# Project Log

Timestamped audit trail. Entries describe actions, not preferences.

## Log
```

- Store durable preferences, corrections, and process rules in `.klimkit/memory.md` as dated one-sentence memories.
- Store meaningful actions in `.klimkit/log.md` as ISO-timestamped one-sentence audit entries.
- Task and feature work belongs under `.klimkit/tasks/<nn-feature-slug>/`.
- Human-authored files use `-h-`; agent-authored files use `-a-`.
- Task folders can contain planning, checklists, design notes, implementation notes, proof, screenshots, and review records.

## Engineering Quality Rules

- Surface assumptions and ambiguities before coding when they affect implementation choices.
- Keep the solution as small as the request allows; avoid speculative features and one-use abstractions.
- Match the repository's existing style, framework, helper APIs, and test conventions.
- Every changed line should trace to the request, checklist, or required verification.
- Broaden tests when touching shared behavior, cross-module contracts, user-visible workflows, or persistence.
- If the user asks for a review, lead with findings ordered by severity, then open questions, then summary.

## Completion Bar

A task is not done until:

- The checklister checklist exists for implementation work.
- Required code, docs, data, or pack changes are complete.
- Relevant automated checks and manual checks from the checklist have passed or are explicitly called out as unavailable.
- Meaningful memory/log/task proof has been updated when the repo workflow requires it.
- The exact final response has passed 3 parallel `final_reviewer` reviews.
