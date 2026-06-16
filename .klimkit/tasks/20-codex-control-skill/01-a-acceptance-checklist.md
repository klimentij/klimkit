# Acceptance Checklist

- [x] Repository is synced from `origin/main` before importing the skill.
- [x] The linked `slf-research` `codex-control` skill is imported under root `skills/` with the Klimkit prefix.
- [x] The imported skill remains agent-neutral: instructions do not require Claude-specific paths or tooling.
- [x] Public inventory files list the new skill consistently (`README.md`, `skills.sh.json`, and tests).
- [x] Skill metadata validates and the root skills test suite passes.
- [x] Intended commit scope is limited to the skill, inventory, test, and task-note changes; push is verified after commit.

## Scope Boundaries

- Do not stage unrelated pre-existing `.klimkit/log.md`, `.klimkit/reflection.md`, or pending task directories.
- Do not change deprecated runtime or plugin code.

## Verification Evidence

- `git pull --ff-only origin main`: already up to date.
- `python3 /home/ubuntu/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/klimkit-codex-control`: `Skill is valid!`
- Python helper syntax check with `compile(...)`: passed for `codex_ws.py` and `find_active.py`.
- `python3 -m unittest discover -s tests -q`: ran 10 tests, OK.
- `npx skills add ./ --list`: found 19 skills including `klimkit-codex-control`.

## Security Review

No actionable findings after adding operational safety guidance. Clean areas checked: local unix socket remains the preferred path, TCP auth examples prefer `--token-file`, token-in-argv risk is called out, and session/history outputs are marked sensitive. Skipped checks: no live Codex app-server probing because the task is packaging and documentation, not runtime operation. Residual risk: the bundled script can still connect to any `ws://` endpoint the operator supplies, so operators must only target servers they control.

## Reflection

### 2026-06-16T09:15:39Z

Observations: Importing third-party skills into Klimkit requires updating both public inventory and tests; `npx skills add ./ --list` is the fastest end-to-end package check.

Derived Pattern: For cross-agent skill imports, normalize install paths away from source-agent folders and add explicit safety notes when helper scripts expose local session data or control surfaces.

Insight: The repo test contract favors single-line frontmatter descriptions for non-imported Klimkit-owned skills, even when the upstream skill used folded YAML.

Next Probe: Consider a small import checklist or script that renames frontmatter, creates `agents/openai.yaml`, updates `skills.sh.json`, and runs the root package validators in one repeatable path.
