# Reflection archive — skills-library-build

> Migrated 2026-07-15 verbatim from the retired project reflection ledger
> (`.klimkit/reflection.md` → `docs/agents/reflection.md`).

### 2026-05-28T09:43:22Z

**Observations:** The root `skills/` package turns the plugin-first and control-plane research threads into a Vercel Skills CLI install/update surface, while deliberately keeping legacy Switchboard, sync, and repo-managed runtime concepts out of the new skill text.
**Derived Pattern:** Klimkit is splitting portable agent behavior into skill-local instructions, references, scripts, and metadata, with long-running runtime machinery treated as deprecated compatibility unless it is reintroduced through a narrow skill-owned helper.
**Insight:** The first report-server reference script is the right salvage model: useful runtime affordances can migrate forward when they become public-safe, progressively loaded, validated skill assets instead of root-level operational assumptions.
**Next Probe:** Before release, make root `skills/` and plugin packaging agree on the canonical skill set, then migrate only the remaining useful helper patterns into skill-local references without reviving the deprecated control plane.
