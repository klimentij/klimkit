# Implementation Plan With Clarifications: Local-First Config, Better Docs, and Harness-Agnostic Packs

## Task Read

Human-authored task file: `01-h-initial-task.md`.

Agent-authored critical review file: `02-a-critical-repo-review.md`.

Agent-authored plan file: `03-a-implementation-plan-with-clarifications.md`.

The `-h-` and `-a-` filename markers mean human and agent. I will preserve that convention for follow-up artifacts in this task folder.

The requested work is not one feature. It is a cleanup of Klimkit's operator model:

- make the README explain the product clearly before mentioning implementation details
- document the tech stack in a separate section
- make generated TOML easier to understand with comments for every meaningful knob
- collapse local Klimkit configuration into one TOML source of truth
- move Klimkit state and config under `~/klimkit/.klimkit`
- prepare pack installation for multiple agent harnesses while still supporting only Codex now
- add strong tests, including optional live Codex startup smoke tests that catch malformed skills, agents, hooks, and config warnings without sending prompts
- teach the Codex AGENTS pack about repo-local memory, logs, and task folders using the `~/klimkipedia/projects` convention as the model

## Current State

Klimkit currently installs a `kk` command from `install.sh`. The command is a Python CLI in `src/klimkit/cli.py`, with planning and application logic in `src/klimkit/install.py`.

The current local config and state defaults are split across home directories:

- main Klimkit config: `~/.config/klimkit/klimkit.toml`
- generated Switchboard server config: `~/.config/klimkit/switchboard.toml`
- generated Switchboard agent config: `~/.config/klimkit/switchboard-agent.toml`
- install manifest and backups: `~/.local/state/klimkit/...`
- Switchboard and agent SQLite state: `~/.local/state/klimkit/...`
- Codex pack projection: `~/AGENTS.md`, `~/.codex/config.toml`, `~/.codex/hooks.json`, `~/.codex/hooks`, `~/.codex/agents`, `~/.codex/skills`
- Telegram config: `~/.config/klimkit/telegram.env`

The config split is the main thing to fix. `render_config()` writes one editable file, but `build_plan()` then writes additional generated TOML files for Switchboard and the agent. That makes the mental model worse because users have to remember which file is editable and which one is generated.

Codex support is also hardcoded in two places:

- `src/klimkit/install.py` hardcodes `packs/codex` and all Codex target paths inside `build_plan()`.
- `src/klimkit/tools/supervisor/supervisor.py` hardcodes live-sync mappings for the Codex pack.

The README currently starts with a stack-shaped description: "Python operator kit", "Codex-oriented machines", "TOML config", and "without a TUI". That is accurate but not helpful as a top-level explanation for a user deciding what Klimkit does.

Tests exist and currently pass:

- `uv run python -m unittest discover -s tests -q`
- result during planning: `Ran 69 tests in 5.220s`, `OK`

Coverage tooling is not installed:

- `uv run python -m coverage ...` fails with `No module named coverage`

## External Docs Checked

I checked current OpenAI Codex docs because the live validation plan depends on current CLI behavior.

Relevant findings:

- Codex non-interactive mode is `codex exec`; it is meant for scripts and CI, without opening the TUI: https://developers.openai.com/codex/noninteractive
- `codex exec` streams progress to `stderr` and prints the final agent message to `stdout`, which makes warning capture practical.
- Useful `codex exec` flags include `--cd`, `--ephemeral`, `--json`, `--sandbox`, `--ignore-user-config`, and `-c/--config`: https://developers.openai.com/codex/cli/reference
- Codex hooks can live in `hooks.json` or inline `[hooks]` in `config.toml`; if a layer contains both `hooks.json` and inline hooks, Codex merges them and warns. That supports moving Klimkit's Codex hooks into the generated Codex TOML projection instead of keeping a separate `hooks.json`: https://developers.openai.com/codex/hooks
- Skills require a directory with `SKILL.md`, and `SKILL.md` must include `name` and `description`: https://developers.openai.com/codex/skills
- Custom subagents are standalone TOML files under `~/.codex/agents/` or `.codex/agents/`; each must define `name`, `description`, and `developer_instructions`: https://developers.openai.com/codex/subagents
- Current Codex docs say global AGENTS guidance lives under `CODEX_HOME` and project AGENTS are discovered from the project root downward: https://developers.openai.com/codex/guides/agents-md

## Target Model

