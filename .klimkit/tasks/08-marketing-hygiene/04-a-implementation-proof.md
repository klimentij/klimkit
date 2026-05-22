# Marketing Hygiene Implementation Proof

Date: 2026-05-22T03:04:00Z

Follow-up: image compression and publish details from this first pass were corrected in `06-a-quality-fix-and-publish-proof.md`. The first PNG optimization pass was rejected as too noisy and was not published.

## Request And Starting State

Klim asked for GitHub/README hygiene, a draft Hacker News post, use of the proud 7.5 hour run image near the top of the repo, and smaller README hero/screenshot assets.

Starting repository state recorded before edits:

- Path: `/home/ubuntu/klimkit`
- Branch: `main`
- Local HEAD: `f8b095708fb1c3956e07d7c77674b6855b56efbf`
- `origin/main`: `f8b095708fb1c3956e07d7c77674b6855b56efbf`
- Pre-existing dirty state: `.klimkit/log.md`, `.klimkit/reflection.md`, and untracked `.klimkit/tasks/07-symphony-reflection/`

Those pre-existing artifacts were preserved. New task artifacts for this work live under `.klimkit/tasks/08-marketing-hygiene/`.

## Changed Files

- `README.md` - added the 7.5 hour dogfood moment near the top and updated release status from `v0.1.6` to `v0.1.8`.
- `assets/brand/README.md` - documented the optimized README hero.
- `assets/brand/klimkit-readme-hero.png` - optimized and resized.
- `assets/screenshots/switchboard-pwa-workspace.png` - optimized and resized.
- `assets/screenshots/switchboard-catalog.png` - optimized and resized.
- `assets/screenshots/telegram-notifications.png` - optimized and resized.
- `assets/screenshots/seven-hour-codex-run.png` - added public-safe 7.5 hour run proof crop.
- `.klimkit/tasks/08-marketing-hygiene/03-a-hacker-news-draft.md` - prepared draft Show HN copy.
- `.klimkit/reports/08-marketing-hygiene/report.html` - browser proof report.

Final `git status --short --branch`:

```text
## main...origin/main
 M .klimkit/log.md
 M .klimkit/reflection.md
 M README.md
 M assets/brand/README.md
 M assets/brand/klimkit-readme-hero.png
 M assets/screenshots/switchboard-catalog.png
 M assets/screenshots/switchboard-pwa-workspace.png
 M assets/screenshots/telegram-notifications.png
?? .klimkit/reports/08-marketing-hygiene/
?? .klimkit/tasks/07-symphony-reflection/
?? .klimkit/tasks/08-marketing-hygiene/
?? assets/screenshots/seven-hour-codex-run.png
```

The untracked `.klimkit/tasks/07-symphony-reflection/` folder was pre-existing and unrelated to this task.

## GitHub Metadata

Checked with `gh repo view` and updated repository topics with `gh repo edit`.

Current topics:

```text
agent-workflows, agentic-engineering, ai-agents, automation, cli, code-server,
codex, codex-cli, developer-tools, proof-reports, pwa, python, tailscale,
worktrees
```

The repository description remains `Agentic engineering across machines, under control.` Homepage remains unset because there is no dedicated docs/landing URL yet. GitHub API returned `open_graph_image_url: null`; social preview configuration could not be changed through the available CLI/API surface.

No commit, push, or GitHub release was created in this pass. The user asked for hygiene and readiness, not publishing a new release, and the working tree started with pre-existing dirty `.klimkit` artifacts that should not be silently folded into a release commit.

## Image Provenance And Size Reduction

The 7.5 hour run image came from:

```text
/home/ubuntu/klimkipedia/.klimkit/tasks/klimkit/01-220526-marketing-exposure/image.png
```

It is the public-safe terminal proof crop, not the full surrounding Slack thread. Final public asset:

```text
assets/screenshots/seven-hour-codex-run.png
```

README-referenced local image sizes:

