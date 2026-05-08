# Better Workflow And Tabs Acceptance Checklist

Human task: `01-h-in.md`
Plan: `02-a-plan.md`
Created by: checklister

## Acceptance Checklist

### Approved Scope And Report Decision

- [x] `02-a-plan.md` is updated before implementation to record the approved reports decision: task reports live inside each project repo under `.klimkit/reports/`, not in a home-level reports folder.
- [x] `02-a-plan.md` states that report HTML is intended to be Git-tracked while large screenshot/video assets are intentionally ignored by Git.
- [x] `02-a-plan.md` states that the Klimkit daemon serves one combined `/reports/` index across multiple configured repo/worktree roots and links to each discovered report.
- [x] The earlier self-contained-HTML recommendation is either replaced or explicitly narrowed so it does not conflict with the approved Git-tracked-HTML plus ignored-media decision.
- [x] `02-a-plan.md` records that agent completion results must include the Tailscale-served report URL when a Tailscale DNS name is available, and that localhost report URLs are only local QA fallback evidence.

### Harness QA And Report Requirements

- [x] `packs/codex/agents/checklister.toml` requires UI QA checklist items to name screenshots, an `agent-browser` CLI native video recording, and a final HTML report artifact when UI behavior is in scope.
- [x] `packs/codex/agents/checklister.toml` requires task proof reports to be placed under the active project repo's `.klimkit/reports/` directory.
- [x] `packs/codex/agents/checklister.toml` requires report HTML to be minimal, responsive, readable without a build step, and to include text evidence plus screenshot and video references.
- [x] `packs/codex/agents/final-reviewer.toml` requires final reviewers to open the final HTML report, inspect every screenshot referenced by the report, and verify the recorded video by playback or sampling representative frames.
- [x] `packs/codex/agents/final-reviewer.toml` instructs reviewers to return KEEP WORKING when report HTML, screenshot evidence, video evidence, or media links are missing, broken, or inconsistent with the final response claims.
- [x] Shared workflow instructions require report screenshots and videos to render as full-width sections so the proof is readable on a laptop display.
- [x] Shared workflow instructions prefer MP4 videos in proof reports for reliable Chrome/PWA scrubbing while allowing native `agent-browser` recordings to be converted for presentation.
- [x] Shared workflow docs that mention proof or final review, including `packs/codex/AGENTS.md` and README content if touched, are consistent with the new `.klimkit/reports/` report workflow.
- [x] Shared workflow docs and agent instructions require the final handoff to include the Tailscale-served report URL when available.
- [x] Pack validation coverage proves the new checklister and final-reviewer report/video requirements are present in the agent TOML files.

### Switchboard Tab Browser Behavior

- [x] The former workspace catalog dialog/drawer behavior is replaced with a first-class "Tab Browser" special tab visible in the tab/navigation model.
- [x] `Control`+`Option`+`0` on macOS, and `Control`+`Alt`+`0` on Linux/Windows, activates Tab Browser without opening a modal dialog.
- [x] `Control`+`Option`+`Left`/`Right` cycles through Tab Browser and regular workspace tabs in visual order.
- [x] `Control`+`Option`+`1` through `9` still switch only to regular workspace tabs by number; Tab Browser is not counted as tab 1.
- [x] Pressing `Escape` while Tab Browser is active returns to the last active regular workspace when one exists.
- [x] Clicking a regular top-bar workspace tab while Tab Browser is active switches directly to that workspace and updates `aria-selected`, panel visibility, loaded-frame recency, URL hash, and document title consistently.
- [x] Tab Browser includes the existing create-workspace controls, filters, batch archive/unarchive controls, active/archived status display, and row click-to-open behavior.
- [x] Empty state is visible and non-broken when there are no workspaces: Tab Browser remains reachable, create controls are usable when machines exist, and the rows area clearly has no rows.
- [x] Loading or refresh states do not remove the active Tab Browser selection, do not flash a modal overlay, and do not reset filters or selected rows unexpectedly.
- [x] API or bootstrap errors reachable from Tab Browser create/open/archive flows leave visible button/error state or non-destructive failure behavior and do not corrupt the local workspace list.
- [x] Tab Browser and regular workspace tabs preserve keyboard focus visibility, tablist/tab/tabpanel semantics, and non-overlapping text at desktop and mobile widths.

