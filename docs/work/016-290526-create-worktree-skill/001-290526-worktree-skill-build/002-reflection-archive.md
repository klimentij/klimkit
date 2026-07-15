# Reflection archive — worktree-skill-build

> Migrated 2026-07-15 verbatim from the retired project reflection ledger
> (`.klimkit/reflection.md` → `docs/agents/reflection.md`).

### 2026-05-29T10:18:05Z

**Observations:** The create-worktree skill is another useful helper migration: a proven repo-local script pattern now lives as a skill-owned deterministic script with a short SKILL.md routing layer and a reference file for flags and handoff fields.
**Derived Pattern:** Klimkit skills should own the operational helper code they need when the helper is narrow, repeatable, and safer as a tested script than as ad hoc shell reconstruction.
**Insight:** The important compatibility detail is remote-first ref resolution for explicit `main`/`dev` syncs; otherwise a stale local `dev` branch could silently diverge from the workflow Klim uses for stable-main, integration-dev, feature-worktree stacks.
**Next Probe:** When this lands, consider adding a fresh-machine smoke check that installs the skill and uses the bundled script against a temporary bare remote, so distribution and behavior are tested together.
