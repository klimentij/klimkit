#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="$SCRIPT_DIR/bin"
TARGET="$BIN_DIR/cc-connect"
VERSION="v1.2.1"
ASSET="cc-connect-v1.2.1-linux-amd64"
URL="https://github.com/chenhg5/cc-connect/releases/download/${VERSION}/${ASSET}"
SHA256="028314fddfaa24b3cf98c4ff52bc71c7421a6eaefb344fc18cb4a387473b80cb"

mkdir -p "$BIN_DIR"
TMP="$(mktemp)"
cleanup() {
  rm -f "$TMP"
}
trap cleanup EXIT

curl -fsSL "$URL" -o "$TMP"
echo "${SHA256}  ${TMP}" | sha256sum -c -
install -m 0755 "$TMP" "$TARGET"
printf '%s\n' "$VERSION" >"$BIN_DIR/.version"
printf 'Installed %s to %s\n' "$VERSION" "$TARGET"
