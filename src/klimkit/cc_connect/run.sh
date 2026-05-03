#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN="$SCRIPT_DIR/bin/cc-connect"
CONFIG_PATH="${CC_CONNECT_CONFIG:-$HOME/.cc-connect/config.toml}"

if [[ ! -x "$BIN" ]]; then
  printf 'Missing %s. Run %s/install.sh first.\n' "$BIN" "$SCRIPT_DIR" >&2
  exit 1
fi

if [[ ! -f "$CONFIG_PATH" ]]; then
  printf 'Missing cc-connect config at %s\n' "$CONFIG_PATH" >&2
  exit 1
fi

if ! command -v codex >/dev/null 2>&1; then
  shopt -s nullglob
  codex_dirs=("$HOME"/.local/share/code-server/extensions/openai.chatgpt-*-linux-x64/bin/linux-x86_64)
  shopt -u nullglob
  if ((${#codex_dirs[@]} > 0)); then
    export PATH="${codex_dirs[-1]}:$PATH"
  fi
fi

exec "$BIN" --config "$CONFIG_PATH"
