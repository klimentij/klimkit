# Review And Plan Checklist

This checklist tracks the requested review and planning work for `01-tui-ux-multi-harness-more`.

Status meanings:

- `[x]` completed
- `[ ]` implementation or verification work still pending

## Clarified Decisions From `05-h-start.md`

- [x] Keep Codex's default home and treat `~/.codex` as a generated projection.
- [x] Git-track `.klimkit/`, including task artifacts.
- [x] Do not preserve legacy Klimkit configs for compatibility; there are no current users.
- [x] Implement the plan fully, not only write planning artifacts.
- [x] Write an agent-authored results/proof artifact as `05-a-...`.
- [x] Run security and other subagent review before final response.
- [x] Require three parallel final reviewer PASS decisions before final response.

## User Request Tracking

- [x] Read the human task file at `.klimkit/tasks/01-tui-ux-multi-harness-more/01-h-initial-task.md`
- [x] Preserve the `-h-` means human and `-a-` means agent filename convention
- [x] Perform an ultra-deep critical repo review
- [x] Surface ambiguity and inconsistency, not only implementation steps
- [x] Aim the review at production-level open-source repo polish
- [x] Write the critical review as `02-a-critical-repo-review.md`
- [x] Write the implementation plan with clarifications as `03-a-implementation-plan-with-clarifications.md`
- [x] Create a large checklist to reduce missed requirements
- [x] Update the implementation plan after the critical review findings
- [x] Verify current tests before final response
- [x] Send the final artifacts and draft response to three parallel `final_reviewer` agents before final response
- [x] Proceed only after all three final reviewers give PASS

## Repository Context Reviewed

- [x] Root `AGENTS.md`
- [x] User-provided AGENTS instructions in the conversation
- [x] `~/klimkipedia/projects/AGENTS.md` memory/log convention
- [x] Example Klimkipedia memory file
- [x] Example Klimkipedia log file
- [x] `.klimkit/memory.md`
- [x] `.klimkit/log.md`
- [x] Top-level `README.md`
- [x] `pyproject.toml`
- [x] `.gitignore`
- [x] `src/README.md`
- [x] `src/klimkit/paths.py`
- [x] `src/klimkit/cli.py`
- [x] `src/klimkit/install.py`
- [x] `src/klimkit/tools/supervisor/supervisor.py`
- [x] `src/klimkit/apps/switchboard/daemon.py`
- [x] `src/klimkit/apps/switchboard/spec.md`
- [x] `src/klimkit/apps/switchboard/static/index.html`
- [x] `src/klimkit/apps/switchboard/static/app.js`
- [x] `src/klimkit/tools/switchboard_agent/switchboard_agent.py`
- [x] `templates/code-server/config.yaml`
- [x] `templates/code-server/User/settings.json`
- [x] `packs/codex/AGENTS.md`
- [x] `packs/codex/config.toml`
- [x] `packs/codex/hooks.json`
- [x] `packs/codex/hooks/stop-notify.sh`
- [x] `packs/codex/agents/*.toml`
- [x] `packs/codex/skills/**`
- [x] `assets/brand/README.md`
- [x] Current tests under `tests/`
- [x] Current Git status

## External Context Checked

- [x] OpenAI Codex non-interactive `codex exec` docs
- [x] OpenAI Codex CLI reference
- [x] OpenAI Codex hooks docs
- [x] OpenAI Codex skills docs
- [x] OpenAI Codex subagents docs
- [x] OpenAI Codex AGENTS.md guidance docs

## Critical Review Coverage

- [x] Product positioning and README first impression
- [x] Tech stack documentation gap
- [x] Local-first path mismatch
- [x] XDG path usage in current code
- [x] Repo-local `.klimkit` target model
- [x] Main Klimkit config file shape
- [x] Split Switchboard server config
- [x] Split Switchboard agent config
- [x] Duplicate supervisor config serialization
- [x] Telegram config split into env file
- [x] Codex pack hardcoding in installer
- [x] Codex pack hardcoding in supervisor live sync
- [x] Harness registry need
- [x] Shared pack guidance need
- [x] Root AGENTS and pack AGENTS drift risk
- [x] Codex docs alignment for `CODEX_HOME`
- [x] Codex docs alignment for inline hooks
- [x] Codex docs alignment for skills and subagents
- [x] Optional live Codex startup smoke test feasibility
- [x] code-server auth and bind behavior
- [x] code-server workspace trust behavior
- [x] code-server automatic task behavior
- [x] code-server network installer risk
- [x] Switchboard API auth model
- [x] Switchboard loopback/no-token model
- [x] Switchboard JSON body limits
- [x] Switchboard auth cookie hardening gap
- [x] Switchboard query-token ambiguity
- [x] Switchboard agent helper bind behavior
- [x] Switchboard-launched Codex sandbox-bypass flags
- [x] Switchboard spec staleness
- [x] `pytest` versus `unittest` inconsistency
- [x] stale `switchboard2` references
- [x] `.gitignore` stale paths
- [x] assets brand README stale paths
- [x] lack of coverage dependency
- [x] lack of CI workflow
- [x] lack of static pack validation gate
- [x] lack of documented release/verification gate
- [x] open-source metadata gaps
- [x] `.klimkit/tasks/` tracking ambiguity
- [x] `.klimkit/memory.md` and `.klimkit/log.md` convention gap

