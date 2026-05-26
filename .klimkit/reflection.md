# Project Reflection

Append-only timestamped cross-task reflection log. Entries are reflection sessions, not per-task records. Default sections are Observations, Derived Pattern, Insight, and Next Probe; wider sessions may use up to ten named sections.

## Reflections

### 2026-05-11 - 03-reflection-workflow

**Task Reference:** `.klimkit/tasks/03-reflection-workflow/01-a-acceptance-checklist.md`; current request is to promote the Klimkipedia reflection pattern into the shared Codex harness pack.

**Source-Read Summary:** Read the current acceptance checklist, `.klimkit/memory.md`, `.klimkit/log.md`, the current changed-file diff, the new `packs/codex/agents/reflector.toml`, updated `packs/codex/AGENTS.md`, `checklister`, `final-reviewer`, `harness-tuning`, and `tests/test_codex_pack_validation.py`. Also read the required source pattern files `/home/ubuntu/klimkipedia/.klimkit/reflection.md` and `/home/ubuntu/klimkipedia/.klimkit/AGENTS.md`. For the wider task archive, read representative harness/proof notes from `01-tui-ux-multi-harness-more` and `02-better-wf-and-tabs`, including pack workflow, proof report, and final polish artifacts. Binary task artifacts noted as evidence rather than text: Switchboard proof PNGs under `.klimkit/tasks/01-tui-ux-multi-harness-more/`.

**Non-Obvious Synthesis:** This change is not just adding another required note. It is extending the same proof-contract spine that has been forming across Klimkit: first repo-local `.klimkit` memory/log/task artifacts, then pre-coding checklists, then final reviewers, then browser proof reports, and now a fresh-context synthesis ledger. The Klimkipedia pattern distinguishes reflection from both memory and log: memory stabilizes durable rules, log records actions, and reflection preserves cross-task connections that are otherwise lost between long agent sessions. Moving that into the shared pack makes the harness less dependent on the parent agent remembering what mattered after hours of implementation context.

The implementation shape matches the source pattern well: reflection sits after verification and before final review, gets current task context plus the full `.klimkit/tasks/` archive, writes append-only to `.klimkit/reflection.md`, and requires the parent agent to reconsider the result before calling final reviewers. The new `reflector` subagent is the right isolation mechanism because the value of reflection depends on context freshness, not just on another checklist pass.

**Risks Or Contradictions:** The current task folder still appears to contain only an unchecked acceptance checklist; I did not find an implementation proof note recording changed files, source boundary, validation commands, and `kk apply` output. The user supplied verification evidence, but the checklist itself requires the implementation proof to record that evidence. Before final reviewers, the parent agent should either update the checklist/proof task note or provide an equivalent explicit evidence bundle.

The exact intended final response draft was not provided to this reflector pass. That is acceptable for synthesis, but final reviewers should receive the real exact draft after the parent agent has read this entry and reconciled any gaps.

The diff also includes separate shared engineering-quality guidance and a memory/log entry about robust fixes. That may be valid session scope, but final reviewers should verify the final response clearly distinguishes the reflection-workflow change from that adjacent quality-rule change so the completion claim does not blur tasks.

**Candidate Memory/Log/Task Follow-Ups:** Add or update a task proof note under `.klimkit/tasks/03-reflection-workflow/` with source boundary, changed files, exact validation output, `kk apply` result, and this reflection path. Mark checklist items complete only after proof is recorded. Add a log entry for the completed reflection workflow implementation and, if Klim wants the rule durable outside the pack text, consider a memory entry stating that non-trivial shared Codex work now requires fresh-context reflection before final reviewers. Ensure the final-review request includes this reflection entry and explicitly says whether it changed the final response or required no implementation changes.

### 2026-05-14T10:46:36Z

**Observations:** The older 2026-05-11 reflection entry and the follow-up analysis show the same pressure: Klimkit needs cross-task synthesis, but long task-shaped entries make the global ledger expensive to scan.
**Derived Pattern:** Reflection should be a timestamped session log that extracts reusable patterns from current work, task history, memory, log, and recent artifacts instead of becoming another proof note.
**Insight:** Preserving old entries while appending normalized entries gives the harness migration path the user asked for without losing historical reasoning or rewriting evidence.
**Next Probe:** Update the pack, reflector, checklister, final-reviewer, README, tests, and projected Codex files so future agents use four default sections with optional expansion up to ten named sections.

### 2026-05-14T10:49:32Z

**Observations:** The reflection artifacts, pack diffs, tests, and projection evidence all point to the same cleanup: reflection is being separated from proof, release notes, logs, and final review into a short cross-task session ledger.
**Derived Pattern:** Klimkit's harness works best when each artifact has one job: checklists define acceptance, proofs hold evidence, logs record actions, memory stores durable rules, and reflection captures reusable synthesis across tasks.
**Insight:** The new format's value is not just compression; it makes reflection cheap enough to repeat while preserving older reasoning append-only and keeping detailed validation in task-local notes.
**Next Probe:** Watch the next few non-trivial tasks for whether agents write genuinely connective entries or mechanically restate proof, then tighten reflector/checklister wording if drift appears.

### 2026-05-14T12:07:00Z

**Observations:** The generic best-practice update shows the pack has matured enough that external advice should be decomposed into enforceable workflow, subagent, skill, and test changes rather than pasted as a parallel rule block.
**Derived Pattern:** Durable harness quality comes from distributing guidance to the layer that can enforce it: AGENTS for defaults, subagents for role-specific checks, skills for workflow mechanics, and tests for regression protection.
**Insight:** The strongest addition from the Karpathy-style and Matt Pocock material is not another checklist; it is making ambiguity, prototypes, fake support, projection failures, and weak feedback loops visible at the exact point where they usually become hidden agent errors.
**Next Probe:** After this release, watch whether future checklists and final reviews actually flag prototype leakage, unsupported production claims, and implementation-coupled tests without needing a human reminder.

