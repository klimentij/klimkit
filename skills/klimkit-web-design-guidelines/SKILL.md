---
name: klimkit-web-design-guidelines
description: Review web UI implementation quality. Use when Codex needs to audit frontend code, pages, components, accessibility, responsive behavior, interaction states, visual polish, or UX best-practice compliance without relying on a product-specific design system.
---

# Klimkit Web Design Guidelines

Use this as a generic web UI review checklist. Keep it independent of Vercel-specific phrasing and do not fetch mutable external rules unless the user asks for current upstream guidance.

The original imported upstream skill is preserved at [references/upstream-skill.md](references/upstream-skill.md). Read it when auditing what changed from upstream or when the user explicitly wants the original Vercel workflow.

## Review Flow

1. Identify the UI surface: files, route, component, or screenshot.
2. Read the relevant code and existing design conventions before judging.
3. If the UI can run, use `klimkit-agent-browser` to inspect screenshots at the states you review.
4. Check the surface against:
   - Semantic HTML and reachable keyboard flow.
   - Visible focus, hover, pressed, disabled, loading, empty, and error states.
   - Text contrast, line length, readable hierarchy, and no overflow.
   - Responsive layout, touch target size, safe areas, and no horizontal scroll.
   - Form labels, inline errors, helper text, and clear destructive confirmations.
   - Media dimensions, lazy loading, reduced motion, and layout-shift prevention.
5. Report findings first, ordered by severity.

## Output

Use this format for findings:

```text
P1 file:line - Problem. Impact. Suggested fix.
```

Then add:

- `Clean Areas Checked`: brief list of important checks that passed.
- `Skipped Checks`: anything unavailable, such as a dev server, browser, auth state, or missing viewport.

For implementation follow-up, route through `klimkit-implement` so TDD, verification, reflection, and final review stay intact.