Klimkit should have one human-edited local config:

```text
~/klimkit/.klimkit/local/klimkit.toml
```

Klimkit runtime state should live near it:

```text
~/klimkit/.klimkit/state/
~/klimkit/.klimkit/backups/
~/klimkit/.klimkit/logs/
```

The exact names can be adjusted during implementation, but the important property is that machine-local state and config are inside the Klimkit checkout. After clarification, `.klimkit/` is not blanket-ignored; task, proof, memory, and log artifacts can be tracked, while local secrets and runtime DBs must be reviewed before adding.

Generated harness files should be called projections, not config sources. A projection is a file Klimkit writes because an external tool expects that location or shape. The user should edit `~/klimkit/.klimkit/local/klimkit.toml`, not generated files.

The single config should cover:

- repo and state paths
- machine role
- components
- services
- workers
- code-server
- Tailscale Serve
- Switchboard server
- Switchboard agent
- notifications, including Telegram
- enabled harnesses, currently only Codex
- per-harness projection choices

Example shape:

```toml
# Klimkit local machine config.
# Edit this file, then run `kk preview` or `kk apply`.

[paths]
# Repo checkout Klimkit should apply from.
repo_root = "/home/ubuntu/klimkit"
# Runtime state directory for manifests, backups, DBs, and logs.
state_dir = "/home/ubuntu/klimkit/.klimkit/state"

[components]
# Client installs local agent harness assets and code-server support.
client = true
# Server runs the central Switchboard on this machine.
server = true

[harnesses.codex]
# Enable the Codex pack projection.
enabled = true
# Optional. If set later, Codex can keep its own runtime home under the Klimkit repo.
codex_home = ""

[switchboard.server]
enabled = true
host = "127.0.0.1"
port = 4721
base_path = "/switchboard"
auth_token = ""

[switchboard.agent]
enabled = false
backend_url = ""
auth_token = ""

[notifications.telegram]
enabled = false
bot_token = ""
chat_id = ""
```

The generated file should contain plain comments beside the knobs users actually change. Comments should explain intent and consequence, not repeat the key name.

## Path Migration Plan

1. Add path constants for repo-local local data.

   - Add `KLIMKIT_LOCAL_DIR`, `KLIMKIT_CONFIG_FILE`, `KLIMKIT_STATE_DIR`, and backup/log helpers in `src/klimkit/paths.py`.
   - Default to `OPS_REPO_ROOT / ".klimkit" / "local" / "klimkit.toml"` for config and `OPS_REPO_ROOT / ".klimkit" / "state"` for state.
   - Preserve environment overrides: `KLIMKIT_CONFIG`, `KLIMKIT_STATE_DIR`, `KLIMKIT_CONFIG_DIR`, and `KLIMKIT_REPO_ROOT`.

   Verify:

   - unit tests assert defaults point under the repo
   - env override tests still pass
   - `kk` welcome, `kk doctor`, `kk preview`, and `kk apply` print the new paths

2. Keep `.klimkit/` visible to Git and avoid committing accidental runtime artifacts.

   - Do not add a blanket ignore for `.klimkit/`; the user clarified to track `.klimkit` artifacts.
   - Commit task, proof, memory, and log artifacts when they explain repo work.
   - Ignore `.klimkit/local/`, `.klimkit/state/`, `.klimkit/backups/`, and `.klimkit/logs/` because they can contain tokens, local DBs, backups, or process logs.
   - Remove transient proof/runtime files that are not source artifacts before commit.

   Verify:

   - `git status --short` shows only the intended `.klimkit` artifacts and code/doc changes

3. Migrate legacy config gracefully.

   - If old `~/.config/klimkit/klimkit.toml` exists and the new repo-local config does not, `kk setup` should copy it into the new location, preserve mode `0600`, and print a migration note.
   - Do not delete old config on migration. Report it as legacy.
   - `kk doctor` should show both current and legacy paths when legacy files exist.

   Verify:

   - temp-home tests cover missing config, migrated config, and explicit `--config`

## Single TOML Plan

1. Make `InstallConfig` represent the single source of truth.

   - Replace `switchboard_config_path` and `switchboard_agent_config_path` as default-generated config targets with server/agent config sections in the main config.
   - Keep legacy fields readable for migration only.
   - Rename internal fields as needed so the code distinguishes "source config" from "projection path".

   Verify:

   - parse/render round trip tests cover first VM, client-only VM, server-only VM, and legacy profile fields
   - generated comments survive render tests

