# Critical Repo Review: Ambiguity, Inconsistency, and Production Polish Gaps

## Scope

This review covers the repository as it exists before implementing the local-first config and multi-harness work requested in `01-h-initial-task.md`.

I reviewed:

- root and pack AGENTS guidance
- top-level README and Switchboard spec
- installer, path, supervisor, Switchboard, and Switchboard agent code
- Codex pack files, agents, hooks, and skills
- tests and local test tooling
- ignored files, task artifacts, and repo hygiene
- current OpenAI Codex docs for config, hooks, skills, subagents, and `codex exec`

I ran the current test suite:

```bash
uv run python -m unittest discover -s tests -q
```

Result during review:

```text
Ran 69 tests in 5.220s
OK
```

I also checked coverage availability:

```bash
uv run python -m coverage run -m unittest discover -s tests -q
```

Result:

```text
No module named coverage
```

## Top-Level Assessment

Klimkit has a strong core idea: one repo should reproduce an agent-ready operator machine, including instructions, harness assets, services, dashboards, and machine-specific state. The current implementation already has useful pieces: a preview/apply installer, manifest ownership, backups, tests, a real Switchboard app, Codex pack assets, and role-aware service planning.

The main problem is that the product model is clearer in the user's requested direction than it is in the repo. The repo currently exposes implementation details first, stores local state across home directories, hardcodes Codex in installer and supervisor paths, and maintains multiple config shapes that users and future maintainers must mentally reconcile.

For production-level open-source polish, the repo needs fewer implicit conventions and more source-of-truth discipline:

- one human-edited Klimkit config
- one documented local state model
- one pack projection model
- one README product story
- one security model for code-server, Switchboard, helper servers, and agent launches
- one test story that includes coverage, static pack validation, CI, and optional live smoke tests

## Critical Findings

### 1. The README opens with implementation details instead of the product promise

Evidence:

- `README.md:5` describes Klimkit as a "Python operator kit"
- `README.md:6` leads with "Codex-oriented machines"
- `README.md:7` says "TOML config"
- `README.md:8` frames the project around "without a TUI"

This is accurate, but it is not the right first impression for a production-grade repo. It explains the mechanism before it explains the job. A new user should learn that Klimkit makes an agent-ready machine reproducible before learning that the implementation is Python, TOML, and Codex-oriented.

Ambiguity:

- Is Klimkit primarily a personal dotfiles/install repo, a reproducible operator environment, a Switchboard product, or a harness-pack manager?
- Is "without a TUI" a design goal users should care about, or just an implementation detail?
- Is Codex the product, or is Codex one supported harness inside a broader machine setup system?

Plan implication:

- Rewrite the README opening around "reproducible agent-ready machine" and move Python/TOML/Codex details into a separate Tech Stack section.

### 2. The local-first promise is contradicted by current default paths

Evidence:

- `src/klimkit/paths.py:11` defaults state to `~/.local/state/klimkit`
- `src/klimkit/paths.py:16` defaults config to `~/.config/klimkit`
- `src/klimkit/install.py:120` to `src/klimkit/install.py:141` uses home-based config and state defaults
- `src/klimkit/apps/switchboard/daemon.py:171` to `src/klimkit/apps/switchboard/daemon.py:232` defaults Switchboard state under `~/.local/state/klimkit`
- `src/klimkit/tools/switchboard_agent/switchboard_agent.py:127` to `src/klimkit/tools/switchboard_agent/switchboard_agent.py:170` defaults agent state under `~/.local/state/klimkit`
- README path examples repeatedly point to `~/.config/klimkit`, `~/.local/state/klimkit`, and `~/.codex`

The requested product direction is "everything under the Klimkit repo except externally required projections." The current repo still behaves like a traditional XDG app.

Ambiguity:

