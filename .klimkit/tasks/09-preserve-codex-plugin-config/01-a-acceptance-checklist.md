# Preserve Codex Plugin Config

## Request

Klim reports that some Klimkit updates and VM synchronization runs cause VM-connected Codex plugins, such as Slack, to be lost or disconnected even though Klim did not disconnect them. The likely cause is that `kk apply` projects the source-controlled `packs/codex/config.toml` over `~/.codex/config.toml`, while the pack config does not include machine-local plugin stanzas such as `[plugins."slack@openai-curated"]`. Create implementation criteria for preserving machine-local Codex plugin and connector configuration across `kk apply` and autosync without putting secrets or VM-specific state into the source-controlled pack.

## Acceptance Checklist

- [x] `kk apply` preserves existing machine-local Codex plugin and connector stanzas from the live `~/.codex/config.toml`, including `[plugins."slack@openai-curated"]`, when projecting the managed Codex pack config.
- [x] Preservation covers plugin enablement and any associated connector/runtime config required for already-connected VM-local Codex plugins to remain connected after apply, while still allowing managed pack settings to update.
- [x] A VM-local plugin that is absent from `packs/codex/config.toml` remains present in the resulting `~/.codex/config.toml` after `kk apply` and after the autosync path invokes apply.
- [x] Managed pack-owned Codex config remains authoritative for shared Klimkit settings, including model, reasoning effort, sandbox mode, approval policy, managed MCP server defaults, features, hooks, and the source-controlled GitHub plugin stanza unless intentionally changed by the implementation.
- [x] If a setting exists in both the managed pack config and machine-local config, the implementation defines and tests a deterministic precedence rule that preserves pack-owned behavior while protecting VM-local plugin/connector state.
- [x] The implementation does not copy Slack tokens, connector credentials, installation IDs, auth files, machine-local runtime state, or other secrets into `packs/codex/config.toml`, other source-controlled pack files, task notes, test fixtures, logs, or proof output.
- [x] `packs/codex/config.toml` remains a public-safe shared default and does not gain a hard-coded Slack plugin stanza merely to fix one VM's local state.
- [x] Existing backup and manifest behavior remains intact: overwritten or updated `~/.codex/config.toml` content is backed up as before, manifest records remain meaningful, and stale managed files are not pruned incorrectly.
- [x] Existing generated-file boundaries remain intact: source changes are made under the Klimkit codebase or `packs/codex` as appropriate, and generated home files under `~/.codex/` are not edited by hand as the implementation strategy.
- [x] Regression tests create a temporary live Codex home containing a local Slack plugin stanza, run the same planning/apply code path used by `kk apply`, and assert the stanza survives in the projected `config.toml`.
- [x] Regression tests cover the negative/control case where ordinary managed pack config changes still land in the projected `config.toml` instead of preserving the entire old file wholesale.
- [x] Regression tests cover a non-secret local plugin/connector fixture with representative nested TOML shape so the merge logic is not limited to one flat Slack stanza.
- [x] Regression tests cover autosync-relevant behavior either by exercising the apply function invoked by autosync or by asserting autosync delegates to the same preservation-safe apply path.
- [x] Existing focused suites continue to pass, including `uv run python -m unittest tests.test_klimkit_install tests.test_codex_pack_validation -q` and any new focused test module added for Codex config preservation.
- [x] `git diff --check` passes.
- [x] Documentation or operator-facing proof explains that VM-local Codex plugin/connector connections are preserved by `kk apply`/autosync and that secrets should stay in machine-local Codex state, not in source-controlled packs.
- [x] A task proof note under `.klimkit/tasks/09-preserve-codex-plugin-config/` records changed files, verification commands, notable outputs, skipped or unavailable checks, and any live-VM validation boundary.
- [x] Reflection Gate is completed after verification and before final review: read `.klimkit/reflection.md`, append a full UTC timestamped session with `Observations`, `Derived Pattern`, `Insight`, and `Next Probe`, reconsider the implementation, and rerun impacted checks if reflection exposes a gap.
- [x] Final Review Gate is completed before any completion claim: draft the final response, run 3 parallel `final_reviewer` passes with this checklist, changed files, verification evidence, reflection entry, and exact draft response, and require all 3 to return PASS / READY FOR USER.
- [x] If the implementation commit lands on `main`, a next patch GitHub release is created for that commit and marked as the latest release, per the repository-local `AGENTS.md` instruction. Not applicable in this turn because no commit landed on `main`.
