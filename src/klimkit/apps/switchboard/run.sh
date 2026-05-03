#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_PATH="${SWITCHBOARD_CONFIG:-${SCRIPT_DIR}/switchboard.toml}"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../../.." && pwd)"

exec "${REPO_ROOT}/klimkit" serve --config "${CONFIG_PATH}" "$@"
