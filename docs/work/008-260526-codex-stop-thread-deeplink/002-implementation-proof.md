# Codex Stop Thread Deeplink Proof

## Summary

Implemented a Codex app deep link in the Codex stop Telegram notification. When the stop-hook payload includes a non-empty `session_id`, the Telegram message now includes:

```text
codex://threads/<raw-session-id>
```

The existing Klimkit Switchboard link remains first when Tailscale DNS is available, and the direct code-server link remains after the Codex app link.

## Changed Files

- `packs/codex/hooks/stop-notify.sh`
- `tests/test_codex_stop_hook.py`
- `.klimkit/tasks/08-codex-stop-thread-deeplink/01-a-acceptance-checklist.md`
- `.klimkit/tasks/08-codex-stop-thread-deeplink/02-a-implementation-proof.md`

## Verification

- `bash -n packs/codex/hooks/stop-notify.sh`: passed.
- `uv run python -m unittest tests.test_codex_stop_hook -q`: passed, 4 tests.
- `uv run python -m unittest tests.test_codex_pack_validation tests.test_codex_stop_hook -q`: passed, 15 tests.
- `git diff --check`: passed.
- `./kk apply --skip-services`: passed; updated `<codex-home>/hooks/stop-notify.sh` and reported live Tailscale URLs.
- `bash -n <codex-home>/hooks/stop-notify.sh`: passed.
- `cmp -s packs/codex/hooks/stop-notify.sh <codex-home>/hooks/stop-notify.sh`: passed with exit code 0.
- `uv run python -m unittest discover -s tests -q`: passed, 175 tests, 1 skipped.

## Pending Publication Evidence

- Commit SHA: `2e9119759bf886c149df4f64531cb70dfb5e6d3e`.
- Push verification: `git ls-remote origin refs/heads/main` returned `2e9119759bf886c149df4f64531cb70dfb5e6d3e`.
- Current VM apply verification:
  - `git rev-parse HEAD origin/main`: both returned `2e9119759bf886c149df4f64531cb70dfb5e6d3e`.
  - `.klimkit/state/supervisor/state.json` records `current_revision` as `2e9119759bf886c149df4f64531cb70dfb5e6d3e`.
  - Projected hook contains `codex_thread_url = f"codex://threads/{session_id}" if session_id else ""`.
- Fleet visibility:
  - `tailscale status --json` showed Linux peers `prod-vm.example-tailnet.ts.net` and `workstation.example-tailnet.ts.net` online and active after the push.
  - Local Switchboard `/api/state` showed online heartbeats after the push from `dev-vm` and `pws`.
  - Direct remote file checks on `oprod` and `pws` were not available: Tailscale SSH lacked advertised host keys for strict mode, and normal SSH attempts as `ubuntu`, `root`, and `klim` returned `Permission denied`.
- GitHub release tag: `v0.1.11`, latest release endpoint returned `v0.1.11 2e9119759bf886c149df4f64531cb70dfb5e6d3e https://github.com/klimentij/klimkit/releases/tag/v0.1.11`.
