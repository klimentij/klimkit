#!/usr/bin/env bash
# install_remote_control.sh — install a supervised Claude Code Remote Control server for
# one project directory, with the memory protections that keep it alive on a busy box.
# Idempotent: re-running updates the units in place.
#
#   sudo install_remote_control.sh --dir /home/ubuntu/myrepo [options]
#
#   --dir PATH             project directory to serve (required)
#   --name NAME            session name at claude.ai/code   (default: vps-<dirname>)
#   --instance NAME        systemd instance name            (default: <dirname>)
#   --user USER            service user            (default: owner of --dir)
#   --capacity N           max concurrent sessions          (default: 8)
#   --permission-mode M    auto|acceptEdits|default|plan|dontAsk|bypassPermissions
#                                                           (default: auto)
#   --spawn MODE           worktree|same-dir|session        (default: worktree)
#   --swap SIZE            swap to create if none exists, e.g. 8G; 0 to skip (default: 8G)
#   --slice-max SIZE       hard memory cap for all servers  (default: 8G)
#   --slice-high SIZE      throttle threshold               (default: 6G)
#   --no-fleet-tools       skip agent-fleet.slice and fleet-run
#   --dry-run              print what would be written, change nothing
#
set -euo pipefail

DIR="" NAME="" INSTANCE="" SVC_USER=""
CAPACITY=8 PERM_MODE=auto SPAWN=worktree
SWAP_SIZE=8G SLICE_MAX=8G SLICE_HIGH=6G
FLEET=1 DRY=0

die() { printf '\033[31merror:\033[0m %s\n' "$*" >&2; exit 1; }
say() { printf '\033[36m::\033[0m %s\n' "$*"; }

while [ $# -gt 0 ]; do
    case "$1" in
        --dir)             DIR="${2:?}"; shift 2 ;;
        --name)            NAME="${2:?}"; shift 2 ;;
        --instance)        INSTANCE="${2:?}"; shift 2 ;;
        --user)            SVC_USER="${2:?}"; shift 2 ;;
        --capacity)        CAPACITY="${2:?}"; shift 2 ;;
        --permission-mode) PERM_MODE="${2:?}"; shift 2 ;;
        --spawn)           SPAWN="${2:?}"; shift 2 ;;
        --swap)            SWAP_SIZE="${2:?}"; shift 2 ;;
        --slice-max)       SLICE_MAX="${2:?}"; shift 2 ;;
        --slice-high)      SLICE_HIGH="${2:?}"; shift 2 ;;
        --no-fleet-tools)  FLEET=0; shift ;;
        --dry-run)         DRY=1; shift ;;
        -h|--help)         sed -n '2,22p' "$0"; exit 0 ;;
        *)                 die "unknown argument: $1" ;;
    esac
done

[ -n "$DIR" ] || die "--dir is required"
DIR="${DIR%/}"
[ -d "$DIR" ] || die "no such directory: $DIR"
command -v systemctl >/dev/null 2>&1 || die "no systemd; see references/systemd-units.md for launchd and container variants"
[ "$DRY" -eq 1 ] || [ "$(id -u)" -eq 0 ] || die "run as root (or --dry-run); a system unit needs it"

[ -n "$SVC_USER" ]  || SVC_USER=$(stat -c '%U' "$DIR")
[ -n "$INSTANCE" ]  || INSTANCE=$(basename "$DIR")
[ -n "$NAME" ]      || NAME="vps-$INSTANCE"
SVC_GROUP=$(id -gn "$SVC_USER")
HOME_DIR=$(getent passwd "$SVC_USER" | cut -d: -f6)
[ -n "$HOME_DIR" ] || die "cannot resolve home for $SVC_USER"

# Resolve the launcher through its stable symlink so upgrades don't orphan the unit.
CLAUDE="$HOME_DIR/.local/bin/claude"
[ -x "$CLAUDE" ] || CLAUDE=$(command -v claude || true)
[ -n "$CLAUDE" ] && [ -x "$CLAUDE" ] || die "claude binary not found for $SVC_USER"

case "$PERM_MODE" in
    auto|acceptEdits|default|plan|dontAsk) ;;
    bypassPermissions) printf '\033[33mwarning:\033[0m bypassPermissions approves every tool call unconditionally.\n' ;;
    *) die "invalid --permission-mode: $PERM_MODE" ;;
