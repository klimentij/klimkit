# Marketing Hygiene Quality Fix And Publish Checklist

Source follow-up request: "I definitely don't like how we compressed the images. They now look very pixelated and noisy, and there is too much loss there. So fix that. But I saw that in the report; I still don't see changes in the actual GitHub repo on GitHub in main."

Repository context supplied for this follow-up:

- Repo: `/home/ubuntu/klimkit`
- Branch: `main`
- Local HEAD and `origin/main`: `f8b095708fb1c3956e07d7c77674b6855b56efbf`
- Prior hygiene changes are local only and have not been pushed to GitHub.
- Existing dirty state includes prior hygiene changes, `.klimkit/log.md`, `.klimkit/reflection.md`, untracked `.klimkit/tasks/07-symphony-reflection/`, `.klimkit/tasks/08-marketing-hygiene/`, `.klimkit/reports/08-marketing-hygiene/`, and `assets/screenshots/seven-hour-codex-run.png`.
- Repo-local `AGENTS.md` requires a latest GitHub release for every commit that lands on `main`, using the next patch version unless Klim specifies otherwise.

All checklist items are blocking unless Klim explicitly changes scope.

## Acceptance Checklist

### Scope And Dirty-State Protection

- [ ] The implementation proof preserves the exact follow-up request and records the starting branch, local HEAD, `origin/main` SHA, and full pre-change dirty state before any file edits.
- [ ] Unrelated pre-existing dirty artifacts, especially `.klimkit/tasks/07-symphony-reflection/`, are not modified, staged, committed, moved, normalized, or deleted.
- [ ] Existing `.klimkit/log.md` and `.klimkit/reflection.md` content is preserved append-only; no previous entries are rewritten, reordered, removed, or silently folded into a new narrative.
- [ ] The follow-up stays focused on fixing README image quality, publishing the already-local marketing hygiene work to GitHub `main`, release creation, and the required proof/log/reflection/review artifacts.
- [ ] No README or asset changes unrelated to the marketing hygiene publish and image-quality correction are introduced.

### Image Quality Fix

- [ ] The current compressed README images are visually inspected before rework and the proof names which assets look pixelated, noisy, over-compressed, or otherwise unacceptable.
- [ ] README-referenced images are restored from better local sources or re-optimized with higher-quality settings so visible text, UI edges, gradients, and screenshots no longer appear pixelated or noisy at normal GitHub README viewing sizes.
- [ ] File-size targets are treated as quality-aware guidance, not a hard cap: final images may be larger than the prior compressed versions when needed for acceptable visual quality.
- [ ] The proof records before/after byte sizes, dimensions, and compression/resize choices for every README-referenced image changed in this follow-up.
- [ ] The hero and screenshot assets still provide a meaningful load-size improvement versus the original pre-hygiene oversized images unless the proof explains a specific quality reason for a larger tradeoff.
- [ ] No public README image exposes secrets, credentials, private URLs, sensitive Slack metadata, unapproved personal details, or unrelated conversation content after the rework.

### README Rendering Verification

- [ ] The README is rendered locally after the image rework and before commit; all referenced images load from intended repo paths with no broken links.
- [ ] Local desktop browser evidence shows the README top section, hero image, 7.5-hour screenshot section, Switchboard screenshots, and Telegram screenshot with acceptable visual quality.
- [ ] Local mobile-width browser evidence shows the README top area and image sections without clipped text, broken layout, or unusable scaling.
- [ ] A native `agent-browser` video recording captures scrolling through the locally rendered README top section, 7.5-hour screenshot/explanation, and resized screenshot areas; the native source recording remains available as evidence.
- [ ] After push, the live GitHub `main` README is opened in a browser and visually checked at the GitHub URL, not only in the local preview.
- [ ] Live GitHub browser evidence shows the new README copy and image changes are actually visible on `main` and that image quality remains acceptable after GitHub rendering/caching.

### Staging, Commit, Push, And Release

- [ ] Before staging, `git status --short --branch`, `git diff --stat`, and focused diffs are reviewed to decide the intentional publish set.
- [ ] Only intentional paths for the marketing hygiene work, the image-quality fix, and required `.klimkit` proof/log/reflection artifacts are staged; unrelated pre-existing artifacts remain unstaged.
- [ ] The commit is made directly on `main` only after the staged diff is reviewed and matches the accepted scope.
- [ ] The commit message clearly describes the marketing README/image-quality publish work.
- [ ] The commit is pushed to `origin/main`.
- [ ] The post-push local `main` HEAD, `origin/main`, and GitHub `main` all resolve to the new commit SHA.
- [ ] The next patch GitHub release is created for that new commit and marked as the latest release, per repo-local `AGENTS.md`.
- [ ] Release notes mention the README marketing hygiene publish and corrected image-quality tradeoff without overstating unrelated functionality.

### GitHub Main Verification

- [ ] GitHub `main` is verified through `gh`, browser, or both to contain the new commit, not just local changes.
- [ ] The live GitHub README on `main` displays the updated README text, 7.5-hour screenshot, and corrected-quality images.
- [ ] GitHub-rendered image URLs return successfully and are not stale broken references from local-only `.klimkit` paths or ignored proof media.
- [ ] The live latest GitHub release points at the pushed commit and uses the expected next patch version tag.

### Proof, Log, Reflection, And Report

- [ ] A follow-up implementation proof note under `.klimkit/tasks/08-marketing-hygiene/` records changed files, intentionally unstaged files, image quality decisions, before/after sizes, verification commands, GitHub URLs, commit SHA, push result, release tag, and any unavailable checks.
- [ ] `.klimkit/log.md` receives one concise ISO-timestamped append-only entry for the quality fix, push to `main`, and release.
- [ ] `.klimkit/reflection.md` is read before the Reflection Gate and receives a full UTC timestamped append-only reflection session after verification and before final review.
- [ ] The reflection entry uses `Observations`, `Derived Pattern`, `Insight`, and `Next Probe` unless a wider named-section format is needed.
- [ ] After reflection, the implementer explicitly reconsiders whether image quality, GitHub visibility, release state, or proof evidence needs correction before final reviewers are called.
- [ ] The final HTML proof report under `.klimkit/reports/08-marketing-hygiene/` is updated or replaced so it includes the follow-up image-quality evidence, local README screenshots, live GitHub screenshots, native `agent-browser` recording, commit SHA, release tag, and GitHub URLs.
- [ ] The proof report remains minimal, responsive, readable without a build step, and displays each screenshot and video as its own full-width section, not a thumbnail grid.
- [ ] If a Tailscale-served report URL is available, it is verified and included in the handoff; localhost report URLs are used only as fallback evidence.

### Automated Checks And Final Review

- [ ] `git diff --check` passes before commit.
- [ ] `uv run python -m unittest tests.test_docs_static -q` passes after README/asset changes, or the proof records the exact reason the focused docs check is unavailable.
- [ ] If Python code, CLI behavior, generated pack files, version metadata, or release metadata files are changed beyond README/assets/task proof, the appropriate broader automated test suite is run and recorded.
- [ ] The exact final response is drafted before final review and includes what changed, image-quality tradeoffs, commit SHA, push status, GitHub README verification, release tag, proof report path/URL, checks run, and any remaining risk.
- [ ] Three `final_reviewer` subagents are run in parallel with the original follow-up request, this checklist, changed files, verification evidence, reflection entry, proof report path/URL, release evidence, and exact draft final response.
- [ ] All three final reviewers return PASS / READY FOR USER before the implementer claims the follow-up task is complete.
