---
name: klimkit-impeccable
description: High-craft frontend design and product UI iteration. Use when Codex needs to design, critique, polish, clarify, harden, adapt, animate, colorize, or otherwise improve a real interface while preserving product context, accessibility, responsive behavior, and visual proof.
---

# Klimkit Impeccable

Use this when the quality bar is visual craft, not just correctness. It adapts Impeccable's design references into the Klimkit workflow.

## Start

1. Read the user's goal and the existing product context. Prefer local `PRODUCT.md`, `DESIGN.md`, design tokens, CSS, component libraries, and representative UI files.
2. If useful, run the local context helper:

   ```bash
   node skills/klimkit-impeccable/scripts/context.mjs
   ```

   Treat update notices and missing product docs as advisory unless the user specifically asks to initialize Impeccable state.
3. Choose the smallest relevant reference:
   - Build or plan: `references/shape.md`, `references/craft.md`, `references/init.md`, `references/document.md`, `references/extract.md`
   - Evaluate: `references/critique.md`, `references/audit.md`
   - Refine: `references/polish.md`, `references/bolder.md`, `references/quieter.md`, `references/distill.md`, `references/harden.md`, `references/onboard.md`
   - Enhance: `references/animate.md`, `references/colorize.md`, `references/typeset.md`, `references/layout.md`, `references/delight.md`, `references/overdrive.md`
   - Fix: `references/clarify.md`, `references/adapt.md`, `references/optimize.md`
4. Read either `references/brand.md` for marketing, portfolio, editorial, and brand-led pages, or `references/product.md` for apps, dashboards, tools, and repeated operational workflows.
5. Inspect the actual UI code before proposing design changes.

## Klimkit Rules

- Route implementation through `klimkit-implement`; TDD remains required for behavior-changing work.
- Use `klimkit-agent-browser` for screenshots at every new screen or state you rely on. Visual inspection is mandatory for UI completion claims.
- Use `klimkit-walkthrough` for proof reports when the user needs reviewable evidence.
- Prefer existing design tokens and components. Introduce new visual language only when it clearly improves the user-facing result.
- Do not use local live-edit servers, tokenized localhost control channels, remote browser sessions, or bundled automation scripts without telling the user what will run and why.

## Craft Checks

- Text is readable, specific, and fits its container.
- Layout is responsive, stable, and free of incoherent overlap.
- Interaction states are visible and consistent.
- Motion has purpose and respects reduced-motion preferences.
- Accessibility is checked through code and rendered screenshots.
- The result does not look like a generic AI template or a pile of cards.

## Output

For reviews, lead with findings and file references. For implementation, state the visual direction briefly, make the smallest coherent change, verify in-browser, and hand off screenshots or a walkthrough report.
