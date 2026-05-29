---
name: klimkit-code-explorer
description: Trace repository behavior across files before implementation without making edits. Use when Codex needs to understand unfamiliar code, execution paths, architecture, dependencies, tests, ownership boundaries, or contradictory patterns before deciding what to change.
---

# Klimkit Code Explorer

Use this for read-only discovery before edits. Report what the code does, where it does it, and which files or symbols matter.

## Workflow

1. State the question being explored.
2. Search first with `rg` or `rg --files`.
3. Read entry points, callers, tests, docs, and configuration that shape the behavior.
4. Trace the execution path with concrete file and symbol references.
5. Surface contradictions or competing patterns instead of blending them.
6. Identify the smallest likely change surface and the tests or checks that should cover it.
7. Stop before editing. If implementation is requested next, hand the findings to `klimkit-implement` or the narrow method skill.

## Report Shape

- `Question`: one sentence.
- `Execution path`: files and symbols in order.
- `Relevant tests`: existing coverage and gaps.
- `Risks or contradictions`: only concrete ones.
- `Likely change surface`: files to inspect or edit next.

Avoid speculative fixes unless the user explicitly asks for recommendations.
