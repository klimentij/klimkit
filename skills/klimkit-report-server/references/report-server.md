# Report Server Notes

Klimkit reports are static HTML files under `.klimkit/<operator>/reports/`. Legacy flat `.klimkit/reports/` folders may be served as historical context, but new skills-first proof reports should be operator-scoped. Serving is optional unless the task requires a shareable report URL.

## Verification Order

1. Confirm the report HTML exists.
2. Confirm linked media exists and stays inside the report directory.
3. Check the local server URL if a Klimkit server is running.
4. Check Tailscale status if a tailnet URL is needed.
5. Fetch the final `/reports/` URL before claiming it works.

## Common Commands

Use commands that are available in the target environment:

```bash
find .klimkit -path '.klimkit/*/reports/*.html' -print -o -path '.klimkit/*/reports/*/*.html' -print
tailscale status
tailscale serve status
```

Use `scripts/serve_reports.py` as the skill-owned reference server when no project-specific server exists.

## Boundaries

- Skills can guide report creation without starting services.
- If a persistent server is needed, copy or adapt the reference script into the target repository with the user's approval.
- Do not expose private tailnet URLs in public artifacts unless the user explicitly wants that.
