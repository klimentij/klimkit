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

Second follow-up paragraph added to `15-h-more-polish.md`:

- `src/klimkit/install.py`
  - Added `[code_server] managed_profile = true` as the default rendered and parsed config.
  - Uses `templates/code-server/User/` as the authoritative managed profile when `managed_profile = true`, while keeping `managed_profile = false` available for seed-only local profiles.
  - Adds a managed code-server extension install action from `templates/code-server/extensions.txt`.
  - Added capture helpers that copy the current code-server `settings.json`, `keybindings.json`, optional snippets, and installed extension IDs into the repo profile.

- `src/klimkit/cli.py`
  - Added `kk code-server capture` so the source VM can tune code-server once, capture the profile into the repo, commit, and let other VMs sync it with `kk pull`.

- `templates/code-server/User/settings.json`
  - Captured dev VM's current code-server settings, including `workbench.colorTheme = "Dark 2026"`, `editor.minimap.enabled = false`, and `security.workspace.trust.enabled = false`.

- `templates/code-server/extensions.txt`
  - Captured the four installed dev VM extension IDs: `doonfrs.terminal-paste-image-vscode`, `humanrace-ai.claude-paste-ssh`, `openai.chatgpt`, and `tamasfe.even-better-toml`.

- `src/klimkit/apps/switchboard/static/app.js`
  - Filters archived tabs out of the main tab bar.
  - Keeps archived workspaces in the catalog/dialog when the archived filter is enabled.
  - Moves the active tab to another unarchived workspace when the current tab is archived from the tab bar or batch archive action.

- `tests/test_klimkit_install.py`, `tests/test_klimkit_cli.py`, `tests/test_code_server_profile.py`, and `tests/test_switchboard.py`
  - Added regression coverage for managed profile defaults, seed-only opt-out, profile capture, extension list parsing, extension install skipping, the new CLI command, and archived-tab tab-bar filtering.

- `README.md` and `SECURITY.md`
  - Documented fork-first install with `./install.sh` from the user's own checkout instead of a remote one-line install of Klim's upstream flavor.
  - Added a code-server managed profile section covering `managed_profile = true`, `kk code-server capture`, synced settings/keybindings/snippets, and extension IDs.

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
  live       Codex projection: <codex-home>
```

Confirmed `packs/codex/hooks/stop-notify.sh` matches `~/.codex/hooks/stop-notify.sh` after projection.

After the code-server managed profile and archived-tab follow-up:

```text
$ uv run python -m unittest tests.test_code_server_profile tests.test_klimkit_install tests.test_klimkit_cli tests.test_switchboard -q
----------------------------------------------------------------------
Ran 87 tests in 7.442s

OK
```

```text
$ uv run python -m unittest discover -s tests -q
installing code-server extension: publisher.example
code-server extension already installed: publisher.example
apply ok
klimkit: sent autosync Telegram notification
----------------------------------------------------------------------
Ran 128 tests in 7.499s

OK (skipped=1)
```

```text
$ git diff --check
# no output
```

## Follow-up: checkout-local installer only

Implemented on 2026-05-06:

- Removed the legacy `install.sh` path that cloned Klim's upstream repo when `~/klimkit` was absent.
- Made `install.sh` resolve the current Git checkout and fail with fork/clone/`./install.sh` instructions when copied or run outside a Klimkit checkout.
- Updated `README.md` and the open-source readiness note so the supported flow is fork first, clone your fork, then run `./install.sh`.
- Added an installer regression test proving a copied installer refuses to run outside a cloned fork checkout.

Verification:

```text
$ uv run python -m unittest tests.test_klimkit_install -q
----------------------------------------------------------------------
Ran 29 tests in 0.097s

OK
```

```text
$ bash -n install.sh && git diff --check
# no output
```

```text
$ rg -n "raw\\.githubusercontent|klimentij/klimkit\\.git|git clone --branch|First run clones|curl-piping|curl-installing|curl install" README.md install.sh .klimkit/tasks/01-tui-ux-multi-harness-more/14-a-open-source-readiness-review.md
# no output
```

```text
$ uv run python -m unittest discover -s tests -q
----------------------------------------------------------------------
Ran 136 tests in 7.585s

OK (skipped=1)
```

```text
$ uv run kk code-server capture
Klimkit / code-server
Managed profile captured.
  repo       <repo-root>
  user       settings.json, keybindings.json
  extensions 4
```

```text
$ cmp -s templates/code-server/User/settings.json ~/.local/share/code-server/User/settings.json && echo settings-match
settings-match
```

```text
$ python3 ... # compare installed extension package metadata with templates/code-server/extensions.txt
doonfrs.terminal-paste-image-vscode
humanrace-ai.claude-paste-ssh
openai.chatgpt
tamasfe.even-better-toml
extensions-match
```

```text
$ uv run kk preview | rg -n "code-server|managed profile|extensions|write|ensure|run"
97:  write   code-server config
100:  write   code-server managed profile: keybindings.json
103:  write   code-server managed profile: settings.json
106:  run     install code-server managed profile extensions (4)
```

```text
$ uv run python -m klimkit.tools.code_server_profile install-extensions templates/code-server/extensions.txt
code-server extension already installed: doonfrs.terminal-paste-image-vscode
code-server extension already installed: humanrace-ai.claude-paste-ssh
code-server extension already installed: openai.chatgpt
code-server extension already installed: tamasfe.even-better-toml
```

```text
$ uv run kk apply --skip-services
Klimkit / apply
Local plan applied.
  actions    30
  changed    2
