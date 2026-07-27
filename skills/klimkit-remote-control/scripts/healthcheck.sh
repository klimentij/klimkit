#!/usr/bin/env bash
# healthcheck.sh — assert that a Remote Control install is actually durable.
# Asserts rather than prints: exits non-zero if any check fails.
#
#   healthcheck.sh --instance myrepo [--kill-test]
#
#   --instance NAME   systemd instance (claude-rc@NAME); repeatable
#   --name NAME       alias for --instance, for callers who think in session names
#   --kill-test       SIGKILL the main PID and assert a NEW pid returns within 30s
#
set -uo pipefail

INSTANCES=()
KILL_TEST=0
FAILED=0

ok()   { printf '\033[32m    OK\033[0m  %s\n' "$*"; }
bad()  { printf '\033[31m  FAIL\033[0m  %s\n' "$*"; FAILED=1; }
warn() { printf '\033[33m  WARN\033[0m  %s\n' "$*"; }

while [ $# -gt 0 ]; do
    case "$1" in
        --instance|--name) INSTANCES+=("${2:?}"); shift 2 ;;
        --kill-test)       KILL_TEST=1; shift ;;
        -h|--help)         sed -n '2,10p' "$0"; exit 0 ;;
        *) printf 'unknown argument: %s\n' "$1" >&2; exit 64 ;;
    esac
done

if [ "${#INSTANCES[@]}" -eq 0 ]; then
    mapfile -t INSTANCES < <(systemctl list-units --all --no-legend 'claude-rc@*.service' 2>/dev/null \
        | awk '{print $1}' | sed 's/^claude-rc@//; s/\.service$//')
    [ "${#INSTANCES[@]}" -gt 0 ] || { echo "no claude-rc@ instances found; pass --instance" >&2; exit 64; }
fi

# Session names are the durable handle: a restart mints a new environment URL
# but keeps the name, so a bookmarked URL breaks exactly when restart works.
for inst in "${INSTANCES[@]}"; do
    unit="claude-rc@${inst}.service"
    echo "== $unit =="

    [ "$(systemctl is-active "$unit")" = active ] \
        && ok "active" || bad "not active: $(systemctl is-active "$unit")"
    [ "$(systemctl is-enabled "$unit" 2>/dev/null)" = enabled ] \
        && ok "enabled (survives reboot)" \
        || bad "not enabled — will NOT come back after a reboot"

    log=$(journalctl -u "$unit" --since "-24h" --no-pager -o cat 2>/dev/null | sed 's/\x1b\[[0-9;]*[A-Za-z]//g')
    if grep -qiE "ready|Code anywhere" <<<"$log"; then
        ok "reached Ready$(grep -oE 'Capacity: [0-9]+/[0-9]+' <<<"$log" | tail -1 | sed 's/^/ · /')"
    else
        bad "never reported Ready — check auth and workspace trust"
    fi
    grep -qiE "requires a (claude.ai subscription|full-scope)" <<<"$log" \
        && bad "authentication error in journal: eligibility, not unit configuration"

    slice=$(systemctl show "$unit" -p Slice --value)
    [ "$(systemctl show "$unit" -p Restart --value)" = always ] \
        && ok "Restart=always" || bad "Restart is not 'always'"
    [ "$(systemctl show "$unit" -p OOMPolicy --value)" = continue ] \
        && ok "OOMPolicy=continue" || warn "OOMPolicy is not 'continue'; a killed session can take the server down"
    restarts=$(systemctl show "$unit" -p NRestarts --value)
    [ "${restarts:-0}" -gt 20 ] && warn "$restarts restarts so far — look for a crash loop"

    if [ "$KILL_TEST" -eq 1 ]; then
        before=$(systemctl show "$unit" -p MainPID --value)
        if [ "${before:-0}" -gt 0 ] && kill -9 "$before" 2>/dev/null; then
            for _ in $(seq 1 15); do
                sleep 2
                after=$(systemctl show "$unit" -p MainPID --value)
                [ "${after:-0}" -gt 0 ] && [ "$after" != "$before" ] && break
            done
            if [ "${after:-0}" -gt 0 ] && [ "$after" != "$before" ]; then
                ok "kill test: respawned $before -> $after"
            else
                bad "kill test: no NEW pid within 30s (same pid proves nothing)"
            fi
        else
            bad "kill test: could not signal MainPID (need root?)"
        fi
    fi
    echo
done

echo "== machine =="
swap_mb=$(awk '/SwapTotal/{printf "%d", $2/1024}' /proc/meminfo)
[ "$swap_mb" -gt 0 ] && ok "swap ${swap_mb}MB" || bad "no swap: a spike becomes an instant OOM kill"
grep -q '^/swapfile' /etc/fstab 2>/dev/null && ok "swap persisted in /etc/fstab" \
    || { [ "$swap_mb" -gt 0 ] && warn "swap is not in /etc/fstab; it disappears at reboot"; }

for s in claude-rc.slice agent-fleet.slice; do
    max=$(systemctl show "$s" -p MemoryMax --value 2>/dev/null)
    case "$max" in
        ""|infinity) warn "$s has no MemoryMax" ;;
        *)           ok "$s MemoryMax=$((max / 1024 / 1024))MB" ;;
    esac
done
[ -x /usr/local/bin/fleet-run ] && ok "fleet-run present" || warn "no fleet-run: fleets will outrank the supervisor for survival"

ooms=$(journalctl -k --since "24 hours ago" 2>/dev/null | grep -ci "oom-kill" || true)
[ "${ooms:-0}" -eq 0 ] && ok "no OOM kills in 24h" || bad "$ooms OOM kill events in 24h — see references/oom-and-capacity.md"

echo
[ "$FAILED" -eq 0 ] && { printf '\033[32mHEALTHY\033[0m\n'; exit 0; }
printf '\033[31mUNHEALTHY\033[0m\n'; exit 1
