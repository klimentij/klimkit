# Deprecated Klimkit Runtime

Klimkit is moving to a skills-first distribution model. New work should live in root `skills/` folders and be installed or updated with the Vercel Skills CLI.

The legacy runtime code is still in its original source paths for compatibility during the migration:

- `deprecated/runtime/install.sh`
- `deprecated/runtime/kk`
- `deprecated/runtime/klimkit`
- `deprecated/runtime/src/klimkit/apps/switchboard/`
- `deprecated/runtime/src/klimkit/tools/switchboard_agent/`
- `deprecated/runtime/src/klimkit/tools/supervisor/`
- `deprecated/runtime/packs/codex/`
- `deprecated/runtime/templates/`
- `deprecated/runtime/examples/create-worktree.sh`
- `deprecated/codex-plugin/plugins/klimkit/`
- `deprecated/codex-plugin/agents-marketplace/`
- repo-managed setup, apply, pull, and sync flows

Do not build new workflows against these paths. When a useful runtime behavior is kept, migrate it into the owning skill as a `scripts/`, `references/`, or `assets/` resource.
