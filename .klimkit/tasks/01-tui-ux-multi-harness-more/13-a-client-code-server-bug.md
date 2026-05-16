# Client Code-Server Bug Fix

Agent-authored implementation note for `12-h-bug.md`.

## Bug

Client-only machines could appear in Switchboard, but manual tabs could still load the central VM's code-server iframe when the client report had an empty `machine_dns` or the saved manual tab had a stale `code_server_url`.

Live evidence before the fix showed `MacBook-Air-8.local` reporting with an empty `machine_dns`, causing Mac workspaces to have empty backend `code_server_url` values and letting the browser fall back to odev URLs.

## Fix Checklist

- [x] Make `switchboard_agent` find the Tailscale CLI from common macOS launchd paths when `tailscale` is not on `PATH`.
- [x] Infer a client DNS name from `tailscale status --json` tailnet suffix when `Self.DNSName` is missing.
- [x] Let the central Switchboard server resolve missing client DNS from Tailscale peer data, including fuzzy `MacBook-Air-8.local` to `macbook-air-23.tail11c448.ts.net` matching.
- [x] Derive backend `code_server_url` from the resolved selected machine DNS and folder, ignoring untrusted submitted URLs.
- [x] Configure Tailscale Serve for client code-server at `/` and Switchboard at `/switchboard` during `kk apply`.
- [x] Keep `kk apply` from crashing when Tailscale operator permission is missing; print the one-time `sudo tailscale set --operator=$USER` fix.
- [x] Prevent the frontend from falling back to the central VM code-server for remote machines with missing DNS.
- [x] Refresh already-loaded iframes when the resolved workspace `code_server_url` changes.
- [x] Remove the manual-tab timestamp gate so stale saved manual tabs inherit the latest trusted backend URL for the same machine/folder.
- [x] Document client code-server Serve URLs and the Tailscale operator requirement.
- [x] Add regression tests for client DNS resolution, Tailscale Serve planning, and Switchboard static behavior.
- [x] Apply locally and verify the live Mac manual tab iframe URL points at `macbook-air-23.tail11c448.ts.net`, not `odev.tail11c448.ts.net`.

## Verification

- `node --check src/klimkit/apps/switchboard/static/app.js`
- `uv run python -m py_compile src/klimkit/apps/switchboard/daemon.py src/klimkit/tools/switchboard_agent/switchboard_agent.py src/klimkit/install.py src/klimkit/cli.py`
- Focused tests: `uv run python -m unittest tests.test_switchboard_agent tests.test_switchboard tests.test_klimkit_install tests.test_klimkit_cli tests.test_docs_static -q`
- `kk apply` configured Tailscale Serve for code-server and Switchboard, restarted `klimkit.service`, printed URLs, and sent the Telegram apply summary.
- Live API proof: `MacBook-Air-8.local` now resolves to `macbook-air-23.tail11c448.ts.net`, and Mac workspace `code_server_url` values use that hostname.
- Browser QA proof: a stale manual Mac tab saved with an odev URL was corrected to `https://macbook-air-23.tail11c448.ts.net/?folder=%2FUsers%2Fklim%2Fcoding-ops` for both `Open directly` and iframe `src`.
- Screenshot: `tmp/qa/switchboard-mac-client-code-server-url.png`.
