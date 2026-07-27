#!/usr/bin/env bash
# preflight.sh — verify a machine can host Claude Code Remote Control before anything
# is installed. Exits non-zero on the first blocking problem, with the reason.
#
#   preflight.sh --dir /home/ubuntu/myrepo [--user ubuntu] [--headless-probe]
#
set -uo pipefail

DIR=""
SVC_USER="${USER:-$(id -un)}"
PROBE=0
FAILED=0

die()  { printf '\033[31mBLOCKED\033[0m  %s\n' "$*" >&2; exit 1; }
bad()  { printf '\033[31m  FAIL\033[0m  %s\n' "$*"; FAILED=1; }
warn() { printf '\033[33m  WARN\033[0m  %s\n' "$*"; }
ok()   { printf '\033[32m    OK\033[0m  %s\n' "$*"; }

while [ $# -gt 0 ]; do
    case "$1" in
        --dir)            DIR="${2:-}"; shift 2 ;;
        --user)           SVC_USER="${2:-}"; shift 2 ;;
        --headless-probe) PROBE=1; shift ;;
        -h|--help)        sed -n '2,8p' "$0"; exit 0 ;;
        *)                die "unknown argument: $1" ;;
    esac
done
[ -n "$DIR" ] || die "--dir is required (the project directory to serve)"

HOME_DIR=$(getent passwd "$SVC_USER" | cut -d: -f6)
[ -n "$HOME_DIR" ] || die "no such user: $SVC_USER"

echo "== Remote Control preflight =="
echo "   user=$SVC_USER home=$HOME_DIR dir=$DIR"
echo

# --- 1. binary and server-mode support -------------------------------------
CLAUDE=$(command -v claude || true)
[ -n "$CLAUDE" ] || CLAUDE="$HOME_DIR/.local/bin/claude"
if [ -x "$CLAUDE" ]; then
    ok "claude at $CLAUDE ($("$CLAUDE" --version 2>/dev/null | head -1))"
    if "$CLAUDE" remote-control --help 2>&1 | grep -q -- "--spawn"; then
        ok "server mode supported (--spawn / --capacity present)"
    else
        bad "this version has no server mode; upgrade, or use single-session --remote-control"
    fi
else
    bad "claude binary not found (looked for $CLAUDE)"
fi

# --- 2. authentication ------------------------------------------------------
CREDS="$HOME_DIR/.claude/.credentials.json"
if [ -r "$CREDS" ]; then
    AUTH=$(python3 - "$CREDS" <<'PY' 2>/dev/null
import json, sys
try:
    d = json.load(open(sys.argv[1])).get("claudeAiOauth") or {}
except Exception:
    print("unreadable|"); sys.exit(0)
print("%s|%s" % (d.get("subscriptionType") or "none", " ".join(d.get("scopes") or [])))
PY
)
    SUB="${AUTH%%|*}"; SCOPES="${AUTH#*|}"
    case "$SUB" in
        none|unreadable|"") bad "no claude.ai OAuth session in $CREDS — run 'claude auth login' as $SVC_USER" ;;
        *)                  ok "claude.ai OAuth session, subscription=$SUB" ;;
    esac
    case "$SCOPES" in
        *user:sessions:claude_code*) ok "full-scope token (user:sessions:claude_code)" ;;
        *)                           bad "token lacks user:sessions:claude_code — setup-token/OAuth-token cannot host Remote Control" ;;
    esac
else
    bad "no credentials at $CREDS — an interactive 'claude auth login' is required (a human step)"
fi
[ -n "${ANTHROPIC_API_KEY:-}" ] && warn "ANTHROPIC_API_KEY is set in this shell; the unit must clear it"

# --- 3. API endpoint --------------------------------------------------------
case "${ANTHROPIC_BASE_URL:-}" in
    ""|https://api.anthropic.com|https://api.anthropic.com/) ok "ANTHROPIC_BASE_URL=${ANTHROPIC_BASE_URL:-<unset>}" ;;
    *) bad "ANTHROPIC_BASE_URL=${ANTHROPIC_BASE_URL} disables Remote Control; unset it" ;;
