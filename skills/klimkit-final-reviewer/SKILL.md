---
name: klimkit-final-reviewer
description: Perform a fresh-context final acceptance review of the exact draft response against the original request, checklist, changed files, verification evidence, reflection, and proof artifacts. Use as the last gate before telling the human work is complete; use from one or two scoped fresh subagents when `klimkit-implement` requests final review, or inline when subagents are unavailable.
---

# Klimkit Final Reviewer

Use this only after the main agent believes the work is complete and has drafted the exact final response. Review; do not implement fixes.

When `klimkit-implement` can spawn final-review subagents, use one or two fresh reviewers, not broad fan-out. Give each reviewer a slightly different scope. If subagents are unavailable or forbidden, the main agent should read this skill and perform the review inline, then state that limitation.

## Required Inputs

- Original user request or task path.
- Acceptance checklist when implementation was involved.
- Changed files and important diffs.
- Verification evidence and skipped checks.
- Reflection entry or explicit reflection-not-applicable note.
- Proof report path and URL for UI/proof work.
- Exact draft response that would be sent to the human.

## Review Workflow

1. Extract every concrete claim from the draft response.
2. Verify each claim against the request, checklist, changed files, test output, release state, and proof artifacts.
3. Confirm unavailable checks and residual risks are named accurately.
4. For UI/proof work, inspect the report and media references when accessible.
5. For non-trivial implementation, require `klimkit-reflector` output or a justified not-applicable note.
6. Return `KEEP WORKING` if any material claim is unsupported, contradicted, vague, incomplete, missing reflection, or missing required proof.
7. Return `READY FOR USER` only when the draft is fully supported.

## Output

Use these sections:

- `User intent`
- `What is verified`
- `What is missing or not proven`
- `Verdict`
- `Next actions for main agent`

The verdict must be exactly `READY FOR USER` or `KEEP WORKING`.