## Artifacts Written

- [x] `02-a-critical-repo-review.md` exists
- [x] `02-a-critical-repo-review.md` includes scope and method
- [x] `02-a-critical-repo-review.md` includes test baseline result
- [x] `02-a-critical-repo-review.md` includes coverage tooling failure
- [x] `02-a-critical-repo-review.md` separates critical findings from already-solid foundations
- [x] `02-a-critical-repo-review.md` names ambiguity explicitly
- [x] `02-a-critical-repo-review.md` maps findings to plan implications
- [x] `02-a-critical-repo-review.md` includes implementation priorities
- [x] `03-a-implementation-plan-with-clarifications.md` exists
- [x] `03-a-implementation-plan-with-clarifications.md` includes the target local-first model
- [x] `03-a-implementation-plan-with-clarifications.md` includes the single TOML plan
- [x] `03-a-implementation-plan-with-clarifications.md` includes the harness-agnostic pack plan
- [x] `03-a-implementation-plan-with-clarifications.md` includes the README plan
- [x] `03-a-implementation-plan-with-clarifications.md` includes AGENTS memory/log/task guidance
- [x] `03-a-implementation-plan-with-clarifications.md` includes review-driven hardening additions
- [x] `03-a-implementation-plan-with-clarifications.md` includes the test plan
- [x] `03-a-implementation-plan-with-clarifications.md` includes implementation sequence
- [x] `03-a-implementation-plan-with-clarifications.md` includes risks and tradeoffs
- [x] `03-a-implementation-plan-with-clarifications.md` includes definition of done
- [x] `03-a-implementation-plan-with-clarifications.md` includes clarification questions
- [x] `03-a-implementation-plan-with-clarifications.md` ends with an exec summary
- [x] `04-a-review-and-plan-checklist.md` exists

## Future Implementation Todos

- [x] Add repo-local path constants for local config, state, backups, and logs
- [x] Preserve existing env overrides
- [x] Keep `.klimkit/tasks/` intentionally trackable
- [x] Ignore `.klimkit/local/`, `.klimkit/state/`, `.klimkit/backups/`, and `.klimkit/logs/` as private/runtime subtrees
- [x] Remove old default dependence on `~/.config/klimkit` and `~/.local/state/klimkit`
- [x] Collapse Klimkit, Switchboard server, Switchboard agent, and notifications config into one TOML
- [x] Stop writing generated Switchboard TOML files by default
- [x] Move Telegram settings into main TOML
- [x] Add useful comments for every meaningful generated config knob
- [x] Add a minimal harness registry
- [x] Move Codex projection action generation out of `install.py`
- [x] Move Codex live-sync mappings out of supervisor hardcoding
- [x] Keep the Codex pack clean and hand-authored without introducing `packs/shared/`
- [x] Add `.klimkit/memory.md` and `.klimkit/log.md` templates/guidance
- [x] Add `-h-` and `-a-` task-file convention to projected AGENTS guidance
- [x] Inline Codex hooks into generated Codex TOML projection
- [x] Decide whether to set repo-local `CODEX_HOME`
- [x] Rewrite README opening around product purpose
- [x] Add README Tech Stack section
- [x] Replace primary README home path references with repo-local paths
- [x] Add README Generated Projections section
- [x] Add README Security Model section
- [x] Clean stale `switchboard2` references
- [x] Update or archive Switchboard spec
- [x] Align docs on `unittest` versus pytest
- [x] Add coverage dependency and commands
- [x] Add static pack validation tests
- [x] Add optional live Codex startup smoke tests
- [x] Add CI workflow for the supported validation command set
- [x] Review code-server installer supply-chain behavior
- [x] Make network installer actions explicit in preview
- [x] Review helper server bind default
- [x] Add cookie `Secure` behavior for HTTPS exposure
- [x] Make sandbox-bypassing Codex launch flags named and documented
- [x] Add or confirm open-source metadata such as LICENSE, SECURITY.md, and CONTRIBUTING.md
- [x] Commit and push completed implementation changes

## Verification Checklist

- [x] Current unit tests pass before implementation planning
- [x] Coverage tool absence is recorded
- [x] Task artifact filenames follow the human/agent convention
- [x] Critical review and implementation plan use no Markdown tables
- [x] The implementation plan includes no more than three primary clarification questions
- [x] The checklist distinguishes completed review work from future implementation work
- [x] Three final reviewers have inspected the final artifacts and draft response
- [x] Final response only after all three reviewers return PASS
- [x] Unit tests pass after implementation
- [x] Coverage command runs after implementation
- [x] Static pack validation passes after implementation
- [x] Optional live Codex smoke test is present and skipped unless explicitly enabled
- [x] `05-a-results-and-proof.md` records commands, results, and any limitations
- [x] Security review PASS is recorded
- [x] Code review or equivalent implementation review PASS is recorded
- [x] Three final reviewer PASS decisions are recorded for the implementation result