esac
for v in CLAUDE_CODE_USE_BEDROCK CLAUDE_CODE_USE_VERTEX; do
    [ -n "${!v:-}" ] && bad "$v is set; Remote Control is unavailable on that provider"
done

# --- 4. directory and trust -------------------------------------------------
if [ -d "$DIR" ]; then
    ok "project directory exists"
    if [ -d "$DIR/.git" ] || git -C "$DIR" rev-parse --git-dir >/dev/null 2>&1; then
        ok "git repository (--spawn worktree usable)"
    else
        warn "not a git repository; use --spawn same-dir"
    fi
    TRUST=$(python3 - "$HOME_DIR/.claude.json" "$DIR" <<'PY' 2>/dev/null
import json, sys
try:
    p = json.load(open(sys.argv[1])).get("projects", {})
except Exception:
    print("unknown"); sys.exit(0)
e = p.get(sys.argv[2].rstrip("/"))
print("yes" if e and e.get("hasTrustDialogAccepted") else "no")
PY
)
    case "$TRUST" in
        yes) ok "workspace trust accepted for this directory" ;;
        *)   bad "workspace trust not accepted — run 'claude' once in $DIR as $SVC_USER, or the server never becomes Ready" ;;
    esac
else
    bad "project directory does not exist: $DIR"
fi

# --- 5. machine capacity ----------------------------------------------------
echo
echo "== capacity =="
MEM_MB=$(awk '/MemTotal/{printf "%d", $2/1024}' /proc/meminfo)
SWAP_MB=$(awk '/SwapTotal/{printf "%d", $2/1024}' /proc/meminfo)
echo "   RAM=${MEM_MB}MB swap=${SWAP_MB}MB cores=$(nproc) free_disk=$(df -h --output=avail / | tail -1 | tr -d ' ')"
if [ "$SWAP_MB" -eq 0 ]; then
    warn "no swap: a memory spike becomes an instant OOM kill — add swap before installing"
else
    ok "swap present"
fi
if command -v journalctl >/dev/null 2>&1; then
    OOMS=$(journalctl -k --since "30 days ago" 2>/dev/null | grep -ci "oom-kill" || true)
    if [ "${OOMS:-0}" -gt 0 ]; then
        warn "$OOMS OOM kill events in the last 30 days — read references/oom-and-capacity.md first"
    else
        ok "no OOM kills in the last 30 days"
    fi
fi
if [ "$(id -u)" -ne 0 ] && ! sudo -n true 2>/dev/null; then
    warn "no passwordless sudo: install a --scope user unit and enable linger"
fi

# --- 6. headless probe ------------------------------------------------------
if [ "$PROBE" -eq 1 ] && [ -x "$CLAUDE" ] && [ -d "$DIR" ]; then
    echo
    echo "== headless probe (25s, no TTY) =="
    LOG=$(mktemp); NAME="preflight-probe-$$"
    ( cd "$DIR" && setsid env -u ANTHROPIC_BASE_URL -u ANTHROPIC_API_KEY \
        "$CLAUDE" remote-control --name "$NAME" --capacity 1 </dev/null >"$LOG" 2>&1 & )
    sleep 25
    if grep -qiE "ready|Code anywhere" "$LOG"; then
        ok "runs headless — a plain systemd unit will work"
    else
        bad "no Ready without a TTY; supervise tmux instead. Output:"
        sed 's/\x1b\[[0-9;]*[A-Za-z]//g' "$LOG" | grep -v '^\s*$' | tail -8 | sed 's/^/         /'
    fi
    pkill -f "$NAME" 2>/dev/null || true
    rm -f "$LOG"
fi

echo
if [ "$FAILED" -eq 0 ]; then
    printf '\033[32mPREFLIGHT PASSED\033[0m — safe to install\n'; exit 0
fi
printf '\033[31mPREFLIGHT FAILED\033[0m — fix the FAIL lines before installing\n'; exit 1
