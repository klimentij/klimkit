---
name: klimkit-diagnose
description: Diagnose bugs, failures, flaky behavior, broken tests, CI failures, or unexpected production signals with a reproduce-first workflow and Klimkit proof. Use when the user asks to debug, investigate, root-cause, fix a failure, or explain why behavior changed.
---

# Klimkit Diagnose

Diagnose before fixing. The output should make the failure, root cause, fix, and regression proof inspectable.

## Workflow

1. Ensure operator-scoped Klimkit context exists. If `.klimkit/<operator>/` is missing or ambiguous, use `klimkit-setup` first.
2. Define the symptom in one sentence and identify the smallest observable failure signal.
3. Read relevant instructions, prior task notes, logs, and nearby tests before changing code.
4. Reproduce the failure with the cheapest deterministic command, UI path, log bundle, or fixture.
5. Minimize the failing surface: isolate the module, route, command, input, environment, or data dependency.
6. Form hypotheses from evidence. Do not patch based only on plausible explanations.
7. Instrument only when needed, and remove temporary instrumentation before handoff unless it becomes useful production diagnostics.
8. Write or update a regression test when the repo has an appropriate test surface.
9. Make the smallest robust fix.
10. Rerun the failing signal, the new regression coverage, and any blast-radius checks.
11. Record proof under `.klimkit/<operator>/tasks/<feature>/`: reproduction, root cause, changed files, checks run, and remaining risk.

## Evidence Rules

- A bug is not fixed until the original signal is rerun and passes or is explicitly unavailable.
- If the failure cannot be reproduced, document what was tried and switch to risk-reduction work only with the user's consent.
- If the root cause is outside this repo or blocked by missing credentials, write a concise blocker note with exact missing access and the safest next action.

Pair this skill with `klimkit-implement` for checklist, reflection, and final review gates.
