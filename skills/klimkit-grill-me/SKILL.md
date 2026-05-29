---
name: klimkit-grill-me
description: Interrogate a plan, design, architecture, product decision, workflow, or release choice one question at a time until shared understanding is reached, while recording each question and approved decision in a Klimkit task note. Use when the user asks to be grilled, stress-test a plan, resolve design branches, clarify tradeoffs, or turn vague intent into explicit decisions.
---

# Klimkit Grill Me

Use this skill to pressure-test a plan through short, sequential questioning. Keep the session useful, not performative: ask the next highest-leverage question, recommend an answer when you can, and record decisions as they become approved.

## Workflow

1. Resolve the active operator folder. If the repo has no clear `.klimkit/<operator>/` context, use `klimkit-setup` first.
2. Create or reuse a grilling-session task folder under `.klimkit/<operator>/tasks/`, for example `.klimkit/<operator>/tasks/15-grilling-session/`.
3. Create or reuse a number-prefixed agent-authored Markdown note in that folder, for example `01-a-grilling-session.md`.
4. Start the note with a short title, the source request, and the current decision target.
5. Ask exactly one question at a time.
6. For each question, include your recommended answer unless codebase exploration or user context makes that premature.
7. If the answer can be discovered from the repository, inspect the repository instead of asking the user.
8. After the user answers, append a short tracking memo to the grilling-session note:
   - `Q:` the question asked.
   - `Approved decision:` the user's decision, or your concise restatement if the user approved your recommendation.
   - `Open follow-up:` only when the answer leaves a real unresolved branch.
9. Continue until the remaining branches are low-risk, explicitly deferred, or converted into concrete tasks.
10. End with a compact decision summary and the path to the grilling-session note.

## Question Style

- Prefer concrete tradeoff questions over broad brainstorming prompts.
- Walk dependencies in order: constraints, users, success criteria, data model, interfaces, failure modes, rollout, verification, and maintenance.
- When the user gives a partial answer, restate the decision you think was approved and ask the next question.
- Keep each question short enough to answer immediately.
- Do not batch multiple questions unless the user explicitly asks for a checklist instead of an interview.

## Tracking Note

Use this shape for the note:

```markdown
# Grilling Session

Source request: <one sentence>
Decision target: <one sentence>

## Decision Log

- Q: <question>
  Approved decision: <short decision>
  Open follow-up: <only if needed>
```

Keep the note append-only during the session. If a later answer changes an earlier decision, add a new entry that says what changed instead of rewriting the old one.
