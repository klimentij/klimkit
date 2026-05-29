# Artifact Workflow

Use this reference when a task needs concrete Klimkit evidence paths.

## Solo Layout

Klimkit's default evidence layout is flat and project-local:

- `.klimkit/memory.md` for durable preferences, corrections, and process rules.
- `.klimkit/log.md` for timestamped action history.
- `.klimkit/reflection.md` for append-only cross-task synthesis.
- `.klimkit/tasks/<feature>/` for checklists, plans, proof notes, screenshots, and review records.
- `.klimkit/reports/<task>/report.html` for browser/UI proof reports.

Machine-local config, runtime DBs, backups, logs, and secrets stay under ignored `.klimkit/local/`, `.klimkit/state/`, `.klimkit/backups/`, and `.klimkit/logs/`.

## Team Layout

Use team layout only when the repo or user explicitly configures it. Team workflow writes under `.klimkit/<operator>/` and treats other operators' folders as attributed read-only context.

When a repo has useful solo artifacts and is switching to team workflow, migrate deliberately with `kk migrate team-workflow --dry-run` before writing new team-scoped artifacts.

## Proof Expectations

For meaningful implementation work, write proof that names changed files, commands run, important outputs, skipped or unavailable checks, and remaining risks. For UI work, include screenshot/video evidence through the report system rather than relying only on text claims.
