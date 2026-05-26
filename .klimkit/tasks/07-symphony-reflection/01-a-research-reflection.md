# Symphony Reflection For Klimkit

Date: 2026-05-21
Author: Codex
Task type: research / product reflection

## Request

Klim asked for a new `.klimkit` task that deeply reflects on OpenAI's Symphony article in the context of Klimkit, evaluates whether the idea is a good and feasible Klimkit evolution, then inspects the Symphony repo to understand why it uses Linear instead of GitHub Issues and what Klimkit would lose by using GitHub Issues.

## Sources Read

- OpenAI article: `https://openai.com/index/open-source-codex-orchestration-symphony/`
- Symphony repo: `https://github.com/openai/symphony`
- Local clone inspected at `/tmp/openai-symphony`, commit `2c1851830477434100fdb8980fcc1fce1a8af81d`
- Symphony files: `README.md`, `SPEC.md`, `elixir/README.md`, `elixir/WORKFLOW.md`, `elixir/lib/symphony_elixir/tracker.ex`, `elixir/lib/symphony_elixir/linear/client.ex`, `elixir/lib/symphony_elixir/linear/adapter.ex`, `.codex/skills/linear/SKILL.md`
- Klimkit context: `README.md`, `src/README.md`, `src/klimkit/tools/supervisor/README.md`, `src/klimkit/apps/switchboard/README.md`, `.klimkit/memory.md`, `.klimkit/log.md`, `.klimkit/reflection.md`
- Current GitHub docs/changelog checked for GitHub Issues, Projects, dependencies, issue fields, and agent-session surfaces.
- Linear docs checked for issue relations and GitHub integration.

## Summary Of Symphony

Symphony is less a giant product than a shift in control plane. Instead of a human opening several Codex sessions, feeding them tasks, remembering where each one is, and nudging them through PRs, Symphony treats the issue tracker as the work queue and state machine. A long-running daemon polls eligible issues, creates an isolated workspace per issue, launches Codex in app-server mode, keeps retrying while the ticket remains active, and exposes status so humans review work rather than supervise each session.

The OpenAI article's core claim is that interactive coding agents hit a human-attention ceiling. Engineers can comfortably manage a few active sessions, but beyond that the bottleneck becomes remembering context, chasing stalled sessions, and shepherding PRs. Symphony changes the unit of management from "a Codex session" to "a deliverable." Tickets can be larger, can form dependency DAGs, can spawn follow-up tickets, and can be started from anywhere because the daemon keeps running.

The repo confirms this framing. `SPEC.md` defines Symphony as a tracker reader plus scheduler/runner. It explicitly separates tracker reads and scheduling from ticket writes, which are normally done by the agent using tools in the workflow. The reference implementation is an Elixir/OTP prototype with a Linear adapter, per-issue workspaces, Codex app-server runner, retries, dynamic `WORKFLOW.md` reloads, optional dashboard/API, and a Linear GraphQL tool injected into the Codex session.

The important article detail for Klimkit is the tradeoff: Symphony reduces context switching, but also reduces mid-flight human steering. OpenAI's answer was not "humans fix bad outputs manually"; it was stronger harness engineering, more guardrails, better skills, browser QA, smoke tests, and clearer definitions of done. That maps directly to Klimkit's existing direction.

## Klimkit Context

Klimkit already has most of the substrate Symphony assumes:

- A long-running supervisor daemon.
- Switchboard as a multi-machine work dashboard.
- Per-worktree/code-server workspace practice.
- Tailscale-served private control surfaces.
- A repo-managed Codex harness pack with agents, skills, hooks, and completion notifications.
- `.klimkit/tasks`, proof reports, memory, logs, reflection, and final-review culture.
- Existing recommendation to keep 5-7 worktrees open across machines, each on its own branch.

The main gap is that Klimkit still treats the human as the dispatcher. Switchboard keeps agent tabs visible, but Klim chooses or creates the worktree, opens the tab, starts the Codex session, watches progress, and decides what to do next. Symphony would move Klimkit toward "work items become runnable objects": file a task, mark it eligible, and Klimkit allocates a worktree/machine/session, tracks progress, and returns proof.

So Symphony is not foreign to Klimkit. It is the next natural layer above Switchboard. Switchboard currently answers "where are my agents and workspaces?" A Klimkit Symphony-style layer would answer "which work items are eligible, which machine owns each one, what state is each run in, and what proof or PR is ready for review?"

