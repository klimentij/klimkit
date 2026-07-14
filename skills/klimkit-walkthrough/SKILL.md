---
name: klimkit-walkthrough
description: Create human-readable Klimkit walkthrough proof reports with steps, screenshots, links, redaction checks, and report-server/Tailscale handoff. Use when a user asks for a walkthrough, proof report, demo evidence, QA narrative, or review packet.
---

# Klimkit Walkthrough

Create a small static HTML report that lets a human inspect what happened without reading the whole conversation.

## Workflow

1. Ensure Klimkit's docs-first context exists. If the repo lacks the `docs/work/` layout, use `klimkit-setup` first.
2. Define the walkthrough purpose: feature proof, bug reproduction, QA pass, setup proof, or decision brief.
3. Write the report as a self-contained single-file HTML, numbered like any other artifact in the current `docs/work/` phase folder (e.g. `003-walkthrough.html`). Keep heavy media in the phase folder's gitignored `.local/` subfolder unless it is irreproducible evidence.
4. Capture fresh evidence. Use screenshots for UI states; add video only when interaction timing or motion matters.
5. Write a concise report with:
   - title and timestamp;
   - source task, PR, or request links;
   - environment and URL under test;
   - ordered steps;
   - expected versus observed result;
   - embedded screenshots/video as full-width sections;
   - redactions and privacy notes;
   - validation summary and residual risk.
6. Validate that image/video links resolve from the report path.
7. Use `klimkit-report-server` to verify local or Tailscale serving when a shareable report URL is needed.
8. Add the report path and verified URL to the task proof or final handoff.

## Redaction Rules

- Do not expose secrets, tokens, private chat, customer data, private repo names, or tailnet internals in public artifacts.
- If sensitive material is necessary evidence, keep it local/ignored and summarize safely in tracked HTML.
- Do not claim a report is served until the served path is checked.

Read [references/walkthrough-report.md](references/walkthrough-report.md) for the first-pass HTML structure and proof checklist.
