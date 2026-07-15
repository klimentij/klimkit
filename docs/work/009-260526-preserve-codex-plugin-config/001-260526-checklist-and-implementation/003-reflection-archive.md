# Reflection archive — checklist-and-implementation

> Migrated 2026-07-15 verbatim from the retired project reflection ledger
> (`.klimkit/reflection.md` → `docs/agents/reflection.md`).

### 2026-05-26T04:15:52Z

**Observations:** The Codex config preservation task verified `kk apply --skip-services` kept `slack@openai-curated` enabled after projecting `packs/codex/config.toml`, and earlier autosync/code-server preference work shows VM-local state is repeatedly exposed when managed projection crosses machine boundaries.
**Derived Pattern:** Klimkit needs explicit ownership boundaries at every projection layer: source-controlled pack tables stay authoritative, while allowlisted VM-local runtime/plugin tables merge forward only when absent from managed config and never copy back into packs or proofs.
**Insight:** The fix is strongest because it treats Slack as one instance of a broader local-state class rather than as a pack default; tests for nested plugin, MCP/project/hook-state tables plus live parsed config evidence cover the user-visible failure without storing secrets.
**Next Probe:** Watch future Codex plugin/app schema changes for new local-only top-level tables or array-of-table shapes, and add live-shape regression fixtures before autosync or `kk apply` can prune newly introduced connection state.

### 2026-05-26T04:24:01Z

**Observations:** The post-reflection security review changed the preservation boundary: once VM-local connector tables are merged into `~/.codex/config.toml`, both the projected live file and its update backup must be treated as potentially secret-bearing artifacts.
**Derived Pattern:** Projection features that preserve local runtime state need to carry permission and backup semantics with the merge logic, because protecting source-controlled packs is not enough if copied live artifacts become world-readable.
**Insight:** Setting `codex-config` to `CONFIG_MODE`/`0600`, chmodding backups after copy, documenting the mode, and asserting both live and backup permissions closes the material security gap exposed after the first reflection.
**Next Probe:** For the next managed-file preservation change, add file-mode and backup-mode expectations to the initial checklist before implementation so security review validates intent instead of discovering an omitted artifact boundary late.
