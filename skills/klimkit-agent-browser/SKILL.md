---
name: klimkit-agent-browser
description: Browser automation for Klimkit UI work. Use when Codex needs to open a site or local app, click through flows, fill forms, inspect rendered UI, capture screenshots, record proof, test responsive states, or verify that visual behavior matches code changes.
---

# Klimkit Agent Browser

Use this skill for browser-facing proof inside Klimkit workflows. It wraps the upstream `agent-browser` tool with Klimkit evidence rules.

The original imported upstream entrypoint is preserved at [references/upstream-skill.md](references/upstream-skill.md). Offline snapshots of upstream CLI skill guidance are preserved as `references/upstream-*.md`; use them only when the installed CLI cannot provide current `agent-browser skills get ...` output.

## Workflow

1. Define the browser goal and the evidence needed before starting.
2. If the CLI is missing, install or ask the user to install it with `npm i -g agent-browser && agent-browser install`.
3. Load current CLI command help only when needed:

   ```bash
   agent-browser skills get core
   agent-browser skills list
   ```

4. Start or attach to a browser session, navigate to the target, and interact through stable element refs when available.
5. Capture a screenshot at every new screen, route, modal, major state change, and responsive breakpoint you rely on.
6. Visually inspect the screenshot before trusting the result. Accessibility trees are useful for interaction, but they can miss overlap, clipping, z-index bugs, canvas/SVG/image rendering, visual disabled states, and text overflow.
7. For UI completion proof, pair this with `klimkit-walkthrough` and save screenshots, video, and notes under `.klimkit/<operator>/reports/`.

## Evidence Rules

- Do not claim UI correctness from DOM text, accessibility snapshots, or route responses alone.
- Check desktop and mobile viewports when layout, navigation, touch targets, or responsive behavior changed.
- Record video for multi-step flows, animations, drag/drop, auth-sensitive paths, or anything hard to understand from screenshots.
- Redact secrets, tokens, private URLs, and personal data before publishing a report.

## Safety

- Keep browser automation scoped to systems the user authorized.
- Do not enter real credentials unless the user explicitly provides the intended test account and confirms use.
- Do not expose local browser or dashboard ports outside localhost unless the user asks for remote proof access.