esac
[ "$SPAWN" = worktree ] && ! git -C "$DIR" rev-parse --git-dir >/dev/null 2>&1 && \
    die "--spawn worktree needs a git repository; use --spawn same-dir"

NODE_BIN=$(dirname "$(command -v node 2>/dev/null || echo /usr/bin/node)")
UNIT_PATH=/etc/systemd/system/claude-rc@.service
SLICE_PATH=/etc/systemd/system/claude-rc.slice

emit() {  # emit <path> <<<content
    local path="$1" content; content=$(cat)
    if [ "$DRY" -eq 1 ]; then
        printf '\n--- would write %s ---\n%s\n' "$path" "$content"
    else
        printf '%s\n' "$content" > "$path"
        say "wrote $path"
    fi
}

# --- swap -------------------------------------------------------------------
CUR_SWAP=$(awk '/SwapTotal/{print $2}' /proc/meminfo)
if [ "$SWAP_SIZE" != "0" ] && [ "${CUR_SWAP:-0}" -eq 0 ]; then
    if [ "$DRY" -eq 1 ]; then
        say "would create $SWAP_SIZE /swapfile, add it to /etc/fstab, set vm.swappiness=10"
    else
        say "no swap present; creating $SWAP_SIZE /swapfile"
        fallocate -l "$SWAP_SIZE" /swapfile || dd if=/dev/zero of=/swapfile bs=1M count=8192
        chmod 600 /swapfile && mkswap -q /swapfile && swapon /swapfile
        grep -q '^/swapfile' /etc/fstab || echo "/swapfile none swap sw 0 0" >> /etc/fstab
        printf 'vm.swappiness=10\nvm.vfs_cache_pressure=50\n' > /etc/sysctl.d/99-swap-tuning.conf
        sysctl -q -p /etc/sysctl.d/99-swap-tuning.conf
    fi
else
    say "swap: $((CUR_SWAP / 1024))MB present (or explicitly skipped)"
fi

# --- parent slice -----------------------------------------------------------
emit "$SLICE_PATH" <<EOF
[Unit]
Description=Claude Code Remote Control servers and their spawned sessions
Documentation=https://code.claude.com/docs/en/remote-control
Before=slices.target

[Slice]
# Bound collectively: with several instances a per-service cap only decides
# which instance dies first, it does not bound the machine.
MemoryHigh=$SLICE_HIGH
MemoryMax=$SLICE_MAX
CPUWeight=200
EOF

# --- shared template --------------------------------------------------------
# Everything project-specific lives in a per-instance drop-in, never here: this
# file is shared by every instance, so a hardcoded WorkingDirectory would make
# installing a second project silently repoint the first.
emit "$UNIT_PATH" <<'EOF'
[Unit]
Description=Claude Code Remote Control server (%i)
Documentation=https://code.claude.com/docs/en/remote-control
Wants=network-online.target
After=network-online.target
# Never let the start limiter latch the unit off. Belongs in [Unit]; systemd
# ignores it in [Service] with only a one-line warning.
StartLimitIntervalSec=0

[Service]
Type=simple
# WorkingDirectory, User, Environment and ExecStart come from
# /etc/systemd/system/claude-rc@<instance>.service.d/10-project.conf
# An instance with no drop-in intentionally refuses to start.

# These three disable Remote Control outright; clear them explicitly, because a
# system service inherits from the system manager rather than from a shell.
UnsetEnvironment=ANTHROPIC_BASE_URL ANTHROPIC_API_KEY CLAUDE_CODE_OAUTH_TOKEN

# Answers the documented ~10-minute network-outage exit, plus crashes and reboots.
Restart=always
RestartSec=5

Slice=claude-rc.slice
# Keep the server alive when the kernel kills one of its sessions.
OOMPolicy=continue
TasksMax=16384
LimitNOFILE=65536

StandardOutput=journal
StandardError=journal
SyslogIdentifier=claude-rc-%i

[Install]
WantedBy=multi-user.target
EOF

