# Better Workflow And Tabs Implementation Proof

Timestamp: 2026-05-08T09:58:05Z

## Summary

- Added the approved repo-local reports workflow to the plan: HTML proof reports live in each repo under `.klimkit/reports/`, screenshot/video media is ignored by Git, and agent handoffs must include the Tailscale-served report URL when available.
- Added the proof inspectability rule: screenshots and videos render as full-width report sections, and report videos prefer MP4 for reliable Chrome/PWA scrubbing.
- Updated Codex pack workflow instructions, `checklister`, `final_reviewer`, README, and harness-tuning guidance for screenshot/video proof reports and Tailscale report URLs.
- Added Klimkit daemon `/reports/` and `/reports/r/<root-id>/<path>` routes with configured multi-root discovery, safe same-tree media serving, auth parity, `HEAD`, empty state, and Tailscale Serve setup.
- Added HTTP byte-range serving for `/reports/` video assets so Chrome can seek and scrub report MP4s through the live Tailscale URL.
- Reworked Switchboard catalog into the Tab Browser special tab, with `Control+Option/Alt+0`, Escape return, arrow cycling through Tab Browser, click-to-switch top tabs, and drag/drop ordering in the top bar plus Tab Browser rows.
- Fixed two QA-found bugs: persisted catalog `status: "all"` now sanitizes to no filter, and manual order for local tabs now uses stable machine+folder keys so it survives reload before server reconciliation completes.
- Fixed the `.gitignore` report-media rule by replacing unsupported brace expansion with explicit media extension patterns.

## Proof URLs

- Tailnet proof report: `https://dev-vm.example-tailnet.ts.net/reports/r/klimkit-dc70a74e9a/02-better-wf-and-tabs/report.html`
- Tailnet reports index: `https://dev-vm.example-tailnet.ts.net/reports/`
- Local report path: `.klimkit/reports/02-better-wf-and-tabs/report.html`

## Verification

- `uv run python -m unittest discover -s tests -q` -> `Ran 142 tests in 8.069s`, `OK (skipped=1)`.
- `uv run python -m unittest tests.test_codex_pack_validation tests.test_docs_static tests.test_switchboard -q` -> `Ran 53 tests in 8.194s`, `OK`.
- `node --check src/klimkit/apps/switchboard/static/app.js` -> passed.
- `git diff --check` -> passed.
- `uv run kk apply` with user DBus environment -> projected updated Codex workflow files, configured Tailscale Serve for code-server, Switchboard, and Klimkit reports; restarted `klimkit.service`; printed `Proof reports: https://dev-vm.example-tailnet.ts.net/reports/`.
- `curl -k -I https://dev-vm.example-tailnet.ts.net/reports/r/klimkit-dc70a74e9a/02-better-wf-and-tabs/report.html` -> `HTTP/2 200`, `content-type: text/html; charset=utf-8`.
- Browser-opened tailnet proof report -> 15 full-width image sections, 2 playable MP4 videos, durations 129s and 6s, with all video sources under the tailnet report route.
- Browser layout check -> single-column screenshot/video grid, first media figures 1183px wide in a 1265px main viewport.
- Browser seek check -> both report MP4s expose full seekable ranges (`0..129` and `0..6`) and successfully seek to `currentTime = 3`.
- Tailscale Range requests -> valid MP4 byte ranges return `206 Partial Content` with `Accept-Ranges: bytes` and `Content-Range`; invalid ranges return `416` with `Content-Range: bytes */size`.
- `ffprobe -v error -show_entries format=duration,size .../tab-browser-flow.mp4` -> `duration=129.000000`, `size=422435`.
- `ffprobe -v error -show_entries format=duration,size .../top-tab-click-switch.mp4` -> `duration=6.000000`, `size=42483`.
- Source WebM evidence also remains available locally: `tab-browser-flow.webm` duration 129s and `top-tab-click-switch.webm` duration 6s.
- `git check-ignore -v` confirms report PNG/MP4/WebM media are ignored; `git check-ignore -v .klimkit/reports/02-better-wf-and-tabs/report.html` returns no match, so HTML is trackable.
- `git status --short --untracked-files=all --ignored .klimkit/reports/02-better-wf-and-tabs` shows `report.html` as untracked and all media under `assets/` as ignored.

## Browser QA

- `agent-browser` native source video: `.klimkit/reports/02-better-wf-and-tabs/assets/tab-browser-flow.webm`.
- Report-embedded MP4 video converted from the native recording for better Chrome/PWA scrubbing: `.klimkit/reports/02-better-wf-and-tabs/assets/tab-browser-flow.mp4`.
- Focused supplemental MP4 video: `.klimkit/reports/02-better-wf-and-tabs/assets/top-tab-click-switch.mp4`, assembled from verified before/after browser screenshots to prove top-tab click switching while Tab Browser is active.
- Screenshots:
  - `01-tab-browser-desktop.png`: desktop Tab Browser with create controls, filters, and rows.
  - `02-topbar-before-drag.png`: top bar before manual reorder.
  - `03-tab-browser-keyboard.png`: Tab Browser opened with `Control+Alt+0`.
  - `04-topbar-after-drag.png`: top tabs after drag/drop reorder.
  - `05-row-before-drag.png`: Tab Browser rows before row reorder.
  - `06-row-after-drag.png`: rows and top tabs after row reorder.
  - `07-archived-visible.png`: archived row visible in Tab Browser while hidden from top bar.
  - `08-reload-persistence.png`: stable manual order after full reload.
  - `09-tab-browser-mobile.png`: mobile Tab Browser layout, captured at 390x844.
  - `10-reports-index-mobile.png`: mobile reports index, captured at 390x844.
  - `11-reports-index-desktop.png`: populated multi-root reports index.
  - `12-reports-empty-state.png`: reports empty state.
  - `13-switchboard-empty-state.png`: Switchboard empty state.
  - `14-top-tab-click-start.png`: Tab Browser active with top tabs visible before regular tab click.
  - `15-top-tab-click-result.png`: regular workspace active after top-tab click.

## Notes

- The first `kk apply` attempt configured Tailscale Serve paths but failed at the user `systemctl` step because the shell lacked `DBUS_SESSION_BUS_ADDRESS` and `XDG_RUNTIME_DIR`. Re-running with `XDG_RUNTIME_DIR=/run/user/1000` and `DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus` completed successfully.
- `ffmpeg` was missing, so native `agent-browser` recording could not be saved until `ffmpeg` was installed through apt. After installation, the final native WebM recording saved; it was then converted to MP4 for the report player.

## Final Review Gate

- Turing: PASS / READY FOR USER.
- Lagrange: PASS / READY FOR USER.
- Dirac: PASS / READY FOR USER.
