# Contributing

Keep changes small, previewable, and easy to verify. For non-trivial work, add task notes under the configured Klimkit artifact workflow: `.klimkit/tasks/<nn-feature-slug>/` in solo workflow, or `.klimkit/<human_name-as-folder>/tasks/<nn-feature-slug>/` in team workflow. Use `-h-` for human-authored notes and `-a-` for agent-authored notes.

In team workflow, the active operator's folder is derived from `human_name` and is the writable workspace. Other `.klimkit/<operator>/` folders are readable team context; preserve source operator attribution when using their memories, logs, reflections, or task notes, and do not edit another operator's artifacts unless the task explicitly requires it.

Use the repo's existing stdlib test harness:

```bash
uv run python -m unittest discover -s tests -q
uv run coverage run -m unittest discover -s tests -q
uv run coverage report -m
```

Optional Codex smoke validation is skipped unless explicitly enabled:

```bash
KLIMKIT_RUN_CODEX_SMOKE=1 uv run python -m unittest tests.test_codex_smoke -q
```

For machine-affecting changes, inspect `kk preview` before applying. Keep task notes, `memory.md`, `log.md`, `reflection.md`, and Git-trackable report HTML trackable in the configured artifact workflow when they explain a task, plan, proof, or decision. Do not commit ignored `.klimkit/local/`, `.klimkit/state/`, `.klimkit/backups/`, `.klimkit/logs/`, or large report media unless a change explicitly needs a sanitized fixture.

When moving a project from solo to team workflow, set `[operator] workflow = "team"` and `human_name`, then run from that project checkout:

```bash
kk migrate team-workflow --dry-run
kk migrate team-workflow
```

From another directory, use `kk migrate team-workflow --repo /path/to/project --human-name <name> --dry-run`, then rerun without `--dry-run`.

For Codex harness changes, edit `packs/codex/` in this repo, then run:

```bash
uv run python -m unittest tests.test_codex_pack_validation -q
kk apply
```

Do not edit generated `~/.codex/` files directly; Klimkit overwrites those projections.
