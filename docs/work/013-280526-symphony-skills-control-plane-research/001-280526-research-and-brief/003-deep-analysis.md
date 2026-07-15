# Symphony, Matt Skills, Klimkit, And A Skill-Only Control Plane

## Source Manifest

This is planning and research only. No adapted skills or production code were implemented.

Public sources inspected:

- OpenAI Symphony local checkout: `<symphony-repo>`, branch `main`, commit `2c1851830477434100fdb8980fcc1fce1a8af81d`, clean at inspection time.
- Symphony files read: `README.md`, `SPEC.md`, `elixir/README.md`, `elixir/WORKFLOW.md`, `elixir/AGENTS.md`, and `.codex/skills/{commit,debug,land,linear,pull,push}/SKILL.md`.
- Prior Klimkit Symphony research: `.klimkit/tasks/07-symphony-reflection/01-a-research-reflection.md` and `.klimkit/tasks/07-symphony-reflection/02-a-expanded-strategy.md`.
- Prior Matt Pocock skills analysis: `.klimkit/tasks/12-matt-skills-merge-plan/01-a-analysis-and-plan.md`.
- Matt Pocock skills snapshot: `third_party/mattpocock-skills/`, copied from `https://github.com/mattpocock/skills` at commit `b8be62ffacb0118fa3eaa29a0923c87c8c11985c`, MIT license preserved.
- Current Klimkit workflow surface: `plugins/klimkit/skills/klimkit-workflow/SKILL.md` and its references.

A private candidate-skill source was also inspected under an ignored local path. This public analysis only summarizes neutral patterns from it. It does not name the source, branch, remote, local checkout path, or quote private source text.

## User-Provided Baseline

Klim's current GitHub experiment is a tracker/control-plane slice, not full Symphony.

What exists now:

- GitHub Issues are work items.
- GitHub issue dependencies represent blockers.
- GitHub Projects are the board/state surface.
- Labels provide repo-visible fallback state.
- `KK Status` provides richer orchestration state in the Project.
- The first real operator knowledge base work item is on the board and has moved to human review.

What does not exist yet:

- No daemon polls eligible issues.
- No automatic claim/lock prevents duplicate workers.
- No scheduler checks blockers before launch.
- No automatic worktree creation per issue.
- No Codex app-server runner starts from issue state.
- No retry, restart, or stale-run recovery.
- No live dashboard of running agents.
- No automatic workpad updates while an agent works.
- No PR creation/attachment loop.
- No CI, review, rework, merge shepherding.
- No enforcement that blocked issues cannot run.

That distinction is exactly right. The GitHub slice is the substrate. Symphony is the missing runner layer above it.

## Three Approaches Side By Side

| Dimension | Matt Pocock skills | Klimkit today | Symphony |
| --- | --- | --- | --- |
| Core idea | A sharp toolbox of task-specific skills. | Evidence-first Codex workflow and proof spine. | Long-running scheduler/runner for issue-backed work. |
| Workflow location | Inside individual `SKILL.md` files plus a setup skill. | Home/repo instructions plus `klimkit-workflow` and `.klimkit` artifacts. | Repo-owned `WORKFLOW.md` loaded by a daemon. |
| Work item model | Optional docs/issues created by skills. | `.klimkit/tasks/` notes, plus GitHub when humans use it. | Tracker issue is the runnable unit. |
| Execution model | Human invokes the right skill. | Human/Codex thread executes with checklist/proof gates. | Daemon polls eligible issues and launches agent sessions. |
| State model | Skill-local checklists, issue labels, repo docs. | `.klimkit/log.md`, task notes, reports, reflection, final review. | Tracker status plus orchestrator runtime state and workpad comments. |
| Isolation | Depends on the repo/session. | Worktrees and Switchboard exist as advanced Klimkit infrastructure. | Per-issue workspace manager is a first-class component. |
| Proof | Skill-dependent. | Required task proof and UI reports when relevant. | Workpad/status/PR links, with validation delegated to workflow policy. |
| Strength | Low ceremony, strong task routing, excellent domain skills. | High trust in completion claims and local evidence. | True unattended execution, retries, concurrency, and dispatch discipline. |
| Weakness | No global completion contract or daemon. | Human still dispatches sessions; orchestration is not automatic. | More service complexity and operational surface. |

## Where The Workflow Lives

Matt's repo has no global `AGENTS.md` equivalent. Its workflow is compositional:

1. Install the skill package.
2. Run a setup skill in a target repo.
3. Invoke the skill that matches the job: diagnosis, TDD, PRD, issue slicing, triage, prototype, architecture review, and so on.

