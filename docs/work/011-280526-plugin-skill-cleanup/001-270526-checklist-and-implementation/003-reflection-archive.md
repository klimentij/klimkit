# Reflection archive — checklist-and-implementation

> Migrated 2026-07-15 verbatim from the retired project reflection ledger
> (`.klimkit/reflection.md` → `docs/agents/reflection.md`).

### 2026-05-27T08:40:43Z

**Observations:** The skill cleanup follows the `v0.1.15` plugin-first release/cache proof by turning the installable package from a copied harness bundle into five validated skills with proper titles, concise trigger descriptions, OpenAI UI metadata, and `klimkit-workflow`-owned references.
**Derived Pattern:** Plugin distribution works best when the plugin owns only skill-level surfaces and public-safe references, while `kk apply` remains the boundary for home-level AGENTS, subagents, hooks, config, Switchboard, Tailscale Serve, autosync, and connector state.
**Insight:** Removing `plugins/klimkit/reference/**` is a quality improvement, not a loss, because users now see the workflow through the skill invocation path that Codex actually loads, and tests enforce that broad copied harness material does not silently become plugin API.
**Next Probe:** Before publishing these content changes, bump the plugin manifest version deliberately and repeat the live marketplace/cache upgrade proof from task 10; until then, the current evidence supports source/package correctness but not installed-cache availability.
