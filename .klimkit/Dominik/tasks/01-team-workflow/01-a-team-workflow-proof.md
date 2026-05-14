# Team Workflow Proof

Task: introduce a first-class team artifact workflow while keeping `.klimkit` as a project evidence layer.

## Acceptance Checklist

- [x] Keep solo workflow as the default so existing installs continue writing flat `.klimkit` artifacts.
- [x] Add explicit team workflow config through `[operator] workflow = "team"` while deriving the team folder from `human_name`.
- [x] Avoid introducing a separate human-edited `artifact_owner` variable; team folder names come from sanitized `human_name`.
- [x] Teach projected Codex guidance and subagents to read shared project/operator context but write only under the current operator folder.
- [x] Explain that each projected harness works for one active human/operator, either solo or as part of a team, with other operators' artifacts available as attributed read-only team context.
- [x] Provide a migration path for existing flat `.klimkit` evidence.
- [x] Support project-local migration commands from inside any repo with `.klimkit/`, plus explicit `--repo` and `--human-name` flags for scripted migrations.
- [x] Instruct team-mode agents to treat flat solo-style `.klimkit` artifacts as an unmigrated project and migrate them to the current operator when dry-run output is clean.
- [x] Do not migrate or track local config, runtime state, backups, logs, secrets, or generated service state.
- [x] Demonstrate the project evidence layout in this repository with existing artifacts under `.klimkit/Klim/` and this contribution under `.klimkit/Dominik/`.

## Migration Evidence

The upstream PR branch used the new CLI against this repository's project `.klimkit` evidence.

Local ignored config was created with:

```bash
uv run kk setup --skip-services
```

The local `.klimkit/local/klimkit.toml` was set to:

```toml
[operator]
human_name = "Klim"
workflow = "solo"
```

The dry run showed the intended moves:

```text
uv run kk migrate team-workflow --dry-run

would move .klimkit/memory.md -> .klimkit/Klim/memory.md
would move .klimkit/log.md -> .klimkit/Klim/log.md
would move .klimkit/reflection.md -> .klimkit/Klim/reflection.md
would move .klimkit/tasks -> .klimkit/Klim/tasks
would move .klimkit/reports -> .klimkit/Klim/reports
```

The real migration then succeeded:

```text
uv run kk migrate team-workflow

moved .klimkit/memory.md -> .klimkit/Klim/memory.md
moved .klimkit/log.md -> .klimkit/Klim/log.md
moved .klimkit/reflection.md -> .klimkit/Klim/reflection.md
moved .klimkit/tasks -> .klimkit/Klim/tasks
moved .klimkit/reports -> .klimkit/Klim/reports
```

This contribution's evidence was then added separately under:

```text
.klimkit/Dominik/
  memory.md
  log.md
  reflection.md
  tasks/01-team-workflow/01-a-team-workflow-proof.md
```

## Operator Context Model

The projected harness now distinguishes the active operator from the wider team:

- Solo workflow means the active operator writes the flat project `.klimkit` artifacts.
- Team workflow means the active operator writes under `.klimkit/<human_name-as-folder>/`.
- The folder name is derived from `human_name`; there is no separate `artifact_owner` setting in the generated config.
- Other `.klimkit/<operator>/` folders are readable team knowledge, not writable current-operator state.
- New memories, logs, reflections, task notes, and reports stay attributed to the active operator; when another operator's artifact shapes the work, the source operator or path should remain visible.

## Project Migration UX

The command supports both project-local and explicit migrations:

```bash
cd /path/to/project
kk migrate team-workflow --dry-run
kk migrate team-workflow
```

When the current checkout contains `.klimkit/`, the no-flag form migrates that project. From another directory, or without a local Klimkit config, use:

```bash
kk migrate team-workflow --repo /path/to/project --human-name Dominik --dry-run
kk migrate team-workflow --repo /path/to/project --human-name Dominik
```

Explicit project migrations do not rewrite the active harness config; they only move that project's trackable `.klimkit` evidence.

## Agent Auto-Migration Rule

When the projected harness is in team workflow and an agent is about to create memory, log, reflection, task, or report artifacts, flat `.klimkit` files such as `memory.md`, `log.md`, `reflection.md`, `tasks/`, or `reports/` mean the project is still in solo layout.

The harness now instructs the agent to run:

```bash
kk migrate team-workflow --dry-run
```

If the dry run only moves flat artifacts into the current operator root and has no blocked targets, the agent should run:

```bash
kk migrate team-workflow
```

Those migrated flat artifacts are attributed to the current operator by default. If targets already exist or ownership is ambiguous, the agent must stop and ask instead of merging histories.

## Test Evidence

- `uv run python -m unittest tests.test_klimkit_install tests.test_klimkit_cli tests.test_switchboard tests.test_codex_pack_validation tests.test_docs_static -q` passed locally: 116 tests.
- `uv run python -m unittest discover -s tests -q` passed locally: 153 tests, 1 existing optional skip.
- `git diff --check` passed locally.

## Scope Boundary

This proof is project evidence. It is not a default settings change and does not require committing `.klimkit/local/`, `.klimkit/state/`, `.klimkit/backups/`, or `.klimkit/logs/`.
