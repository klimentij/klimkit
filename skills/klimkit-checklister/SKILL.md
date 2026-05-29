---
name: klimkit-checklister
description: Convert an implementation, debugging, release, UI, backend, security, or research request into a concrete pass/fail acceptance checklist before code changes start. Use when Codex needs blocking success criteria, scope boundaries, verification targets, or a task note for Klimkit-managed work.
---

# Klimkit Checklister

Use this before implementation work. The output is an agent-authored task note with observable acceptance criteria, not a loose plan.

## Workflow

1. Read the user request, repo instructions, existing `.klimkit` memory/log/task notes, relevant docs, and enough nearby code to understand the real acceptance surface.
2. Resolve the active operator folder. If there is no clear `.klimkit/<operator>/` context, use `klimkit-setup` first.
3. Create or update `.klimkit/<operator>/tasks/<feature>/<nn-a-acceptance-checklist>.md`.
4. Add an `Acceptance Checklist` section using checkbox bullets.
5. Make every item observable: a file exists, a command passes, a behavior is visible, a release points to a commit, a proof report renders, or an explicit risk is named.
6. Include scope boundaries and skipped work. For prototypes, require the prototype question, run command, and deletion-or-absorption decision.
7. Include verification expectations that match the blast radius:
   - UI: screens, states, screenshots/video, report path, and report URL expectations.
   - Backend/API: request/response shape, validation, auth, errors, logs, and tests.
   - Persistence/sync: files, database rows, caches, queues, services, restart behavior, and cross-machine effects.
   - Security-sensitive work: require `klimkit-security-auditor`.
8. Include reflection/final-review expectations for non-trivial work: `klimkit-reflector` after verification and `klimkit-final-reviewer` before completion.
9. End with the checklist path and any unresolved scope questions.

Treat checklist items as blocking unless the user explicitly changes scope.
