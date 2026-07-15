---
name: klimkit-reflector
description: Write a concise cross-task reflection note after verification and before final review for non-trivial Klimkit work. Use when Codex should connect the current task to prior work history, patterns, risks, or future process improvements.
---

# Klimkit Reflector

Use this after verification and before final review. Reflection is synthesis for future work, not a chronological proof note.

## Workflow

1. Read the current request, work notes, changed-file summary, verification evidence, intended final result, the repo's `AGENTS.md`, and relevant `docs/work/` LOGs from earlier work folders (descend selectively — never bulk-load the tree).
2. Write the reflection as the next numbered note in the current `docs/work/` phase folder, e.g. `004-reflection.md`, headed with a UTC timestamp line like `Reflected: YYYY-MM-DDTHH:MM:SSZ`.
3. Use these default sections unless a wider reflection needs more:
   - `Observations`
   - `Derived Pattern`
   - `Insight`
   - `Next Probe`
4. Keep each section concise and grounded in evidence.
5. Add a one-line entry for the note to the phase `LOG.md`.
6. If the reflection surfaces a preference or process rule that should bind every future session, propose adding it to the repo's `AGENTS.md` instead of leaving it buried in the note.
7. Reconsider the work after writing the reflection. If it exposes a material gap, fix the work and rerun impacted verification before final review.

Tiny one-command tasks may mark reflection not applicable, but the reason must be explicit.
