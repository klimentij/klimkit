# Project Reflection

Append-only timestamped cross-task reflection log. Entries are reflection sessions, not per-task records. Default sections are Observations, Derived Pattern, Insight, and Next Probe; wider sessions may use up to ten named sections.

## Reflections

### 2026-05-11 - 03-reflection-workflow

**Task Reference:** `.klimkit/tasks/03-reflection-workflow/01-a-acceptance-checklist.md`; current request is to promote the operator knowledge base reflection pattern into the shared Codex harness pack.

**Source-Read Summary:** Read the current acceptance checklist, `.klimkit/memory.md`, `.klimkit/log.md`, the current changed-file diff, the new `packs/codex/agents/reflector.toml`, updated `packs/codex/AGENTS.md`, `checklister`, `final-reviewer`, `harness-tuning`, and `tests/test_codex_pack_validation.py`. Also read the required source pattern files `<knowledge-base-repo>/.klimkit/reflection.md` and `<knowledge-base-repo>/.klimkit/AGENTS.md`. For the wider task archive, read representative harness/proof notes from `01-tui-ux-multi-harness-more` and `02-better-wf-and-tabs`, including pack workflow, proof report, and final polish artifacts. Binary task artifacts noted as evidence rather than text: Switchboard proof PNGs under `.klimkit/tasks/01-tui-ux-multi-harness-more/`.

**Non-Obvious Synthesis:** This change is not just adding another required note. It is extending the same proof-contract spine that has been forming across Klimkit: first repo-local `.klimkit` memory/log/task artifacts, then pre-coding checklists, then final reviewers, then browser proof reports, and now a fresh-context synthesis ledger. The operator knowledge base pattern distinguishes reflection from both memory and log: memory stabilizes durable rules, log records actions, and reflection preserves cross-task connections that are otherwise lost between long agent sessions. Moving that into the shared pack makes the harness less dependent on the parent agent remembering what mattered after hours of implementation context.

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

### 2026-05-21T10:12:05Z

**Observations:** Symphony reframes exactly the pressure Klimkit has been building around: Switchboard makes parallel Codex work visible, but the human still dispatches sessions; Symphony moves the control plane to durable work items and lets a daemon own dispatch, retry, and handoff.
**Derived Pattern:** Klimkit's next orchestration layer should preserve its local evidence model while adding a tracker adapter and run scheduler above existing worktrees, reports, Tailscale surfaces, and harness packs.
**Insight:** Linear is not the essence of Symphony; the essence is a normalized work-item contract with strong status, dependency, proof, and handoff semantics. GitHub Issues can be Klimkit's default if Projects/labels/issue fields are treated as an adapter detail rather than assumed to be equivalent to Linear.
**Next Probe:** Draft a small Klimkit orchestration spec that stops at Human Review first, uses `.klimkit/tasks` as the durable evidence spine, and compares a local queue with a GitHub Issues/Projects adapter before any daemon implementation.

### 2026-05-22T02:59:45Z

**Observations:** The operator knowledge base raw/index pass shows that Klim's search and orchestration problems are linked: the raw corpus is large enough to need a maintained evidence index, while Symphony-style work dispatch needs small context packs that can pull prior thinking into each runnable issue.
**Derived Pattern:** Klimkit's autonomy layer should combine two adapters, not one: a work-item adapter for GitHub/Linear/local tasks and a knowledge adapter for operator knowledge base/wiki/raw retrieval, with `.klimkit/tasks` bridging execution evidence back into durable memory.
**Insight:** The years-long trajectory is a steady move from chat surfaces toward explicit system boundaries. The next boundary is not a prettier board; it is an issue-backed scheduler plus proof packet pipeline that can use GitHub dependencies for DAG execution and operator knowledge base search for operator-specific context.
**Next Probe:** Write the first orchestrator spec around local queue plus GitHub Issues/Projects, and separately promote SQLite FTS from experiment to maintained operator knowledge base search before relying on raw-corpus context packs in autonomous runs.

### 2026-05-22T03:04:00Z

#### Observations

The marketing hygiene patch turns a private-pride moment into a public repo signal by using the cropped terminal proof instead of the surrounding Slack thread. That preserves the point of the story without importing private conversational context.

#### Derived Pattern

Klimkit's public README works best when it shows evidence discipline in the first screenful: not just the product logo or dashboard screenshots, but a concrete long-running agent result and the checks that made the result inspectable.

#### Insight

The 7.5 hour screenshot is valuable because it makes the abstract proof-contract thesis visceral. The launch story should keep emphasizing that the scarce asset is not runtime or autonomy by itself; it is reviewable state after the run ends.

#### Next Probe

After this hygiene lands, watch whether visitors click into `.klimkit/tasks`, reports, or harness files from the README. If they do, add a small public example artifact gallery; if they only react to the dashboard, sharpen the README toward proof reports and final-review gates.

