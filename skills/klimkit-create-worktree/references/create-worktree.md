# Create Worktree Reference

The bundled script supports two common workflows:

- Create a new branch worktree from a base ref.
- Create a temporary sync worktree, merge one branch into the base branch, optionally push the base branch, then create a feature branch worktree from the synced commit.

## Script

```bash
skills/klimkit-create-worktree/scripts/create_worktree.sh \
  --branch "<branch name>" \
  [--base <branch-or-ref>] \
  [--sync-from <branch-or-ref>] \
  [--push-base] \
  [--worktree-root <path>] \
  [--code-server-base-url <url>] \
  [--repo-root <path>] \
  [--dry-run]
```

## Defaults

- `--base`: current branch.
- `--remote`: `origin`.
- `--worktree-root`: `${KLIMKIT_WORKTREE_ROOT:-$HOME/wt}`.
- Worktree folder name: branch name with `/` replaced by `--`.
- Code-server base URL:
  - `$KLIMKIT_CODE_SERVER_BASE_URL`, then
  - `$KLIMKIT_DEFAULT_CODE_SERVER_BASE_URL`, then
  - `https://${KLIMKIT_DEV_HOST}` when `KLIMKIT_DEV_HOST` is set.

## Dev Sync Pattern

For repos where `main` is the stable staging branch, `dev` is the integration branch, and feature branches merge into `dev`, use:

```bash
skills/klimkit-create-worktree/scripts/create_worktree.sh \
  --branch "<feature>" \
  --base dev \
  --sync-from main \
  --push-base
```

This fetches/prunes, creates a detached temporary worktree from `origin/dev` when available, merges `origin/main` or `main` into it, pushes the result to `origin/dev`, then creates the new feature branch worktree from that synced commit.

## Handoff Fields

Record these values after creation:

- repository path;
- worktree path;
- code-server URL when printed;
- branch name;
- base branch/ref;
- sync source when used;
- start commit;
- dirty status at handoff.

## Cleanup

The script removes only its own temporary sync worktree on failure. Do not remove the created worktree, local branch, or remote branch unless the user explicitly asks and current status has been inspected.
