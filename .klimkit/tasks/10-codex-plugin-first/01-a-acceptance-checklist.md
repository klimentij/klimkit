# Codex Plugin First

## Request

On branch `codex-plugin-first`, extract Klimkit's Codex harness pack into a public Codex plugin called Klimkit; make plugin-first Codex usage the default README path; include correct install and upgrade commands; reposition the Codex app as the recommended default over Switchboard given recent multi-machine interaction; make existing Switchboard, fork/adapt, and autosync harness workflows secondary for technical users; keep autosync and Telegram notifications off by default; run verification; and use one final `final_reviewer` pass for this task.

## Acceptance Checklist

- [ ] The public plugin lives in a clear repo-local plugin location with root folder/name `klimkit`, includes `.codex-plugin/plugin.json`, and keeps the manifest `name` aligned with the folder name.
- [ ] `.codex-plugin/plugin.json` validates as a public Codex plugin manifest with strict semver, non-empty `name`, `version`, `description`, `author.name`, and required `interface` fields including `displayName`, `shortDescription`, `longDescription`, `developerName`, `category`, `capabilities`, and `defaultPrompt` or `default_prompt`.
- [ ] The plugin manifest uses real public metadata for Klimkit, including repository/homepage/license/keywords as appropriate, and contains no `[TODO: ...]` placeholders, private URLs, local machine paths, or operator-specific claims.
- [ ] Plugin asset references, if present, point to existing repo-local files inside the plugin package and use relative `./` paths accepted by plugin validation.
- [ ] The plugin exposes the migrated Codex harness content through supported plugin surfaces: skills under `skills/`, MCP or app manifests only when corresponding `.mcp.json` or `.app.json` files exist, and no unsupported manifest fields.
- [ ] The migrated plugin content preserves the functional intent of Klimkit's Codex harness pack: shared AGENTS guidance, custom agents/subagents, local skills, hook behavior, and config defaults are represented either inside the plugin or explicitly documented as still requiring `kk apply`.
- [ ] The implementation deliberately handles `packs/codex/AGENTS.md`, `packs/codex/agents/`, `packs/codex/skills/`, `packs/codex/hooks/`, and `packs/codex/config.toml`, with a documented decision for each: migrated into the plugin, retained as Klimkit-managed projection input, or removed only if no longer needed.
- [ ] Harness projection tokens such as `__HUMAN_NAME__`, `__KLIMKIT_ARTIFACT_WORKFLOW__`, `__KLIMKIT_OPERATOR_FOLDER__`, and `__KLIMKIT_ARTIFACT_ROOT__` are either removed from public plugin content, replaced with plugin-safe generic language, or kept only in files that are still projected by Klimkit rather than installed directly as plugin content.
- [ ] Plugin-first usage does not leak VM-local Codex state: plugin/connector tables, auth state, MCP runtime state, hook trust state, project trust, Slack state, tokens, and generated `~/.codex/config.toml` content stay out of source-controlled plugin files.
- [ ] The public marketplace file is created or updated with a Klimkit entry that points at `./plugins/klimkit` or the implemented repo-relative plugin source path, includes `policy.installation`, `policy.authentication`, and `category`, and preserves the marketplace-level `interface.displayName` pattern.
- [ ] Marketplace policy is appropriate for a public plugin: Klimkit is available to install, authentication behavior is explicit, and product gating is omitted unless deliberately justified.
- [ ] The README's first-path setup recommends the Codex app plus the Klimkit Codex plugin as the default way to use Klimkit's harness.
- [ ] README install instructions use the current Codex CLI command shape verified from local help or official docs, including `codex plugin marketplace add <source>` and `codex plugin add klimkit@<marketplace>` or an equivalent validated selector for the implemented marketplace.
- [ ] README upgrade instructions use the current Codex CLI command shape verified from local help or official docs, including `codex plugin marketplace upgrade [MARKETPLACE_NAME]`, and explain when to rerun `codex plugin add` only if that is actually required by the CLI behavior.
- [ ] README copy clearly distinguishes installing the public Klimkit plugin from forking this repository and running `./install.sh`, so users do not need to fork/adapt the whole repo for the default Codex app path.
- [ ] README copy repositions the Codex app as the recommended day-to-day default for multi-machine Codex interaction and explains why Switchboard is now secondary without removing Switchboard's value for technical users.
- [ ] README keeps Switchboard, fork/adapt, `kk apply`, `kk pull`, worktree, code-server, Tailscale Serve, and autosync workflows documented as secondary/advanced paths for users who want full repo-managed machine orchestration.
- [ ] README preserves accurate safety language for the existing yolo/default Codex harness profile and makes clear which risks apply to plugin usage versus repo-managed VM projection.
- [ ] README and default config documentation continue to state that autosync is off by default, with `[workers] auto_sync = false`, and that users must opt in before daemon-managed pull/apply/restart behavior occurs.
- [ ] README and config examples continue to state that Telegram notifications are off by default with `[notifications.telegram] enabled = false`, and enabling Telegram remains an explicit opt-in.
- [ ] The existing Switchboard docs and screenshots remain truthful: Switchboard is no longer presented as the default entry point, but its local/Tailscale URLs, PWA guidance, workspace catalog, and technical multi-worktree use cases remain discoverable.
- [ ] Any installer, `kk setup`, or default TOML changes required by the docs are implemented so new local configs keep autosync and Telegram disabled unless the user opts in.
- [ ] Any Codex plugin validation helper added to the repo checks `.codex-plugin/plugin.json`, marketplace entry shape, required plugin files, missing assets, and rejected placeholders.
- [ ] Existing static validation is extended or kept passing for Codex pack/plugin content, including the current `tests.test_codex_pack_validation` expectations or a deliberately renamed/reworked plugin validation suite.
- [ ] Focused tests cover plugin package layout and manifest/marketplace validity without relying on the developer's live `~/.codex` state.
- [ ] Focused tests cover documentation command accuracy enough to fail if README reintroduces obsolete commands such as `codex plugin install` for this workflow.
- [ ] Focused tests or static checks confirm autosync and Telegram defaults remain disabled in generated/default config examples.
- [ ] Existing projection preservation guarantees from task `09-preserve-codex-plugin-config` remain intact: `kk apply` still preserves VM-local plugin/connector tables and writes secret-bearing projected Codex config with restrictive permissions.
- [ ] Verification includes `python3 <codex-home>/skills/.system/plugin-creator/scripts/validate_plugin.py <plugin-path>` or an equivalent repo-local validator against the implemented plugin root.
- [ ] Verification includes `codex plugin marketplace add --help`, `codex plugin marketplace upgrade --help`, and `codex plugin add --help` or official Codex docs evidence showing the README commands match the current CLI.
- [ ] Verification includes the focused plugin/pack/docs tests added or changed for this task.
- [ ] Verification includes `uv run python -m unittest tests.test_codex_pack_validation tests.test_docs_static -q` unless those suites are deliberately renamed or replaced, in which case the replacement suites are named in proof.
- [ ] Verification includes `uv run python -m unittest discover tests -q`, with any skipped tests or unavailable external smoke checks explicitly recorded.
- [ ] Verification includes `git diff --check`.
- [ ] Optional live Codex smoke testing is run only if a signed-in Codex CLI and safe environment are available; if skipped, the proof states why and what static/CLI-help checks covered instead.
- [ ] A task proof note under `.klimkit/tasks/10-codex-plugin-first/` records changed files, install/upgrade command evidence, validation commands, notable outputs, skipped or unavailable checks, and any remaining risk.
- [ ] `.klimkit/log.md` receives a concise timestamped entry describing the implementation and verification outcome.
- [ ] Reflection Gate is completed after verification and before final review: read `.klimkit/reflection.md`, append a full UTC timestamped session with `Observations`, `Derived Pattern`, `Insight`, and `Next Probe`, reconsider plugin-first positioning and verification after reflection, and rerun impacted checks if reflection exposes a gap.
- [ ] Final Review Gate follows the user override for this task: draft the exact final response, run one `final_reviewer` pass with this checklist, changed files, verification evidence, reflection entry, proof note path, and exact draft response, and require PASS / READY FOR USER before claiming completion.
- [x] If the implementation commit lands on `main`, a next patch GitHub release is created for that commit and marked latest per repository-local `AGENTS.md`; if no commit lands on `main`, proof records that the release step is not applicable.