# --- per-instance drop-in ---------------------------------------------------
DROPIN_DIR="/etc/systemd/system/claude-rc@${INSTANCE}.service.d"
[ "$DRY" -eq 1 ] || mkdir -p "$DROPIN_DIR"
emit "$DROPIN_DIR/10-project.conf" <<EOF
# Project settings for claude-rc@${INSTANCE}. Safe to edit; re-run the installer
# to regenerate. 'systemctl daemon-reload && systemctl restart' to apply.
[Service]
User=$SVC_USER
Group=$SVC_GROUP
# Workspace trust is per-directory and is never saved for \$HOME, so this must
# be the project directory or the server waits forever on a trust dialog.
WorkingDirectory=$DIR

# Without HOME the claude.ai OAuth credentials are not found, which presents as
# an authentication failure rather than a configuration one.
Environment=HOME=$HOME_DIR
Environment=PATH=$(dirname "$CLAUDE"):$NODE_BIN:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

# Reset before setting: a drop-in appends to ExecStart unless cleared first.
ExecStart=
ExecStart=$CLAUDE remote-control \\
    --name $NAME \\
    --spawn $SPAWN \\
    --capacity $CAPACITY \\
    --permission-mode $PERM_MODE
EOF

# --- fleet containment ------------------------------------------------------
if [ "$FLEET" -eq 1 ]; then
    emit /etc/systemd/system/agent-fleet.slice <<'EOF'
[Unit]
Description=Disposable agent fleets
Before=slices.target

[Slice]
MemoryHigh=4G
MemoryMax=5G
CPUWeight=50
EOF

    emit /usr/local/bin/fleet-run <<'EOF'
#!/usr/bin/env bash
# Launch disposable agent work so the kernel kills the FLEET, not the supervisor.
set -euo pipefail
[ $# -ge 1 ] || { echo "usage: fleet-run <command> [args...]" >&2; exit 64; }

# Scope units take cgroup properties but not exec properties, so the OOM score
# is set by choom inside the scope rather than by -p OOMScoreAdjust=.
if sudo -n true 2>/dev/null; then
    exec sudo -n systemd-run --quiet --collect --scope \
        --slice=agent-fleet.slice \
        --uid="$(id -u)" --gid="$(id -g)" \
        --setenv=HOME="$HOME" --setenv=PATH="$PATH" \
        -- choom -n 800 -- "$@"
fi
# Unprivileged processes may always make themselves MORE killable.
exec choom -n 800 -- "$@"
EOF
    [ "$DRY" -eq 1 ] || chmod 0755 /usr/local/bin/fleet-run
fi

# --- activate ---------------------------------------------------------------
if [ "$DRY" -eq 1 ]; then
    say "dry run complete; nothing was changed"
    exit 0
fi

systemctl daemon-reload
# Verify the merged instance, not the bare template: the template deliberately
# has no ExecStart of its own.
systemd-analyze verify "claude-rc@${INSTANCE}.service" || die "unit failed verification"
systemctl enable "claude-rc@${INSTANCE}.service" >/dev/null
systemctl restart "claude-rc@${INSTANCE}.service"

say "waiting for the server to report Ready"
for _ in $(seq 1 30); do
    sleep 2
    journalctl -u "claude-rc@${INSTANCE}.service" --since "-2min" --no-pager -o cat 2>/dev/null \
        | grep -qiE "ready|Code anywhere" && break
done

systemctl is-active --quiet "claude-rc@${INSTANCE}.service" \
    || die "service is not active; run: journalctl -u claude-rc@${INSTANCE} -n 50"

cat <<SUMMARY

  installed   claude-rc@${INSTANCE}.service   ($(systemctl is-active "claude-rc@${INSTANCE}.service"), $(systemctl is-enabled "claude-rc@${INSTANCE}.service"))
  directory   $DIR
  session     $NAME          <- find it by NAME at claude.ai/code, not by URL
  sessions    capacity $CAPACITY, spawn $SPAWN, permission mode $PERM_MODE
  memory      claude-rc.slice high=$SLICE_HIGH max=$SLICE_MAX, swap $(awk '/SwapTotal/{printf "%dMB", $2/1024}' /proc/meminfo)

  verify      $(dirname "$0")/healthcheck.sh --instance $INSTANCE --kill-test
SUMMARY
