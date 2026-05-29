# Walkthrough Report Notes

Use this structure for first-pass static walkthrough reports.

## HTML Sections

- Title, timestamp, and source task, PR, or request.
- Environment and URLs checked.
- Summary verdict.
- Step-by-step walkthrough.
- Evidence media as full-width sections.
- Validation checklist.
- Redaction/privacy note.
- Remaining risk.

## Evidence Rules

- Use fresh screenshots for visual state.
- Use video only when timing, animation, drag/drop, or multi-step interaction matters.
- Prefer relative media paths inside the report directory.
- Verify every referenced asset exists.
- Keep sensitive media ignored and summarize it safely if it cannot be public.

## Handoff

Include both the local `.klimkit/<operator>/reports/<slug>/report.html` path and any verified served URL. If Tailscale serving is unavailable, say what was checked and what is missing.
