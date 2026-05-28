#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel)"

IMAGE_NAME="${IMAGE_NAME:-klimkit-fresh-codex-smoke:latest}"
KLIMKIT_REPO="${KLIMKIT_REPO:-https://github.com/klimentij/klimkit.git}"
KLIMKIT_REF="${KLIMKIT_REF:-$(git -C "$REPO_ROOT" branch --show-current)}"
CODEX_HOME_SRC="${CODEX_HOME:-$HOME/.codex}"
DOCKER_BIN="${DOCKER_BIN:-docker}"

if ! $DOCKER_BIN version >/dev/null 2>&1; then
  if command -v sudo >/dev/null 2>&1 && sudo docker version >/dev/null 2>&1; then
    DOCKER_BIN="sudo docker"
  fi
fi

AUTH_DIR="$(mktemp -d)"
cleanup() {
  rm -rf "$AUTH_DIR"
}
trap cleanup EXIT

if [[ -f "$CODEX_HOME_SRC/auth.json" ]]; then
  cp "$CODEX_HOME_SRC/auth.json" "$AUTH_DIR/auth.json"
fi
if [[ -f "$CODEX_HOME_SRC/installation_id" ]]; then
  cp "$CODEX_HOME_SRC/installation_id" "$AUTH_DIR/installation_id"
fi

if [[ ! -f "$AUTH_DIR/auth.json" && -z "${OPENAI_API_KEY:-}" ]]; then
  cat >&2 <<EOF
No Codex auth found at $CODEX_HOME_SRC/auth.json.

Run codex login on the host first, or pass an auth environment supported by your
Codex CLI build. This script copies only auth.json and installation_id into a
temporary read-only Docker mount; it does not mount your full Codex home.
EOF
  exit 2
fi

$DOCKER_BIN build -t "$IMAGE_NAME" "$SCRIPT_DIR"

$DOCKER_BIN run --rm \
  -e "KLIMKIT_REPO=$KLIMKIT_REPO" \
  -e "KLIMKIT_REF=$KLIMKIT_REF" \
  -e "OPERATOR_NAME=${OPERATOR_NAME:-SmokeOperator}" \
  -e "PERSONALITY_NAME=${PERSONALITY_NAME:-Steady Operator}" \
  -e "PERSONALITY_DESCRIPTION=${PERSONALITY_DESCRIPTION:-Direct, careful, evidence-first, and conservative with scope.}" \
  ${OPENAI_API_KEY:+-e OPENAI_API_KEY="$OPENAI_API_KEY"} \
  -v "$AUTH_DIR:/host-codex-auth:ro" \
  "$IMAGE_NAME"