- Should config/state be moved under `~/klimkit/.klimkit` for every process, including Switchboard DBs and agent DBs?
- Should `~/.codex` remain a generated projection, or should Klimkit set `CODEX_HOME` under the repo-local ignored tree?
- Should `.klimkit/tasks/` be tracked while `.klimkit/local/` and `.klimkit/state/` are ignored?

Plan implication:

- Change defaults to repo-local ignored local/state directories, preserve env overrides, and make the `~/.codex` question explicit before implementation.

### 3. Config is split across multiple TOML files and duplicate writers

Evidence:

- `src/klimkit/install.py:161` to `src/klimkit/install.py:210` renders the main Klimkit config
- `src/klimkit/install.py:213` to `src/klimkit/install.py:248` renders a separate Switchboard server config
- `src/klimkit/install.py:251` to `src/klimkit/install.py:277` renders a separate Switchboard agent config
- `src/klimkit/install.py:443` to `src/klimkit/install.py:477` plans writes for generated Switchboard TOML files
- `src/klimkit/tools/supervisor/supervisor.py:190` to `src/klimkit/tools/supervisor/supervisor.py:220` has another machine config writer with its own shape

This creates an unclear ownership model:

- Users edit one TOML but Klimkit writes more TOML files.
- Switchboard and agent configs are both generated artifacts and operational inputs.
- The supervisor has config serialization logic that can drift from installer serialization.

Ambiguity:

- Which TOML is authoritative after `kk apply`?
- Are `switchboard.toml` and `switchboard-agent.toml` user-editable, generated, or legacy compatibility files?
- Should the supervisor ever write config directly, or should it consume the same parser/renderer as `kk`?

Plan implication:

- Collapse local settings into one commented `klimkit.toml`, project Switchboard server/agent runtime config in memory, and deprecate separate generated TOML files except as explicit compatibility mode.

### 4. Codex is hardcoded as the only mental model, not represented as one harness

Evidence:

- `src/klimkit/install.py:479` to `src/klimkit/install.py:499` hardcodes Codex pack paths and projection targets
- `src/klimkit/tools/supervisor/supervisor.py:223` to `src/klimkit/tools/supervisor/supervisor.py:232` hardcodes Codex live-sync mappings
- README repeatedly presents Codex as central before defining a harness abstraction
- `packs/codex/` contains reusable workflow guidance that is not clearly separated from Codex-specific material

The task explicitly asks for future harness support while supporting only Codex today. That does not require a plugin framework, but it does require Codex to live behind a small registry or renderer boundary.

Ambiguity:

- What belongs to "shared agent guidance" versus "Codex-specific projection"?
- Should the pack source be edited directly, generated from templates, or composed from shared fragments?
- What is the future unit of extension: harness, pack, projection, or component?

Plan implication:

- Introduce a minimal harness registry and move Codex projection logic out of generic installer/supervisor code.

### 5. Codex docs and current projection targets do not fully line up

Evidence:

- Current Codex docs say global AGENTS guidance lives under `CODEX_HOME`
- Klimkit currently projects root guidance to `~/AGENTS.md`
- Current Codex docs support inline hook config in `config.toml`
- Klimkit currently maintains `packs/codex/hooks.json` as a separate hook source
- Current Codex docs warn when `hooks.json` and inline hooks coexist in the same config layer

The existing setup may work, but it is not aligned with the cleanest current Codex model.

Ambiguity:

- Is `~/AGENTS.md` intentionally retained for compatibility, or should Klimkit move to `CODEX_HOME/AGENTS.md`?
- Should Klimkit remove `hooks.json` entirely and generate inline hooks in the Codex TOML projection?
- Should validation test against Codex's current parser by running `codex exec`?

Plan implication:

- Prefer inline hooks in generated Codex TOML and add static plus optional live validation. Decide whether to keep `~/AGENTS.md` as a legacy projection.

### 6. Security-sensitive defaults need an explicit threat model

Evidence:

