# Worktree Stack Notes

Use this when setting up or recording isolated workspaces.

## Recommended Fields

Record these in the task note or handoff:

- repository path;
- worktree path;
- branch name;
- base branch and commit;
- linked task, PR, or external tracker item when available;
- report URL when available;
- dirty status at handoff.

## Basic Commands

Create a worktree from the current repository:

```bash
git fetch origin
git worktree add -b "<branch-name>" "<worktree-path>" origin/main
```

If the repository has its own current helper, use it and record the values it prints. Treat older Klimkit helper scripts as deprecated unless the user explicitly asks to maintain legacy runtime workflows.

## Cleanup

Do not remove a worktree, branch, or remote ref unless the user explicitly asks and the current status has been inspected.