### Drag And Drop Ordering

- [x] Default workspace order remains newest-created first before the user manually reorders anything.
- [x] Creating a new tab with the create-tab button places the new tab leftmost in the top tab bar and nearest the top of Tab Browser before any manual override applies to that tab.
- [x] Dragging regular unarchived workspace tabs in the top tab bar reorders them visually, updates keyboard navigation order, and does not trigger copy/archive button actions during the drag.
- [x] Dragging rows in Tab Browser reorders all visible rows and updates the same underlying order used by top tabs, keyboard navigation, loaded-frame recency fallback order, and row rendering.
- [x] Archived workspaces remain hidden from the top tab bar, appear in Tab Browser only when archived rows are shown, and can be reordered there without being unarchived.
- [x] Unarchiving an archived workspace restores it to the top tab bar at the manual order position proven in Tab Browser.
- [x] Manual order is stored in `localStorage` using stable workspace identity so it survives full browser reloads, daemon state refreshes, and local/server workspace identity reconciliation.
- [x] Manual order entries for deleted or permanently missing workspaces are pruned without breaking remaining order.
- [x] Newly created or newly discovered unordered tabs sort newest-first without destroying the relative order of previously manually ordered tabs.
- [x] Drag hover, drop-target, and active-drag visual states are visible in both the top tab bar and Tab Browser rows.
- [x] Drag/drop can be performed with pointer input on desktop Chrome and does not break horizontal scrolling of the tab strip.
- [x] Responsive QA proves the top tab bar, Tab Browser table/list, drag affordances, filters, and create controls remain usable and non-overlapping at mobile and desktop viewport sizes.

### Reports Daemon And Combined Index

- [x] Klimkit configuration supports multiple report roots/repo roots or worktree roots, including the primary `[paths].repo_root`, without scanning arbitrary home directories by default.
- [x] Missing, duplicate, unreadable, or non-directory configured report roots are skipped or reported in the index without crashing the daemon.
- [x] Only files under each configured root's `.klimkit/reports/` directory are discovered as reports.
- [x] `GET /reports/` on the Klimkit daemon returns an HTML index page, outside the `/switchboard/` base path, without breaking existing `/switchboard/` routes.
- [x] Server-mode `kk apply`, `kk pull`, and `kk doctor` output include the Tailscale `https://<machine>.<tailnet>.ts.net/reports/` proof reports URL when Tailscale DNS is available.
- [x] The `/reports/` index lists reports from at least two configured roots in one table with observable columns for project/root label, report title or filename, timestamp or mtime, relative report path, and a link to open the report.
- [x] The `/reports/` index sorts reports newest-first by report timestamp metadata when available, otherwise by file mtime.
- [x] The `/reports/` index has a clear empty state when no configured root has `.klimkit/reports/*.html`.
- [x] Report detail links serve the selected HTML report with `text/html; charset=utf-8` and preserve relative media links inside that report.
- [x] Screenshot and video files referenced by report HTML load from the same repo-local `.klimkit/reports/` tree when present, even though those media files are ignored by Git.
- [x] Report serving rejects path traversal, absolute-path injection, symlink escape, and requests for files outside configured `.klimkit/reports/` trees with 404 or 403 behavior.
- [x] Report routes use the same auth boundary as Switchboard: loopback tokenless access remains allowed, non-loopback deployments require the configured Switchboard auth token or valid auth cookie.
- [x] `HEAD /reports/` and `HEAD` for an individual report return correct status, content type, and content length without a response body.
- [x] Report index HTML uses minimal responsive CSS and remains readable on mobile and desktop without JavaScript.

### Gitignore And Git Tracking

- [x] `.gitignore` ignores large report media under `.klimkit/reports/`, including at least `*.png`, `*.jpg`, `*.jpeg`, `*.gif`, `*.webp`, `*.mp4`, `*.webm`, and `*.mov`.
- [x] `.gitignore` does not ignore `.klimkit/reports/**/*.html`, so final report HTML can be added to Git.
- [x] Existing tracked task notes and small proof files under `.klimkit/tasks/` remain trackable.
- [x] Verification includes `git check-ignore -v` proof that report media files are ignored and report HTML is not ignored.
- [x] Verification includes `git status --short --ignored` or equivalent proof showing report HTML as trackable and generated screenshot/video media as ignored.

