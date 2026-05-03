#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_PATH="${SCRIPT_DIR}/switchboard_agent.py"

if command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python3)"
elif [[ -x "/usr/bin/python3" ]]; then
  PYTHON_BIN="/usr/bin/python3"
else
  printf 'switchboard-agent: python3 is missing\n' >&2
  exit 1
fi

exec "${PYTHON_BIN}" "${SCRIPT_PATH}" "$@"
