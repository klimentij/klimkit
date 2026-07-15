# Reflection archive — team-workflow-fixes

> Migrated 2026-07-15 verbatim from the retired project reflection ledger
> (`.klimkit/reflection.md` → `docs/agents/reflection.md`).

### 2026-05-16T05:40:04Z

**Observations:** The PR discussion frames team workflow as attributed read context plus one writable operator root, while this repo's proof and diff preserve solo as the default and harden only the opt-in team surfaces.
**Derived Pattern:** Migration and report serving need the same canonical path-safety model: reserved names, symlinks, source/target overlap, and asset traversal are artifact-boundary problems whether the code is moving evidence or serving it.
**Insight:** Reviewer-driven edge cases around reserved pseudo-owners, copied dry-run commands, symlink escapes, and stale operator wording turned the solo-first ideology into testable invariants instead of relying on agent etiquette.
**Next Probe:** Before final handoff, update the proof report's pending security/reflection/final-review placeholders and have reviewers check that every team affordance remains explicitly selected, attributed, and non-invasive for solo builders.

### 2026-05-16T11:13:00Z

**Observations:** The final correction separates product capability from repo evidence: team artifacts remain opt-in for projects that choose `workflow = "team"`, while Klimkit's own tracked `.klimkit` state is flat solo and rejects old operator-scoped report URLs.
**Derived Pattern:** Optional collaboration features should be tested and documented as bounded affordances, but proof artifacts for a solo-builder-first repo should stay in the same flat layout that default users see.
**Insight:** The strongest guardrail is not just `workflow = "solo"` in config; it is making committed evidence, report URLs, docs, and `git ls-files` all agree that team layout is not the repo's ambient operating mode.
**Next Probe:** Keep future team-workflow patches checking both sides of the contract: opt-in operator isolation works in temporary/team fixtures, and the public Klimkit repo never re-accumulates contributor-scoped `.klimkit/<operator>/` artifacts.
