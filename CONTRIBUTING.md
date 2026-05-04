# Contributing

Use the repo's existing stdlib test harness.

```bash
uv run python -m unittest discover -s tests -q
uv run coverage run -m unittest discover -s tests -q
uv run coverage report -m
```

Optional Codex smoke validation is skipped unless explicitly enabled:

```bash
KLIMKIT_RUN_CODEX_SMOKE=1 uv run python -m unittest tests.test_codex_smoke -q
```

For machine-affecting changes, inspect `kk preview` before applying. Keep `.klimkit/tasks/`, `.klimkit/memory.md`, and `.klimkit/log.md` trackable when they explain a task, plan, proof, or decision. Do not commit ignored `.klimkit/local/`, `.klimkit/state/`, `.klimkit/backups/`, or `.klimkit/logs/` content unless a change explicitly needs a sanitized fixture.
