---
name: klimkit-reflector
description: Append a concise cross-task reflection after verification and before final review for non-trivial Klimkit work. Use when Codex should connect the current task to project memory, logs, task history, patterns, risks, or future process improvements.
---

# Klimkit Reflector

Use this after verification and before final review. Reflection is synthesis for future work, not a chronological proof note.

## Workflow

1. Read the current request, task notes, changed-file summary, verification evidence, intended final result, `.klimkit/<operator>/memory.md`, `.klimkit/<operator>/log.md`, and relevant `.klimkit/<operator>/tasks/` history.
2. If `.klimkit/<operator>/reflection.md` is missing, create it with:
   - `# Project Reflection`
   - a one-line append-only description.
   - `## Reflections`
3. Append one UTC timestamped session headed like `### YYYY-MM-DDTHH:MM:SSZ`.
4. Use these default sections unless a wider reflection needs more:
   - `Observations`
   - `Derived Pattern`
   - `Insight`
   - `Next Probe`
5. Keep each section concise and grounded in evidence.
6. Preserve older reflection entries exactly. If an old format matters, append a new-format follow-up instead of rewriting history.
7. Reconsider the work after writing the reflection. If it exposes a material gap, fix the work and rerun impacted verification before final review.

Tiny one-command tasks may mark reflection not applicable, but the reason must be explicit.
