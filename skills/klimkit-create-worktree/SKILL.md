---
name: klimkit-create-worktree
description: Create isolated Git worktrees for Klimkit agent work, including simple branch worktrees and feature branches from a base branch that is first updated by merging another branch. Use when the user asks to create a worktree, make a new branch checkout, start isolated feature work, or prepare a dev-synced worktree.
---

# Klimkit Create Worktree

Use this skill to create deterministic, isolated worktrees. The default worktree root is `${KLIMKIT_WORKTREE_ROOT:-$HOME/wt}`, so new checkouts normally land under `~/wt/<branch-name>`.

## If The Request Is Ambiguous

If the user invokes this skill without saying the branch or base, inspect branches and suggest two or three concrete options, then ask for clarification. Prefer options like:

- `Klimkit create worktree feature checkout from main`
- `Klimkit create worktree feature sync from dev updated with main`
- `Klimkit create worktree bugfix login from origin/main without syncing another branch`

Ask which base branch to use and whether the base should first be updated from another branch. When a repo has `main` and `dev`, suggest `dev updated with main` for feature branches that should target `dev`.

## Workflow

1. Inspect repo root, current branch, remotes, existing local/remote branches, and `git worktree list`.
2. Convert the requested branch name into a safe branch slug.
3. Choose the creation mode:
   - Simple: create `<branch>` from `<base>`.
   - Synced base: merge `<sync-from>` into `<base>` in a temporary worktree, optionally push the synced base, then create `<branch>` from that merge commit.
4. Prefer the bundled script for deterministic behavior:

   ```bash
   skills/klimkit-create-worktree/scripts/create_worktree.sh \
     --branch "<branch name>" \
     --base dev \
     --sync-from main \
     --push-base
   ```

5. Record the printed `path=...`, `branch=...`, `base=...`, `start_commit=...`, and `url=...` in the task note or final handoff.
6. Verify the new worktree exists and run `git -C <path> status --short`.

## Examples

Create from `main`:

```bash
skills/klimkit-create-worktree/scripts/create_worktree.sh --branch "checkout polish" --base main
```

Create from `dev` after merging `main` into `dev`, then push updated `dev`:

```bash
skills/klimkit-create-worktree/scripts/create_worktree.sh --branch "feature sync" --base dev --sync-from main --push-base
```

Create from a remote base without syncing:

```bash
skills/klimkit-create-worktree/scripts/create_worktree.sh --branch "bugfix auth redirect" --base origin/main
```

Dry-run a plan:

```bash
skills/klimkit-create-worktree/scripts/create_worktree.sh --branch "new flow" --base dev --sync-from main --dry-run
```

Read [references/create-worktree.md](references/create-worktree.md) for script flags, branch model notes, and handoff fields.

## Safety Rules

- Do not delete worktrees or branches unless the user explicitly asks.
- Refuse if the target branch, remote branch, or worktree path already exists.
- Do not push a synced base branch unless the user asked for sync-and-push behavior or the repo convention clearly requires it.
- Do not hand-reconstruct URLs from memory. Use script output or verified repo config.