That makes each skill easy to understand and easy to distribute, but it means no one skill owns the universal "done" contract.

Klimkit currently owns the universal "done" contract. Its workflow says: read repo context, write a checklist, implement narrowly, verify, record proof, reflect, run final review, then report. That is stronger for reliability, but weaker as a skill ecosystem because too much guidance historically lived in harness references rather than task-specific skills.

Symphony puts the workflow in `WORKFLOW.md`, not in scattered skills. The service reads tracker state, creates a workspace, renders a prompt from issue data, launches Codex app-server, and lets the in-repo workflow tell the agent how to update the tracker/workpad/PR. Symphony's `.codex/skills` are operational helpers for that runner: pull, push, commit, land, debug, and tracker access.

The merge should preserve all three ideas:

- Matt's skills should teach precise task methods.
- Klimkit should keep the proof/completion gates.
- Symphony should provide the unattended runner only where automatic execution is wanted.

## GitHub Project Model

The correct GitHub model is not "put all work in one repo." It is:

- Issues stay in the repository that owns the code, docs, or artifact.
- A personal aggregate GitHub Project can include issues across personal repos.
- A product-specific GitHub Project can include only issues inside that product boundary.
- Repo-local labels remain a fallback state surface for humans and simple tooling.
- Project fields such as `KK Status` hold richer orchestration state when the Project is available.

That gives each issue the right permissions, audit trail, branch linkage, and PR linkage while still letting Klim see a personal or product-wide board.

The orchestrator should treat GitHub Projects as an index/view, not as the canonical work item store. The canonical runnable unit is still the repo issue. The Project supplies prioritization, cross-repo visibility, and richer board state.

## Mapping Symphony Into Klimkit Terms

| Symphony concept | Klimkit term | GitHub adaptation |
| --- | --- | --- |
| Issue | Work item | GitHub Issue in the owning repo. |
| Active states | Runnable queue | Project `KK Status` plus labels such as `kk/todo`, `kk/in-progress`, `kk/rework`. |
| Terminal states | Finished/closed work | Closed issue, `Done`, `Cancelled`, or equivalent label/field. |
| Blockers | Dependency graph | GitHub issue dependencies plus optional fallback links/labels. |
| Orchestrator | Thin Klimkit runner | Polls eligible issues, claims, launches, retries, reconciles. |
| Workspace manager | Worktree stack manager | Creates one isolated worktree/workspace per issue/run. |
| Agent runner | Codex app-server or Codex app launcher | Starts the session with rendered issue/workflow context. |
| Workpad comment | Issue-facing run ledger | Single persistent issue comment with plan, checklist, proof links, status. |
| Status surface | Board plus dashboard | GitHub Project, labels, optional local dashboard, report index. |
| Workflow loader | Skill/workflow loader | Uses `klimkit-workflow` and task-specific skills instead of one monolithic prompt. |
| Retry queue | Recovery loop | Retries stale/failed active runs with bounded attempts and notes. |
| Human Review | Handoff state | Project field/label plus PR link, `.klimkit` proof, and final-review notes. |

Symphony is most useful to Klimkit as a layer above the current harness, not as a replacement. The existing `.klimkit/tasks`, proof reports, Tailscale report URLs, Switchboard, and worktree discipline become the runner's local evidence layer.

## What The Private Candidate Skills Add

The private candidate source matters because it shows that "everything as a skill" can work even for workflows that currently feel like infrastructure.

Public-safe patterns observed:

- `walkthrough`: a strong proof/handoff skill. It creates a Tailscale-hosted static HTML walkthrough report with steps, screenshots, security/redaction rules, URL validation, and task-log integration. This is not the same as Matt's prototype or architecture report. It is closer to a Klimkit proof report specialized for human review.
- Worktree stack management: a skill that asks supported local launcher tooling for the true frontend/backend/report URLs instead of reconstructing them by hand. This maps directly to Symphony's workspace manager and Klimkit's Switchboard/worktree surfaces.
- Domain tool setup/config/task skills: a pattern for packaging external-service expertise as skills. The value is not the specific service; it is the separation into setup, config, task authoring, realtime/UI integration, and cost audit.
- Forensic session investigation: a debugging skill that first collects a bundle through one supported command, then analyzes locally and reports ranked causes. This is close to Matt's `diagnose` skill, but with stronger evidence-bundle discipline.

Verdict: preserve the walkthrough pattern. It should become a first-wave Klimkit skill because it connects the skill-only direction to the existing Tailscale/report-server proof system.

## Skill-Only Distribution Is Viable, With One Caveat

Klim's proposed direction is sound: distribute Klimkit as skills first, not as a custom home projection system by default.

