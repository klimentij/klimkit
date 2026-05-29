---
name: klimkit-improve-codebase-architecture
description: Find codebase architecture improvement candidates. Use when Codex needs to identify shallow modules, weak interfaces, coupling, missing locality, testability problems, or refactoring opportunities before implementation.
---

# Klimkit Improve Codebase Architecture

Use this for architecture review and candidate selection. It adapts Matt Pocock's deep-module language to the Klimkit workflow.

## Vocabulary

Read [references/LANGUAGE.md](references/LANGUAGE.md) when the distinction matters. Use these terms consistently:

- `Module`: something with an interface and an implementation.
- `Interface`: everything callers must know to use the module.
- `Implementation`: the code behind the interface.
- `Depth`: how much behavior sits behind a smaller interface.
- `Locality`: whether change, bugs, and knowledge stay concentrated.
- `Leverage`: what callers gain from the module.

Use the deletion test: if deleting a module makes complexity vanish, it may be pass-through; if complexity spreads into callers, it was earning its keep.

## Workflow

1. Read repo context first: `CONTEXT.md`, `CONTEXT-MAP.md`, `docs/adr/`, relevant README sections, and recent `.klimkit` task notes when present.
2. Use `klimkit-code-explorer` for read-only tracing. Do not require an Explorer subagent.
3. Look for:
   - Shallow wrappers where the interface is as complex as the implementation.
   - Concepts that require bouncing across many files.
   - Testing seams that do not match real behavior.
   - Hidden coupling, leaked ordering rules, or duplicated invariants.
   - ADRs whose tradeoff may be worth revisiting because real friction appeared.
4. Write candidates into `.klimkit/<operator>/tasks/<task>/` or the repo's active flat `.klimkit/tasks/<task>/` layout.
5. For each candidate include files, problem, proposed direction, benefit in locality/leverage terms, risk, verification path, and recommendation strength.
6. Ask the user which candidate to explore before proposing a detailed interface or editing code.
7. Use `klimkit-grill-me` for the selected candidate when the tradeoff is unclear.

## Output Shape

Lead with the top recommendation, then list candidates:

```text
Strong - Extract order pricing policy
Files: ...
Problem: ...
Direction: ...
Why this is deeper: ...
Verification: ...
```

If a visual report is useful, create it through `klimkit-walkthrough` under `.klimkit/<operator>/reports/`. Do not write architecture reports to OS temp directories as the default handoff.
