---
name: klimkit-grill-me
description: Interview the user relentlessly about a plan, design, architecture, product decision, workflow, or release choice until shared understanding is reached, using repo and web research to prioritize the most important unresolved questions while recording each question and approved decision in a Klimkit task note. Use when the user asks to be grilled, stress-test a plan, resolve design branches, clarify tradeoffs, or turn vague intent into explicit decisions.
---

# Klimkit Grill Me

Interview the user relentlessly about every important part of the plan until both sides can see the same shape of the decision. Walk down the design tree branch by branch, resolve dependencies between decisions one at a time, and provide your recommended answer for each question.

Keep the session direct and human. This is a working conversation, not a form: ask the question you would actually ask if you were trying to save the plan from a hidden flaw, a vague assumption, or a weak tradeoff. The Klimkit addition is that every approved decision gets a short written trail.

## Workflow

1. Resolve the active operator folder. If the repo has no clear `.klimkit/<operator>/` context, use `klimkit-setup` first.
2. Create or reuse a grilling-session task folder under `.klimkit/<operator>/tasks/`, for example `.klimkit/<operator>/tasks/15-grilling-session/`.
3. Create or reuse a number-prefixed agent-authored Markdown note in that folder, for example `01-a-grilling-session.md`.
4. Start the note with a short title, the source request, and the current decision target.
5. Prepare under the hood before asking:
   - Inspect the relevant codebase, docs, task notes, and existing decisions.
   - Search the web for current outside context when market, product, API, framework, legal, pricing, or best-practice facts could affect the answer.
   - Draft a private top-question list, estimate each question's importance, and rank contradictions or complete requirement gaps first.
6. Ask exactly one question at a time: the current highest-importance question from the ranked list.
7. For each question, include your recommended answer unless repo/web research or user context makes that premature.
8. After the user answers, append a short tracking memo to the grilling-session note:
   - `Q:` the question asked.
   - `Approved decision:` the user's decision, or your concise restatement if the user approved your recommendation.
   - `Open follow-up:` only when the answer leaves a real unresolved branch.
9. Rebuild and rerank the private top-question list after every answer, using the new state and any new facts discovered from the repo or web.
10. Continue until the remaining branches are low-risk, explicitly deferred, or converted into concrete tasks.
11. End with a compact decision summary and the path to the grilling-session note.

## Question Style

- Be relentless about unresolved ambiguity, but do not be theatrical or adversarial.
- Hunt first for contradictions, missing requirements, weak assumptions, and decisions that would invalidate downstream work.
- Prefer concrete tradeoff questions over broad brainstorming prompts.
- Walk dependencies in order: constraints, users, success criteria, data model, interfaces, failure modes, rollout, verification, and maintenance.
- Ask like a senior collaborator who cares about the outcome: short, plain, and specific.
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
