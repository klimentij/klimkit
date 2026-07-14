---
name: klimkit-report-server
description: Check, explain, or set up Klimkit static proof-report serving for `docs/work` HTML reports and Tailscale URLs. Use when a task needs report-server readiness, `/reports/` links, Tailscale Serve verification, or troubleshooting report visibility.
---

# Klimkit Report Server

Use this skill to make proof reports reachable and inspectable. The skill owns a small reference server script so report hosting can live with the skills package instead of depending on deprecated Klimkit runtime code.

## Workflow

1. Ensure Klimkit's docs-first context exists. If the repo lacks the `docs/work/` layout, use `klimkit-setup` first.
2. Identify the repository root and expected report locations:
   - Default: self-contained numbered HTML artifacts anywhere under `docs/work/` (excluding gitignored `.local/` folders)
   - Legacy readable fallback: `.klimkit/reports/` and `.klimkit/<operator>/reports/`
3. Check local report files before checking network serving.
4. If no report server is running, use `scripts/serve_reports.py` as the reference implementation or copy it into the target repo when the user asks for a persistent local setup.
5. If a local report server is configured, check the local `/reports/` URL.
6. If Tailscale is available, check the machine DNS name and the `/reports/` Tailscale URL.
7. If serving is unavailable, report the missing layer precisely:
   - no report HTML exists;
   - local server is not running;
   - Tailscale is not authenticated;
   - a tailnet proxy is not forwarding to the local report server;
   - permissions require operator setup.
8. Do not claim a Tailscale URL works until it has been fetched or otherwise verified in this session.

## Report Expectations

- HTML reports should be self-contained single files, tracked when they are part of work proof.
- Large screenshots/videos should usually stay in a gitignored `.local/` folder as local media referenced by the report.
- Report media should render full-width for inspection.
- Prefer MP4 presentation embeds when Chrome/PWA scrubbing matters.

Read [references/report-server.md](references/report-server.md) for the reference server boundary and common verification commands.