### Automated Tests

- [x] `uv run python -m unittest tests.test_codex_pack_validation -q` passes and includes assertions for checklister/final-reviewer screenshot, video, HTML report, and `.klimkit/reports/` requirements.
- [x] `uv run python -m unittest tests.test_switchboard -q` passes with focused coverage for `/reports/` index discovery, multi-root aggregation, report serving, media serving, auth, HEAD, missing roots, empty state, and traversal rejection.
- [x] `uv run python -m unittest tests.test_docs_static -q` passes with static assertions for Tab Browser copy/docs, report workflow docs, and Gitignore/report tracking guidance.
- [x] If Klimkit config parsing/rendering changes, `uv run python -m unittest tests.test_klimkit_install -q` passes with coverage for the new configured report roots.
- [x] If CLI output or doctor/apply URL reporting changes for `/reports/`, `uv run python -m unittest tests.test_klimkit_cli -q` passes with coverage for the report URL.
- [x] `node --check src/klimkit/apps/switchboard/static/app.js` passes after Switchboard JavaScript changes.
- [x] `uv run python -m unittest discover -s tests -q` passes before final review.

### Browser QA Screenshots And Video

- [x] Browser QA uses the `agent-browser` CLI against a running local Klimkit/Switchboard server.
- [x] Browser QA captures screenshots for Tab Browser active state, empty or seeded rows state, create controls, filters, archived rows visible, top-bar drag before/after, Tab Browser row drag before/after, and reload persistence.
- [x] Browser QA captures screenshots for desktop and mobile viewport widths showing no overlapping controls or clipped text in the tab bar, Tab Browser, and report index.
- [x] Browser QA captures screenshots for `/reports/` empty state and populated multi-root index.
- [x] Browser QA captures a native `agent-browser` video recording that demonstrates keyboard activation of Tab Browser, arrow-key navigation through Tab Browser, top tab click switching, top-bar drag/drop reorder, Tab Browser row drag/drop reorder, reload persistence, archived-tab reorder/unarchive behavior, and opening a report from `/reports/`.
- [x] The browser QA video is saved under `.klimkit/reports/` or a report-local media subdirectory and is referenced by the final HTML report.
- [x] Any browser QA failure includes a focused reproduction note or debugger/root-cause note before implementation is called complete.

### Final HTML Report Proof

- [x] A final HTML proof report is created under this repo's `.klimkit/reports/` directory.
- [x] The final report HTML is minimal, responsive, and opens directly from disk and through the daemon `/reports/` route.
- [x] The final report contains the task summary, changed-file list, acceptance checklist link, automated command outputs or concise pass/fail summaries, manual QA notes, all required screenshots, and the required video with playback controls.
- [x] The final report displays every screenshot and video as a full-width section, not as small thumbnails.
- [x] The final report embeds MP4 videos for the playable report controls, with the native `agent-browser` recording retained as source evidence.
- [x] Every screenshot referenced by the final report exists locally, renders in a browser, and shows the claimed UI state.
- [x] The required video exists locally, plays in a browser, and contains the claimed end-to-end QA flow.
- [x] The final report HTML can be staged by Git while its large screenshots/videos remain ignored.

### Final Review Gate

- [x] Before the final user-facing completion response, the exact draft response is prepared.
- [x] Three `final_reviewer` subagents are run in parallel with the original request/task path, this checklist, changed files, automated test evidence, browser QA screenshots/video, the final HTML report path or URL, and the exact draft response.
- [x] Each final reviewer explicitly verifies the final HTML report, every screenshot, and representative video frames or playback.
- [x] All three final reviewers return PASS / READY FOR USER before any completion claim is sent.
- [x] The final response reports what changed, what checks passed, the final HTML report path, how Klim can manually verify `/reports/` and Tab Browser behavior, and any unavailable verification or residual risk.