2. Stop writing generated Switchboard TOML by default.

   - Remove `switchboard-config` and `switchboard-agent-config` write actions from the default plan.
   - Update `kk daemon`, supervisor, `kk serve`, and switchboard agent loading so they read the main config and project the relevant `AppConfig` or `AgentConfig` in memory.
   - Keep compatibility loaders for old standalone `switchboard.toml` and `switchboard-agent.toml` when a user explicitly passes those paths.

   Verify:

   - `build_plan(default_config(), skip_services=True)` includes one Klimkit local TOML and no separate Switchboard TOML actions
   - supervisor tests prove the service starts with the single `KLIMKIT_CONFIG`
   - Switchboard tests still cover server auth, API state, archive endpoints, and agent ingest

3. Move Telegram settings into the single TOML.

   - Add `[notifications.telegram]` settings.
   - Update `packs/codex/hooks/stop-notify.sh` to read Telegram config from `KLIMKIT_CONFIG` or the repo-local default via Python TOML parsing.
   - Preserve support for the old env file as a fallback for one release.

   Verify:

   - hook unit/shell tests cover disabled Telegram, TOML-enabled Telegram, and legacy env fallback
   - no docs tell users to edit `telegram.env` as the main path

## Harness-Agnostic Pack Plan

1. Introduce a minimal harness registry.

   Do not build a generic plugin framework yet. Use a small Python registry that returns harness projections for enabled harnesses.

   Suggested files:

   ```text
   src/klimkit/harnesses/__init__.py
   src/klimkit/harnesses/base.py
   src/klimkit/harnesses/codex.py
   ```

   The Codex harness should own:

   - projected config
   - hooks
   - AGENTS guidance
   - agents
   - skills
   - validation checks
   - optional live smoke test command shape

   Verify:

   - `install.py` no longer hardcodes `packs/codex` target paths directly
   - tests can inspect Codex projection actions through the registry

2. Keep the Codex pack clean and hand-authored for now.

   Klim explicitly deferred shared pack extraction after implementation started. Do not add `packs/shared/` in this pass. Keep the Codex pack ready as a non-generated pack, and revisit shared fragments when a second harness exists.

   Current structure:

   ```text
   packs/codex/AGENTS.md
   packs/codex/config.toml
   packs/codex/hooks/stop-notify.sh
   packs/codex/agents/*.toml
   packs/codex/skills/**
   ```

   Verify:

   - no `packs/shared/` directory is introduced
   - Codex AGENTS content includes the memory/log/task guidance directly

3. Inline Codex hooks into the generated Codex TOML projection.

   - Replace separate `packs/codex/hooks.json` with TOML hook config generation.
   - Keep hook scripts in `packs/codex/hooks/`.
   - This aligns with the "single TOML" direction and avoids future startup warnings from mixed hook representations in one config layer.

   Verify:

   - JSON hook action disappears from the plan
   - generated TOML parses
   - live Codex startup smoke test has no hook-source warning

4. Decide Codex home behavior after clarification.

   There are two viable models:

   - Conservative model: keep projecting to `~/.codex` because current Codex defaults expect it, while the editable source of truth and Klimkit state live under `~/klimkit/.klimkit`.
   - Strong local-first model: set `CODEX_HOME=~/klimkit/.klimkit/harnesses/codex` so Codex config, sessions, skills, agents, hooks, and SQLite state all live under the Klimkit repo-local ignored directory.

   I recommend implementing the conservative model first unless Klim explicitly wants the stronger migration now. Moving `CODEX_HOME` changes where Codex stores auth, sessions, history, and possibly existing Switchboard inputs, so it needs a deliberate migration.

## README Plan

1. Rewrite the opening explanation without stack terms.

   Proposed direction:

   ```text
   Klimkit keeps an agent-ready machine reproducible. One repo owns the local
   instructions, harness packs, services, dashboards, and machine-specific
   settings needed to make a fresh VM behave like Klim's working environment.
   You edit the repo, preview exactly what will change, apply it locally, and
   use normal Git flow to carry the same operator setup to another machine.
   ```

   The opening should answer:

   - what Klimkit is for
   - what problem it removes
   - what the user edits
   - how changes move between VMs

   It should not mention Python, TOML, Codex, no-TUI design, or implementation details in the first paragraph.

