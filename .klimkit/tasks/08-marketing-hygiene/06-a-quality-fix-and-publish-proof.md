# Marketing Hygiene Quality Fix Proof

Date: 2026-05-22T04:03:14Z

## Follow-Up Request

Klim said the first compression pass made the images look pixelated, noisy, and too lossy, and also noted that the changes were not visible on GitHub `main`.

## Starting State

- Repo: `/home/ubuntu/klimkit`
- Branch: `main`
- Local HEAD before publish work: `f8b095708fb1c3956e07d7c77674b6855b56efbf`
- `origin/main` before publish work: `f8b095708fb1c3956e07d7c77674b6855b56efbf`
- Dirty state included the prior marketing hygiene work, `.klimkit/log.md`, `.klimkit/reflection.md`, untracked `.klimkit/tasks/08-marketing-hygiene/`, untracked `.klimkit/reports/08-marketing-hygiene/`, the new 7.5 hour screenshot asset, and unrelated untracked `.klimkit/tasks/07-symphony-reflection/`.

The unrelated `.klimkit/tasks/07-symphony-reflection/` folder was not modified or staged.

## Image Quality Correction

The rejected first pass used smaller PNGs that hit the size target but visibly degraded the dark hero/screenshot assets. The noisy tracked PNG edits were restored from `HEAD` so they are not part of the publish set.

The README now uses higher-quality JPEGs for the large hero and screenshots:

| README asset | Source size and dimensions | Rejected lossy PNG size | Final size and dimensions | Choice |
| --- | ---: | ---: | ---: | --- |
| `assets/brand/klimkit-readme-hero.jpg` | 1,129,098 bytes, 1916x821 | 143,471 bytes | 111,190 bytes, 1600x686 | High-quality JPEG keeps the glow/grid clean while staying much smaller than source. |
| `assets/screenshots/switchboard-pwa-workspace.jpg` | 1,571,234 bytes, 3104x2030 | 490,703 bytes | 558,623 bytes, 2200x1439 | Larger than the rejected PNG because legibility mattered more than a hard 500 KB cap. |
| `assets/screenshots/switchboard-catalog.jpg` | 1,499,833 bytes, 3104x2030 | 400,066 bytes | 234,623 bytes, 2200x1439 | JPEG keeps UI edges readable with a large size reduction. |
| `assets/screenshots/telegram-notifications.jpg` | 822,886 bytes, 980x1744 | 109,252 bytes | 153,995 bytes, 820x962 | Cropped to the relevant notification stack and encoded without the noisy low-bit-depth look. |
| `assets/screenshots/seven-hour-codex-run.png` | new public-safe crop | n/a | 83,184 bytes, 980x510 | Kept as PNG because it is a small terminal screenshot with sharp text. |

Total README-local image payload moved from 5,023,051 bytes for the original four oversized images to 1,141,615 bytes for the five current README images, including the new 7.5 hour proof crop.

## Local Verification

- Visual inspection: final hero, Switchboard PWA, workspace catalog, and Telegram JPEGs no longer show the obvious paletted/noisy compression from the first pass.
- Local README render: `http://127.0.0.1:8765/tmp/readme-preview/index.html`
- Browser image-load check: all README images completed with non-zero natural dimensions.
- Desktop evidence: `.klimkit/reports/08-marketing-hygiene/assets/readme-top-desktop.png`, `readme-seven-hour-desktop.png`, `readme-switchboard-desktop.png`, `readme-catalog-desktop.png`, and `readme-telegram-desktop.png`.
- Mobile evidence: `.klimkit/reports/08-marketing-hygiene/assets/readme-top-mobile.png` and `readme-switchboard-mobile.png`.
- Native recording: `.klimkit/reports/08-marketing-hygiene/assets/readme-scroll.webm`.
- MP4 presentation copy: `.klimkit/reports/08-marketing-hygiene/assets/readme-scroll.mp4`.

Automated checks:

```text
git diff --check
uv run python -m unittest tests.test_docs_static -q
```

Both passed before staging.

## Publish Plan

The intentional publish set is the README, public image assets, brand asset note, docs static test update, the Hacker News draft/task notes, and the proof report HTML. The noisy PNG edits are not staged. The unrelated `.klimkit/tasks/07-symphony-reflection/` artifact is not staged.

Per repo-local `AGENTS.md`, after the commit lands on `main`, the next patch GitHub release should be created and marked latest. The expected release tag for this publish is `v0.1.9`.
