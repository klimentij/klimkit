# Klimkit Artifact Workflow

Use these paths unless the repository has more specific instructions.

## Evidence Files

Klimkit's skills-first default is operator-scoped. Ask for the operator name first, derive a filesystem-safe `<operator>` folder, and write all mutable project evidence there:

- `.klimkit/<operator>/config.toml`: project-local operator settings.
- `.klimkit/<operator>/memory.md`: durable preferences, corrections, and process rules.
- `.klimkit/<operator>/log.md`: timestamped action history.
- `.klimkit/<operator>/reflection.md`: append-only cross-task synthesis.
- `.klimkit/<operator>/tasks/<feature>/`: task checklists, plans, proof, screenshots, review notes, and handoff records.
- `.klimkit/<operator>/reports/<task>/`: HTML proof reports and local media assets.

Legacy flat paths such as `.klimkit/tasks/` and `.klimkit/reports/` may be read as historical context, but new skills-first setup should not create them by default.

## Templates

Memory:

```markdown
# Project Memory

Durable preferences, corrections, and process rules.

## Memories
```

Log:

```markdown
# Project Log

Timestamped audit trail. Entries describe actions, not preferences.

## Log
```

Reflection:

```markdown
# Project Reflection

Append-only timestamped cross-task reflection log.

## Reflections
```

Config:

```toml
[operator]
name = "Klim"
folder = "Klim"

[workflow]
artifact_layout = "operator-scoped"

[agent]
personality_name = "Steady Operator"
personality_description = "Direct, careful, evidence-first, and conservative with scope."

[reports]
enabled = true
host = "127.0.0.1"
port = 8765
tailnet_url = ""
```

## Local State

Do not commit machine-local runtime state, secrets, tokens, logs, or backups. Keep those under ignored local paths such as `.klimkit/local/`, `.klimkit/state/`, `.klimkit/backups/`, and `.klimkit/logs/`.
