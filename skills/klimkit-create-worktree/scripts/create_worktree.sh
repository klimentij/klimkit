#!/usr/bin/env bash

set -euo pipefail

usage() {
  cat >&2 <<'USAGE'
Usage:
  create_worktree.sh --branch <name> [options]

Options:
  --branch <name>              Required branch name or natural-language title.
  --base <ref>                 Base branch/ref. Defaults to current branch.
  --sync-from <ref>            Merge this ref into the base in a temporary worktree before creating the new worktree.
  --push-base                  Push the synced base branch back to the remote. Only valid with --sync-from.
  --remote <name>              Remote name. Defaults to origin.
  --worktree-root <path>       Worktree root. Defaults to ${KLIMKIT_WORKTREE_ROOT:-$HOME/wt}.
  --code-server-base-url <url> Optional code-server base URL for printed handoff URL.
  --repo-root <path>           Repository root. Defaults to git root from current directory.
  --dry-run                    Print the plan without creating anything.
  -h, --help                   Show this help.

Examples:
  create_worktree.sh --branch "checkout polish" --base main
  create_worktree.sh --branch "feature sync" --base dev --sync-from main --push-base
  create_worktree.sh --branch "bugfix auth redirect" --base origin/main
USAGE
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
# shellcheck source=worktree_lib.sh
source "$SCRIPT_DIR/worktree_lib.sh"

BRANCH_RAW=""
BASE_REF=""
SYNC_FROM=""
PUSH_BASE=0
REMOTE="origin"
WORKTREE_ROOT="${KLIMKIT_WORKTREE_ROOT:-$HOME/wt}"
CODE_SERVER_BASE_URL="${KLIMKIT_CODE_SERVER_BASE_URL:-${KLIMKIT_DEFAULT_CODE_SERVER_BASE_URL:-}}"
REPO_ROOT=""
DRY_RUN=0
SYNC_WORKTREE=""

cleanup() {
  if [ -n "${SYNC_WORKTREE:-}" ] && [ -d "${SYNC_WORKTREE:-}" ]; then
    git -C "$REPO_ROOT" worktree remove --force "$SYNC_WORKTREE" >/dev/null 2>&1 || rm -rf "$SYNC_WORKTREE"
  fi
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --branch)
      [ "$#" -ge 2 ] || kwt_fail "--branch requires a value"
      BRANCH_RAW="$2"
      shift 2
      ;;
    --base)
      [ "$#" -ge 2 ] || kwt_fail "--base requires a value"
      BASE_REF="$2"
      shift 2
      ;;
    --sync-from)
      [ "$#" -ge 2 ] || kwt_fail "--sync-from requires a value"
      SYNC_FROM="$2"
      shift 2
      ;;
    --push-base)
      PUSH_BASE=1
      shift
      ;;
    --remote)
      [ "$#" -ge 2 ] || kwt_fail "--remote requires a value"
      REMOTE="$2"
      shift 2
      ;;
    --worktree-root)
      [ "$#" -ge 2 ] || kwt_fail "--worktree-root requires a value"
      WORKTREE_ROOT="$2"
      shift 2
      ;;
    --code-server-base-url)
      [ "$#" -ge 2 ] || kwt_fail "--code-server-base-url requires a value"
      CODE_SERVER_BASE_URL="$2"
      shift 2
      ;;
    --repo-root)
      [ "$#" -ge 2 ] || kwt_fail "--repo-root requires a value"
      REPO_ROOT="$2"
      shift 2
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      kwt_fail "Unknown argument: $1"
      ;;
  esac
done

[ -n "$BRANCH_RAW" ] || { usage; exit 1; }

if [ -z "$REPO_ROOT" ]; then
  REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || true)"
fi
[ -n "$REPO_ROOT" ] || kwt_fail "Could not determine repository root."
[ -d "$REPO_ROOT/.git" ] || git -C "$REPO_ROOT" rev-parse --git-dir >/dev/null 2>&1 || kwt_fail "Not a git repository: $REPO_ROOT"

if [ -z "$BASE_REF" ]; then
  BASE_REF="$(git -C "$REPO_ROOT" branch --show-current)"
  [ -n "$BASE_REF" ] || BASE_REF="HEAD"
fi

if [ "$PUSH_BASE" -eq 1 ] && [ -z "$SYNC_FROM" ]; then
  kwt_fail "--push-base requires --sync-from"
fi

BRANCH_NAME="$(kwt_slugify_branch "$BRANCH_RAW")"
[ -n "$BRANCH_NAME" ] || kwt_fail "Branch name resolved to an empty string."
git check-ref-format --branch "$BRANCH_NAME" >/dev/null 2>&1 || kwt_fail "Invalid branch name after normalization: $BRANCH_NAME"