The caveat is that "skill-only" should not mean "no code." A skill can own references, templates, scripts, and install snippets. The important boundary is that the code needed for a capability is bundled inside the skill package and installed or copied by the agent only when the skill is invoked.

That suggests this rule:

> Klimkit public distribution should expose capabilities as skills. Runtime services are allowed, but their setup/check/run logic and source templates should live under the relevant skill, not as an implicit global harness projection.

For example:

- A `klimkit-report-server` skill can check whether Tailscale is up, check whether the report server is running, copy the bundled report-server reference implementation if missing, start it, and verify the Tailscale URL.
- A `klimkit-walkthrough` skill can depend on that report-server skill conceptually, then write `.klimkit/reports/<slug>/index.html` and validate screenshots/links.
- A `klimkit-github-control-plane` skill can create issues, link dependencies, put them into the personal or product Project, set labels/fields, and update the workpad.
- A later `klimkit-orchestrator` skill can install or operate the thin daemon, but the daemon itself remains a runtime service after installation.

This keeps distribution simple while acknowledging that unattended orchestration still requires a process, locks, workspaces, and recovery state.

## Proposed Merged Architecture

### Layer 1: Skills As The Product Surface

Klimkit should publish a root `skills/` package for the Vercel skills installer and use the Codex plugin as the Codex-native install surface. The source of truth should be one set of Klimkit skills, generated or copied into the plugin package as needed.

Recommended first-class skills:

- `klimkit-workflow`: invariant checklist, proof, reflection, and final-review gates.
- `klimkit-setup`: repo setup for `.klimkit`, domain docs, issue tracker docs, and skills pointers.
- `klimkit-diagnose`: Matt-style feedback-loop-first diagnosis plus Klimkit evidence.
- `klimkit-tdd`: Matt-style red/green/refactor plus task proof.
- `klimkit-to-issues`: PRD/plan slicing into repo issues with acceptance criteria.
- `klimkit-triage`: issue grooming, labels, project fields, and agent-ready briefs.
- `klimkit-report-server`: Tailscale/report server check/install/start/verify skill.
- `klimkit-walkthrough`: static HTML walkthrough reports with screenshot evidence.
- `klimkit-worktree-stack`: create/check/record isolated local worktree stacks.
- `klimkit-github-control-plane`: GitHub Issues/Projects/dependencies/labels/workpad operations.

Matt's strongest skills become task methods inside Klimkit's proof gates. The candidate walkthrough/report skill becomes the proof UX layer. Symphony's workpad and runner concepts become the future automation layer.

### Layer 2: Manual GitHub Control Plane

Before a daemon exists, agents should still be able to create and triage issues correctly.

Minimum behavior:

- Create issues in the owning repo, not a central dumping repo.
- Add them to the appropriate aggregate Project.
- Set labels and `KK Status`.
- Link blockers/dependencies.
- Write an agent-ready brief with acceptance criteria and validation.
- Link `.klimkit/tasks/<slug>/` proof when work is performed.
- Move to Human Review only when proof and PR/review status support it.

This is the "tracker/control-plane only" mode. It is useful immediately and aligns with the user's current experiment.

### Layer 3: Thin Orchestrator

The next layer is a small runner that reads the GitHub control plane and actually launches/refuses work.

Responsibilities:

- Poll eligible issues across configured repos/projects.
- Enforce blockers before launch.
- Claim/lock one issue before starting.
- Create an isolated worktree/workspace.
- Render a Codex prompt from issue, project fields, `.klimkit` context, and skill guidance.
- Launch Codex app-server or an equivalent Codex app-controlled runner.
- Update the single issue workpad while running.
- Attach PRs and proof links.
- Retry/restart stale active runs.
- Move issues through `In Progress`, `Human Review`, `Rework`, `Merging`, and terminal states only when gates are satisfied.

This is the part that turns the current GitHub experiment into real Symphony-like behavior.

### Layer 4: Review/Merge Shepherd

Full Symphony behavior needs the PR loop:

- Attach PR to issue.
- Sweep review comments and CI failures.
- Move issue to rework when needed.
- Relaunch or resume work.
- Land only after approval and checks pass.
- Close/mark done only after merge state and release/proof expectations are satisfied.

This should come after the thin orchestrator works for `Todo -> In Progress -> Human Review`.

## Recommended State Model

Use a normalized work item internally:

```text
WorkItem
  source_repo
  issue_number
  issue_url
  aggregate_project
  product_project_or_null
  title
  body
  labels
  kk_status
  blockers
  priority
  assigned_runner_or_null
  claim_token_or_null
  worktree_path_or_null
  workpad_comment_id_or_null
  task_artifact_path_or_null
  report_url_or_null
  pr_url_or_null
  last_run_status
  last_error_or_null
```

