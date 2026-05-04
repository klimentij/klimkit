# AGENTS.md43

You're Klim's coding agent.

These are the shared, home-level defaults for every project. Repository-local `AGENTS.md` files add project-specific rules and take precedence when they are more specific.

## Shared Workflow

- Understand before changing. For unfamiliar code, explore first or delegate the read-heavy work to `code_explorer`.
- Prefer red/green TDD for behavior-changing work when the repository has an automated test harness.
- Every change should include cleanup: remove duplication, reuse existing helpers, and leave the touched area cleaner than you found it.
- Review meaningful changes before presenting them. Use `code_reviewer` when the task is substantial, risky, or spread across multiple files.
- If tests fail or behavior is surprising, use `debugger` to isolate the root cause before guessing.
- For external APIs, libraries, standards, or best-practice checks, use `web_research` and prefer official documentation.
- For auth, secrets, API boundaries, infra, sandbox, or container work, run `security_auditor` before calling the task done.
- When a task changes user-visible behavior, end with a short `How Klim can check this` section with concrete manual verification steps.
- When the user wants proof or a quick verification artifact, default to a tiny static HTML report that is easy to skim, mostly visual, and shared by URL. Do not default to notebooks unless the user explicitly asks for one.

## Shared Subagents

Custom Codex agents are managed from `packs/codex/agents/` and synced into `~/.codex/agents/`.

- Use delegation when it materially reduces context noise or lets independent work happen in parallel.
- Prefer waves of 2-3 subagents. Avoid broad 5+ agent fan-out unless the task truly benefits from it.
- Do not delegate purely for ceremony. Small, direct tasks should stay inline.
- `final_reviewer` is the final gate before any response that claims the work is complete. Give it the original request, acceptance criteria, and the exact draft response.
- Reach for the shared agents intentionally:
  - `code_explorer` for unfamiliar code and architecture tracing
  - `code_reviewer` for bug-risk and regression review
  - `debugger` for diagnosis without fixing
  - `manual_tester` for browser and UI verification when the repo provides the needed environment
  - `security_auditor` for security-sensitive changes
  - `test_writer` for planning, writing, and running tests
  - `web_research` for external verification and source-backed answers

## Shared Skills

Shared skills live in `~/.codex/skills/`. Prefer a matching documented skill over ad-hoc command sequences when one exists, and let repository-local skills add project-specific workflows as needed.

## Klimkit Project Memory, Logs, And Tasks

At the start of meaningful repo work, read `.klimkit/memory.md` and `.klimkit/log.md` when they exist. If either file is missing and meaningful repo work is starting, create it under `.klimkit/` before the first memory or log update.

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

Store durable preferences, corrections, and process rules in `.klimkit/memory.md` as dated one-sentence memories. Store meaningful actions in `.klimkit/log.md` as ISO-timestamped one-sentence audit entries. Logs describe what happened, not preferences.

Task and feature work belongs under `.klimkit/tasks/<nn-feature-slug>/`. Human-authored files use `-h-` in the filename. Agent-authored files use `-a-` in the filename. Task folders can contain planning, design, discussion, proof, and implementation notes.


# Behavioral guidelines

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.
