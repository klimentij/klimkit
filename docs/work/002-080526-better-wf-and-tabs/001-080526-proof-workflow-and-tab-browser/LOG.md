# LOG — 001-080526-proof-workflow-and-tab-browser

> Migrated 2026-07-15 from `.klimkit/tasks/02-better-wf-and-tabs/`; predates the phase
> convention — authorship below is recovered from the old `-h-` (human) / `-a-` (agent)
> file names.

- **2026-05-08** (human) [001-in.md](001-in.md) — voice-transcribed ask: checklister must require screenshots + `agent-browser`-recorded video + a minimal self-contained HTML report for every UI QA task, reviewed by final-reviewer; plus drag-and-drop tab reordering and a "Tab Browser" special tab (`Control+Option+0`).
- **2026-05-08** (agent) [002-plan.md](002-plan.md) — evaluated PDF vs. sibling-media-folder vs. self-contained HTML for reports; approved Git-tracked HTML under `.klimkit/reports/` with ignored media, served via a combined `/reports/` index, with Tailscale report URLs required in handoffs.
- **2026-05-08** (agent) [003-acceptance-checklist.md](003-acceptance-checklist.md) — checklist covering the report-workflow decision, `checklister`/`final-reviewer` TOML requirements, and Switchboard Tab Browser drag/drop behavior.
- **2026-05-08** (agent) [004-implementation-proof.md](004-implementation-proof.md) — proof: pack workflow + `/reports/` daemon routes with byte-range video serving shipped; Tab Browser rework with keyboard cycling and drag/drop; 142 tests passing; live Tailscale report URL verified.
- **2026-05-08** (agent) [005-proof-report.html](005-proof-report.html) — the resulting self-contained QA proof report itself: embedded before/after screenshots and two MP4s (129s tab-browser flow, 6s top-tab click) demonstrating the shipped Tab Browser behavior.
- **2026-07-15** (agent) [006-durable-rulings.md](006-durable-rulings.md) — migrated 2 durable rulings from the retired `docs/agents/memory.md` during `docs/agents` dissolution.
