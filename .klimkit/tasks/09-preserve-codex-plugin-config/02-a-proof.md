# Preservation Proof

## Summary

Implemented Codex config projection preservation for VM-local TOML tables that should not be source-controlled in `packs/codex/config.toml`.

## Changed Files

- `src/klimkit/install.py`: merges selected existing `~/.codex/config.toml` tables into the managed Codex config projection before writing.
- `tests/test_klimkit_install.py`: adds regression coverage for local Slack-style plugin preservation, nested plugin connector config, pack precedence, runtime MCP/project/hook-state tables, and backup behavior.
- `README.md`: documents that VM-local Codex plugin/connector state is preserved and must stay out of the shared pack.
- `.klimkit/tasks/09-preserve-codex-plugin-config/01-a-acceptance-checklist.md`: acceptance checklist.

## Verification

- `uv run python -m unittest tests.test_klimkit_install.KlimkitInstallTests.test_codex_config_projection_preserves_vm_local_plugin_tables tests.test_klimkit_install.KlimkitInstallTests.test_codex_config_projection_preserves_local_runtime_tables -q`
  - Passed: 2 tests.
- `uv run python -m unittest tests.test_klimkit_install tests.test_codex_pack_validation -q`
  - Passed: 56 tests.
- `uv run python -m unittest tests.test_klimkit_supervisor -q`
  - Passed: 15 tests.
- `uv run python -m unittest discover tests -q`
  - Passed: 177 tests, 1 skipped.
- `git diff --check`
  - Passed.
- `./kk apply --skip-services`
  - Passed on the current VM. It updated `/home/ubuntu/.codex/config.toml` on the first run, then reran cleanly after the security fix with no content changes and skipped service restarts.

## Live VM Boundary

After `./kk apply --skip-services`, parsed `/home/ubuntu/.codex/config.toml` still contained both `github@openai-curated` and `slack@openai-curated`, with `slack@openai-curated` enabled. The file mode was `0600` after the security fix. The verification printed plugin names and boolean enablement only; no connector credentials or tokens were read into task proof.

## Notes

- Pack-owned tables have precedence on exact TOML table conflicts, so shared managed settings still update from `packs/codex/config.toml`.
- VM-local tables under `plugins`, `plugin_settings`, `connectors`, `apps`, `mcp_servers`, `projects`, and `hooks.state` are preserved when absent from the managed pack config.
- Autosync remains covered through the existing supervisor path that invokes `kk apply --defer-service-restart`, plus the install/projection regression tests on the shared apply path.
- Reflection Gate appended `.klimkit/reflection.md` entries `2026-05-26T04:15:52Z` and, after the security fix changed implementation, `2026-05-26T04:24:01Z`; the second pass found no material gap remaining.
- Security review found that preserved connector config made `~/.codex/config.toml` potentially secret-bearing; the implementation now writes Codex config and its update backup with `0600`, and regression tests assert both modes.
- Follow-up security review found no blocking security issues remaining. Residual forward-compatibility risk: future Codex schemas may store connector state in root inline keys or array-of-table shapes that need new fixtures.
