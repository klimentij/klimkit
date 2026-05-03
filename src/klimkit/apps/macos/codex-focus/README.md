# Codex Focus

Small local macOS helper app for deep-linking from notifications into an already-open Chrome tab without reloading it.

## What it does

- Registers a custom `codexfocus://` URL scheme on your Mac.
- Accepts either a named target or a raw URL.
- Finds an existing Chrome tab with the matching URL.
- Brings Chrome to the front, unminimizes the window, and activates that tab.
- Closes any Safari localhost trampoline tab after handing off into Chrome.
- Falls back to opening the URL in Chrome if no matching tab is open yet.
- Re-signs the installed app so macOS Automation prompts work correctly.
- Starts a tiny local `http://127.0.0.1:43123` redirect server so Telegram URL buttons can open `Codex Focus`.

The core behavior is implemented in [CodexFocus.applescript](./CodexFocus.applescript). A standalone example of the Chrome-focus AppleScript lives in [focus-tab-by-url.applescript](./focus-tab-by-url.applescript).

## Why this exists

Agents already send Telegram notifications. This helper turns the notification into a one-click deep link back to the exact code-server tab on your Mac.

Examples:

- `codexfocus://open?url=https%3A%2F%2Fyour-host.tailnet.ts.net%2F%3Ffolder%3D%2Fabsolute%2Fworkspace%2Fpath`

## Install

Run:

```bash
~/klimkit/src/klimkit/apps/macos/codex-focus/install.sh
```

This builds `~/Applications/Codex Focus.app` and registers the `codexfocus://` scheme.

The installer also ad-hoc signs the installed app bundle after modifying its `Info.plist`, which is required so `tccd` can compute a valid designated requirement and show Automation prompts.

It also installs and starts a local redirect server on:

`http://127.0.0.1:43123/open?url=<url-encoded-code-server-url>`

## Current status

- The helper app is implemented and tested locally on this Mac.
- Existing-tab focus works without reloading the tab.
- The app can be triggered through `codexfocus://` deep links.
- First-run Automation prompting works after the app is signed and any stale Apple Events decision is reset.

## First run

Run:

```bash
open 'codexfocus://open?url=https%3A%2F%2Fyour-host.tailnet.ts.net%2F%3Ffolder%3D%2Fabsolute%2Fworkspace%2Fpath'
```

On the first successful run, macOS should prompt to allow `Codex Focus` to control `Google Chrome` and possibly `System Events`. Click `Allow`.

If the prompt does not appear after reinstalling or changing the bundle:

```bash
tccutil reset AppleEvents com.klim.codexfocus
```

Then run the deep link again.

## Telegram usage

Telegram does not accept custom protocols like `codexfocus://` directly in inline keyboard buttons. Use the local HTTP trampoline instead:

- `http://127.0.0.1:43123/open?url=https%3A%2F%2Fyour-host.tailnet.ts.net%2F%3Ffolder%3D%2Fabsolute%2Fworkspace%2Fpath`
- `http://127.0.0.1:43123/open?url=https%3A%2F%2Fexample.com%2Fpage`

## Notes

- Existing-tab focus does not reload the tab.
- Setting a Chrome tab's `URL` does reload; this helper avoids that path.
- `url=` is the preferred mode for dynamic workspace links generated from the current machine and current working directory.
- `focus-tab-by-url.applescript` is kept as a standalone reference script; the app uses its own embedded AppleScript logic.
- The Telegram button targets `http://127.0.0.1:43123/...`, which only works on the Mac where the local redirect server is running.
