# Team Workflow Fixes Implementation Proof

Task: harden Dominik's PR #1 team artifact workflow while keeping Klimkit solo-first.

## What Changed

- Hardened team migration validation so sanitized operator folder names cannot collide with flat `.klimkit` artifact names or reserved runtime directories.
- Added migration preflight target-collision, overlap, trailing-name, and artifact-shape checks so invalid, malformed, partially migrated, or self-overlapping plans fail before any artifact moves.
- Escaped rendered config paths with JSON/TOML-safe string serialization so unusual checkout paths cannot inject TOML sections.
- Changed dry-run follow-up output to print a copyable `kk migrate team-workflow` command that preserves explicit and implicit `--config`, `--repo`, and `--human-name` context with shell quoting.
- Fixed explicit `--repo` migration semantics so passing the configured repo still updates that config to `workflow = "team"` after safe migration.
- Hardened Switchboard report discovery and serving so only `.klimkit/reports/` and valid `.klimkit/<operator>/reports/` sources are accepted.
- Rejected reserved pseudo-owners such as `@tasks`, hidden/invalid operator names, symlinked `.klimkit` roots, symlinked operator roots, and symlinked report roots that escape the repo `.klimkit` tree.
- Skipped duplicate configured report roots with a warning instead of indexing duplicate report rows.
- Replaced the stale hard-coded `Human` in the projected Codex pack team-migration guidance with `__HUMAN_NAME__`.
- Applied the Codex projection so live `~/.codex/AGENTS.md` now says `ask Klim` in both migration-conflict prompts.
- Updated README wording to keep `solo` as the default solo-builder workflow and describe team workflow as light opt-in support.
- Added SECURITY.md wording for the report-serving boundary and symlink policy.
- Flattened this repository's committed proof evidence back to the solo `.klimkit/` layout and removed contributor operator-scoped `.klimkit` artifacts from the public repo.
- Recorded the durable preference that this repo remains solo-flat while team workflow stays optional product functionality.

## Changed Files

- `src/klimkit/install.py`
- `src/klimkit/cli.py`
- `src/klimkit/apps/switchboard/daemon.py`
- `packs/codex/AGENTS.md`
- `README.md`
- `SECURITY.md`
- `tests/test_klimkit_install.py`
- `tests/test_klimkit_cli.py`
- `tests/test_switchboard.py`
- `tests/test_codex_pack_validation.py`
- `tests/test_docs_static.py`
- `.klimkit/memory.md`
- `.klimkit/log.md`
- `.klimkit/reflection.md`
- `.klimkit/tasks/05-team-workflow-fixes/01-a-acceptance-checklist.md`
- `.klimkit/tasks/05-team-workflow-fixes/02-a-implementation-plan.md`
- `.klimkit/tasks/05-team-workflow-fixes/03-a-implementation-proof.md`
- `.klimkit/reports/05-team-workflow-fixes/report.html`

## Repo Evidence Layout

Klim clarified that this repository itself should remain solo. The team workflow feature still supports operator-scoped artifacts for opt-in team projects, but this repo's committed evidence now stays flat:

```text
git ls-files .klimkit/Klim .klimkit/Dominik
passed with no output

git ls-files .klimkit | cut -d/ -f1-3 | sort -u | sed -n '1,12p'
.klimkit/reports
.klimkit/reports/02-better-wf-and-tabs
.klimkit/reports/05-team-workflow-fixes
.klimkit/tasks
.klimkit/tasks/01-tui-ux-multi-harness-more
.klimkit/tasks/02-better-wf-and-tabs
.klimkit/tasks/03-reflection-workflow
.klimkit/tasks/04-generic-best-practice-up
.klimkit/tasks/05-team-workflow-fixes
```

## Automated Verification

All focused suites passed:

```text
uv run python -m unittest tests.test_klimkit_install -q
Ran 43 tests in 0.139s
OK

uv run python -m unittest tests.test_klimkit_cli -q
Ran 28 tests in 0.293s
OK

uv run python -m unittest tests.test_switchboard -q
Ran 46 tests in 9.736s
OK

uv run python -m unittest tests.test_codex_pack_validation -q
Ran 11 tests in 0.020s
OK

uv run python -m unittest tests.test_docs_static -q
Ran 4 tests in 0.008s
OK
```

Full suite and whitespace checks passed:

```text
uv run python -m unittest discover -s tests -q
installing code-server extension: publisher.example
code-server extension already installed: publisher.example
apply ok
klimkit: sent autosync Telegram notification
Ran 169 tests in 10.247s
OK (skipped=1)

git diff --check
passed with no output
```

## Manual And Adversarial QA

Reserved operator folder migration now fails before moving files:

```text
status=1
error Apply is blocked until the local config is complete.
required [operator] human_name maps to a reserved .klimkit directory
tree:
.klimkit/local/klimkit.toml
.klimkit/log.md
.klimkit/memory.md
.klimkit/reflection.md
.klimkit/tasks/feature/01-a.md
```

Dry-run follow-up command preserves and quotes explicit context:

```text
kk --config '/tmp/.../config dir/klimkit.toml' migrate team-workflow --repo '/tmp/.../project with spaces' --human-name 'Alice O'"'"'Connor; rm -rf nope'
```

Normal team migration still works:

```text
workflow   team
human      Alice Example
folder     Alice-Example
moved      .../.klimkit/memory.md -> .../.klimkit/Alice-Example/memory.md
moved      .../.klimkit/tasks -> .../.klimkit/Alice-Example/tasks
```

Report-serving probes:

```text
reports= [('@Alice/ok/report.html', 'Valid Team Report')]
reserved_asset= None
symlink_asset= None
symlink_operator_root_ok= False
symlink_operator_root_messages= ['operator artifact root must not be a symlink']
symlink_klimkit_root_reports= []
symlink_klimkit_root_asset= None
symlink_operator_alias_asset= None
configured_repo_config= workflow = "team"
implicit_dry_run_next= kk --config /tmp/.../klimkit.toml migrate team-workflow --repo /tmp/.../project --human-name Alice
malformed_tasks_file_ok= False
malformed_memory_dir_ok= False
partial_existing_target_ok= False
truncated_operator_folder= AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
repo_root_toml_injection_ok= False
duplicate_report_roots_indexed= False
live_codex_conflict_prompt= ask Klim

status valid team: 200
status reserved tasks: 404
status traversal: 404
status media range: 206 4
2345
```

Browser QA used `agent-browser` with Chrome `--no-sandbox`, required by this VM. Evidence assets were captured under `.klimkit/reports/05-team-workflow-fixes/assets/`:

- `01-reports-index-desktop.png`
- `02-team-report-detail.png`
- `03-reserved-rejected.png`
- `04-reports-index-mobile.png`
- `05-reports-empty-state.png`
- `reports-flow.webm`
- `reports-flow.mp4`

## Report

The final story-style proof report is:

```text
.klimkit/reports/05-team-workflow-fixes/report.html
```

The local QA servers were:

```text
http://127.0.0.1:4879/reports/
http://127.0.0.1:4880/reports/
```

Tailscale DNS is available as `odev.tail11c448.ts.net`; the stable report handoff URL is expected under:

```text
https://odev.tail11c448.ts.net/reports/
https://odev.tail11c448.ts.net/reports/r/klimkit-dc70a74e9a/05-team-workflow-fixes/report.html
```

The flattened report URL was verified after removing operator-scoped committed evidence:

```text
curl -I -sS https://odev.tail11c448.ts.net/reports/r/klimkit-dc70a74e9a/05-team-workflow-fixes/report.html
HTTP/2 200
content-type: text/html; charset=utf-8

curl -I -sS https://odev.tail11c448.ts.net/reports/r/klimkit-dc70a74e9a/@Klim/05-team-workflow-fixes/report.html
HTTP/2 404
```

## Review Status

- Code review PASS after repeated blocker-driven passes. Final pass reported no findings after checking config TOML escaping, migration hardening, dry-run quoting, and report serving.
- Security review PASS after repeated path/auth review. Final pass reported no findings across TOML serialization, migration preflight, report symlink/traversal boundaries, command quoting/context, auth, README, and SECURITY.
- Reflection appended at `.klimkit/reflection.md` under `2026-05-16T05:40:04Z`; it required updating this proof report and the HTML report placeholders before final review.
- Final review round 1 produced one PASS and two blockers: live projection still said `ask Human`, and duplicate report roots produced duplicate index rows. Both blockers were fixed, verified, and passed quick code/security review before round 2.
- Final review round 2 returned three `PASS / READY FOR USER` results.