- `templates/code-server/config.yaml` sets `bind-addr: 127.0.0.1:8080`, `auth: none`, and `cert: false`
- `templates/code-server/User/settings.json` disables workspace trust and allows automatic tasks
- `src/klimkit/tools/switchboard_agent/switchboard_agent.py:719` to `src/klimkit/tools/switchboard_agent/switchboard_agent.py:734` binds the helper server to `0.0.0.0`
- `src/klimkit/apps/switchboard/static/app.js` defines `CODEX_LAUNCH_FLAGS` with `--dangerously-bypass-approvals-and-sandbox`
- `src/klimkit/install.py:521` to `src/klimkit/install.py:533` installs code-server through `curl -fsSL https://code-server.dev/install.sh | sh`
- `src/klimkit/apps/switchboard/daemon.py:2425` to `src/klimkit/apps/switchboard/daemon.py:2431` builds the auth cookie without a `Secure` flag

Some of these choices may be intentional for a private tailnet operator box. They are still security-sensitive and should be documented as deliberate, previewed clearly, and covered by tests where possible.

Ambiguity:

- Is Switchboard intended to be private-loopback only, tailnet-only, or safe behind arbitrary reverse proxies?
- Is code-server auth intentionally delegated to Tailscale Serve, or should Klimkit ever set code-server auth?
- Should the helper server bind to all interfaces, loopback only, or a configurable host?
- Should "dangerously bypass approvals and sandbox" be the default launch mode, a role-specific setting, or an explicit user choice?
- Is `curl | sh` acceptable as the default installer path for a production-open-source repo, or should it be opt-in with pinned/provenance-aware alternatives?

Plan implication:

- Add a security model section to docs, make risky defaults visible in preview output, add config knobs where necessary, and gate supply-chain-sensitive installers behind explicit choices.

### 7. Switchboard server auth is better than older docs imply, but still under-documented

Evidence:

- `src/klimkit/apps/switchboard/daemon.py:2068` to `src/klimkit/apps/switchboard/daemon.py:2206` authorizes API reads and mutations
- `src/klimkit/apps/switchboard/daemon.py:2219` to `src/klimkit/apps/switchboard/daemon.py:2237` protects local write routes with API auth plus JSON and either header token or same-origin checks
- `src/klimkit/apps/switchboard/daemon.py:2310` to `src/klimkit/apps/switchboard/daemon.py:2323` enforces a max JSON body size
- `src/klimkit/apps/switchboard/daemon.py:2332` to `src/klimkit/apps/switchboard/daemon.py:2336` allows loopback when no token is configured
- `src/klimkit/apps/switchboard/daemon.py:2441` to `src/klimkit/apps/switchboard/daemon.py:2443` rejects non-loopback configs without an auth token

This is a solid base. The issue is not that auth is missing. The issue is that the public docs and config comments do not make the intended model obvious.

Ambiguity:

- Are query-string tokens acceptable as a login bootstrap if they are converted to cookies?
- Should cookies be `Secure` when the public URL is HTTPS, even if the local daemon sees HTTP behind a proxy?
- What exactly does "loopback without auth" mean when exposed through code-server/Tailscale flows?

Plan implication:

- Document the actual auth model and add small hardening improvements such as `Secure` cookie support when configured behind HTTPS.

### 8. The Switchboard spec is useful but stale and partly inconsistent with code

Evidence:

- `src/klimkit/apps/switchboard/spec.md` is labeled "Draft for review"
- The spec contains rebuild-era failure analysis that may no longer reflect the current daemon
- The spec references path and config models that conflict with the desired repo-local single TOML direction
- The spec names tests as `pytest`, while the repo uses `unittest`

Ambiguity:

- Is the spec intended to be a living source of truth, historical rationale, or a stale design note?
- Should implementation plans update the spec before code changes, after code changes, or retire it into an archive?
- Which test framework should contributors use?

Plan implication:

- Either update the spec as part of the implementation or explicitly mark it historical. README and tests should consistently say `unittest` unless the repo adopts pytest.

