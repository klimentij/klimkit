# Plugin Skill Cleanup Proof

## Changed Files

- `plugins/klimkit/skills/*/SKILL.md`
- `plugins/klimkit/skills/*/agents/openai.yaml`
- `plugins/klimkit/skills/klimkit-workflow/references/artifact-workflow.md`
- `plugins/klimkit/skills/klimkit-workflow/references/repo-managed-mode.md`
- `plugins/klimkit/.codex-plugin/plugin.json`
- `plugins/klimkit/README.md`
- `README.md`
- `tests/test_codex_pack_validation.py`
- `.klimkit/tasks/11-plugin-skill-cleanup/01-a-acceptance-checklist.md`
- `.klimkit/tasks/11-plugin-skill-cleanup/02-a-proof.md`
- `.klimkit/log.md`

## Implementation Notes

- Reworked plugin skill frontmatter so each installable skill has only `name` and `description`.
- Moved invocation guidance into descriptions and gave each skill body a human-facing title.
- Added `agents/openai.yaml` for `frontend-design`, `grill-me`, `harness-tuning`, and `klimkit-workflow`; updated `agent-browser` metadata.
- Replaced the plugin root `reference/` harness copy with skill-owned references under `skills/klimkit-workflow/references/`.
- Removed copied root harness files from the installable plugin package: `reference/AGENTS.md`, subagent TOML, `reference/config.toml`, and `reference/hooks/stop-notify.sh`.
- Updated plugin docs and README language to describe skill-owned references and the boundary between plugin installation and repo-managed `kk apply`.
- Added tests that enforce skill frontmatter shape, proper skill titles, required OpenAI UI metadata, absence of root reference packaging, and public-safe plugin content.

## Validation

```text
for skill in plugins/klimkit/skills/*; do python3 <codex-home>/skills/.system/skill-creator/scripts/quick_validate.py "$skill"; done
Skill is valid!
Skill is valid!
Skill is valid!
Skill is valid!
Skill is valid!
```

```text
python3 <codex-home>/skills/.system/plugin-creator/scripts/validate_plugin.py <repo-root>/plugins/klimkit
Plugin validation passed: <repo-root>/plugins/klimkit
```

```text
uv run python -m unittest tests.test_codex_pack_validation -q
Ran 17 tests in 0.022s
OK
```

```text
uv run python -m unittest tests.test_docs_static -q
Ran 4 tests in 0.006s
OK
```

```text
uv run python -m unittest tests.test_klimkit_install -q
Ran 45 tests in 0.170s
OK
```

```text
uv run python -m unittest discover -q
Ran 0 tests in 0.000s
OK
```

The root discovery command does not discover this repository's test layout, so the meaningful full-suite command was also run:

```text
uv run python -m unittest discover -s tests -q
Ran 183 tests in 11.840s
OK (skipped=1)
```

```text
git diff --check
passed with no output
```

## Skipped Or Not Applicable

- UI proof report was not applicable because this task changed plugin packaging, docs, and tests, not a browser UI.
- Live Codex plugin cache install/upgrade proof was not rerun because this branch did not change the plugin manifest version, marketplace source, or installed VM plugin cache. No claim is made that these branch changes are live in `~/.codex/plugins/cache`.
- Release proof is not applicable yet because this branch has not landed on `main`.

## Remaining Risk

- The plugin package version remains `0.1.15` on this branch. The next plugin-content release should bump the manifest version deliberately and rerun live cache upgrade proof before claiming installed users can refresh to the new package.
