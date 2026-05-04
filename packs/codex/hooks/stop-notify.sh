#!/bin/bash
set -euo pipefail

payload="$(cat)"

KLIMKIT_CONFIG="${KLIMKIT_CONFIG:-$HOME/klimkit/.klimkit/local/klimkit.toml}"

telegram_json="$(
  KLIMKIT_CONFIG="$KLIMKIT_CONFIG" /usr/bin/python3 -c '
import json
import os
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    try:
        import tomli as tomllib
    except ModuleNotFoundError:
        print(json.dumps({"enabled": False, "bot_token": "", "chat_id": ""}))
        raise SystemExit(0)

path = Path(os.environ.get("KLIMKIT_CONFIG", "")).expanduser()
try:
    data = tomllib.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
except Exception:
    data = {}
telegram = data.get("notifications", {}).get("telegram", {}) if isinstance(data, dict) else {}
print(json.dumps({
    "enabled": bool(telegram.get("enabled", False)),
    "bot_token": str(telegram.get("bot_token", "")),
    "chat_id": str(telegram.get("chat_id", "")),
}))
'
)"

TELEGRAM_ENABLED="${KLIMKIT_TELEGRAM_ENABLED:-$(printf '%s' "$telegram_json" | /usr/bin/python3 -c 'import json, sys; print(str(json.load(sys.stdin).get("enabled", False)).lower())')}"
BOT_TOKEN="${KLIMKIT_TELEGRAM_BOT_TOKEN:-$(printf '%s' "$telegram_json" | /usr/bin/python3 -c 'import json, sys; print(json.load(sys.stdin).get("bot_token", ""))')}"
CHAT_ID="${KLIMKIT_TELEGRAM_CHAT_ID:-$(printf '%s' "$telegram_json" | /usr/bin/python3 -c 'import json, sys; print(json.load(sys.stdin).get("chat_id", ""))')}"

metadata_json="$(
  printf '%s' "$payload" | /usr/bin/python3 -c '
import json
import fcntl
import time
import os
import re
import socket
import subprocess
import sys
import datetime as dt
import urllib.parse
import urllib.request
import html

MAX_LEN = 320
STATE_ROOT = os.path.expanduser(os.environ.get("KLIMKIT_STATE_DIR", "~/klimkit/.klimkit/state"))
STATE_PATH = os.path.join(STATE_ROOT, "codex-hooks", "stop-notify-seen.json")
EVENTS_PATH = os.path.join(STATE_ROOT, "switchboard", "events.jsonl")
DEFAULT_FORWARD_ENDPOINT = os.environ.get("SWITCHBOARD_EVENT_ENDPOINT", "")
TRIVIAL_MESSAGES = {
    "yes",
    "yes.",
    "no",
    "no.",
    "ok",
    "ok.",
    "okay",
    "okay.",
    "sure",
    "sure.",
    "done",
    "done.",
    "stopped.",
}
QUESTION_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\?\s*$",
        r"\b(clarify|which|what|how would you like|do you want|please provide|let me know)\b",
        r"\b(need your input|need you to choose|waiting for your answer|before I can continue)\b",
    )
]

try:
    data = json.load(sys.stdin)
except Exception:
    data = {}

session_id = data.get("session_id") or ""
turn_id = data.get("turn_id") or ""
message = (data.get("last_assistant_message") or "").strip()
cwd = data.get("cwd") or os.getcwd()
workspace = os.path.basename(cwd.rstrip("/")) or cwd or "unknown"
folder = cwd.rstrip("/") or cwd or "unknown"
host = socket.gethostname()

def seen_turn_before(session_id: str, turn_id: str) -> bool:
    if not session_id or not turn_id:
        return False

    state_dir = os.path.dirname(STATE_PATH)
    os.makedirs(state_dir, exist_ok=True)

    with open(STATE_PATH, "a+", encoding="utf-8") as fh:
        fcntl.flock(fh.fileno(), fcntl.LOCK_EX)
        fh.seek(0)
        try:
            state = json.load(fh)
        except Exception:
            state = {}

        now = int(time.time())
        cutoff = now - 7 * 24 * 60 * 60
        state = {
            key: ts for key, ts in state.items()
            if isinstance(ts, int) and ts >= cutoff
        }

        dedupe_key = f"{session_id}:{turn_id}"
        already_seen = dedupe_key in state
        state[dedupe_key] = now

        fh.seek(0)
        fh.truncate()
        json.dump(state, fh)
        fh.flush()
        os.fsync(fh.fileno())
        fcntl.flock(fh.fileno(), fcntl.LOCK_UN)

    return already_seen

def is_title_only_payload(value: object) -> bool:
    return (
        isinstance(value, dict)
        and set(value.keys()) <= {"title"}
        and isinstance(value.get("title"), str)
        and bool(value.get("title").strip())
    )

def starts_with_internal_title_json(text: str) -> bool:
    try:
        parsed, _ = json.JSONDecoder().raw_decode(text)
    except Exception:
        return False

    return is_title_only_payload(parsed)

skip_notification = False
if data.get("stop_hook_active"):
    skip_notification = True
elif not message:
    skip_notification = True
elif starts_with_internal_title_json(message):
    skip_notification = True
elif message.strip().lower() == "do not send me the hook":
    skip_notification = True
elif message.strip().lower() in TRIVIAL_MESSAGES:
    skip_notification = True
elif seen_turn_before(session_id, turn_id):
    skip_notification = True

