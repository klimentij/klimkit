# Root Skills Library Implementation Proof

## Source Intake

- Vercel Skills CLI repository: `vercel-labs/skills`, branch `main`, commit `b469d6954dd10be20d3e8d9bb59463584d42efbb`.
- Vercel public agent skills examples: `vercel-labs/agent-skills`, branch `main`, commit `180115660cfb8a86b808f117475a01f54caf3bc5`.
- Vercel Agent Skills docs: `https://vercel.com/docs/agent-resources/skills`.
- Vercel Agent Skills creation guide: `https://vercel.com/kb/guide/agent-skills-creating-installing-and-sharing-reusable-agent-context`.
- Vercel CLI README confirmed `npx skills add <source> --list`, `--skill`, `--agent`, `--global`, and `npx skills update`.
- Vercel CLI source confirmed root `skills/` discovery and one extra nested category level, but this repo uses the requested flat `skills/<skill-name>/SKILL.md` layout.
- Web research did not find a Vercel Skills-specific mutable state store for globally installed skills. The package model is static skill folders with `SKILL.md` plus optional `references/`, `scripts/`, and `assets/`.
- The XDG Base Directory Specification was used for user-global defaults: `${XDG_CONFIG_HOME:-~/.config}/klimkit/config.toml` for config and `${XDG_STATE_HOME:-~/.local/state}/klimkit/` for non-portable runtime state.
- Local skill-creator guidance confirmed required `SKILL.md` frontmatter, folder/name equality, concise descriptions, and optional `scripts/`, `references/`, and `assets/`.
- Local Klimkit plugin examples inspected before deprecation under the then-current plugin paths, now moved to `deprecated/codex-plugin/plugins/klimkit/`.
- Public Matt Pocock skills snapshot inspected as prior art under `third_party/mattpocock-skills/`, with upstream metadata in `third_party/mattpocock-skills/UPSTREAM.md`.
- Prior planning source: `.klimkit/tasks/13-symphony-skills-control-plane-research/03-a-deep-analysis.md`.

## Files Added Or Updated

- Added root skills package under `skills/`:
  - `klimkit-workflow`
  - `klimkit-setup`
  - `klimkit-diagnose`
  - `klimkit-tdd`
  - `klimkit-report-server`
  - `klimkit-walkthrough`
  - `klimkit-worktree-stack`
- Added skill-local `agents/openai.yaml` metadata for each skill.
- Added targeted references under the owning skills.
- Added `skills/klimkit-setup/references/state-config.md` to document mutable state/config storage outside installed skill package folders.
- Added `skills/klimkit-report-server/scripts/serve_reports.py` as a skill-owned reference report server.
- Updated `README.md` to make the Vercel Skills CLI the primary install/update path and mark the old runtime as deprecated.
- Updated setup/workflow/report/walkthrough/worktree skills so new skills-first artifacts default to `.klimkit/<operator>/`.
- Moved the legacy runtime, launchers, installer, pack projection, templates, examples, tests, and Codex plugin prototype under `deprecated/`.
- Added root `tests/test_root_skills.py` and updated CI to validate the skills-first surface without the deprecated Python runtime.

## Scope Update

Klim clarified during implementation that Klimkit should become the skills library itself. The old Switchboard, synchronization scripts, repo-managed projection, and related runtime machinery are deprecated and should not shape new skills. I removed those legacy concepts from root skills and kept the legacy runtime code in place for compatibility rather than moving Python modules and breaking existing tests in this first review version.

Klim later clarified that operator-name subfolders should become the default. The setup skill now asks for the operator name first, creates `.klimkit/<operator>/config.toml`, `memory.md`, `log.md`, `reflection.md`, `tasks/`, and `reports/`, and treats legacy flat `.klimkit/tasks/` and `.klimkit/reports/` as readable historical context rather than the default write target.

Mutable state is not stored inside installed skill folders. Project-local operator state lives in `.klimkit/<operator>/config.toml`; optional user-global defaults live in `${XDG_CONFIG_HOME:-~/.config}/klimkit/config.toml`; non-portable runtime state belongs under `${XDG_STATE_HOME:-~/.local/state}/klimkit/`.

Klim then removed tracker, board, triage, and control-plane skills from this first phase. The root package now keeps only workflow, setup, diagnose, TDD, report-server, walkthrough, and worktree-stack. The removed tracker-oriented skills can be reintroduced later after the base workflow is polished.

Setup now discovers operator context from the current repo, home Klimkit repo, and user-global config; asks when ambiguous; creates a new operator skeleton in both current and home repos when needed; and records an agent personality preference.

## Validation

- Initial `python3 "$HOME/.codex/skills/.system/skill-creator/scripts/quick_validate.py" skills/<skill>` for the earlier 10-skill draft: passed before scope reduction.
- `python3 -m py_compile skills/klimkit-report-server/scripts/serve_reports.py`: passed.
- `skills/klimkit-report-server/scripts/serve_reports.py` runtime smoke test with a temporary `.klimkit/Klim/reports/demo/report.html`, local server on `127.0.0.1:8876`, and two `curl -fsS` fetches: passed.
- `python3 -m unittest discover -s tests -q`: passed.
- `npx skills add ./ --list`: passed, found 7 skills and listed the intended first-wave package.
- `python3 "$HOME/.codex/skills/.system/skill-creator/scripts/quick_validate.py" skills/<skill>` for all 7 final root skills: passed.
- `rg -n "klimkit-to-issues|klimkit-triage|klimkit-github-control-plane|KK Status|GitHub control|issue workpad" skills README.md`: no matches.
- `rg -n "Switchboard|switchboard|autosync|Telegram|kk apply|kk pull|repo-managed|code-server" skills`: no matches.
- Targeted privacy grep over `skills`, `deprecated`, `README.md`, changed tests, task files, and log for local home paths and known private identifiers: no matches.
- Targeted privacy grep over the added `.klimkit/reflection.md` diff for local home paths and known private identifiers: no matches. Older historical reflection entries were not rewritten.
- `git diff --check -- README.md skills tests .github deprecated .klimkit/tasks/14-root-skills-library .klimkit/log.md .klimkit/reflection.md`: passed.

## Verification Boundary

No UI proof report or browser video was required. The changed user-facing surface is Markdown and skill package metadata; no app UI or runtime service behavior changed. The report server script was syntax-checked but not installed as a persistent service.

The latest scope update was completed without subagents per Klim's explicit instruction. No final-review subagents were run after that instruction.

## Remaining Risks

- The root `skills/` package is ready for review, but the deprecated Codex plugin package has not been regenerated from it.
- Legacy runtime code has moved under `deprecated/runtime/`, but its internal docs and tests still describe old behavior and are not part of the skills-first validation surface.
- The report server script is intentionally minimal and should receive focused testing before being treated as a supported long-running service.
