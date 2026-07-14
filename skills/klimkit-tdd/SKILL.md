---
name: klimkit-tdd
description: Implement behavior changes with narrow red-green-refactor loops and Klimkit proof. Use when adding features, fixing bugs with clear expected behavior, changing shared contracts, or when the user asks for TDD or test-first work.
---

# Klimkit TDD

Use TDD to protect intent, not to create mechanical coverage. Keep each loop small enough that a failing test names the behavior being changed.

## Workflow

1. Ensure Klimkit's docs-first context exists. If the repo lacks the `docs/work/` layout, use `klimkit-setup` first.
2. Read the request, acceptance checklist, existing tests, and nearby implementation before writing a test.
3. Choose one vertical behavior slice. Avoid broad refactors before the first red test.
4. Write or update the smallest test that should fail for the requested behavior.
5. Run the focused test and confirm it fails for the expected reason.
6. Implement the smallest robust change that makes the test pass.
7. Run the focused test again.
8. Refactor only the code touched by this slice, preserving green tests.
9. Repeat for the next slice until the checklist is complete.
10. Run broader checks that match the blast radius.
11. Record the red/green evidence, final checks, skipped checks, and residual risk as a numbered note in the current `docs/work/` phase folder.

## Test Quality

- Test business behavior or safety properties, not implementation trivia.
- Prefer existing test frameworks, fixtures, factories, and naming conventions.
- Add integration or UI tests only when unit tests cannot catch the failure mode.
- If no suitable test harness exists, document the gap and provide a manual proof that directly exercises the behavior.

Use `klimkit-diagnose` first when the expected behavior is still unclear.
