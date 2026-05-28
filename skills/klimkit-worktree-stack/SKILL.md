---
name: klimkit-worktree-stack
description: Create, inspect, or record isolated Klimkit worktree stacks for parallel agent work. Use when setting up feature branches, task workspaces, or separate checkouts so agents do not collide.
---

# Klimkit Worktree Stack

Use isolated worktrees for parallel work. Treat `git worktree list`, branch state, and task notes as authoritative; do not invent URLs or paths from memory.

## Workflow

1. Ensure operator-scoped Klimkit context exists. If `.klimkit/<operator>/` is missing or ambiguous, use `klimkit-setup` first.
2. Read the repository's branch and worktree conventions before creating anything.
3. Inspect current branch, worktree list, status, and remotes.
4. Choose a branch name from the task slug or requested outcome.
5. Create the worktree with `git worktree add` or the target repo's current supported helper when one exists.
6. Record:
   - repo path;
   - worktree path;
   - branch;
   - base branch and commit;
   - report URL when available.
7. Verify that the worktree is clean or document expected dirty files.
8. Keep one agent per worktree unless the human explicitly wants shared-checkout collaboration.

## Safety Rules

- Do not delete worktrees or branches unless the user explicitly asks.
- Do not run destructive git commands to "clean up" another agent's work.
- Do not hand-reconstruct local or tailnet URLs. Verify them from the running app or report server.
- If a task comes from an external tracker, include the external link in the worktree or task proof.

Read [references/worktree-stack.md](references/worktree-stack.md) when recording worktree handoff fields.