| Asset | Before | After | Dimensions Before | Dimensions After |
| --- | ---: | ---: | --- | --- |
| `assets/brand/klimkit-readme-hero.png` | 1,129,098 B | 143,471 B | 1916 x 821 | 1280 x 548 |
| `assets/screenshots/switchboard-pwa-workspace.png` | 1,571,234 B | 490,703 B | 3104 x 2030 | 1600 x 1046 |
| `assets/screenshots/switchboard-catalog.png` | 1,499,833 B | 400,066 B | 3104 x 2030 | 1600 x 1046 |
| `assets/screenshots/telegram-notifications.png` | 822,886 B | 109,252 B | 980 x 1744 | 700 x 820 |
| `assets/screenshots/seven-hour-codex-run.png` | n/a | 83,184 B | n/a | 980 x 510 |

Total README image payload changed from 5,023,051 B to 1,226,676 B, including the new 7.5 hour screenshot. Net reduction: 3,796,375 B.

The Telegram notification screenshot was cropped during optimization so actual tailnet URLs are no longer visible in the README asset. Remaining machine labels in the Switchboard and Telegram screenshots are non-secret demo aliases from existing product evidence; no tokens, credentials, or live auth material are visible.

## Hacker News Draft

Draft path:

```text
.klimkit/tasks/08-marketing-hygiene/03-a-hacker-news-draft.md
```

No Hacker News post was submitted, and no HN credentials or cookies were used.

## Browser Evidence

Rendered the README locally at:

```text
http://127.0.0.1:8765/tmp/readme-preview/index.html
```

Captured evidence under `.klimkit/reports/08-marketing-hygiene/assets/`:

- `readme-top-desktop.png`
- `readme-seven-hour-desktop.png`
- `readme-switchboard-desktop.png`
- `readme-catalog-desktop.png`
- `readme-top-mobile.png`
- `readme-scroll.webm`
- `readme-scroll.mp4`

The final HTML proof report is:

```text
.klimkit/reports/08-marketing-hygiene/report.html
```

The report HTML is in a non-ignored repo path, but it has not been staged or committed. Report screenshots and videos under `.klimkit/reports/**` are intentionally Git-ignored by this repository. Treat the report media as local/Tailscale QA evidence, not public GitHub content. If HN readers should inspect proof artifacts directly, create a separate public example artifact page with deliberately tracked or hosted media.

Tailscale report URL verified with HTTP 200:

```text
https://odev.tail11c448.ts.net/reports/r/klimkit-dc70a74e9a/08-marketing-hygiene/report.html
```

## Verification Commands

```bash
git diff --check
uv run python -m unittest tests.test_docs_static -q
agent-browser --args "--no-sandbox" open http://127.0.0.1:8765/tmp/readme-preview/index.html
agent-browser screenshot /home/ubuntu/klimkit/.klimkit/reports/08-marketing-hygiene/assets/readme-top-desktop.png
agent-browser screenshot /home/ubuntu/klimkit/.klimkit/reports/08-marketing-hygiene/assets/readme-seven-hour-desktop.png
agent-browser screenshot /home/ubuntu/klimkit/.klimkit/reports/08-marketing-hygiene/assets/readme-switchboard-desktop.png
agent-browser screenshot /home/ubuntu/klimkit/.klimkit/reports/08-marketing-hygiene/assets/readme-top-mobile.png
```

Results:

- `git diff --check`: passed.
- `uv run python -m unittest tests.test_docs_static -q`: passed, 4 tests.
- Browser screenshots/video captured successfully after launching Chrome with `--no-sandbox`, which is required in this VM.
- Tailscale report URL returned HTTP 200.
- Post-correction reflection was appended at `.klimkit/reflection.md` with timestamp `2026-05-22T03:30:23Z` after adding catalog browser proof, cropping the Telegram README screenshot, and correcting tracked/published wording.

Full Python test suite was not run because no Python code, CLI behavior, generated pack, or release metadata files changed.