### 2026-05-16T05:40:04Z

**Observations:** The PR discussion frames team workflow as attributed read context plus one writable operator root, while this repo's proof and diff preserve solo as the default and harden only the opt-in team surfaces.
**Derived Pattern:** Migration and report serving need the same canonical path-safety model: reserved names, symlinks, source/target overlap, and asset traversal are artifact-boundary problems whether the code is moving evidence or serving it.
**Insight:** Reviewer-driven edge cases around reserved pseudo-owners, copied dry-run commands, symlink escapes, and stale operator wording turned the solo-first ideology into testable invariants instead of relying on agent etiquette.
**Next Probe:** Before final handoff, update the proof report's pending security/reflection/final-review placeholders and have reviewers check that every team affordance remains explicitly selected, attributed, and non-invasive for solo builders.

### 2026-05-16T11:13:00Z

**Observations:** The final correction separates product capability from repo evidence: team artifacts remain opt-in for projects that choose `workflow = "team"`, while Klimkit's own tracked `.klimkit` state is flat solo and rejects old operator-scoped report URLs.
**Derived Pattern:** Optional collaboration features should be tested and documented as bounded affordances, but proof artifacts for a solo-builder-first repo should stay in the same flat layout that default users see.
**Insight:** The strongest guardrail is not just `workflow = "solo"` in config; it is making committed evidence, report URLs, docs, and `git ls-files` all agree that team layout is not the repo's ambient operating mode.
**Next Probe:** Keep future team-workflow patches checking both sides of the contract: opt-in operator isolation works in temporary/team fixtures, and the public Klimkit repo never re-accumulates contributor-scoped `.klimkit/<operator>/` artifacts.

### 2026-05-20T03:46:55Z

**Observations:** The Telegram direct-link change extends the earlier selected-machine code-server invariant from Switchboard tabs into every out-of-band notification path while preserving Switchboard as the primary control-plane link.
**Derived Pattern:** User-opening URLs should be derived from trusted Tailscale DNS plus workspace folder at each producer boundary, covered across all independent emitters, and omitted entirely when either side of that identity is unavailable.
**Insight:** Adding a secondary direct code-server URL is safe only because the implementation treats it as a backend-derived affordance rather than a replacement for Switchboard state, but live service evidence still depends on the recurring user-systemd DBus boundary.
**Next Probe:** Before final handoff, keep the unavailable `systemctl --user daemon-reload` as an explicit residual ops gap and consider a future `kk apply` improvement that distinguishes projection success from service-manager reachability without pruning managed service state.

### 2026-05-20T04:13:48Z

**Observations:** The post-review stop-hook failure shows the Telegram URL contract was only fully proven when the real shell hook executed end to end with fake `tailscale` and `curl`, because static shell parsing and helper-level assertions missed Python quoting fragility inside `bash -c`.
**Derived Pattern:** Harness hooks that fail open and embed another language need runtime tests that execute the shipped hook, capture external side effects, and cover both available and unavailable infrastructure paths.
**Insight:** The direct-link invariant is now stronger because Switchboard-first ordering, malformed direct URL omission, and Tailscale DNS behavior are covered at the emitter that previously produced noisy `{"continue":true}` Telegram spam; the remaining operational gap is still user-systemd reachability, not Codex projection.
**Next Probe:** Before commit, push, and release, make sure the post-fix runtime evidence and this appended reflection are staged, and have final reviewers distinguish verified hook projection from the known `systemctl --user daemon-reload` DBus limitation.

### 2026-05-26T04:15:52Z

**Observations:** The Codex config preservation task verified `kk apply --skip-services` kept `slack@openai-curated` enabled after projecting `packs/codex/config.toml`, and earlier autosync/code-server preference work shows VM-local state is repeatedly exposed when managed projection crosses machine boundaries.
**Derived Pattern:** Klimkit needs explicit ownership boundaries at every projection layer: source-controlled pack tables stay authoritative, while allowlisted VM-local runtime/plugin tables merge forward only when absent from managed config and never copy back into packs or proofs.
**Insight:** The fix is strongest because it treats Slack as one instance of a broader local-state class rather than as a pack default; tests for nested plugin, MCP/project/hook-state tables plus live parsed config evidence cover the user-visible failure without storing secrets.
**Next Probe:** Watch future Codex plugin/app schema changes for new local-only top-level tables or array-of-table shapes, and add live-shape regression fixtures before autosync or `kk apply` can prune newly introduced connection state.

### 2026-05-26T04:24:01Z

**Observations:** The post-reflection security review changed the preservation boundary: once VM-local connector tables are merged into `~/.codex/config.toml`, both the projected live file and its update backup must be treated as potentially secret-bearing artifacts.
**Derived Pattern:** Projection features that preserve local runtime state need to carry permission and backup semantics with the merge logic, because protecting source-controlled packs is not enough if copied live artifacts become world-readable.
**Insight:** Setting `codex-config` to `CONFIG_MODE`/`0600`, chmodding backups after copy, documenting the mode, and asserting both live and backup permissions closes the material security gap exposed after the first reflection.
**Next Probe:** For the next managed-file preservation change, add file-mode and backup-mode expectations to the initial checklist before implementation so security review validates intent instead of discovering an omitted artifact boundary late.