2. Add a separate "Tech Stack" section.

   Keep it simple:

   - Python 3.11+ package
   - `uv` for local execution and packaging
   - stdlib CLI with `argparse`
   - TOML for the local machine config
   - SQLite for Switchboard and agent state
   - systemd user service and launchd LaunchAgent for the supervisor
   - code-server for browser IDE access
   - Tailscale Serve for private tailnet exposure
   - Codex CLI pack projection for AGENTS, config, hooks, subagents, and skills
   - vanilla HTML/CSS/JS for Switchboard
   - `unittest` plus optional `coverage`

   Then add one paragraph explaining how it fits together: `kk` reads the repo-local config, builds an action plan, writes managed projections and services, and uses the manifest to back up, prune, and uninstall only files it owns.

3. Replace path references.

   - Replace `~/.config/klimkit/...` and `~/.local/state/klimkit/...` as the primary paths.
   - Add a short "Generated Projections" subsection explaining that some external tools may still require files under their own homes unless `CODEX_HOME` migration is enabled.

4. Explain config knobs better.

   - Mirror the comments in the generated TOML.
   - Group common role switches first.
   - Move advanced settings below a clear "Advanced" subsection.
   - Explicitly explain `client`, `server`, `switchboard.agent`, `services.enable`, `live_sync`, and `code_server.install_if_missing`.

## AGENTS Pack Plan

Use `~/klimkipedia/projects/AGENTS.md` as the model, not as a verbatim copy.

Add a section to `packs/codex/AGENTS.md` that says:

- At the start of meaningful repo work, read `.klimkit/memory.md` and `.klimkit/log.md` when they exist.
- If meaningful repo work starts and either file is missing, create it under `.klimkit/` with the documented template before the first memory or log update.
- `memory.md` stores durable preferences, corrections, and process rules as dated one-sentence memories.
- `log.md` stores timestamped one-sentence audit entries describing actions taken, not preferences.
- New reusable preferences should be prepended to `.klimkit/memory.md`.
- New meaningful actions should be appended or prepended consistently under `.klimkit/log.md` with an ISO timestamp.
- Task and feature work should live under `.klimkit/tasks/<nn-feature-slug>/`.
- Human-authored files use `-h-` in the filename.
- Agent-authored files use `-a-` in the filename.
- Task folders can contain planning, design, discussion, proof, and implementation notes.

Also add template content or examples for empty root files:

```markdown
# Project Memory

Durable preferences, corrections, and process rules. Add dated one-sentence memories.

## Memories
```

```markdown
# Project Log

Timestamped audit trail. Entries describe actions, not preferences.

## Log
```

Verify:

- tests assert the generated/projected AGENTS content includes the memory/log/task convention
- README mentions `.klimkit/tasks/` only in the operator/project-work section, not as Klimkit runtime state

## Review-Driven Hardening Additions

These items come from `02-a-critical-repo-review.md` and should be handled as part of the implementation, not left as separate cleanup unless explicitly deferred.

1. Clean stale Switchboard naming.

   - Remove or update stale `switchboard2` references in `.gitignore` and `assets/brand/README.md`.
   - Audit README and Switchboard spec references for old app names and old paths.

   Verify:

   - `rg "switchboard2|Switchboard 2"` has no current-doc references unless intentionally marked historical

2. Make security-sensitive defaults explicit.

   - Document the intended threat model for loopback, Tailscale Serve, code-server, Switchboard auth, helper server binding, and launched agent terminals.
   - Add config comments for code-server auth delegation, workspace trust, automatic tasks, and launch flags.
   - Consider changing the Switchboard agent helper default host from `0.0.0.0` to loopback unless a concrete proxy requirement needs all-interface binding.
   - Add `Secure` cookie support when the public Switchboard URL or explicit config indicates HTTPS.
   - Make `--dangerously-bypass-approvals-and-sandbox` a named trusted-local setting rather than an unexplained JS constant.

   Verify:

   - tests cover non-loopback auth requirements, helper host config, cookie flags, and launch flag rendering
   - README has a concise Security Model section

3. Treat network installers as high-risk actions.

   - Revisit the `curl -fsSL https://code-server.dev/install.sh | sh` action.
   - At minimum, classify it clearly in `kk preview`.
   - Prefer an explicit opt-in flag or a documented package-manager-specific install path before running network installer scripts.

   Verify:

   - preview tests distinguish file projections, service actions, and external network installer actions

