# Better Workflow And Tabs Plan

Human task: `01-h-in.md`.

## Report Artifact Approaches

1. **PDF with embedded media**: good for static screenshots, bad for video. Browser/PDF viewer support for embedded video is inconsistent, and generated PDFs are harder for final reviewers to inspect frame-by-frame. Do not use.
2. **HTML plus sibling media folder**: simple, readable, small HTML, video stays as a normal `.webm`/`.mp4`. It is zero hosting, but not one file; moving the report requires keeping the folder together.
3. **Self-contained HTML with embedded screenshots and video data URIs**: one file, zero hosting, opens locally, responsive with minimal CSS, supports `<img>` and `<video controls>`. File can get large, but it best matches “embedded screenshots and videos.”

**Approved decision:** use repo-local HTML reports under each project's `.klimkit/reports/` directory. Track the report `.html` in Git, but keep screenshots and videos as repo-local ignored media files so large QA artifacts do not bloat commits. Klimkit should serve one combined `/reports/` index across configured repo/worktree roots and link to each discovered repo-local report plus its local media.

The earlier self-contained-HTML option is still acceptable only for tiny proof reports. The default for UI QA is now Git-tracked HTML with relative media references to ignored screenshots/videos in the same `.klimkit/reports/` tree.

**Approved Tailscale URL decision:** agent completion results must include the Tailscale-served report URL when the machine has a Tailscale DNS name. Localhost report URLs are acceptable only as local QA fallback evidence; the useful handoff URL is `https://<machine>.<tailnet>.ts.net/reports/` or the specific report URL under that index.

**Approved inspectability decision:** proof reports must show screenshots and videos as full-width sections instead of thumbnail grids. Embedded report videos should prefer MP4 so Chrome/PWA playback supports reliable drag-to-seek; native `agent-browser` recordings may be converted to MP4 for the report while retaining the source recording as evidence.

## Implementation Plan

1. **Harness QA workflow**
   - Update `packs/codex/agents/checklister.toml` so UI QA checklist items require screenshots, an `agent-browser` recorded video, and a final report artifact.
   - Update `packs/codex/agents/final-reviewer.toml` so final reviewers must open the report, inspect screenshots, and verify video content by sampling frames or playback.
   - Require reports under `.klimkit/reports/`, with HTML tracked and large media ignored.
   - Require final responses and agent proof handoffs to include the Tailscale `/reports/` URL when available.
   - Update `packs/codex/AGENTS.md` and `harness-tuning` only if needed to keep the workflow consistent.
   - Add pack validation tests proving the report/video requirements exist.

2. **Reports server**
   - Add read-only Klimkit daemon routes for `/reports/` and `/reports/r/<root-id>/<path>`.
   - Discover `.klimkit/reports/**/*.html` inside configured repo/worktree roots, including `[paths].repo_root`, without scanning the whole home directory.
   - Render one minimal responsive HTML table across multiple repos with newest reports first.
   - Serve report HTML and same-tree media safely; reject traversal, absolute path injection, and symlink escape.
   - Configure Tailscale Serve for `/reports` on Switchboard server machines and print the Tailscale reports URL in `kk apply`, `kk pull`, and `kk doctor` output.
   - Add `.gitignore` rules for report media extensions while keeping report HTML trackable.

3. **Switchboard tab browser**
   - Replace the catalog drawer mental model with a first “Tab Browser” special tab.
   - `Ctrl+Option+0` activates Tab Browser. `Ctrl+Option+Left/Right` includes Tab Browser in the navigation cycle. Clicking a normal top tab while Tab Browser is active switches directly to that tab.
   - Keep `Ctrl+Option+1..9` mapped to regular workspace tabs, not Tab Browser, so existing muscle memory stays useful.
   - Keep `Escape` as a quick way out of Tab Browser by returning to the last regular workspace.

4. **Drag/drop ordering**
   - Add a client-side manual order list keyed by stable workspace id/identity in `localStorage`.
   - Default order stays newest-created first. Manual drag/drop overrides that order; new unordered tabs still appear newest-first around the manually ordered list.
   - Support drag/drop in the top tab bar for non-archived tabs and in Tab Browser rows for all visible rows. Archived tabs remain hidden from the top tab bar but can still be reordered in Tab Browser when visible.
   - Reuse one ordering helper for tab bar, Tab Browser, keyboard navigation, and loaded-frame recency inputs.

5. **Verification**
   - Before coding, run the new `checklister` workflow and write the acceptance checklist into the next `*-a-*.md` task note.
   - Automated checks: focused pack validation, Switchboard static/docs tests, `node --check src/klimkit/apps/switchboard/static/app.js`, and full `uv run python -m unittest discover -s tests -q`.
   - Browser QA: use `agent-browser` with screenshots and video proving Tab Browser activation, arrow navigation through Tab Browser, tab click switching, top-bar drag/drop, row drag/drop, reload persistence, archived-tab behavior, reports index behavior, and responsive layout.
   - Produce the final HTML proof report under this repo's `.klimkit/reports/` tree and give it to the 3 final reviewers with the checklist and final draft.


---

can i make a part of klimkit daemon a simple web searve that would look into all repos for ./klimkit/reports/ subfolders and list them in a single page like <ts url>/reports and then url for each report?

and i'd like to gittrack only html, git ignore imgs and video as large

can it list in the same table in reports/ page from mutliple repos? i don't want a home folder with reports i wanna keep them in repo projects
