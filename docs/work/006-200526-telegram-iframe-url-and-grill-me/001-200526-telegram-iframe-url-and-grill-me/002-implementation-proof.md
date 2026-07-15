# Implementation Proof

## Request

Klim asked that every Telegram notification keep the Switchboard link as the main option while also including a direct Tailscale code-server iframe URL when available, and asked to add `mattpocock/skills` `grill-me` to the Codex pack.

## Changed Files

- `src/klimkit/notifications.py`: added `build_direct_code_server_url` for consistent direct code-server URL construction.
- `src/klimkit/cli.py`: apply/pull Telegram summaries now include a secondary direct code-server URL when code-server and Tailscale DNS are available.
- `src/klimkit/tools/supervisor/supervisor.py`: autosync Telegram summaries now include a Switchboard link and a secondary direct code-server URL when available.
- `src/klimkit/apps/switchboard/daemon.py`: Switchboard attention Telegram notifications now derive and include the safe direct code-server URL after the Switchboard link.
- `packs/codex/hooks/stop-notify.sh`: Codex stop-hook Telegram notifications now include the direct code-server URL and forward `machine_dns`/`code_server_url` in hook events.
- `packs/codex/skills/grill-me/SKILL.md`: added the external `grill-me` skill to the source-controlled Codex pack.
- `tests/test_codex_stop_hook.py`, `tests/test_klimkit_cli.py`, `tests/test_klimkit_supervisor.py`, `tests/test_switchboard.py`, `tests/test_docs_static.py`: added coverage for direct URL inclusion, unavailable URL omission, Switchboard-first ordering, runtime stop-hook Telegram payload behavior, and hook/pack static expectations.

## Verification

- `bash -n packs/codex/hooks/stop-notify.sh`: passed.
- `bash -n ~/.codex/hooks/stop-notify.sh`: passed after projecting the fixed hook.
- `uv run python -m unittest tests.test_codex_stop_hook -q`: passed, 2 tests.
- `uv run python -m unittest tests.test_codex_stop_hook tests.test_switchboard tests.test_klimkit_supervisor tests.test_klimkit_cli tests.test_docs_static tests.test_codex_pack_validation tests.test_klimkit_install -q`: passed, 151 tests.
- `uv run python -m unittest discover -s tests -q`: passed, 173 tests, 1 skipped.
- `git diff --check`: passed.
- `./klimkit apply`: projected initial actions but failed at `systemctl --user daemon-reload` because `$DBUS_SESSION_BUS_ADDRESS` and `$XDG_RUNTIME_DIR` are not defined in this shell.
- `./klimkit apply --skip-services`: completed projection-only apply, verified `~/.codex/skills/grill-me/SKILL.md` and updated `~/.codex/hooks/stop-notify.sh`; it also sent an apply summary to Telegram.
- `./klimkit apply --defer-service-restart`: restored the managed `~/.config/systemd/user/klimkit.service` file but still failed at the same unavailable user DBus `systemctl --user daemon-reload` step.
- After final review found a runtime stop-hook quoting bug that caused `{"continue":true}` Telegram messages, `./klimkit apply --defer-service-restart` projected the fixed hook into `~/.codex/hooks/stop-notify.sh`; it still failed at the same unavailable user DBus reload after projection and did not send another apply Telegram notification.
- `test -f ~/.codex/skills/grill-me/SKILL.md && test -f ~/.codex/hooks/stop-notify.sh`: passed.

## Notes

The current shell cannot complete systemd user-manager reloads because it lacks a user DBus session. Source changes and Codex projections are verified; live service restart remains unavailable from this shell.