WORKTREE_NAME="$(kwt_worktree_dir_name "$BRANCH_NAME")"
WORKTREE_PATH="$WORKTREE_ROOT/$WORKTREE_NAME"

if [ -n "$CODE_SERVER_BASE_URL" ]; then
  CODE_SERVER_BASE_URL="${CODE_SERVER_BASE_URL%/}"
elif [ -n "${KLIMKIT_DEV_HOST:-}" ]; then
  CODE_SERVER_BASE_URL="https://${KLIMKIT_DEV_HOST}"
fi

CODE_SERVER_URL=""
if [ -n "$CODE_SERVER_BASE_URL" ]; then
  CODE_SERVER_URL="$CODE_SERVER_BASE_URL/?folder=$WORKTREE_PATH"
fi

printf 'branch=%s\n' "$BRANCH_NAME"
printf 'base=%s\n' "$BASE_REF"
[ -z "$SYNC_FROM" ] || printf 'sync_from=%s\n' "$SYNC_FROM"
printf 'worktree_root=%s\n' "$WORKTREE_ROOT"
printf 'path=%s\n' "$WORKTREE_PATH"
[ -z "$CODE_SERVER_URL" ] || printf 'url=%s\n' "$CODE_SERVER_URL"

if git -C "$REPO_ROOT" show-ref --verify --quiet "refs/heads/$BRANCH_NAME"; then
  kwt_fail "Local branch already exists: $BRANCH_NAME"
fi

if git -C "$REPO_ROOT" show-ref --verify --quiet "refs/remotes/$REMOTE/$BRANCH_NAME"; then
  kwt_fail "Remote branch already exists: $REMOTE/$BRANCH_NAME"
fi

if [ -e "$WORKTREE_PATH" ]; then
  kwt_fail "Target worktree path already exists: $WORKTREE_PATH"
fi

if [ "$DRY_RUN" -eq 1 ]; then
  printf 'dry_run=true\n'
  exit 0
fi

trap cleanup EXIT

kwt_step "1/7" "Fetching $REMOTE and pruning deleted refs"
git -C "$REPO_ROOT" fetch "$REMOTE" --prune

BASE_RESOLVED="$(kwt_resolve_ref "$REPO_ROOT" "$REMOTE" "$BASE_REF")"
START_COMMIT=""
PUSH_TARGET=""

if [ -n "$SYNC_FROM" ]; then
  SYNC_RESOLVED="$(kwt_resolve_ref "$REPO_ROOT" "$REMOTE" "$SYNC_FROM")"
  REPO_NAME="$(basename "$REPO_ROOT")"
  SYNC_WORKTREE="$(mktemp -d "/tmp/${REPO_NAME}-worktree-sync-XXXXXX")"

  kwt_step "2/7" "Creating temporary sync worktree at $SYNC_WORKTREE from $BASE_RESOLVED"
  git -C "$REPO_ROOT" worktree add --detach "$SYNC_WORKTREE" "$BASE_RESOLVED" >/dev/null

  kwt_step "3/7" "Merging $SYNC_RESOLVED into $BASE_REF"
  git -C "$SYNC_WORKTREE" merge --no-edit -m "Merge $SYNC_FROM into $BASE_REF for worktree sync" "$SYNC_RESOLVED"
  START_COMMIT="$(git -C "$SYNC_WORKTREE" rev-parse HEAD)"

  if [ "$PUSH_BASE" -eq 1 ]; then
    PUSH_TARGET="$(kwt_push_target_branch "$REMOTE" "$BASE_REF")"
    kwt_step "4/7" "Pushing synced commit ${START_COMMIT:0:12} to $REMOTE/$PUSH_TARGET"
    git -C "$SYNC_WORKTREE" push "$REMOTE" "HEAD:$PUSH_TARGET"
  else
    kwt_step "4/7" "Leaving synced base unpushed"
  fi
else
  kwt_step "2/7" "Using base ref $BASE_RESOLVED"
  START_COMMIT="$(git -C "$REPO_ROOT" rev-parse "$BASE_RESOLVED")"
  kwt_step "3/7" "No base sync requested"
  kwt_step "4/7" "No base push requested"
fi

kwt_step "5/7" "Ensuring worktree root exists at $WORKTREE_ROOT"
mkdir -p "$WORKTREE_ROOT"

kwt_step "6/7" "Creating worktree $WORKTREE_PATH on branch $BRANCH_NAME"
git -C "$REPO_ROOT" worktree add -b "$BRANCH_NAME" "$WORKTREE_PATH" "$START_COMMIT"

kwt_step "7/7" "Worktree ready"
printf 'start_commit=%s\n' "$START_COMMIT"
printf 'path=%s\n' "$WORKTREE_PATH"
[ -z "$CODE_SERVER_URL" ] || printf 'url=%s\n' "$CODE_SERVER_URL"
git -C "$WORKTREE_PATH" status --short