### 2026-05-22T03:08:51Z

**Observations:** The marketing patch publishes lightweight repo-facing evidence in README while the richer browser proof packet remains a local/Tailscale artifact with screenshot and video assets intentionally ignored by Git.
**Derived Pattern:** Klimkit launch material needs two evidence tiers: small public assets that make the proof-contract story fast to load, and heavier proof reports that stay inspectable through the configured report server unless they are deliberately promoted into a public gallery.
**Insight:** The 7.5 hour crop is the right public hook precisely because it is bounded and cheap; the final handoff should not imply the full proof-report media bundle is public GitHub content just because the report HTML exists in `.klimkit/reports`.
**Next Probe:** If Klim wants HN readers to inspect proof artifacts directly, create a consciously public example artifact page with tracked media or stable hosted assets instead of relying on ignored report media or private Tailscale URLs.

### 2026-05-22T03:30:23Z

#### Observations

The post-review corrections tightened the proof boundary rather than changing the marketing thesis: the Telegram screenshot now removes actual tailnet URLs, the proof report includes both Switchboard screenshots, and the proof note no longer calls uncommitted files tracked or already public.

#### Derived Pattern

Marketing hygiene for Klimkit has to distinguish three states that are easy to blur: ready in the working tree, committed/tracked in Git, and live on GitHub. The same applies to evidence media: public-facing assets can live in non-ignored repo paths, while report media remains local/Tailscale unless deliberately promoted.

#### Insight

The corrected package is stronger because it does not trade proof for exposure. It shows enough evidence to make the 7.5 hour story credible, removes unnecessary live-network details from the public README asset, and leaves heavier QA evidence behind the report server where the harness expects it.

#### Next Probe

Before publishing the HN link, either commit and push the README/assets as the public surface, or create a dedicated public proof-gallery page with intentionally committed/hosted media so readers do not depend on ignored report assets or private Tailscale URLs.

### 2026-05-22T04:08:45Z

#### Observations

Klim's correction exposed the difference between numeric optimization and visual acceptability: the first image pass satisfied the byte-size instinct but damaged the public first impression. The publish gap was equally concrete: until `f1eb323` was pushed and checked in the browser, the work existed only in local proof.

#### Derived Pattern

README marketing assets should be judged by the rendered GitHub page, not only by local file size or a local report. For dark UI screenshots, a slightly larger high-quality JPEG can be the better public artifact than a smaller noisy PNG.

#### Insight

The launch workflow needs a hard distinction between "ready", "committed", "pushed", and "visible on GitHub main". The final proof should include the live README image URLs and release state because the user's trust issue was not just asset quality; it was whether the public repo actually changed.

#### Next Probe

Before the HN post goes out, inspect the GitHub README once more from a logged-out or clean browser and decide whether the Telegram screenshot belongs in the public narrative or should be replaced by a smaller purpose-built notification example.

### 2026-05-24T05:52:04Z

**Observations:** The stop-hook deep link is a narrow extension of the Telegram opening contract: Switchboard stays primary, direct code-server remains infrastructure-dependent, and `codex://threads/<raw-session-id>` is rendered only when the hook payload has a non-empty `session_id`, with runtime hook tests plus projection/cmp evidence covering the shipped path.
**Derived Pattern:** Klimkit notification links are safest when each affordance owns one boundary: Switchboard for control-plane state, code-server for Tailscale workspace reachability, and Codex app links for raw agent thread identity without normalization.
**Insight:** The earlier post-review stop-hook quoting failure shaped the right proof level here; adding a link inside a fail-open hook is not proven by static diff alone, but by executing the hook with fake external commands and verifying both presence and omission cases.
**Next Probe:** Before final reviewers, close the checklist/proof gap around main push, autosync consumption, and latest-release evidence, and avoid claiming publication until concrete SHA/tag checks exist.

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

### 2026-05-27T05:19:03Z

**Observations:** The plugin-first task deliberately reverses the older fork/Switchboard/autosync onboarding emphasis while preserving the repo-managed harness as an advanced path and carrying forward task 09's VM-local Codex state boundary.
**Derived Pattern:** Klimkit needs layered adoption contracts: the public Codex plugin should install skills, workflow, and safe reference material; `kk apply` should remain the explicit machine-projection boundary; autosync and Telegram should stay opt-in automation beyond that boundary.
**Insight:** The extraction is strongest when docs and tests prevent surface confusion, because a plugin can make Klimkit's completion discipline portable without inheriting yolo-mode, hooks, connector state, Tailscale serving, or daemon-managed restarts.
**Next Probe:** Before final review, make the handoff precise that live plugin installation was intentionally skipped, v0.1.14 covered the prior autosync-default-off publication, and this branch's plugin-first work is verified by manifest/CLI-help/static tests until it lands and is released.

