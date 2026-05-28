---
name: klimkit-workflow
description: Use Klimkit's evidence-first workflow for implementation, debugging, planning, review, and release tasks that need checklist-driven execution, `.klimkit` task artifacts, verification proof, reflection, final review, or handoff discipline.
---

# Klimkit Workflow

Use this as the coordination skill. Pair it with task-method skills such as `klimkit-diagnose`, `klimkit-tdd`, `klimkit-walkthrough`, `klimkit-report-server`, or `klimkit-worktree-stack` instead of expanding this skill into a monolith.

## Default Path

- Treat Klimkit as a Vercel Skills CLI package first: install and update the root `skills/` library with `npx skills`.
- Use normal Codex app or CLI sessions plus installed Klimkit skills for day-to-day work.
- Keep task evidence in the project repository, not in generated home files.
- Treat older Klimkit runtime machinery as deprecated legacy material. Do not route new workflows through it unless the user explicitly asks to maintain legacy code.

## Workflow

1. Identify the active operator folder. If the repo has no clear `.klimkit/<operator>/` context, use `klimkit-setup` and ask for the operator name before creating files.
2. Read repository instructions, the active task note, `.klimkit/<operator>/memory.md`, `.klimkit/<operator>/log.md`, relevant prior tasks, and nearby tests or docs.
3. For implementation work, create or update an agent-authored checklist in `.klimkit/<operator>/tasks/<feature>/` before code changes.
4. Pick the narrowest useful method skill: diagnose, TDD, walkthrough, report-server, or worktree-stack.
5. Implement or plan only the requested scope. Do not refactor adjacent code unless the checklist requires it.
6. Verify against the checklist. For UI or workflow proof, produce real screenshots/video or a report when the local repo requires it.
7. Record proof: files changed, checks run, important outputs, skipped checks, and remaining risk.
8. For non-trivial work, append a timestamped reflection session to `.klimkit/<operator>/reflection.md`.
9. Run final review according to the repository rules before claiming completion.
10. Report what changed, what passed, and how the human can inspect the result.

## Evidence Layout

Read [references/artifact-workflow.md](references/artifact-workflow.md) when concrete `.klimkit` paths, task-note naming, proof reports, memory/log/reflection, or team/solo layout details matter.

If a task asks to migrate old Klimkit runtime behavior into skills, make the target skill own any reference scripts, templates, and setup instructions it needs.