### 9. Repo docs have stale path references and stale names

Evidence:

- `.gitignore` ignores `src/klimkit/apps/switchboard2/static/reports/*`, but there is no `switchboard2` app directory
- `assets/brand/README.md` references `src/klimkit/apps/switchboard2/static/icons/`
- README still describes old home config paths as primary
- Some discussions still refer to "Switchboard 2" concepts while the actual app path is `src/klimkit/apps/switchboard`

Ambiguity:

- Was `switchboard2` renamed to `switchboard`, or is another app expected later?
- Should generated reports still live under Switchboard static assets, or should that ignore rule be removed?

Plan implication:

- Clean stale `switchboard2` references as part of docs/repo hygiene.

### 10. Test coverage exists but is not production-grade yet

Evidence:

- Unit tests pass
- `coverage` is not installed
- No `.github` workflow directory exists
- No lint, formatting, type check, shell script, TOML pack validation, or live harness validation command is documented as a supported gate
- Existing tests likely assert some old home path behavior, so they currently protect parts of the model the task wants to change

Ambiguity:

- Should the project standardize on `unittest` only, or add pytest?
- What minimum CI gate is required for an open-source repo?
- Should optional live Codex checks run in CI, locally only, or behind a secret-enabled workflow?

Plan implication:

- Add coverage tooling, static validation, and CI. Keep live Codex smoke tests opt-in because they need credentials/network/account state.

### 11. The installer has ownership safety, but supply-chain and preview semantics need tightening

Evidence:

- The installer tracks managed files through a manifest and backup directory
- It avoids overwriting unmanaged files unless ownership is known or force is used
- `code-server` installation is represented as a command action using `curl | sh`
- Service installation and Tailscale Serve actions are planned alongside file writes

This is close to a good operator pattern, but external command actions should be treated as high-risk, high-visibility actions.

Ambiguity:

- Is `kk apply` allowed to install software from the network by default?
- Should network installers require a separate flag such as `--allow-network-installers`?
- Should commands be separated into "file projection", "service management", and "external installer" plan groups?

Plan implication:

- Make preview output classify external installers clearly and consider requiring explicit opt-in for network install scripts.

### 12. Root AGENTS and Codex pack AGENTS guidance can drift

Evidence:

- Root `AGENTS.md` contains shared coding-agent instructions
- `packs/codex/AGENTS.md` contains very similar instructions for projected Codex guidance
- The root file says custom agents are managed from `~/klimkit/packs/codex/agents/`
- The pack file says custom agents are managed from `packs/codex/agents/`

The difference is small, but it shows the drift risk. The pack likely should be composed from shared guidance and harness-specific text, not maintained as near-duplicate prose.

Ambiguity:

- Which AGENTS file is the source of truth?
- Should repo-local AGENTS include instructions that are not projected to Codex?
- Should pack AGENTS include `.klimkit/memory.md`, `.klimkit/log.md`, and task-folder conventions?

Plan implication:

- Add shared pack fragments and tests that generated AGENTS content includes memory/log/task guidance exactly once.

### 13. `.klimkit/memory.md` and `.klimkit/log.md` exist but have no local convention yet

Evidence:

- `.klimkit/memory.md` and `.klimkit/log.md` exist in the working tree and are currently empty
- `~/klimkipedia/projects/AGENTS.md` provides a clear convention for memory and log files
- The current Codex pack guidance does not yet teach the local `.klimkit/` convention

Ambiguity:

- Should missing memory/log files be created automatically by agents during meaningful work?
- Should entries be prepended or appended?
- Should task artifacts under `.klimkit/tasks/` be git-tracked?

Plan implication:

- Add AGENTS guidance and templates for `.klimkit/memory.md`, `.klimkit/log.md`, and task folders, including `-h-` and `-a-` filename markers.

### 14. Public open-source repo polish is incomplete

Evidence:

