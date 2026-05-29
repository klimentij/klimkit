---
name: klimkit-ui-ux-pro-max
description: UI/UX planning and heuristic lookup for web and mobile interfaces. Use when Codex needs to choose product-fit style, color, typography, chart, layout, accessibility, platform, or responsive guidance while designing, reviewing, or improving UI.
---

# Klimkit UI/UX Pro Max

Use this as a searchable heuristic pack, not as a replacement for product judgment. It is most useful before UI implementation and during review when the agent needs concrete options for product type, style, color, typography, charts, accessibility, or platform behavior.

## Workflow

1. Start from the product context, existing design system, target audience, and the user-visible task.
2. Pick one primary design lens:
   - Use `klimkit-impeccable` for high-craft product UI work.
   - Use this skill when you need broad heuristic lookup or comparisons.
   - Use `klimkit-web-design-guidelines` for checklist-style review findings.
3. Query the bundled database only for the decision you need:

   ```bash
   python3 skills/klimkit-ui-ux-pro-max/scripts/search.py "<query>" --domain ux
   python3 skills/klimkit-ui-ux-pro-max/scripts/search.py "<query>" --domain color
   python3 skills/klimkit-ui-ux-pro-max/scripts/search.py "<query>" --stack react
   python3 skills/klimkit-ui-ux-pro-max/scripts/search.py "<product industry style>" --design-system
   ```

4. Treat script output as candidates. Reconcile it with existing repo conventions and the user request before editing code.
5. For visual implementation, verify with `klimkit-agent-browser` screenshots and put proof into `klimkit-walkthrough`.

## Priority Checks

- Accessibility: contrast, labels, keyboard reachability, focus visibility, reduced motion.
- Interaction: touch targets, loading feedback, destructive confirmation, error recovery.
- Layout: mobile-first fit, no horizontal scroll, no overlapping controls, stable dimensions.
- Typography and color: semantic tokens, readable scale, product-fit palette, no gray-on-gray copy.
- Motion: purposeful, interruptible, reduced-motion-safe, no blank reveal states.
- Data visualization: chart type matches the data, exact values are recoverable, color is not the only signal.

## Boundaries

- Do not persist generated `design-system/` files unless the user wants a design system artifact.
- Do not let database recommendations override a stronger existing brand or component system.
- Do not use this skill for backend-only, infrastructure-only, or non-visual automation work.