...
  ran        install code-server managed profile extensions (4)
  live       code-server settings: <code-server-data>/User/settings.json
```

Browser QA:

- Started a temporary Switchboard server at `http://127.0.0.1:4877/switchboard/`.
- Seeded one manual local tab in browser `localStorage`.
- Confirmed the tab hover action is `Archive repo`, not `Close`.
- Confirmed the copy button command title begins with `tmux new-session -A -s 'local-qa-repo'`.
- Opened the catalog, checked the manual-tab row checkbox, confirmed the `ARCHIVE` batch button became enabled, clicked it, and confirmed local storage persisted `"archived": true`.
- Screenshot: `004-switchboard-archive-dialog-proof.png`.

Archived-hidden tab-bar QA:

- Started a temporary Switchboard server at `http://127.0.0.1:4878/switchboard/`.
- Seeded one active local tab and one archived local tab in browser `localStorage`.
- Confirmed the tab bar rendered only `active @ dev-vm` with `tabCount = 1` and `archivedTabVisible = false`.
- Opened the catalog with `showArchived = true` and confirmed both active and archived rows were present in the dialog.
- Screenshot: `005-switchboard-archived-hidden-tabbar-proof.png`.

## Follow-up: done/unseen status, Tailscale Serve skip, and full Telegram message

Implemented on 2026-05-06:

- Tightened Switchboard done-message question detection so completion summaries that start with `What changed:` now stay `done` with `completion_unseen`, not `needs_input` / `ASK`.
- Bumped the Switchboard daemon rollout cache to version 4 and added a parser version to the Switchboard agent cache so stale misclassified summaries are re-parsed.
- Changed Tailscale Serve permission denial handling so `Access denied: serve config denied` remains non-fatal but records a skipped action instead of a successful served action.
- Updated CLI Live and apply/pull Telegram summaries to show the skipped Tailscale Serve action and the one-time `sudo tailscale set --operator=$USER` fix.
- Removed the 220-character notification truncation for Switchboard Telegram attention messages and added a regression that asserts the full done message body, including its tail sentinel, is sent.

Verification:

```text
$ uv run python -m unittest tests.test_switchboard tests.test_switchboard_agent tests.test_klimkit_install tests.test_klimkit_cli -q
----------------------------------------------------------------------
Ran 102 tests in 7.517s

OK
```

```text
$ uv run python -m unittest discover -s tests -q
----------------------------------------------------------------------
Ran 133 tests in 7.478s

OK (skipped=1)
```

```text
$ git diff --check
# no output
```

## Follow-up: configurable loaded code-server tabs

Implemented on 2026-05-06:

- Added `[switchboard.server] max_loaded_tabs = 5` to the generated local config.
- Added config comments noting that Switchboard keeps that many code-server tabs loaded most-recently-used first and that each loaded tab costs roughly 400 MB RAM.
- Exposed `max_loaded_tabs` in Switchboard state so the PWA can tune iframe retention without a frontend code edit.
- Updated the Switchboard PWA to keep the active and most recently used code-server iframes warm, filling remaining slots from visible unarchived tabs up to the configured limit.
- Documented the loaded-tab memory tradeoff in `README.md`.

Verification:

```text
$ uv run python -m unittest tests.test_switchboard tests.test_klimkit_install -q
----------------------------------------------------------------------
Ran 68 tests in 7.275s

OK
```

```text
$ uv run python -m unittest tests.test_switchboard tests.test_switchboard_agent tests.test_klimkit_install tests.test_klimkit_cli -q
----------------------------------------------------------------------
Ran 104 tests in 6.950s

OK
```

```text
$ uv run python -m unittest discover -s tests -q
----------------------------------------------------------------------
Ran 135 tests in 7.517s

OK (skipped=1)
```

```text
$ git diff --check
# no output
```

## Follow-up: final reviewer blocker and Switchboard shortcuts

Implemented on 2026-05-06:

- Fixed the final-review blocker by preserving a separate `latest_event_notification_message` for completion notifications while keeping the compact tab/event summary clipped for UI storage.
- Added a parser-to-projection-to-Telegram regression with a completion body longer than 300 characters and a tail sentinel beyond the old 240-character projection clip.
- Added `Control` + `Option` + `0` / `Control` + `Alt` + `0` to open the Switchboard workspace catalog dialog without clicking.
- Updated `README.md` with Chrome/PWA guidance and Switchboard keyboard shortcuts.

Verification:

```text
$ uv run python -m unittest tests.test_switchboard tests.test_switchboard_agent tests.test_klimkit_install tests.test_klimkit_cli -q
----------------------------------------------------------------------
Ran 103 tests in 7.558s

OK
```

```text
$ uv run python -m unittest discover -s tests -q
----------------------------------------------------------------------
Ran 134 tests in 7.504s

OK (skipped=1)
```

```text
$ git diff --check
# no output
```
