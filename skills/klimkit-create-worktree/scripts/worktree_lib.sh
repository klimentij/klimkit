#!/usr/bin/env bash

set -euo pipefail

kwt_fail() {
  printf 'Error: %s\n' "$1" >&2
  exit 1
}

kwt_step() {
  printf '[%s] %s\n' "$1" "$2"
}

kwt_slugify_branch() {
  local raw branch
  raw="$*"
  branch="$(printf '%s' "$raw" \
    | tr '[:upper:]' '[:lower:]' \
    | sed -E 's/[[:space:]]+/-/g; s/[^a-z0-9._/-]+/-/g; s#-+#-#g; s#/{2,}#/#g; s#(^[-./]+|[-./]+$)##g')"
  printf '%s' "$branch"
}

kwt_worktree_dir_name() {
  local branch
  branch="$1"
  printf '%s' "$branch" | sed 's#/#--#g'
}

kwt_ref_exists() {
  local repo ref
  repo="$1"
  ref="$2"
  git -C "$repo" rev-parse --verify --quiet "$ref" >/dev/null
}

kwt_resolve_ref() {
  local repo remote ref
  repo="$1"
  remote="$2"
  ref="$3"

  if [ "$ref" = "HEAD" ] || [[ "$ref" == refs/* ]]; then
    if kwt_ref_exists "$repo" "$ref"; then
      printf '%s' "$ref"
    else
      kwt_fail "Could not resolve ref: $ref"
    fi
  elif kwt_ref_exists "$repo" "refs/remotes/$remote/$ref"; then
    printf '%s' "refs/remotes/$remote/$ref"
  elif kwt_ref_exists "$repo" "refs/heads/$ref"; then
    printf '%s' "refs/heads/$ref"
  elif kwt_ref_exists "$repo" "$ref"; then
    printf '%s' "$ref"
  else
    kwt_fail "Could not resolve ref: $ref"
  fi
}

kwt_push_target_branch() {
  local remote ref
  remote="$1"
  ref="$2"

  case "$ref" in
    refs/heads/*)
      printf '%s' "${ref#refs/heads/}"
      ;;
    refs/remotes/"$remote"/*)
      printf '%s' "${ref#refs/remotes/$remote/}"
      ;;
    "$remote"/*)
      printf '%s' "${ref#"$remote"/}"
      ;;
    HEAD|refs/*)
      kwt_fail "Cannot infer push target branch from base ref: $ref"
      ;;
    *)
      printf '%s' "$ref"
      ;;
  esac
}
