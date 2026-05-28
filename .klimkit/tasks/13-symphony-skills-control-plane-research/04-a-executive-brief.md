# Executive Brief: Merging Skills, Klimkit, And Symphony

## Decision Summary

Use skills as Klimkit's default distribution surface, then add a thin Symphony-style orchestrator later. Do not start with the daemon.

The best combined model is:

- Matt Pocock's approach for sharp, task-specific skills.
- Klimkit's approach for proof, checklist, reflection, and final-review gates.
- Symphony's approach for unattended scheduling, isolated workspaces, retries, status updates, and PR/review loops.
- The private candidate `walkthrough` pattern for Tailscale-hosted human proof reports.

## Why This Beats The Alternatives

GitHub tracker/control-plane only is useful but not enough. It gives visible work items, dependencies, labels, `KK Status`, and boards. It does not run agents, enforce blockers, claim work, create worktrees, retry failed runs, or shepherd PRs.

Full Symphony immediately is too much surface area. It introduces a daemon, locks, workspace lifecycle, Codex runner behavior, retry policy, dashboard/status, and PR automation before the skill contracts are clean.

Skill-first is the right middle path. It improves daily Codex work now, keeps distribution simple through the Codex plugin and Vercel skills installer, and creates the exact contracts a later orchestrator can call.

## Board And Issue Model

Keep issues in the repo that owns the work. Use GitHub Projects as views:

- A personal aggregate Project can show issues across personal repos.
- A product-specific Project should show only issues inside that product boundary.
- Labels remain the repo-visible fallback state.
- `KK Status` remains the richer Project orchestration state.

The Project is a board and index. The owning repo issue is the canonical runnable work item.

## Recommended First Wave

Build these skills first:

- `klimkit-report-server`: check Tailscale, check/start the reports server, verify the served URL.
- `klimkit-walkthrough`: generate inspectable `.klimkit/reports/<slug>/index.html` walkthroughs with screenshots and links.
- `klimkit-github-control-plane`: create/triage issues, set labels and `KK Status`, link blockers, update the workpad, attach proof/PR links.
- `klimkit-to-issues` and `klimkit-triage`: adapt Matt's issue-slicing and triage strengths into Klimkit's proof model.
- Update `klimkit-workflow` so it composes these skills instead of acting like a monolith.

Then build the orchestrator:

- Poll eligible GitHub issues.
- Refuse blocked work.
- Claim/lock work.
- Create per-issue worktrees.
- Launch Codex.
- Update the workpad.
- Stop first at Human Review.

Add PR/CI/review/merge shepherding after that path is stable.

## Key Principle

"Skill-only" should not mean "no code." It means the install/check/run logic and reference code for a capability live inside the skill package, and the agent installs or copies them only when needed.

That makes a report server, walkthrough generator, GitHub control-plane helper, and future orchestrator compatible with the skill-first direction.

## Main Risks

- Private leakage if aggregate boards mix repo trust boundaries.
- Duplicate workers unless the runner implements claims/locks.
- Blocked issues running unless the runner enforces dependencies.
- Drift between the Codex plugin and Vercel skills installer.
- Publishing private-derived skill text instead of recreating public Klimkit versions from approved requirements.

## Recommendation

Proceed with a skill-only Klimkit refactor first, starting with walkthrough/report-server and GitHub control-plane skills. Treat full Symphony behavior as the next layer: a thin runner that consumes the same GitHub and `.klimkit` contracts rather than replacing them.