4. Remove duplicate config serialization.

   - Deprecate or delete supervisor-side config writing once the single config parser/renderer owns serialization.
   - Keep supervisor code focused on reading config, syncing managed projections, and starting processes.

   Verify:

   - config render/parse tests only need one production serializer
   - supervisor tests consume the same config shape as `kk`

5. Align docs with the test harness.

   - Keep `unittest` as the documented test command unless the project intentionally adopts pytest.
   - Update `src/klimkit/apps/switchboard/spec.md` so it is either current or clearly historical.

   Verify:

   - `rg "pytest"` only returns intentional references
   - README, spec, and CI use the same test command

6. Add open-source repo gates.

   - Add a minimal GitHub Actions workflow once coverage/static validation commands exist.
   - If this repo is going public, add or confirm `LICENSE`, `SECURITY.md`, and `CONTRIBUTING.md`.
   - Keep these docs short and practical; they should explain supported setup, issue/security reporting, and the verification command set.

   Verify:

   - a fresh clone has one documented command path for tests and validation
   - CI runs that same path

## Test Plan

1. Add test tooling.

   - Add `coverage` as a dev dependency or test extra.
   - Add a documented command:

   ```bash
   uv run coverage run -m unittest discover -s tests -q
   uv run coverage report -m
   ```

   - Add a threshold command once the first coverage pass is healthy.

2. Split tests by risk area.

   Path and config tests:

   - repo-local default paths
   - env overrides
   - legacy config migration
   - file mode `0600`
   - one TOML render/parse round trip
   - no generated Switchboard TOML actions by default

   Harness registry tests:

   - only Codex is supported now
   - disabled Codex produces no Codex actions
   - unknown harness config is rejected with a helpful error
   - Codex projections include config, AGENTS, hooks, agents, and skills
   - live-sync mappings come from the Codex harness, not hardcoded supervisor lists

   Pack validation tests:

   - every skill has `SKILL.md`
   - every skill frontmatter includes `name` and `description`
   - every subagent TOML includes `name`, `description`, and `developer_instructions`
   - every subagent TOML parses
   - generated Codex config TOML parses
   - hook scripts pass `bash -n`
   - no separate `hooks.json` projection remains unless explicitly enabled for compatibility

   Switchboard and agent tests:

   - main config projects valid server config in memory
   - main config projects valid agent config in memory
   - auth requirements still protect non-loopback server configs
   - archive and ingest API behavior remains stable
   - single-config supervisor startup uses the same config path everywhere

   CLI UX tests:

   - `kk` welcome prints repo-local config and state paths
   - `kk setup` migration note is shown when old config exists
   - `kk preview` groups projections clearly
   - `kk doctor` reports current, legacy, and projection paths

3. Add optional live Codex startup smoke tests.

   These tests should be skipped by default because they require a working signed-in Codex CLI and an interactive terminal startup path.

   Suggested opt-in:

   ```bash
   KLIMKIT_RUN_CODEX_SMOKE=1 uv run python -m unittest tests.test_codex_smoke -q
   ```

   The smoke test should:

   - start the Codex TUI in a pseudo-terminal with no prompt
   - capture startup output long enough for config, hooks, skills, and subagent warnings to print
   - fail on pack-warning patterns such as `hooks.json`, `failed to load hook`, `failed to load skill`, `failed to load subagent`, `invalid config`, `invalid skill`, `invalid subagent`, `toml error`, or `toml parse`
   - terminate Codex before sending any user message

   The conservative `~/.codex` projection remains, so this smoke checks startup behavior for the configured VM and avoids mutating user files.

4. Coverage target.

   - For changed installer/config/harness code: aim for 98-100% line coverage.
   - For total package coverage: add a ratcheting threshold after the first report.
   - Exclude one-off analysis scripts and platform-specific helper scripts only with explicit comments.
   - Do not chase meaningless coverage by testing private formatting minutiae unless the output is user-visible or consumed by another tool.

## Implementation Sequence

1. Baseline and safety net

   - Add coverage dependency and initial report command.
   - Add static pack validation tests first.
   - Add path/config tests that describe the desired repo-local layout.
   - Confirm existing tests still pass before implementation changes.

2. Repo-local paths

   - Update `paths.py`.
   - Update CLI welcome, doctor, preview, and README path mentions.
   - Add migration behavior for old home config.
   - Keep env overrides working.