remote_url = None
quick_open_url = None
try:
    tailscale_status = subprocess.run(
        ["tailscale", "status", "--json"],
        capture_output=True,
        text=True,
        check=True,
    )
    tailscale_data = json.loads(tailscale_status.stdout)
    self_info = tailscale_data.get("Self") or {}
    host = str(self_info.get("HostName") or host).strip() or host
    dns_name = (self_info.get("DNSName") or "").rstrip(".")
    if dns_name:
        folder_query = urllib.parse.quote(folder, safe="/")
        remote_url = f"https://{dns_name}/?folder={folder_query}"
        quick_open_url = "http://127.0.0.1:43123/open?url=" + urllib.parse.quote(remote_url, safe="")
except Exception:
    remote_url = None
    quick_open_url = None

def load_thread_title(session_id: str) -> str:
    if not session_id:
        return ""
    index_path = os.path.expanduser("~/.codex/session_index.jsonl")
    if not os.path.exists(index_path):
        return ""
    title = ""
    try:
        with open(index_path, "r", encoding="utf-8") as fh:
            for line in fh:
                text = line.strip()
                if not text:
                    continue
                try:
                    payload = json.loads(text)
                except Exception:
                    continue
                if str(payload.get("id") or "").strip() == session_id:
                    title = str(payload.get("thread_name") or "").strip() or title
    except Exception:
        return ""
    return title

def current_branch(cwd: str) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", cwd, "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        branch = result.stdout.strip()
        if branch:
            return branch
    except Exception:
        pass
    return workspace

def classify_status(text: str) -> str:
    compact = re.sub(r"\s+", " ", text or "").strip()
    if not compact:
        return "done"
    lowered = compact.lower()
    if lowered in TRIVIAL_MESSAGES:
        return "done"
    if any(pattern.search(compact) for pattern in QUESTION_PATTERNS):
        return "needs_input"
    return "done"

def append_event(event: dict) -> None:
    os.makedirs(os.path.dirname(EVENTS_PATH), exist_ok=True)
    with open(EVENTS_PATH, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(event))
        fh.write("\n")

def post_event(url: str, event: dict) -> None:
    if not url:
        return
    data = json.dumps(event).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=5):
        pass

message = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", message)
message = re.sub(r"`([^`]+)`", r"\1", message)
message = re.sub(r"\s+", " ", message).strip()
if len(message) > MAX_LEN:
    message = f"{message[:MAX_LEN - 3]}..."

status_emoji = "🟢"
parts = [
    f"{status_emoji} <b>Codex finished</b>",
    f"💻 <b>Machine</b>: <code>{html.escape(host)}</code>",
    f"📁 <b>Workspace</b>: <code>{html.escape(workspace)}</code>",
    f"📍 <b>Path</b>: <code>{html.escape(folder)}</code>",
    "",
    "📝 <b>Latest message</b>",
    html.escape(message),
]

if remote_url:
    parts.extend([
        "",
        "🔗 <b>Open from phone / any Tailscale device</b>",
        remote_url,
    ])

if quick_open_url:
    parts.extend([
        "",
        "⚡ <b>Quick open on this Mac</b>",
        quick_open_url,
    ])

notification = "\n".join(parts)
if skip_notification:
    notification = ""

event = None
if not skip_notification:
    event = {
        "event_id": f"{session_id}:{turn_id}",
        "session_id": session_id,
        "turn_id": turn_id,
        "machine": host,
        "cwd": folder,
        "workspace": workspace,
        "status": classify_status(message),
        "title": load_thread_title(session_id) or workspace,
        "branch": current_branch(cwd),
        "message": message,
        "remote_url": remote_url or "",
        "created_at": dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z"),
        "source": "codex_stop_hook",
    }
    try:
        append_event(event)
    except Exception:
        pass

    if DEFAULT_FORWARD_ENDPOINT:
        try:
            post_event(DEFAULT_FORWARD_ENDPOINT, event)
        except Exception:
            pass

print(json.dumps({
    "text": notification,
    "parse_mode": "HTML",
    "disable_web_page_preview": True,
}))
'
)"

notification="$(
  printf '%s' "$metadata_json" | /usr/bin/python3 -c 'import json, sys; data=json.load(sys.stdin); print(data["text"])'
)"

parse_mode="$(
  printf '%s' "$metadata_json" | /usr/bin/python3 -c '
import json
import sys

data = json.load(sys.stdin)
print(data.get("parse_mode", ""))
'
)"

disable_web_page_preview="$(
  printf '%s' "$metadata_json" | /usr/bin/python3 -c '
import json
import sys

data = json.load(sys.stdin)
print("true" if data.get("disable_web_page_preview") else "false")
'
)"

telegram_enabled_lc="${TELEGRAM_ENABLED,,}"
if [[ "$telegram_enabled_lc" =~ ^(1|true|yes|on)$ && -n "$notification" && -n "$BOT_TOKEN" && -n "$CHAT_ID" ]] && command -v curl >/dev/null 2>&1; then
  curl_args=(
    -fsS --retry 2 --max-time 10
    -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
    --data-urlencode "chat_id=${CHAT_ID}" \
    --data-urlencode "text=${notification}" \
    --data-urlencode "disable_web_page_preview=${disable_web_page_preview}" \
  )

  if [[ -n "$parse_mode" ]]; then
    curl_args+=(--data-urlencode "parse_mode=${parse_mode}")
  fi

  /usr/bin/curl "${curl_args[@]}" >/dev/null 2>&1 || true
fi

printf '{"continue":true}\n'
