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

## Publish, Merge, Release, And Live Plugin Proof

- Branch baseline commit: `cb59fc521fd3458162d911d7f8dc02a188d65a2c` (`Add Klimkit Codex plugin`) was pushed to `origin/codex-plugin-first`.
- Live install baseline: `codex plugin marketplace add klimentij/klimkit --ref codex-plugin-first` added marketplace `klimkit`, then `codex plugin add klimkit@klimkit` installed cache root `/home/ubuntu/.codex/plugins/cache/klimkit/klimkit/0.1.14`.
- Upgrade commit: `dbd4e1aac03734a49d0204522ba398193633b887` (`Bump Klimkit plugin update guidance`) bumped plugin manifest version from `0.1.14` to `0.1.15` and added this `klimkit-workflow` skill line: `For Git-backed plugin updates, refresh the marketplace snapshot and re-add the plugin so the local cache moves to the new version.`
- Upgrade proof: `codex plugin marketplace upgrade klimkit` refreshed the Git marketplace, and `codex plugin add klimkit@klimkit` installed cache root `/home/ubuntu/.codex/plugins/cache/klimkit/klimkit/0.1.15`.
- Home/cache proof: `codex plugin list --marketplace klimkit` reported `klimkit@klimkit` as `installed, enabled` at version `0.1.15`, and `/home/ubuntu/.codex/plugins/cache/klimkit/klimkit/0.1.15/skills/klimkit-workflow/SKILL.md` contains the modified skill line.
- PR proof: [PR #2](https://github.com/klimentij/klimkit/pull/2) passed GitHub Actions and was squash-merged into `main` at `f8b8700c7a325daed15a2cbda69ce2f58407d361`.
- Release proof: [v0.1.15](https://github.com/klimentij/klimkit/releases/tag/v0.1.15) was created as latest for `main`; `origin/main` and tag `v0.1.15` both pointed at `f8b8700c7a325daed15a2cbda69ce2f58407d361`.
- Post-merge VM state: the local Klimkit marketplace was repointed from `codex-plugin-first` to released `main`; `~/.codex/config.toml` records `source = "https://github.com/klimentij/klimkit.git"`, `ref = "main"`, and `last_revision = "f8b8700c7a325daed15a2cbda69ce2f58407d361"`.
- Publication proof location: the `v0.1.15` GitHub release notes and PR #2 comment both include the live install/upgrade proof so the published artifact carries the runtime evidence.

## Skipped Checks

- UI/browser proof report was not applicable: this task changed packaging, documentation, and static tests, not a browser UI surface.

## Remaining Risk

- Codex plugin updates are pull-based. Users should run `codex plugin marketplace upgrade klimkit` and rerun `codex plugin add klimkit@klimkit` when they want the newest cached plugin copy.

## Reflection

- Appended `.klimkit/reflection.md` session `2026-05-27T05:19:03Z`.
- Appended a fresh post-publish/live-plugin reflection session after the PR merge, release, install, upgrade, and cache verification.
