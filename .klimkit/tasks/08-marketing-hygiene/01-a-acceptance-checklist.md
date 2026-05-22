# Marketing Hygiene Acceptance Checklist

Source request: "All right, go to this repo and do hygiene, and then prepare a draft of the Hacker News post. also there was a moment i was proud of, 7.5h of work, great results no loop goal ralf etc. Here's the image I attached, and they also uploaded it to the task folder in .klimkit. So maybe use it somewhere near the top of the GitHub repo with the explanation why it's cool. And also, maybe resize the hero image in the screenshots so they don't take so much space. The hero image in GitHub is currently over a megabyte and takes time to load. It could be like two, three hundred kilobytes easily. Let me know when everything is ready."

Pre-checklist repo state supplied by the requester: `/home/ubuntu/klimkit`, branch `main`, HEAD `f8b095708fb1c3956e07d7c77674b6855b56efbf`, `origin/main` at the same SHA, and pre-existing dirty artifacts `.klimkit/log.md`, `.klimkit/reflection.md`, and untracked `.klimkit/tasks/07-symphony-reflection/`.

All checklist items are blocking unless Klim explicitly changes scope.

## Acceptance Checklist

### Scope And Preservation

- [ ] The implementation proof records the exact source request, the starting branch/SHA, and the known pre-existing dirty state so later review can separate this work from prior user or agent artifacts.
- [ ] Pre-existing changes in `.klimkit/log.md`, `.klimkit/reflection.md`, and `.klimkit/tasks/07-symphony-reflection/` are preserved; any updates to log or reflection are append-only and do not rewrite, reorder, delete, normalize, or silently absorb existing content.
- [ ] Final `git status --short --branch` and `git diff --stat` evidence clearly distinguishes intentional changes for this task from pre-existing dirty work.
- [ ] The implementation stays inside the requested surface: README/GitHub presentation hygiene, public image assets, the Hacker News draft, task proof, log/reflection updates, and release/GitHub metadata only when required or feasible.
- [ ] No Hacker News post is submitted, no HN credentials or cookies are used, and no public posting action is attempted.

### README And GitHub Hygiene

- [ ] The README top section presents Klimkit clearly as an agentic engineering/workspace control repo without adding unsupported product claims or generic marketing filler.
- [ ] The README near-top image order and text are reviewed so the main hero, the new 7.5h screenshot moment, and existing Switchboard screenshots form a coherent public first impression.
- [ ] GitHub repository description, topics, homepage/social/share preview state, and README release status are checked; feasible safe updates are applied, and any unavailable GitHub metadata change is documented with the exact permission/API limitation.
- [ ] If release-facing changes are committed to `main`, `pyproject.toml`, README release status, tag/release notes, and the latest GitHub release are updated consistently to the next patch version per `AGENTS.md`; if the work remains uncommitted or no release is made, the proof explicitly records why.
- [ ] Public copy avoids leaking local-only workflow assumptions, private names, private Slack context, machine names, credentials, tokens, internal URLs, or non-public user details.

### 7.5h Screenshot Moment

- [ ] The attached/user-uploaded Slack screenshot is located from the task artifacts before use, and the proof records both its source path and the final public asset path.
- [ ] If the expected screenshot is missing from `.klimkit/tasks/`, the implementer stops and records the missing artifact instead of inventing or substituting a different image.
- [ ] Before publishing the screenshot in README/GitHub-facing content, the image is reviewed and cropped/redacted as needed so it does not expose secrets, private URLs, sensitive Slack metadata, unapproved personal details, or unrelated conversation content.
- [ ] A trackable optimized copy of the safe screenshot is added under a public asset path rather than referencing a temporary, ignored, or `.klimkit` task-file path from the README.
- [ ] The README uses the screenshot near the top with concise alt text and a grounded explanation of why the moment is cool: a roughly 7.5-hour agent work session produced strong results, stayed on goal, and did not loop.
- [ ] The screenshot explanation does not overstate the evidence, does not imply universal reliability, and does not publish private names or attributions unless they are already safe and approved for public README use.

### Image Size And Display Quality

