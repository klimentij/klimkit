# Generic Best-Practice Release Proof

## Scope

Release the reviewed generic best-practice harness update as the next latest
Klimkit release.

## Changed Areas

- `packs/codex/AGENTS.md`
- `packs/codex/agents/checklister.toml`
- `packs/codex/agents/code-explorer.toml`
- `packs/codex/agents/code-reviewer.toml`
- `packs/codex/agents/debugger.toml`
- `packs/codex/agents/final-reviewer.toml`
- `packs/codex/agents/test-writer.toml`
- `packs/codex/skills/harness-tuning/SKILL.md`
- `tests/test_codex_pack_validation.py`
- `README.md`
- `pyproject.toml`
- `uv.lock`
- `.klimkit/log.md`
- `.klimkit/tasks/04-generic-best-practice-up/01-h-in.md`
- `.klimkit/tasks/04-generic-best-practice-up/02-a.md`
- `.klimkit/tasks/04-generic-best-practice-up/image.png`
- `.klimkit/tasks/04-generic-best-practice-up/03-a-release-proof.md`

## Validation

- `git diff --check` -> passed.
- `uv run python -m unittest tests.test_codex_pack_validation -q` -> 10 tests OK.
- `uv run python -m unittest tests.test_klimkit_install tests.test_harness_registry -q` -> 32 tests OK.
- `uv run python -m unittest discover -s tests -q` -> 145 tests OK, 1 skipped.

## Projection

- `kk preview` -> 39 planned actions.
- `XDG_RUNTIME_DIR=/run/user/$(id -u) DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$(id -u)/bus kk apply` -> succeeded.
- `kk apply` updated 9 live projected Codex files, reloaded the systemd user manager, enabled and restarted `klimkit.service`, sent a Telegram apply summary, and printed:
  - Switchboard serve: `https://odev.tail11c448.ts.net/switchboard/`
  - Proof reports: `https://odev.tail11c448.ts.net/reports/`
- Projection check found the new best-practice rules in `/home/ubuntu/.codex/AGENTS.md`, role subagents, and `harness-tuning`.
- Service check with the same DBus environment -> `klimkit.service` is enabled and active.

## Reflection

- Reflection entry: `.klimkit/reflection.md`, `2026-05-14T12:07:00Z`.
- Reconsideration result: no extra pack edit was needed after reflection; the entry confirms the implementation pattern of distributing external guidance to enforceable pack layers and tests.

## Release

- Target tag: `v0.1.6`
- Release URL: `https://github.com/klimentij/klimkit/releases/tag/v0.1.6`
- Published: `2026-05-14T12:08:45Z`
- Latest verification: `gh release list --limit 4` showed `Klimkit v0.1.6 - generic agent best practices` with the `Latest` marker.
- Final tag target: verified in the final handoff after this proof note commit exists.
