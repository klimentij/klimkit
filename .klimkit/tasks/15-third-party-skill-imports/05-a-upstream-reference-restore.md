# Upstream Reference Restore

## Correction

The imported skills should not lose their upstream instruction surfaces when Klimkit rewrites the active `SKILL.md` entrypoints. The correct layout is:

- Klimkit-facing `SKILL.md` stays concise and workflow-oriented.
- Original upstream `SKILL.md` is preserved as `references/upstream-skill.md`.
- Other upstream references, scripts, assets, and data remain bundled where the imported skill shipped them.
- Central attribution remains in `THIRD_PARTY_NOTICES.md`; per-skill `references/upstream.md` metadata files stay removed because they were packaging noise, not usable instructions.

## Restored Files

- `skills/klimkit-agent-browser/references/upstream-skill.md`
- `skills/klimkit-agent-browser/references/upstream-core.md`
- `skills/klimkit-agent-browser/references/upstream-electron.md`
- `skills/klimkit-agent-browser/references/upstream-slack.md`
- `skills/klimkit-agent-browser/references/upstream-dogfood.md`
- `skills/klimkit-agent-browser/references/upstream-vercel-sandbox.md`
- `skills/klimkit-agent-browser/references/upstream-agentcore.md`
- `skills/klimkit-web-design-guidelines/references/upstream-skill.md`
- `skills/klimkit-ui-ux-pro-max/references/upstream-skill.md`
- `skills/klimkit-improve-codebase-architecture/references/upstream-skill.md`
- `skills/klimkit-impeccable/references/upstream-skill.md`
- `skills/klimkit-antigravity-security-auditor/references/upstream-skill.md`