- No CI workflow is present
- No coverage command works out of the box
- No clear SECURITY policy is visible in the reviewed tree
- No license file was visible in the top-level file scan
- README contains implementation detail but not a concise maintainer/contributor path
- Risky local automation defaults are not collected in one security model section

Ambiguity:

- Is Klimkit intended to become a public open-source package, a personal repo, or both?
- If public, what license and vulnerability reporting process should apply?
- Which commands define the release gate?

Plan implication:

- Add CI, license/security/contributing polish if this repo is intended to be shared beyond a personal operator setup.

## What Is Already Solid

The review should not flatten everything into criticism. Several foundations are good:

- The test suite exists and passes.
- The installer uses plans, manifests, backups, and ownership checks rather than blind writes.
- Switchboard auth has meaningful protections around non-loopback exposure, API auth, body size limits, and local write routes.
- The repo already has a real Codex pack with agents, skills, hooks, and config.
- The CLI already has preview/apply concepts, which is the right operator UX for risky machine changes.
- The product direction does not require a rewrite. It requires aligning paths, docs, config ownership, harness boundaries, and validation.

## Ambiguities To Resolve Before Implementation

1. Should Klimkit set `CODEX_HOME` under `~/klimkit/.klimkit/harnesses/codex`, or keep projecting to `~/.codex` for the first pass?

2. Should `.klimkit/tasks/` be intentionally git-trackable while `.klimkit/local/`, `.klimkit/state/`, `.klimkit/backups/`, and `.klimkit/logs/` are ignored?

3. Should legacy `~/.config/klimkit` and `~/.local/state/klimkit` files be copied only, or should Klimkit offer an explicit cleanup command after migration?

4. Should code-server network installation through `curl | sh` remain available by default, require explicit opt-in, or be replaced with a pinned/package-manager-specific path?

5. Should Switchboard agent helper bind to `0.0.0.0` by default, or should the default be loopback with a documented override?

6. Should launching Codex with `--dangerously-bypass-approvals-and-sandbox` be the default from Switchboard, a config option, or a separate "trusted local box" mode?

7. Should the Switchboard spec remain a living spec, or should it be split into current docs plus historical rebuild notes?

8. Should the repo stay on `unittest`, or intentionally add pytest? The docs should stop saying both.

9. Should Klimkit add public open-source metadata now: LICENSE, SECURITY.md, CONTRIBUTING.md, and GitHub Actions?

10. Should generated projections include comments warning users not to edit them, while the single local config contains the meaningful knob comments?

## Review-Driven Implementation Priorities

1. Make the product legible.

   Rewrite the README opening, add a Tech Stack section, and describe the operator model before implementation details.

2. Make config ownership obvious.

   Move editable local config and runtime state under repo-local ignored directories. Collapse Klimkit, Switchboard server, Switchboard agent, and Telegram local settings into one TOML.

3. Separate source config from projections.

   Treat Codex, code-server, systemd, launchd, and any compatibility TOML files as generated outputs. Make generated files say where the source config lives.

4. Put Codex behind a harness boundary.

   Add a small registry that only supports Codex today but removes Codex path hardcoding from generic install and supervisor code.

5. Harden and document runtime exposure.

   Document loopback, Tailscale, cookies, helper server binding, code-server auth delegation, workspace trust, automatic tasks, and sandbox-bypassing Codex launches.

6. Add validation gates.

   Add coverage, static pack validation, CI, and optional `codex exec` smoke tests that fail on warnings from malformed hooks, skills, subagents, or config.

7. Clean stale names and docs.

   Remove stale `switchboard2` references, align test framework docs, and decide whether the Switchboard spec is current or historical.

## Bottom Line

The repo is already useful, but it is not yet polished enough to present as a top-tier open-source operator kit. The highest-leverage work is not adding more features. It is removing ambiguity: one config, clear paths, clear projections, clear harness boundaries, clear security posture, and clear validation gates.
