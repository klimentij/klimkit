# Klimkit Artifact Workflow

Use these paths unless the repository has more specific instructions.

## Evidence Files

Klimkit's skills-first default is operator-scoped:

- `.klimkit/<operator>/config.toml`: project-local operator settings.
- `.klimkit/<operator>/memory.md`: durable preferences, corrections, and process rules.
- `.klimkit/<operator>/log.md`: timestamped action history.
- `.klimkit/<operator>/reflection.md`: append-only cross-task synthesis.
- `.klimkit/<operator>/tasks/<feature>/`: task checklists, plans, proof, screenshots, review notes, and handoff records.
- `.klimkit/<operator>/reports/<task>/`: HTML proof reports and local media assets.

When the operator folder is unknown, ask the user or use `klimkit-setup`. Legacy flat `.klimkit/tasks/` and `.klimkit/reports/` paths are readable historical context, not the default write target for new skill-based work.

## Task Notes

- Human-authored notes use `-h-`.
- Agent-authored notes use `-a-`.
- Keep implementation proof close to the task folder that drove the work.
- Name changed files, checks run, important outputs, skipped checks, and remaining risk.

## Local State

Do not commit machine-local runtime state, secrets, tokens, logs, or backups. Keep those under ignored local paths such as `.klimkit/local/`, `.klimkit/state/`, `.klimkit/backups/`, and `.klimkit/logs/`.

## Reports

For UI or workflow proof, create tracked HTML under `.klimkit/<operator>/reports/<task>/`. Keep large screenshots and videos ignored unless the user explicitly wants a public proof gallery. Render media full-width so it can be inspected without opening thumbnails.
