# LOG — 021-150726-docs-work-adoption

Adoption of the docs/work work-journal convention (from conversation-be PR #3680,
sanitized to be project-generic) as Klimkit's default evidence layout, replacing the
`.klimkit/` folder, including migration of this repo's own `.klimkit` history. This
folder is the first Klimkit instance journaled under the new convention.

- **07-15** [001-150726-adoption-and-migration](001-150726-adoption-and-migration/) —
  Klim's directive; convention copied and sanitized; 17 legacy task folders + reports +
  agent state migrated; skills, docs, tests, and smoke test rewritten around
  `docs/work/` + `docs/agents/`; shipped as one PR.
- **07-15** [002-150726-hosted-report-publishing](002-150726-hosted-report-publishing/) —
  Klim's follow-up: human-facing HTML in `docs/work/` deploys by default through the
  harness's native, auth-protected hosting (Claude Code Artifacts / Codex Sites);
  researched both features, updated `AGENTS.md`, the convention README, walkthrough and
  report-server skills, and both artifact-workflow references.
