---
name: klimkit-implement
description: Run Klimkit's full implementation workflow for code, docs, release, configuration, UI, backend, security-sensitive, or proof-producing changes. Use when the user asks Codex to implement, fix, refactor, release, migrate, wire up, or complete non-trivial repository work with checklist, verification, reflection, and final review.
---

# Klimkit Implement

Use this as the skills-first replacement for the old global `AGENTS.md` implementation workflow. Keep the work in the main agent by default. Do not use subagents for exploration, checklists, debugging, security, or reflection unless the user explicitly asks; the only built-in subagent use is the final-review gate.

## Workflow

1. **Intake**
   - Read the latest user request, repo instructions, relevant memory/log/task notes, docs, and nearby code.
   - If `.klimkit/<operator>/` is missing or ambiguous, use `klimkit-setup`.
   - Decide whether the work is implementation, debugging, release, review, research, UI/proof, or security-sensitive.
2. **Explore**
   - Use `klimkit-code-explorer` inline when the code path is unfamiliar, broad, or risky.
   - Use direct repo reads for simple tasks.
3. **Checklist**
   - Use `klimkit-checklister` before code changes for implementation work.
   - Treat the checklist as blocking unless the user changes scope.
4. **Implement**
   - Choose the narrow method skill when helpful: `klimkit-diagnose`, `klimkit-tdd`, `klimkit-walkthrough`, `klimkit-report-server`, or `klimkit-worktree-stack`.
   - Keep edits surgical and aligned with existing repo style.
   - Do not route new work through deprecated runtime, Switchboard, sync scripts, or plugin machinery unless explicitly maintaining legacy code.
5. **Verify**
   - Run checks that match the checklist and blast radius.
   - Record exact commands, important outputs, skipped checks, and remaining risk.
   - For UI/proof work, produce inspectable report evidence when the repo workflow requires it.
6. **Security**
   - Use `klimkit-security-auditor` before completion when the change touches auth, secrets, permissions, containers, network exposure, infrastructure, user data, or unsafe defaults.
7. **Reflect**
   - Use `klimkit-reflector` after verification and before final review for non-trivial work.
   - If reflection exposes a material gap, fix it and rerun impacted checks.
8. **Final Review**
   - Draft the exact final response.
   - Run fresh final-review passes with `klimkit-final-reviewer`.
   - Prefer 3 independent final-review subagents when subagents are available and the user has not forbidden them. Give each only the original request, checklist, changed files, verification evidence, reflection note, proof artifacts, and exact draft response.
   - If subagents are unavailable or forbidden, run `klimkit-final-reviewer` inline and state that limitation.
   - Do not claim completion until final review returns `READY FOR USER` or all remaining gaps are explicitly reported.
9. **Report**
   - Tell the user what changed, what passed, what was skipped, and how to inspect the result.
   - For commits on `main` in this repo, create or update the latest GitHub release according to repo instructions.

## Skill Routing

- `klimkit-checklister`: acceptance criteria before edits.
- `klimkit-code-explorer`: read-only tracing before edits.
- `klimkit-security-auditor`: security-sensitive review.
- `klimkit-reflector`: cross-task synthesis after verification.
- `klimkit-final-reviewer`: final gate, preferably from fresh subagents.