### 2026-05-27T08:12:45Z

**Observations:** The publish/live-plugin phase proved a different boundary than the original extraction: Git marketplace upgrade moved the live Codex cache from `0.1.14` to `0.1.15`, while the post-merge VM marketplace now follows released `main` at `f8b8700`.
**Derived Pattern:** Klimkit plugin distribution needs two proofs: source/release proof that the public marketplace points at the intended commit, and home/cache proof that Codex has materialized the expected version and skill text under `~/.codex/plugins/cache`.
**Insight:** Keeping the repo-managed harness as the advanced path is credible only if the plugin path is verified with Codex's real cache behavior; the decisive evidence is not just PR merge or manifest validation, but the installed cache containing the modified skill after `codex plugin marketplace upgrade` and `codex plugin add`.
**Next Probe:** When the next plugin package release changes installable content, bump the plugin manifest version deliberately, verify cache movement on a non-development marketplace ref if possible, and record the installed cache path before final review rather than relying only on release notes.

### 2026-05-27T08:40:43Z

**Observations:** The skill cleanup follows the `v0.1.15` plugin-first release/cache proof by turning the installable package from a copied harness bundle into five validated skills with proper titles, concise trigger descriptions, OpenAI UI metadata, and `klimkit-workflow`-owned references.
**Derived Pattern:** Plugin distribution works best when the plugin owns only skill-level surfaces and public-safe references, while `kk apply` remains the boundary for home-level AGENTS, subagents, hooks, config, Switchboard, Tailscale Serve, autosync, and connector state.
**Insight:** Removing `plugins/klimkit/reference/**` is a quality improvement, not a loss, because users now see the workflow through the skill invocation path that Codex actually loads, and tests enforce that broad copied harness material does not silently become plugin API.
**Next Probe:** Before publishing these content changes, bump the plugin manifest version deliberately and repeat the live marketplace/cache upgrade proof from task 10; until then, the current evidence supports source/package correctness but not installed-cache availability.

### 2026-05-28T02:37:11Z

**Observations:** The Symphony/control-plane research resolves several prior threads into one staged path: Matt Pocock's composable task skills supply method, Klimkit's checklist/proof/reflection/final-review gates supply trust, the neutral private candidate walkthrough/report pattern supplies human-review UX, and Symphony supplies the later scheduler/runner shape.
**Derived Pattern:** Klimkit's next autonomy layer should expose skills first, make GitHub Issues/Projects the manual control-plane contract, then add a thin orchestrator that consumes the same issue, workpad, worktree, and `.klimkit/tasks` evidence surfaces before attempting PR/CI/merge shepherding.
**Insight:** The useful synthesis is not choosing between skill-only distribution and orchestration; it is making skills define the stable, reviewable contracts that an eventual daemon can call without replacing Klimkit's local evidence spine or leaking private-derived implementation text.
**Next Probe:** For the first implementation wave, test whether `klimkit-report-server`, `klimkit-walkthrough`, and `klimkit-github-control-plane` can be built as public-safe skills with shared validation for both root `skills/` distribution and Codex plugin packaging before any runner service is introduced.

### 2026-05-28T09:43:22Z

**Observations:** The root `skills/` package turns the plugin-first and control-plane research threads into a Vercel Skills CLI install/update surface, while deliberately keeping legacy Switchboard, sync, and repo-managed runtime concepts out of the new skill text.
**Derived Pattern:** Klimkit is splitting portable agent behavior into skill-local instructions, references, scripts, and metadata, with long-running runtime machinery treated as deprecated compatibility unless it is reintroduced through a narrow skill-owned helper.
**Insight:** The first report-server reference script is the right salvage model: useful runtime affordances can migrate forward when they become public-safe, progressively loaded, validated skill assets instead of root-level operational assumptions.
**Next Probe:** Before release, make root `skills/` and plugin packaging agree on the canonical skill set, then migrate only the remaining useful helper patterns into skill-local references without reviving the deprecated control plane.

### 2026-05-29T10:18:05Z

**Observations:** The create-worktree skill is another useful helper migration: a proven repo-local script pattern now lives as a skill-owned deterministic script with a short SKILL.md routing layer and a reference file for flags and handoff fields.
**Derived Pattern:** Klimkit skills should own the operational helper code they need when the helper is narrow, repeatable, and safer as a tested script than as ad hoc shell reconstruction.
**Insight:** The important compatibility detail is remote-first ref resolution for explicit `main`/`dev` syncs; otherwise a stale local `dev` branch could silently diverge from the workflow Klim uses for stable-main, integration-dev, feature-worktree stacks.
**Next Probe:** When this lands, consider adding a fresh-machine smoke check that installs the skill and uses the bundled script against a temporary bare remote, so distribution and behavior are tested together.