## Is This A Good Evolution?

Yes, but only if Klimkit adapts the concept instead of cloning Symphony whole.

The good fit:

- Klimkit's identity is "agentic engineering across machines, under control"; issue-backed orchestration is exactly the missing control plane above parallel worktrees.
- Klimkit already cares about reproducible harnesses and proof artifacts; Symphony's success depends on that more than on Linear itself.
- The `.klimkit` artifact layer is a strong local source of truth for plans, proofs, reports, and reflections. It could become the local evidence backing an external issue.
- Switchboard can become the operator surface for orchestration status, not just iframe tabs.
- The supervisor can host an orchestrator loop, or a sibling service can do it.

The caution:

- Klimkit should not start by promising unattended merge-to-main behavior. That is a later-stage capability after issue routing, worktree isolation, app-server launching, status reporting, proof generation, PR creation, and review loops are all reliable.
- Klimkit's current trust model is high-trust yolo-mode on dedicated VMs. More autonomy increases blast radius, especially if agents can fetch untrusted issues, run commands, open network links, and push PRs.
- The biggest engineering risk is not polling a tracker; it is making restarts, cancellation, duplicate dispatch prevention, dirty worktrees, stalled sessions, auth failures, and partial PR handoffs legible and recoverable.
- Klimkit should preserve interactive mode. Some ambiguous work is better as a human-steered Codex session; Symphony itself says not every task fits ticket-level autonomy.

Recommended direction: build "Klimkit Orchestrator" as an optional layer over Switchboard, with a conservative first milestone:

1. Treat a work item as canonical: external issue or `.klimkit/tasks/<slug>/` task note.
2. Generate or select a worktree per item.
3. Launch a Codex session with the current harness and a task prompt.
4. Record runtime state in Switchboard and `.klimkit`.
5. Stop at "Human Review" with a proof report and branch/PR link.

Only later add CI watching, rebase/retry, review-comment loops, and merge shepherding.

## What The Symphony Repo Actually Uses Linear For

I did not find an explicit "we chose Linear over GitHub Issues because..." section in the repo. The rationale is inferable from the spec, workflow, Linear adapter, and skills.

The reference implementation uses Linear as:

- The candidate-work source: poll by `project_slug` and configured active states.
- The task state machine: statuses such as `Todo`, `In Progress`, `Human Review`, `Merging`, `Rework`, and terminal states.
- The scheduling metadata source: `priority`, `labels`, `assignee`, timestamps, URL, and normalized identifier.
- The branch metadata source: `branchName`.
- The dependency source: Linear issue relations are normalized into `blocked_by`.
- The agent workpad: one persistent `## Codex Workpad` Linear comment is updated in place with plan, acceptance criteria, validation, notes, and confusions.
- The proof/link surface: PRs can be attached with `attachmentLinkGitHubPR`, generic URLs can be attached, and files/videos can be uploaded for comments.
- The follow-up task target: agents are instructed to create separate Backlog issues for out-of-scope discoveries, with related/blocking links.

The implementation also injects a `linear_graphql` tool into Codex app-server sessions, so the agent can query/update Linear using the same Symphony-provided auth instead of each repo inventing shell helpers.

My read: Linear is used because it is a purpose-built, project-level planning system with customizable workflow states, first-class issue relations, issue priority, branch metadata, GitHub PR integration, comment/attachment APIs, and a good mobile/PM/designer work-entry path. OpenAI's article frames Symphony around a "project-management board like Linear"; the repo implements the first adapter against the tracker their workflow was already using.

This does not mean Symphony fundamentally requires Linear. `SPEC.md` has an issue tracker client boundary and says the current supported tracker kind is Linear. A GitHub tracker is feasible if we define equivalent normalized fields and accept some adapter complexity.

## GitHub Issues As Klimkit's Default Tracker

GitHub Issues is feasible for Klimkit, and probably a better default for Klimkit's public/fork-first model, but "GitHub Issues" alone is not equivalent to the Linear surface Symphony uses.

GitHub has enough building blocks:

- Issues, labels, assignees, comments, milestones, linked PRs, and native issue/PR APIs.
- Issue dependencies and sub-issues are now documented GitHub features.
- Projects v2 provides boards/tables and custom fields accessible through GraphQL.
- Issue fields are in public preview for selected organizations, with typed metadata and API support.
- GitHub recently added more agent-session visibility directly in Issues and Projects.