## Publish And Live Plugin Proof Checklist

- [x] The `codex-plugin-first` worktree is reviewed for intended changes only, then committed on the branch; proof records the commit SHA and the tracked proof artifacts included in the commit.
- [x] The branch is pushed to `origin/codex-plugin-first`, and the remote branch points at the intended commit as verified by GitHub or `git ls-remote`.
- [x] A PR from `codex-plugin-first` into `main` is created with summary, verification, and task proof references; required review and CI/status checks pass or any unavailable checks are explicitly recorded.
- [x] The PR is merged or otherwise accepted into `main`, local `main` is updated to the accepted commit, and proof records the merge/acceptance method and resulting `main` commit SHA.
- [x] A next patch GitHub release is created for the new `main` commit, marked latest, and proof records the tag, release URL, and release commit SHA.
- [x] Before install or upgrade, live VM Codex plugin state is captured, including Codex plugin list output, marketplace state, and relevant `~/.codex` plugin/cache/home paths showing whether Klimkit is absent, present, or stale.
- [x] The released Klimkit Codex plugin is installed on this VM from the published marketplace/source, and post-install proof shows the installed plugin version plus the home-directory/cache paths Codex actually uses.
- [x] A slight, intentional skill modification is made in the plugin source, with a manifest version bump or marketplace metadata change if Codex upgrade detection requires it; proof records the exact skill text/version before and after.
- [x] The marketplace refresh or upgrade path is exercised, including `codex plugin marketplace upgrade ...` and any `codex plugin add` or refresh command the current CLI requires, with before/after evidence proving the upgraded Klimkit plugin is selected.
- [x] Home/cache verification proves the modified skill reached the live installed copy by inspecting the relevant `~/.codex` plugin/cache files and comparing them against the released plugin source and CLI-reported version.
- [x] Verification reruns the affected repository and CLI checks, including plugin validation, focused plugin/docs tests, full unittest discovery or named replacement suites, `git diff --check`, and safe Codex CLI help/state checks used by the proof.
- [x] The task proof note and `.klimkit/log.md` are updated with commit, push, PR, merge, release, install, upgrade, command outputs, home/cache file paths, skipped checks, and remaining risks.
- [x] Reflection Gate is completed after publish/install/upgrade verification and before final review: append a fresh `.klimkit/reflection.md` session and reconsider the release/live-install evidence before reviewers.
- [ ] Final Review Gate is completed with the exact final response, this updated checklist, publish/live plugin proof, reflection entry, and 3 parallel `final_reviewer` PASS / READY FOR USER results before completion is claimed.

## Progress

- [x] Plugin package, marketplace entry, README repositioning, and static validation tests are implemented.
- [x] Plugin validator, CLI help checks, focused tests, full unittest discovery, and `git diff --check` have passed.
- [x] Reflection Gate appended `.klimkit/reflection.md` session `2026-05-27T05:19:03Z` and no material rework was required.
- [ ] Final reviewer pass remains before completion.