- [ ] Before/after byte sizes and pixel dimensions are recorded for every local image referenced by README, including `assets/brand/klimkit-readme-hero.png`, `assets/screenshots/switchboard-pwa-workspace.png`, `assets/screenshots/switchboard-catalog.png`, `assets/screenshots/telegram-notifications.png`, and the new 7.5h screenshot asset if added.
- [ ] The README hero image is reduced from its current over-1 MB size to approximately 200-300 KB, or the proof documents why a slightly larger final size is necessary to preserve acceptable display quality.
- [ ] Existing README screenshots that are over 1 MB are resized and/or recompressed to materially reduce load, with a target of no more than about 500 KB each unless the proof shows that target damages legibility.
- [ ] The total payload of README-referenced local images is materially reduced, and the proof includes the total before/after byte count.
- [ ] Image dimensions are appropriate for GitHub README display; oversized source dimensions are not kept when they provide no visible README benefit.
- [ ] Optimized images remain readable on desktop and mobile README renders, with no broken links, no accidental cropping of important content, no unreadable UI text, and no obvious compression artifacts.
- [ ] Original image formats are changed only when GitHub README rendering, file size, and quality are improved; no unnecessary duplicate public assets are left behind.

### Hacker News Draft

- [ ] A draft Show HN post is prepared under `.klimkit/tasks/08-marketing-hygiene/` and is clearly labeled as a draft, not a submitted post.
- [ ] The draft includes a concise title candidate and body text suitable for a Hacker News Show HN submission.
- [ ] The draft explains what Klimkit does, why it exists, what is interesting about the workflow, and the current caveats or maturity level without making unsupported claims.
- [ ] The draft can mention the 7.5h/no-loop moment only if it reads as factual project context rather than private Slack gossip or self-congratulatory noise.
- [ ] The proof records where the draft lives and confirms it was not posted.

### Verification And Evidence

- [ ] An agent-authored proof note under `.klimkit/tasks/08-marketing-hygiene/` records changed files, source image provenance, before/after image sizes, GitHub metadata checks, draft HN post path, exact verification commands, and any unavailable checks.
- [ ] `git diff --check` passes.
- [ ] `uv run python -m unittest tests.test_docs_static -q` passes after README/asset changes, or the proof records why that focused docs check is unavailable.
- [ ] If `pyproject.toml`, Python code, generated pack files, release metadata, or CLI behavior changes, `uv run python -m unittest -q` passes, or any failure is root-caused and explicitly reported.
- [ ] GitHub/README image links are verified by rendering the README locally or on GitHub after push; all referenced images load from the intended paths.
- [ ] Browser QA captures a desktop screenshot of the rendered README top section showing the hero and near-top public positioning.
- [ ] Browser QA captures a desktop screenshot of the rendered README section containing the 7.5h screenshot and explanation.
- [ ] Browser QA captures a desktop screenshot of the resized Switchboard screenshots in the README showing acceptable legibility after compression.
- [ ] Browser QA captures a mobile-width screenshot of the rendered README top area showing no clipped text, broken layout, or unusable image scaling.
- [ ] A native `agent-browser` video recording captures scrolling through the rendered README top section, the 7.5h screenshot/explanation, and the resized screenshot area; the native source recording is retained as evidence.
- [ ] A final HTML proof report is created at `.klimkit/reports/08-marketing-hygiene/report.html`.
- [ ] The proof report is minimal, responsive, readable without a build step, and includes text evidence plus relative references to every screenshot and video.
- [ ] The proof report displays each screenshot and video as its own full-width section, not as a thumbnail grid.
- [ ] If a Tailscale DNS report URL is available, the final handoff includes the Tailscale-served report URL; localhost URLs are used only as fallback evidence.

### Log, Reflection, And Final Review

- [ ] `.klimkit/log.md` receives one concise ISO-timestamped entry for the completed marketing hygiene/HN draft work, appended without disturbing pre-existing dirty log content.
- [ ] `.klimkit/reflection.md` is read before the Reflection Gate and receives a full UTC timestamped reflection session after verification and before final review.
- [ ] The reflection entry uses the default `Observations`, `Derived Pattern`, `Insight`, and `Next Probe` sections unless the synthesis requires a wider named-section format.
- [ ] The reflection pass considers current results against relevant `.klimkit` task history, memory, log, and the README/release/public-proof pattern, then the implementer explicitly reconsiders whether any work or verification must be updated before final review.
- [ ] The exact final response is drafted before final review and includes changed areas, HN draft path, asset size reductions, verification results, proof report path/URL, release/GitHub metadata status, and any unavailable checks.
- [ ] Three `final_reviewer` subagents are run in parallel with the original request, this checklist, changed files, verification evidence, reflection entry, proof report path/URL, and the exact draft final response.
- [ ] All three final reviewers return PASS / READY FOR USER before the implementer claims the task is complete.
