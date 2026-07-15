# LOG — 002-150726-hosted-report-publishing

- **2026-07-15 ~01:35** (human) — Klim directed making Claude Code Artifacts and Codex
  Sites the default deployment path for all human-facing HTML in `docs/work/`, always
  authentication-protected: [001-klim-directive.md](001-klim-directive.md).
- **2026-07-15 ~01:40** (agent) — Web-researched both features (official Claude Code
  artifacts doc, Codex Sites doc): both are private/authenticated by default, republish
  to a stable URL; findings and the applied ruling in
  [002-feature-research.md](002-feature-research.md).
- **2026-07-15 ~01:45** (agent) — Applied the default: new "HTML reports and explainers"
  section in `AGENTS.md`; "Viewing for the human driver" paragraph in
  `docs/work/README.md`; `klimkit-walkthrough` deploys via Artifact/Sites by default
  with `klimkit-report-server` demoted to fallback (SKILL + references updated); publish
  rules added to both `artifact-workflow.md` references.