GitHub remains the external system of record. The orchestrator can keep local runtime state, but it should be able to reconcile from GitHub plus filesystem artifacts after restart.

## Phased Plan

### Phase 1: Skill-Only Refactor

Goal: make skills the primary Klimkit distribution surface.

- Keep the copied Matt snapshot unmodified as reference.
- Adapt only selected Matt workflows into Klimkit-prefixed skills.
- Add a root `skills/` layout for Vercel skills installer compatibility.
- Keep Codex plugin skills and root skills in sync through a small validator or generation step.
- Keep advanced repo-managed projection as secondary.

### Phase 2: Walkthrough And Report Server

Goal: preserve the strongest proof UX from the candidate skills.

- Create `klimkit-report-server`.
- Create `klimkit-walkthrough`.
- Bundle report-server reference code under the skill if that is the chosen public distribution model.
- Require Tailscale URL verification when a Tailscale name is available.
- Keep reports under `.klimkit/reports/` and task notes under `.klimkit/tasks/`.

### Phase 3: GitHub Control Plane Skill

Goal: make issue/project creation and triage agent-friendly.

- Create issues in owning repos.
- Add to the personal aggregate Project or a product-specific Project based on config.
- Manage labels, `KK Status`, dependencies, workpad comment, PR links, and proof links.
- Keep labels as fallback state when Projects fields are unavailable.
- Add privacy/trust-boundary checks before cross-repo aggregation.

### Phase 4: Thin Orchestrator

Goal: add the missing Symphony behavior without overbuilding.

- Start with one configured project/repo set.
- Implement eligibility, blocker checks, claim/lock, worktree creation, launch, status updates, and stale-run recovery.
- Stop first at `Human Review`.
- Reuse `klimkit-workflow`, `klimkit-worktree-stack`, and `klimkit-github-control-plane` instead of embedding all policy in the daemon.

### Phase 5: PR/CI/Merge Loop

Goal: complete the unattended lifecycle.

- Add PR attachment, CI check polling, review comment sweep, rework relaunch, merge shepherding, and release-state validation where repo policy requires it.

## Risks And Controls

- Privacy leakage: aggregate Projects can mix repos. Keep issues in owning repos and require explicit project mapping by trust boundary.
- Skill-only confusion: skills can install runtime code, but they must make that boundary explicit and idempotent.
- Duplicate execution: GitHub Projects alone do not lock work. The orchestrator needs claim tokens and reconciliation.
- Blocker enforcement: issue dependency links are visibility until the runner refuses blocked work.
- API complexity: GitHub Projects v2 fields and issue dependencies are less straightforward than labels. Keep labels as fallback.
- Trigger ambiguity: many skills can apply to one task. Use concise skill descriptions and a setup block that explains routing.
- Distribution drift: Codex plugin and Vercel skills installer can diverge. Add tests that compare installable skill manifests.
- Report-server assumptions: Tailscale/report URLs must be checked live, not assumed from config.
- Private-derived content: do not publish private candidate skill text directly. Recreate public Klimkit versions from requirements, patterns, and explicit approval.

## Recommendation

Adopt the skill-only direction as the default product shape, but do not pretend skills alone replace orchestration.

The strongest merged model is:

1. Matt-style task skills for how to think and work.
2. Klimkit workflow gates for proof and completion quality.
3. Candidate-style walkthrough/report skills for human-readable evidence.
4. Symphony-style thin orchestrator for unattended execution when the GitHub board is ready.

Immediate next implementation should not start with the daemon. It should start with the skills that make manual work better and prepare the daemon's contracts:

- `klimkit-report-server`
- `klimkit-walkthrough`
- `klimkit-github-control-plane`
- `klimkit-to-issues`
- `klimkit-triage`
- updated `klimkit-workflow` composition guidance

After those exist, build the orchestrator against the same contracts instead of inventing a second workflow.

## Open Decisions For Klim

- Should public adapted skill names be `klimkit-*` to avoid collisions, or short names like `walkthrough` for ergonomics?
- Should the report server's full code be bundled inside a skill as reference/scripts, or kept in a small runtime package installed by a skill?
- What is the initial GitHub Project mapping: one personal aggregate plus one product-specific board, or only the personal aggregate first?
- Should the first orchestrator use Codex app-server directly, Switchboard, or both behind a runner adapter?
- Should Linear compatibility remain a future adapter only, or should the data model be designed and tested with a fake Linear adapter from the start?