3. Single config

   - Expand `InstallConfig` and parser/rendering.
   - Move Switchboard server/agent runtime config projection in memory.
   - Stop writing generated Switchboard TOML files by default.
   - Move Telegram settings into the main TOML and update the hook.

4. Harness registry

   - Add the minimal harness module.
   - Move Codex action creation out of `install.py`.
   - Move supervisor live-sync mappings behind the Codex harness.
   - Keep only Codex enabled and documented.

5. Pack template cleanup

   - Add shared pack sections.
   - Generate or compose Codex AGENTS from shared guidance.
   - Add memory/log/task instructions.
   - Inline hooks into Codex TOML projection.

6. README rewrite

   - Replace top-level description.
   - Add Tech Stack.
   - Clarify common commands and role setup.
   - Explain single config, repo-local state, and generated projections.

7. Integration and final verification

   - Run unit tests and coverage.
   - Run static pack validation.
   - Run optional live Codex smoke test if credentials/environment are available.
   - Run `kk setup --skip-services`, `kk preview`, `kk doctor`, and a dry apply path in a temp home/repo fixture if possible.

## Risks And Tradeoffs

- Moving `CODEX_HOME` is the biggest behavioral risk. It can make the "all state/config under `~/klimkit`" goal cleaner, but it changes where Codex stores sessions, auth, history, and runtime DBs. This should be an explicit decision.
- A fully generic harness plugin system would be overbuilt right now. The right first step is a small registry and Codex harness module.
- "Single TOML" should mean one human-edited Klimkit source of truth. External tools may still require generated projection files unless their home directories are also moved.
- Live Codex smoke tests are valuable but should be opt-in. They depend on account state, model availability, network behavior, and CLI changes.
- Near-100% coverage is realistic for the changed installer/config/harness code. It is less useful for generated static assets, one-off analysis scripts, or platform-specific app helpers unless those become supported surfaces.

## Definition Of Done

- `kk` defaults to `~/klimkit/.klimkit/local/klimkit.toml` and repo-local state paths.
- The generated local config is one TOML file with useful comments.
- Switchboard server and agent use the single config by default.
- `kk preview` no longer plans generated `switchboard.toml` or `switchboard-agent.toml` unless compatibility mode is explicitly requested.
- README opens with a clear high-level explanation and has a separate Tech Stack section.
- Codex pack projection is implemented through a harness registry, not hardcoded in `install.py`.
- `packs/codex/AGENTS.md` includes memory/log/task-folder guidance and the `-h-` / `-a-` convention.
- Static validation catches malformed skills, subagents, hooks, and generated TOML.
- Unit tests pass.
- Coverage tooling is installed and reports meaningful coverage.
- Optional live Codex startup smoke test exists and is documented.

## Clarification Questions

1. Should Klimkit set `CODEX_HOME` to a repo-local ignored path so Codex sessions/history/config also live under `~/klimkit/.klimkit`, or should we keep Codex's default home and treat `~/.codex` as a generated projection for now?

   Answer: keep Codex's default home and treat `~/.codex` as a generated projection

2. Should `.klimkit/tasks/` be intentionally git-trackable for task artifacts, or should the whole `.klimkit/` tree stay local and ignored by default?

   Answer: git track all .klimkit!

3. For legacy configs, should `kk setup` only copy old `~/.config/klimkit/klimkit.toml` into the new repo-local path, or should it also offer a cleanup command that removes old generated files after a successful apply?

   Answer: go with whatever recommended, no need to preserve legacy, no users still

## Exec Summary

Implement this as a local-first cleanup, not a big generic framework. Move Klimkit's editable config and runtime state under `~/klimkit/.klimkit`, collapse local settings into one commented `klimkit.toml`, and treat Codex/Code Server/service files as generated projections. Keep Codex's default `~/.codex` home for this pass. Refactor hardcoded Codex install logic into a small harness registry so only Codex is supported now but Claude Code can be added later without rewriting `install.py` and `supervisor.py`. Rewrite README so it explains the product first and the stack separately. Add AGENTS guidance for `.klimkit/memory.md`, `.klimkit/log.md`, and `.klimkit/tasks/<feature>/` with `-h-` and `-a-` file naming. Build tests around paths, harness projections, pack validation, and optional Codex TUI startup smoke checks that fail on startup warnings without sending prompts. Track `.klimkit/` task and proof artifacts in Git.
