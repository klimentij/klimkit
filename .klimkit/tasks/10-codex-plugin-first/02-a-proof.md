# Codex Plugin First Proof

## Changed Files

- `.agents/plugins/marketplace.json`
- `plugins/klimkit/.codex-plugin/plugin.json`
- `plugins/klimkit/README.md`
- `plugins/klimkit/skills/**`
- `plugins/klimkit/reference/**`
- `README.md`
- `tests/test_codex_pack_validation.py`
- `tests/test_docs_static.py`
- `.klimkit/tasks/10-codex-plugin-first/01-a-acceptance-checklist.md`

## Implementation Notes

- Created the public repo-local Codex plugin at `plugins/klimkit/` with manifest name `klimkit`.
- Created the repo marketplace at `.agents/plugins/marketplace.json` with source path `./plugins/klimkit`, `AVAILABLE`, `ON_INSTALL`, and `Productivity`.
- Copied installable skills from `packs/codex/skills/` into the plugin and added `skills/klimkit-workflow/SKILL.md` as the plugin-first workflow entry point.
- Copied public-safe harness references into `plugins/klimkit/reference/`: AGENTS guidance, subagent TOML, config defaults, and Stop hook reference.
- Left machine-level activation of `AGENTS.md`, `config.toml`, subagent TOML, and Stop hooks in the repo-managed `kk apply` path because plugin installation loads skills but does not rewrite home-level Codex config.
- Updated README so the default path is the Codex app plus the Klimkit plugin, with Switchboard/fork/`kk apply` positioned as advanced repo-managed options.
- README keeps autosync and Telegram documented as disabled by default.

## Command Evidence

- `codex plugin marketplace add --help` confirms `codex plugin marketplace add <SOURCE>` and `--ref <REF>`.
- `codex plugin marketplace upgrade --help` confirms `codex plugin marketplace upgrade [MARKETPLACE_NAME]`.
- `codex plugin add --help` confirms `codex plugin add <PLUGIN[@MARKETPLACE]>`.

README commands:

```bash
codex plugin marketplace add klimentij/klimkit --ref main
codex plugin add klimkit@klimkit
codex plugin marketplace upgrade klimkit
codex plugin add klimkit@klimkit
```

## Verification

```text
python3 /home/ubuntu/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py /home/ubuntu/klimkit/plugins/klimkit
Plugin validation passed: /home/ubuntu/klimkit/plugins/klimkit
```

```text
uv run python -m unittest tests.test_codex_pack_validation tests.test_docs_static -q
Ran 19 tests in 0.029s
OK
```

```text
uv run python -m unittest discover -s tests -q
Ran 181 tests in 11.945s
OK (skipped=1)
```

```text
git diff --check
passed with no output
```

## Skipped Checks

- Live plugin installation into the current `~/.codex` was skipped to avoid mutating the operator's live Codex marketplace/config state. Static plugin validation, CLI help checks, and repository tests cover manifest shape, marketplace shape, install/upgrade command syntax, docs text, and default-off settings.
- UI/browser proof report was not applicable: this task changed packaging, documentation, and static tests, not a browser UI surface.

## Remaining Risk

- Codex plugin updates are pull-based. Users should run `codex plugin marketplace upgrade klimkit` and rerun `codex plugin add klimkit@klimkit` when they want the newest cached plugin copy.

## Reflection

- Appended `.klimkit/reflection.md` session `2026-05-27T05:19:03Z`.
- Reconsideration outcome: keep the handoff precise that `v0.1.14` was the autosync-default-off main release, the plugin-first work remains on `codex-plugin-first`, and live plugin installation was intentionally skipped to avoid mutating the operator's Codex config.
