#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="$SCRIPT_DIR/build"
APP_NAME="Codex Focus.app"
APP_BUILD_PATH="$BUILD_DIR/$APP_NAME"
APP_INSTALL_DIR="$HOME/Applications"
APP_INSTALL_PATH="$APP_INSTALL_DIR/$APP_NAME"
SUPPORT_DIR="$HOME/Library/Application Support/CodexFocus"
LAUNCH_AGENT_ID="com.klim.codex-focus-link-server"
LAUNCH_AGENT_PATH="$HOME/Library/LaunchAgents/$LAUNCH_AGENT_ID.plist"
PLIST_BUDDY="/usr/libexec/PlistBuddy"
LSREGISTER="/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister"

log() {
  printf '[codex-focus] %s\n' "$*"
}

set_or_add_plist_string() {
  local key="$1"
  local value="$2"

  if ! "$PLIST_BUDDY" -c "Set :$key $value" "$PLIST" >/dev/null 2>&1; then
    "$PLIST_BUDDY" -c "Add :$key string $value" "$PLIST"
  fi
}

set_or_add_plist_bool() {
  local key="$1"
  local value="$2"

  if ! "$PLIST_BUDDY" -c "Set :$key $value" "$PLIST" >/dev/null 2>&1; then
    "$PLIST_BUDDY" -c "Add :$key bool $value" "$PLIST"
  fi
}

mkdir -p "$BUILD_DIR" "$APP_INSTALL_DIR" "$SUPPORT_DIR"
rm -rf "$APP_BUILD_PATH"

log "building applet"
osacompile -o "$APP_BUILD_PATH" "$SCRIPT_DIR/CodexFocus.applescript"

PLIST="$APP_BUILD_PATH/Contents/Info.plist"

set_or_add_plist_string "CFBundleIdentifier" "com.klim.codexfocus"
set_or_add_plist_string "CFBundleName" "Codex Focus"
set_or_add_plist_string "CFBundleDisplayName" "Codex Focus"
"$PLIST_BUDDY" -c "Delete :LSUIElement" "$PLIST" >/dev/null 2>&1 || true

"$PLIST_BUDDY" -c "Delete :CFBundleURLTypes" "$PLIST" >/dev/null 2>&1 || true
"$PLIST_BUDDY" -c "Add :CFBundleURLTypes array" "$PLIST"
"$PLIST_BUDDY" -c "Add :CFBundleURLTypes:0 dict" "$PLIST"
"$PLIST_BUDDY" -c "Add :CFBundleURLTypes:0:CFBundleURLName string com.klim.codexfocus" "$PLIST"
"$PLIST_BUDDY" -c "Add :CFBundleURLTypes:0:CFBundleURLSchemes array" "$PLIST"
"$PLIST_BUDDY" -c "Add :CFBundleURLTypes:0:CFBundleURLSchemes:0 string codexfocus" "$PLIST"

log "installing app to $APP_INSTALL_PATH"
rm -rf "$APP_INSTALL_PATH"
ditto "$APP_BUILD_PATH" "$APP_INSTALL_PATH"

log "signing app"
codesign --force --deep --sign - "$APP_INSTALL_PATH" >/dev/null

cp "$SCRIPT_DIR/focus_link_server.py" "$SUPPORT_DIR/focus_link_server.py"

mkdir -p "$HOME/Library/LaunchAgents"
cat >"$LAUNCH_AGENT_PATH" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
  <dict>
    <key>Label</key>
    <string>$LAUNCH_AGENT_ID</string>
    <key>ProgramArguments</key>
    <array>
      <string>/usr/bin/python3</string>
      <string>$SUPPORT_DIR/focus_link_server.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$SUPPORT_DIR/focus-link-server.log</string>
    <key>StandardErrorPath</key>
    <string>$SUPPORT_DIR/focus-link-server.log</string>
  </dict>
</plist>
EOF

if command -v launchctl >/dev/null 2>&1; then
  launchctl bootout "gui/$(id -u)" "$LAUNCH_AGENT_PATH" >/dev/null 2>&1 || true
  launchctl bootstrap "gui/$(id -u)" "$LAUNCH_AGENT_PATH"
  launchctl kickstart -k "gui/$(id -u)/$LAUNCH_AGENT_ID" >/dev/null 2>&1 || true
fi

if [[ -x "$LSREGISTER" ]]; then
  log "registering codexfocus:// URL scheme"
  "$LSREGISTER" -f "$APP_INSTALL_PATH" >/dev/null
fi

log "done"
printf '\n'
printf 'Deep link example:\n'
printf '  codexfocus://open?url=https%%3A%%2F%%2Fyour-host.tailnet.ts.net%%2F%%3Ffolder%%3D%%2Fabsolute%%2Fworkspace%%2Fpath\n'
printf '\n'
printf 'Local button server:\n'
printf '  http://127.0.0.1:43123/open?url=https%%3A%%2F%%2Fyour-host.tailnet.ts.net%%2F%%3Ffolder%%3D%%2Fabsolute%%2Fworkspace%%2Fpath\n'
printf '\n'
printf 'First-run note:\n'
printf '  macOS should prompt once for Automation access so Codex Focus can control Google Chrome and Safari.\n'
