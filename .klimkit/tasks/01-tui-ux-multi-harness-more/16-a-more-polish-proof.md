# Switchboard More Polish Proof

Date: 2026-05-06

## Request

Implement `.klimkit/tasks/01-tui-ux-multi-harness-more/15-h-more-polish.md`:

- Per-tab copyable commands should use `tmux new-session -A -s ...` so re-running a command attaches to an existing Codex tmux session instead of launching a duplicate.
- Hover tab actions should archive/unarchive tabs, not show `Close`.
- Catalog/archive dialog checkboxes should be clickable so batch archive works.

## Implementation

- `src/klimkit/apps/switchboard/static/app.js`
  - Added `tmuxSessionName()` and `tmuxWrappedCommand()` so copied commands are shaped like `tmux new-session -A -s '<stable-tab-name>' '<codex ...>'`.
  - Preserved `archived` and `archived_at` for manual tabs in local storage.
  - Replaced the manual-tab `Close` path with archive/unarchive.
  - Added `setLocalArchiveStates()` and updated batch archive/unarchive to operate on selected manual tabs and any backing server sessions.
  - Removed the catalog checkbox disablement for manual tabs and made select-visible/select-all include every visible row.

- `tests/test_switchboard.py`
  - Added static regression assertions for the tmux wrapper, local archive path, non-`Close` tab action, and clickable catalog checkbox behavior.

Follow-up paragraph added to `15-h-more-polish.md`:

- `src/klimkit/notifications.py`
  - Added `send_telegram_message(..., parse_mode="")` while keeping `send_telegram_notification()` as the plain-text compatibility wrapper.

- `src/klimkit/apps/switchboard/daemon.py`
  - Switched Switchboard attention Telegram messages to HTML formatting with the same structured shape as the Codex Stop hook.
  - Parses Codex rollout `session_meta.source.subagent` and suppresses completion attention for subagent `done` results.

- `src/klimkit/tools/switchboard_agent/switchboard_agent.py`
  - Mirrors subagent parsing and suppresses completion attention in client snapshots before forwarding to Switchboard.

- `packs/codex/hooks/stop-notify.sh`
  - Detects subagent sessions from rollout metadata and skips direct Stop-hook Telegram messages for those subagent sessions.

## Verification

Automated:

```text
$ uv run python -m unittest tests.test_switchboard -q
----------------------------------------------------------------------
Ran 36 tests in 7.152s

OK
```

```text
$ uv run python -m unittest discover -s tests -q
apply ok
klimkit: sent autosync Telegram notification
----------------------------------------------------------------------
Ran 117 tests in 7.442s

OK (skipped=1)
```

After the notification/subagent follow-up:

```text
$ uv run python -m unittest tests.test_switchboard tests.test_switchboard_agent tests.test_codex_pack_validation -q
----------------------------------------------------------------------
Ran 54 tests in 7.158s

OK
```

```text
$ uv run python -m unittest tests.test_codex_pack_validation -q
----------------------------------------------------------------------
Ran 5 tests in 0.008s

OK
```

```text
$ uv run python -m unittest discover -s tests -q
apply ok
klimkit: sent autosync Telegram notification
----------------------------------------------------------------------
Ran 120 tests in 7.493s

OK (skipped=1)
```

Projection:

```text
$ uv run kk apply
... failed at `systemctl --user daemon-reload` because this shell had no user DBus/systemd session.

$ uv run kk apply --skip-services
Klimkit / apply
Local plan applied.
  actions    29
  changed    1
...
  live       Codex projection: /home/ubuntu/.codex
```

Confirmed `packs/codex/hooks/stop-notify.sh` matches `~/.codex/hooks/stop-notify.sh` after projection.

Browser QA:

- Started a temporary Switchboard server at `http://127.0.0.1:4877/switchboard/`.
- Seeded one manual local tab in browser `localStorage`.
- Confirmed the tab hover action is `Archive repo`, not `Close`.
- Confirmed the copy button command title begins with `tmux new-session -A -s 'local-qa-repo'`.
- Opened the catalog, checked the manual-tab row checkbox, confirmed the `ARCHIVE` batch button became enabled, clicked it, and confirmed local storage persisted `"archived": true`.
- Screenshot: `16-a-switchboard-archive-dialog-proof.png`.
