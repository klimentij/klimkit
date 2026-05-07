#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat >&2 <<'EOF'
Usage: create-worktree.sh <branch name>

Creates a feature worktree from a synced integration branch.

Environment:
  BASE_BRANCH       Integration branch to start from. Default: dev
  SYNC_BRANCH       Branch to fast-forward into BASE_BRANCH first. Default: main
  WORKTREE_ROOT     Directory that will contain worktrees. Default: $HOME/wt
  PUSH_SYNCED_BASE  Push the synced BASE_BRANCH back to origin when 1. Default: 0
  CODE_SERVER_BASE_URL
                    Optional base URL such as https://host.example.ts.net.
                    When set, the script prints a code-server folder URL.
EOF
}

step() {
  printf '[%s] %s\n' "$1" "$2"
}

fail() {
  printf 'Error: %s\n' "$1" >&2
  exit 1
}

slugify_branch() {
  local raw branch
  raw="$*"
  branch="$(printf '%s' "$raw" \
    | tr '[:upper:]' '[:lower:]' \
    | sed -E 's/[[:space:]]+/-/g; s/[^a-z0-9._/-]+/-/g; s#-+#-#g; s#/{2,}#/#g; s#(^[-./]+|[-./]+$)##g')"
  printf '%s' "$branch"
}

worktree_dir_name() {
  printf '%s' "$1" | sed 's#/#--#g'
}

cleanup() {
  if [ -n "${SYNC_WORKTREE:-}" ] && [ -d "${SYNC_WORKTREE:-}" ]; then
    git -C "$REPO_ROOT" worktree remove --force "$SYNC_WORKTREE" >/dev/null 2>&1 || rm -rf "$SYNC_WORKTREE"
  fi
}

if [ "$#" -eq 0 ] || [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
  usage
  exit 0
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
REPO_ROOT="$(git -C "$SCRIPT_DIR/.." rev-parse --show-toplevel 2>/dev/null || true)"
[ -n "$REPO_ROOT" ] || fail "Could not determine the repository root."

BASE_BRANCH="${BASE_BRANCH:-dev}"
SYNC_BRANCH="${SYNC_BRANCH:-main}"
WORKTREE_ROOT="${WORKTREE_ROOT:-$HOME/wt}"
PUSH_SYNCED_BASE="${PUSH_SYNCED_BASE:-0}"
RAW_BRANCH_NAME="$*"
BRANCH_NAME="$(slugify_branch "$RAW_BRANCH_NAME")"
[ -n "$BRANCH_NAME" ] || fail "Branch name resolved to an empty string."
git check-ref-format --branch "$BRANCH_NAME" >/dev/null 2>&1 || fail "Invalid branch name after normalization: $BRANCH_NAME"

WORKTREE_NAME="$(worktree_dir_name "$BRANCH_NAME")"
WORKTREE_PATH="$WORKTREE_ROOT/$WORKTREE_NAME"

if git -C "$REPO_ROOT" show-ref --verify --quiet "refs/heads/$BRANCH_NAME"; then
  fail "Local branch already exists: $BRANCH_NAME"
fi

if git -C "$REPO_ROOT" show-ref --verify --quiet "refs/remotes/origin/$BRANCH_NAME"; then
  fail "Remote branch already exists: origin/$BRANCH_NAME"
fi

if [ -e "$WORKTREE_PATH" ]; then
  fail "Target worktree path already exists: $WORKTREE_PATH"
fi

step "1/7" "Requested branch: \"$RAW_BRANCH_NAME\" -> $BRANCH_NAME"
step "2/7" "Fetching origin and pruning deleted refs"
git -C "$REPO_ROOT" fetch origin --prune

git -C "$REPO_ROOT" show-ref --verify --quiet "refs/remotes/origin/$BASE_BRANCH" \
  || fail "Missing origin/$BASE_BRANCH. Set BASE_BRANCH to an existing integration branch."
git -C "$REPO_ROOT" show-ref --verify --quiet "refs/remotes/origin/$SYNC_BRANCH" \
  || fail "Missing origin/$SYNC_BRANCH. Set SYNC_BRANCH to an existing branch."

SYNC_WORKTREE="$(mktemp -d "/tmp/worktree-sync-XXXXXX")"
trap cleanup EXIT

step "3/7" "Creating temporary sync worktree from origin/$BASE_BRANCH"
git -C "$REPO_ROOT" worktree add --detach "$SYNC_WORKTREE" "refs/remotes/origin/$BASE_BRANCH" >/dev/null

step "4/7" "Fast-forwarding $BASE_BRANCH with origin/$SYNC_BRANCH"
git -C "$SYNC_WORKTREE" merge --ff-only "refs/remotes/origin/$SYNC_BRANCH"
BASE_COMMIT="$(git -C "$SYNC_WORKTREE" rev-parse HEAD)"

if [ "$PUSH_SYNCED_BASE" = "1" ]; then
  step "5/7" "Pushing synced commit ${BASE_COMMIT:0:12} to origin/$BASE_BRANCH"
  git -C "$SYNC_WORKTREE" push origin "HEAD:$BASE_BRANCH"
else
  step "5/7" "Leaving origin/$BASE_BRANCH unchanged; set PUSH_SYNCED_BASE=1 to push the synced base"
fi

step "6/7" "Creating worktree root at $WORKTREE_ROOT"
mkdir -p "$WORKTREE_ROOT"

step "7/7" "Creating worktree $WORKTREE_PATH on branch $BRANCH_NAME"
git -C "$REPO_ROOT" worktree add -b "$BRANCH_NAME" "$WORKTREE_PATH" "$BASE_COMMIT"

printf 'path=%s\n' "$WORKTREE_PATH"
if [ -n "${CODE_SERVER_BASE_URL:-}" ]; then
  CODE_SERVER_BASE_URL="${CODE_SERVER_BASE_URL%/}"
  printf 'code_server_url=%s/?folder=%s\n' "$CODE_SERVER_BASE_URL" "$WORKTREE_PATH"
fi
printf 'switchboard_folder=%s\n' "$WORKTREE_PATH"
