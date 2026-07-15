# Reflection archive — checklist-and-implementation

> Migrated 2026-07-15 verbatim from the retired project reflection ledger
> (`.klimkit/reflection.md` → `docs/agents/reflection.md`).

### 2026-05-27T05:19:03Z

**Observations:** The plugin-first task deliberately reverses the older fork/Switchboard/autosync onboarding emphasis while preserving the repo-managed harness as an advanced path and carrying forward task 09's VM-local Codex state boundary.
**Derived Pattern:** Klimkit needs layered adoption contracts: the public Codex plugin should install skills, workflow, and safe reference material; `kk apply` should remain the explicit machine-projection boundary; autosync and Telegram should stay opt-in automation beyond that boundary.
**Insight:** The extraction is strongest when docs and tests prevent surface confusion, because a plugin can make Klimkit's completion discipline portable without inheriting yolo-mode, hooks, connector state, Tailscale serving, or daemon-managed restarts.
**Next Probe:** Before final review, make the handoff precise that live plugin installation was intentionally skipped, v0.1.14 covered the prior autosync-default-off publication, and this branch's plugin-first work is verified by manifest/CLI-help/static tests until it lands and is released.

### 2026-05-27T08:12:45Z

**Observations:** The publish/live-plugin phase proved a different boundary than the original extraction: Git marketplace upgrade moved the live Codex cache from `0.1.14` to `0.1.15`, while the post-merge VM marketplace now follows released `main` at `f8b8700`.
**Derived Pattern:** Klimkit plugin distribution needs two proofs: source/release proof that the public marketplace points at the intended commit, and home/cache proof that Codex has materialized the expected version and skill text under `~/.codex/plugins/cache`.
**Insight:** Keeping the repo-managed harness as the advanced path is credible only if the plugin path is verified with Codex's real cache behavior; the decisive evidence is not just PR merge or manifest validation, but the installed cache containing the modified skill after `codex plugin marketplace upgrade` and `codex plugin add`.
**Next Probe:** When the next plugin package release changes installable content, bump the plugin manifest version deliberately, verify cache movement on a non-development marketplace ref if possible, and record the installed cache path before final review rather than relying only on release notes.