The practical issue is where status and priority live. A GitHub issue's native lifecycle is mostly open/closed. A Symphony-like workflow needs `Todo`, `In Progress`, `Human Review`, `Merging`, `Rework`, blocked states, maybe per-state concurrency, and sorting priority. On GitHub, that probably means one of:

- GitHub Projects v2 status and priority fields.
- Labels such as `kk:todo`, `kk:in-progress`, `kk:human-review`, `kk:merging`, `priority:p1`.
- New issue fields where available.
- A repo-local `.klimkit` state mirror tied to issue numbers.

The cleanest Klimkit default is likely GitHub Issues plus GitHub Projects v2 when available, with a label-only fallback for simple repos.

## What Klimkit Would Lose By Using GitHub Issues Instead Of Linear

Losses or added complexity:

- No built-in Linear-style ticket key. GitHub issue numbers are repo-scoped; Klimkit would need canonical IDs like `owner/repo#123` or GraphQL node IDs for multi-repo orchestration.
- Plain GitHub Issues do not provide custom workflow states as native issue state. Projects fields or labels are required.
- Priority is not a universal native issue field. It must come from project fields, preview issue fields, labels, or a `.klimkit` mirror.
- Linear's `branchName` is a ready tracker field. GitHub can link branches/PRs, but Klimkit may need to generate branch names itself.
- Linear's project-centric API query is straightforward for this use case. GitHub Projects v2 requires querying project items and field values, then mapping those back to issues/PRs.
- Linear's workpad/comment/upload flow is already encoded in Symphony's `linear` skill. GitHub equivalents are possible but need a separate skill and media/proof attachment strategy.
- Linear's GitHub integration can update issue status based on PR lifecycle while keeping the board as the source of work. With GitHub as the source, Klimkit must avoid double-counting an issue and its PR as separate project items.
- Product/designer/mobile task-entry ergonomics may be better in Linear for some teams.

What Klimkit gains:

- One public, open-source-friendly system of record beside code, PRs, CI, releases, and permissions.
- Fewer required external services and tokens.
- Better fit with Klimkit's fork-first operator repo model.
- Native PR/CI/review context without syncing between two planning systems.
- Easier adoption by users who already have GitHub but not Linear.

Net: using GitHub Issues would not lose anything essential to the orchestration idea. It would lose some polished project-management ergonomics and ready-made structured fields, and it would force Klimkit to be explicit about status/priority/dependency mappings. For Klimkit, that tradeoff is probably acceptable and even desirable if the implementation starts with a clear adapter contract.

## Proposed Klimkit Adapter Contract

Normalize every tracker into a `WorkItem`:

- `id`: stable tracker ID.
- `identifier`: human-readable stable key, e.g. `KLIM-123` or `klimentij/klimkit#123`.
- `title`.
- `description`.
- `state`: normalized orchestration state.
- `priority`: nullable integer.
- `labels`: normalized list.
- `blocked_by`: list of item refs.
- `branch_name`: optional; generated if missing.
- `url`.
- `comments`: read/update capability for a single workpad.
- `links`: PR/proof/report attachment capability.
- `created_at` / `updated_at`.

Then implement adapters:

- `local-klimkit`: `.klimkit/tasks/**` as the first safe backend.
- `github-issues`: issue labels or issue fields as state, issue comments as workpad, dependencies/sub-issues when available.
- `github-projects`: Projects v2 fields as state/priority and issue/PR aggregation.
- `linear`: future compatibility with Symphony-like flows if Klim wants it.

## Recommended Next Step

Write a Klimkit orchestration spec before code. Keep it smaller than Symphony:

- Problem: turn eligible work items into isolated Klimkit worktrees and Codex sessions.
- Non-goal: fully autonomous merge-to-main.
- State model: queued, claimed, running, blocked, human-review, rework, done, terminal/cancelled.
- Isolation: one worktree per work item.
- UI: Switchboard surfaces orchestration state and links to workspace, task note, PR, and report.
- Evidence: `.klimkit/tasks/<item>/` remains the durable proof folder even when the tracker is GitHub or Linear.
- First backend: GitHub Issues/labels or local `.klimkit` queue.

My product conclusion: this is a strong and feasible evolution of Klimkit. It should become Klimkit's optional "work orchestration" layer, not a replacement for the current interactive Switchboard workflow. Use GitHub Issues as the default public implementation, design the tracker boundary so Linear remains possible, and keep human review as the first completion target.
