#!/usr/bin/env python3

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import socket
import sqlite3
import subprocess
import sys
import threading
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib import error, parse, request

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib

from klimkit.paths import KLIMKIT_CONFIG_FILE, KLIMKIT_STATE_DIR

DEFAULT_CONFIG_PATH = KLIMKIT_CONFIG_FILE
HELPER_STATIC_DIR = Path(__file__).with_name("helper_static")
CACHE_VERSION = 2
TIMESTAMP_RE = re.compile(
    r"^(?P<head>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})"
    r"(?P<fraction>\.\d+)?"
    r"(?P<tz>Z|[+-]\d{2}:\d{2})?$"
)
QUESTION_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\?\s*$",
        r"\b(please clarify|can you clarify|could you clarify|how would you like|do you want|please provide|let me know)\b",
        r"\b(need your input|need you to choose|waiting for your answer|before I can continue)\b",
    )
]
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
TAILSCALE_COMMAND_CANDIDATES = (
    "/Applications/Tailscale.app/Contents/MacOS/Tailscale",
    "/opt/homebrew/bin/tailscale",
    "/usr/local/bin/tailscale",
    "/usr/bin/tailscale",
)


@dataclass(frozen=True)
class AgentConfig:
    sessions_root: Path
    session_index: Path
    state_dir: Path
    backend_url: str
    backend_auth_token: str
    timeout_seconds: int
    interval_seconds: int
    heartbeat_seconds: int
    max_session_age_days: int
    helper_enabled: bool
    helper_host: str
    helper_port: int


@dataclass(frozen=True)
class MachineIdentity:
    machine: str
    dns_name: str


@dataclass
class SessionSummary:
    session_id: str
    cwd: str
    branch: str
    created_at: str
    updated_at: str
    title: str
    last_event_at: str
    last_assistant_message: str
    last_agent_message: str
    last_task_message: str
    last_task_turn_id: str
    last_task_completed_at: str
    pending_input_request_id: str
    pending_input_request_at: str
    pending_input_request_message: str
    in_progress: bool
    current_turn_id: str
    is_subagent: bool


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Publish local Codex session state to the central Switchboard backend."
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path(os.environ.get("SWITCHBOARD_AGENT_CONFIG", DEFAULT_CONFIG_PATH)),
        help="Path to the switchboard agent TOML config.",
    )
    parser.add_argument(
        "--loop",
        action="store_true",
        help="Run forever instead of one reporting pass.",
    )
    parser.add_argument(
        "--print-snapshot",
        action="store_true",
        help="Print the generated snapshot JSON to stdout.",
    )
    return parser.parse_args(argv)


def load_config(path: Path) -> AgentConfig:
    raw = tomllib.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    is_klimkit_config = "switchboard" in raw and isinstance(raw.get("switchboard"), dict)
    root_paths = raw.get("paths", {}) if isinstance(raw.get("paths", {}), dict) else {}
    switchboard = raw.get("switchboard", {}) if isinstance(raw.get("switchboard", {}), dict) else {}
    server_config = switchboard.get("server", {}) if isinstance(switchboard.get("server", {}), dict) else {}
    agent_config = switchboard.get("agent", {}) if isinstance(switchboard.get("agent", {}), dict) else {}
    state_root = Path(str(root_paths.get("state_dir", KLIMKIT_STATE_DIR))).expanduser()
    defaults = {
        "paths": {
            "sessions_root": str(Path.home() / ".codex" / "sessions"),
            "session_index": str(Path.home() / ".codex" / "session_index.jsonl"),
            "state_dir": str(state_root / "switchboard-agent"),
        },
        "backend": {
            "base_url": "",
            "auth_token": "",
            "timeout_seconds": 15,
        },
        "agent": {
            "interval_seconds": 5,
            "heartbeat_seconds": 60,
            "max_session_age_days": 14,
        },
        "helper": {
            "enabled": True,
            "host": "127.0.0.1",
            "port": 4632,
        },
    }

    paths_config = {**(switchboard.get("paths", {}) if is_klimkit_config else root_paths)}
    backend_config = {**raw.get("backend", {})}
    agent_legacy_config = raw.get("agent", {})
    helper_config = raw.get("helper", {})
    server_enabled = bool(server_config.get("enabled", False))
    server_port = max(1, int(server_config.get("port", 4721)))
    server_base_path = str(server_config.get("base_path", "/switchboard")).strip() or "/switchboard"
    if not server_base_path.startswith("/"):
        server_base_path = "/" + server_base_path
    server_base_path = server_base_path.rstrip("/") or "/switchboard"

    def nested(section: str, key: str) -> Any:
        if section == "paths":
            return paths_config.get(key, defaults[section][key])
        if section == "backend":
            if key == "base_url":
                return agent_config.get("backend_url", backend_config.get(key, defaults[section][key]))
            if key == "auth_token":
                return agent_config.get("auth_token", backend_config.get(key, defaults[section][key]))
            return backend_config.get(key, defaults[section][key])
        if section == "agent":
            mapping = {
                "interval_seconds": "interval_seconds",
                "heartbeat_seconds": "heartbeat_seconds",
                "max_session_age_days": "max_session_age_days",
            }
            return agent_config.get(mapping[key], agent_legacy_config.get(key, defaults[section][key]))
        if section == "helper":
            mapping = {"enabled": "enabled", "host": "helper_host", "port": "helper_port"}
            return agent_config.get(mapping[key], helper_config.get(key, defaults[section][key]))
        return raw.get(section, {}).get(key, defaults[section][key])

    backend_url = str(nested("backend", "base_url")).rstrip("/")
    if not backend_url and server_enabled:
        backend_url = f"http://127.0.0.1:{server_port}{server_base_path}"

    return AgentConfig(
        sessions_root=Path(str(nested("paths", "sessions_root"))).expanduser(),
        session_index=Path(str(nested("paths", "session_index"))).expanduser(),
        state_dir=Path(str(nested("paths", "state_dir"))).expanduser(),
        backend_url=backend_url,
        backend_auth_token=str(nested("backend", "auth_token")).strip(),
        timeout_seconds=max(1, int(nested("backend", "timeout_seconds"))),
        interval_seconds=max(1, int(nested("agent", "interval_seconds"))),
        heartbeat_seconds=max(5, int(nested("agent", "heartbeat_seconds"))),
        max_session_age_days=max(1, int(nested("agent", "max_session_age_days"))),
        helper_enabled=bool(nested("helper", "enabled")),
        helper_host=str(nested("helper", "host")).strip() or "127.0.0.1",
        helper_port=max(1, int(nested("helper", "port"))),
    )


def tailnet_suffix_from_status(payload: dict[str, Any]) -> str:
    suffix = str(payload.get("MagicDNSSuffix") or "").strip().strip(".")
    if suffix:
        return suffix
    current_tailnet = payload.get("CurrentTailnet")
    if isinstance(current_tailnet, dict):
        return str(current_tailnet.get("MagicDNSSuffix") or "").strip().strip(".")
    return ""


def tailnet_suffix_from_url(url: str) -> str:
    try:
        hostname = parse.urlparse(url).hostname or ""
    except Exception:
        return ""
    parts = hostname.strip(".").split(".")
    if len(parts) >= 3 and parts[-2:] == ["ts", "net"]:
        return ".".join(parts[1:])
    return ""


def strip_local_hostname(machine: str) -> str:
    name = str(machine or "").strip().strip(".")
    if name.lower().endswith(".local"):
        return name[:-6]
    return name


def dns_label_from_machine(machine: str) -> str:
    label = strip_local_hostname(machine).split(".", 1)[0].lower()
    label = re.sub(r"[^a-z0-9-]+", "-", label)
    label = re.sub(r"-{2,}", "-", label).strip("-")
    return label


def infer_tailnet_dns_name(machine: str, suffix: str) -> str:
    label = dns_label_from_machine(machine)
    normalized_suffix = str(suffix or "").strip().strip(".")
    if not label or not normalized_suffix:
        return ""
    return f"{label}.{normalized_suffix}"


def tailscale_command() -> str:
    command = shutil.which("tailscale")
    if command:
        return command
    for candidate in TAILSCALE_COMMAND_CANDIDATES:
        if Path(candidate).exists():
            return candidate
    return "tailscale"


def load_tailscale_status_payload() -> dict[str, Any]:
    result = subprocess.run(
        [tailscale_command(), "status", "--json"],
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(result.stdout)
    return payload if isinstance(payload, dict) else {}


def init_db(state_dir: Path) -> sqlite3.Connection:
    state_dir.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(state_dir / "state.sqlite3")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS rollout_cache (
            path TEXT PRIMARY KEY,
            size INTEGER NOT NULL,
            mtime_ns INTEGER NOT NULL,
            summary_json TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS agent_state (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
        """
    )
    conn.commit()
    return conn


def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def parse_iso_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    text = value.strip()
    if not text:
        return None
    match = TIMESTAMP_RE.match(text)
    if not match:
        return None

    fraction = match.group("fraction") or ""
    if fraction:
        fraction = "." + fraction[1:7].ljust(6, "0")

    tz = match.group("tz") or "Z"
    normalized = match.group("head") + fraction + ("+00:00" if tz == "Z" else tz)
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def earliest_timestamp(*values: str) -> str:
    filtered = [value for value in values if value]
    if not filtered:
        return ""
    return min(filtered)


def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def extract_message_text(content: list[dict[str, Any]]) -> str:
    parts: list[str] = []
    for item in content:
        if not isinstance(item, dict):
            continue
        if item.get("type") in {"input_text", "output_text"}:
            text = str(item.get("text") or "").strip()
            if text:
                parts.append(text)
    return "\n".join(parts).strip()


def fallback_title_from_message(message: str, cwd: str) -> str:
    text = normalize_whitespace(message)
    if not text:
        return os.path.basename(cwd.rstrip("/")) or cwd or "Untitled"
    return text.splitlines()[0][:80]


def classify_message_status(message: str) -> str:
    text = normalize_whitespace(message)
    lower = text.lower()
    if not text:
        return "done"
    if lower in TRIVIAL_MESSAGES:
        return "done"
    if any(pattern.search(text) for pattern in QUESTION_PATTERNS):
        return "needs_input"
    return "done"


def summarize_request_user_input(arguments: str) -> str:
    if not arguments:
        return "Waiting for user input."
    try:
        payload = json.loads(arguments)
    except json.JSONDecodeError:
        return "Waiting for user input."
    questions = payload.get("questions")
    if not isinstance(questions, list) or not questions:
        return "Waiting for user input."
    prompt_texts = [
        normalize_whitespace(str(question.get("question") or ""))
        for question in questions
        if isinstance(question, dict)
    ]
    prompt_texts = [text for text in prompt_texts if text]
    if len(prompt_texts) == 1:
        return prompt_texts[0]
    if prompt_texts:
        return f"Asked {len(prompt_texts)} questions. {prompt_texts[0]}"
    return f"Asked {len(questions)} questions."


def load_thread_index(path: Path) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    if not path.exists():
        return index
    for line in path.read_text(encoding="utf-8").splitlines():
        text = line.strip()
        if not text:
            continue
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            continue
        session_id = str(payload.get("id") or "").strip()
        if session_id:
            index[session_id] = payload
    return index


def decode_summary(row: sqlite3.Row) -> SessionSummary:
    payload = json.loads(str(row["summary_json"]))
    payload.pop("_parser_version", None)
    payload.setdefault(
        "created_at",
        earliest_timestamp(
            str(payload.get("updated_at") or ""),
            str(payload.get("last_task_completed_at") or ""),
            str(payload.get("last_event_at") or ""),
        ),
    )
    payload.setdefault("pending_input_request_id", "")
    payload.setdefault("pending_input_request_at", "")
    payload.setdefault("pending_input_request_message", "")
    payload.setdefault("is_subagent", False)
    return SessionSummary(**payload)


def cached_summary(conn: sqlite3.Connection, path: Path, stat: os.stat_result) -> SessionSummary | None:
    row = conn.execute(
        "SELECT summary_json FROM rollout_cache WHERE path = ? AND size = ? AND mtime_ns = ?",
        (str(path), stat.st_size, stat.st_mtime_ns),
    ).fetchone()
    if row is None:
        return None
    try:
        payload = json.loads(str(row["summary_json"]))
    except json.JSONDecodeError:
        return None
    if int(payload.get("_parser_version") or 0) != CACHE_VERSION:
        return None
    return decode_summary(row)


def save_cached_summary(
    conn: sqlite3.Connection,
    path: Path,
    stat: os.stat_result,
    summary: SessionSummary,
) -> None:
    payload = asdict(summary)
    payload["_parser_version"] = CACHE_VERSION
    conn.execute(
        """
        INSERT INTO rollout_cache(path, size, mtime_ns, summary_json)
        VALUES(?, ?, ?, ?)
        ON CONFLICT(path) DO UPDATE SET
          size = excluded.size,
          mtime_ns = excluded.mtime_ns,
          summary_json = excluded.summary_json
        """,
        (str(path), stat.st_size, stat.st_mtime_ns, json.dumps(payload, ensure_ascii=True)),
    )


def get_agent_state(conn: sqlite3.Connection, key: str) -> str:
    row = conn.execute("SELECT value FROM agent_state WHERE key = ?", (key,)).fetchone()
    return str(row["value"]) if row is not None else ""


def set_agent_state(conn: sqlite3.Connection, key: str, value: str) -> None:
    conn.execute(
        """
        INSERT INTO agent_state(key, value)
        VALUES(?, ?)
        ON CONFLICT(key) DO UPDATE SET value = excluded.value
        """,
        (key, value),
    )


def parse_rollout(path: Path, index: dict[str, dict[str, Any]]) -> SessionSummary:
    session_id = ""
    cwd = ""
    branch = ""
    created_at = ""
    updated_at = ""
    title = ""
    last_event_at = ""
    first_event_at = ""
    last_assistant_message = ""
    last_agent_message = ""
    last_task_message = ""
    last_task_turn_id = ""
    last_task_completed_at = ""
    pending_input_request_id = ""
    pending_input_request_at = ""
    pending_input_request_message = ""
    current_turn_id = ""
    is_subagent = False
    open_input_requests: dict[str, tuple[str, str]] = {}

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        text = raw_line.strip()
        if not text:
            continue
        try:
            row = json.loads(text)
        except json.JSONDecodeError:
            continue

        timestamp = str(row.get("timestamp") or "")
        row_type = row.get("type")
        payload = row.get("payload") or {}
        if timestamp:
            first_event_at = first_event_at or timestamp
            last_event_at = timestamp

        if row_type == "session_meta":
            session_id = str(payload.get("id") or session_id)
            cwd = str(payload.get("cwd") or cwd)
            branch = str(((payload.get("git") or {}).get("branch")) or branch)
            source = payload.get("source") if isinstance(payload, dict) else {}
            is_subagent = is_subagent or (
                isinstance(source, dict)
                and isinstance(source.get("subagent"), dict)
            )
            created_at = created_at or timestamp
            updated_at = timestamp or updated_at
        elif row_type == "event_msg":
            event_type = payload.get("type")
            if event_type == "agent_message":
                last_agent_message = str(payload.get("message") or last_agent_message)
            elif event_type == "task_started":
                current_turn_id = str(payload.get("turn_id") or "")
            elif event_type == "task_complete":
                last_task_turn_id = str(payload.get("turn_id") or "")
                last_task_message = str(payload.get("last_agent_message") or "")
                last_task_completed_at = timestamp
                if current_turn_id == last_task_turn_id:
                    current_turn_id = ""
        elif row_type == "response_item":
            payload_type = payload.get("type")
            if payload_type == "message" and payload.get("role") == "assistant":
                message_text = extract_message_text(payload.get("content") or [])
                if message_text:
                    last_assistant_message = message_text
            elif payload_type == "function_call" and payload.get("name") == "request_user_input":
                call_id = str(payload.get("call_id") or "").strip()
                if call_id:
                    open_input_requests[call_id] = (
                        timestamp,
                        summarize_request_user_input(str(payload.get("arguments") or "")),
                    )
            elif payload_type == "function_call_output":
                call_id = str(payload.get("call_id") or "").strip()
                if call_id:
                    open_input_requests.pop(call_id, None)
        elif row_type == "turn_context":
            git = row.get("payload", {}).get("git") or {}
            branch = str(git.get("branch") or branch)

    thread_meta = index.get(session_id, {})
    title = str(thread_meta.get("thread_name") or "").strip()
    thread_created_at = earliest_timestamp(
        str(thread_meta.get("created_at") or "").strip(),
        str(thread_meta.get("thread_created_at") or "").strip(),
        str(thread_meta.get("first_message_at") or "").strip(),
        str(thread_meta.get("first_user_message_at") or "").strip(),
    )
    thread_updated_at = str(thread_meta.get("updated_at") or "").strip()
    created_at = earliest_timestamp(thread_created_at, created_at, first_event_at)
    updated_at = max(
        [value for value in (thread_updated_at, updated_at, last_event_at, last_task_completed_at) if value],
        default="",
    )
    if not title:
        title = fallback_title_from_message(last_assistant_message, cwd)
    if not branch:
        branch = os.path.basename(cwd.rstrip("/")) or cwd or "unknown"
    if open_input_requests:
        pending_input_request_id, (pending_input_request_at, pending_input_request_message) = max(
            open_input_requests.items(),
            key=lambda item: item[1][0] or "",
        )

    return SessionSummary(
        session_id=session_id,
        cwd=cwd,
        branch=branch,
        created_at=created_at or earliest_timestamp(updated_at, last_task_completed_at, last_event_at),
        updated_at=updated_at or last_event_at,
        title=title,
        last_event_at=last_event_at,
        last_assistant_message=last_assistant_message,
        last_agent_message=last_agent_message,
        last_task_message=last_task_message,
        last_task_turn_id=last_task_turn_id,
        last_task_completed_at=last_task_completed_at,
        pending_input_request_id=pending_input_request_id,
        pending_input_request_at=pending_input_request_at,
        pending_input_request_message=pending_input_request_message,
        in_progress=bool(current_turn_id),
        current_turn_id=current_turn_id,
        is_subagent=is_subagent,
    )


def load_session_summaries(
    conn: sqlite3.Connection,
    sessions_root: Path,
    session_index: Path,
) -> dict[str, SessionSummary]:
    summaries: dict[str, SessionSummary] = {}
    index = load_thread_index(session_index)
    if not sessions_root.exists():
        return summaries

    for path in sorted(sessions_root.rglob("rollout-*.jsonl")):
        try:
            stat = path.stat()
        except FileNotFoundError:
            continue
        summary = cached_summary(conn, path, stat)
        if summary is None:
            try:
                summary = parse_rollout(path, index)
            except Exception:
                continue
            save_cached_summary(conn, path, stat, summary)
        if not summary.session_id or not summary.cwd:
            continue
        current = summaries.get(summary.session_id)
        if current is None or summary.updated_at >= current.updated_at:
            summaries[summary.session_id] = summary

    conn.commit()
    return summaries


def detect_machine_identity(config: AgentConfig | None = None) -> MachineIdentity:
    machine = socket.gethostname()
    dns_name = ""
    tailnet_suffix = ""
    try:
        payload = load_tailscale_status_payload()
        self_info = payload.get("Self") or {}
        machine = str(self_info.get("HostName") or machine).strip() or machine
        dns_name = str(self_info.get("DNSName") or "").strip().rstrip(".")
        tailnet_suffix = tailnet_suffix_from_status(payload)
    except Exception:
        pass
    if not tailnet_suffix and config is not None:
        tailnet_suffix = tailnet_suffix_from_url(config.backend_url)
    if not dns_name:
        dns_name = infer_tailnet_dns_name(machine, tailnet_suffix)
    if dns_name:
        machine = strip_local_hostname(machine)
    return MachineIdentity(machine=machine, dns_name=dns_name)


def build_code_server_url(identity: MachineIdentity, cwd: str) -> str:
    if identity.dns_name:
        return f"https://{identity.dns_name}/?folder={parse.quote(cwd, safe='/')}"
    return ""


def build_same_origin_helper_url(
    identity: MachineIdentity,
    helper_port: int,
    summary: SessionSummary,
) -> str:
    if not identity.dns_name:
        return ""
    query = parse.urlencode(
        {
            "folder": summary.cwd,
            "session_id": summary.session_id,
            "title": summary.title,
            "code_server_url": build_code_server_url(identity, summary.cwd),
        }
    )
    return f"https://{identity.dns_name}/proxy/{helper_port}/session.html?{query}"


def summarize_session(identity: MachineIdentity, summary: SessionSummary, helper_port: int) -> dict[str, Any]:
    folder_name = os.path.basename(summary.cwd.rstrip("/")) or summary.cwd or "unknown"
    needs_attention = False
    attention_kind = ""
    latest_event_notification_message = ""
    if summary.pending_input_request_id:
        activity_state = "needs_input"
        latest_event_status = "needs_input"
        latest_event_id = summary.pending_input_request_id or summary.current_turn_id
        latest_event_message = (
            summary.pending_input_request_message
            or summary.last_agent_message
            or summary.last_assistant_message
        )
        latest_event_created_at = summary.pending_input_request_at or summary.updated_at or summary.last_event_at
        needs_attention = True
        attention_kind = "needs_input"
    elif summary.in_progress:
        activity_state = "working"
        latest_event_status = ""
        latest_event_id = ""
        latest_event_message = ""
        latest_event_created_at = ""
    elif summary.last_task_completed_at:
        activity_state = classify_message_status(summary.last_task_message or summary.last_assistant_message)
        latest_event_status = activity_state
        latest_event_id = summary.last_task_turn_id
        latest_event_message = summary.last_task_message or summary.last_assistant_message
        latest_event_notification_message = latest_event_message
        latest_event_created_at = summary.last_task_completed_at
        if activity_state == "needs_input":
            needs_attention = True
            attention_kind = "needs_input"
        elif not summary.is_subagent:
            needs_attention = True
            attention_kind = "completion_unseen"
    else:
        activity_state = "idle"
        latest_event_status = ""
        latest_event_id = ""
        latest_event_message = ""
        latest_event_created_at = ""

    return {
        "session_id": summary.session_id,
        "cwd": summary.cwd,
        "folder_name": folder_name,
        "branch": summary.branch or folder_name,
        "title": summary.title or folder_name,
        "detail": summary.last_agent_message or summary.last_assistant_message,
        "activity_state": activity_state,
        "created_at": summary.created_at or earliest_timestamp(summary.updated_at, latest_event_created_at, summary.last_event_at),
        "updated_at": summary.updated_at or summary.last_event_at or iso_now(),
        "latest_event_id": latest_event_id,
        "latest_event_status": latest_event_status,
        "latest_event_message": latest_event_message,
        "latest_event_notification_message": latest_event_notification_message,
        "latest_event_created_at": latest_event_created_at,
        "needs_attention": needs_attention,
        "attention_kind": attention_kind,
        "code_server_url": build_code_server_url(identity, summary.cwd),
        "same_origin_helper_url": build_same_origin_helper_url(identity, helper_port, summary),
    }


def session_sort_stamp(item: dict[str, Any]) -> str:
    return str(
        item.get("latest_event_created_at")
        or item.get("updated_at")
        or item.get("created_at")
        or ""
    )


def build_snapshot(
    conn: sqlite3.Connection,
    config: AgentConfig,
    identity: MachineIdentity,
) -> dict[str, Any]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=config.max_session_age_days)
    sessions: list[dict[str, Any]] = []
    for summary in load_session_summaries(conn, config.sessions_root, config.session_index).values():
        updated = parse_iso_timestamp(summary.updated_at) or parse_iso_timestamp(summary.last_event_at)
        if updated is not None and updated < cutoff:
            continue
        sessions.append(summarize_session(identity, summary, config.helper_port))

    sessions.sort(key=lambda item: item.get("session_id") or "")
    sessions.sort(key=session_sort_stamp, reverse=True)
    return {
        "machine": identity.machine,
        "machine_dns": identity.dns_name,
        "generated_at": iso_now(),
        "sessions": sessions,
    }


def snapshot_hash(snapshot: dict[str, Any]) -> str:
    encoded = json.dumps(snapshot, sort_keys=True, ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def should_send_snapshot(
    conn: sqlite3.Connection,
    current_hash: str,
    heartbeat_seconds: int,
    now: float | None = None,
) -> bool:
    timestamp = now if now is not None else time.time()
    previous_hash = get_agent_state(conn, "last_snapshot_hash")
    last_sent_raw = get_agent_state(conn, "last_sent_at")
    last_sent = float(last_sent_raw) if last_sent_raw else 0.0
    if current_hash != previous_hash:
        return True
    return (timestamp - last_sent) >= heartbeat_seconds


def post_snapshot(config: AgentConfig, snapshot: dict[str, Any]) -> dict[str, Any]:
    body = json.dumps(snapshot, ensure_ascii=True).encode("utf-8")
    endpoint = config.backend_url + "/api/agent-snapshot"
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if config.backend_auth_token:
        headers["X-Switchboard-Token"] = config.backend_auth_token
    req = request.Request(
        endpoint,
        data=body,
        headers=headers,
        method="POST",
    )
    with request.urlopen(req, timeout=config.timeout_seconds) as response:
        data = response.read().decode("utf-8") or "{}"
    return json.loads(data)


class HelperStaticHandler(BaseHTTPRequestHandler):
    server_version = "SwitchboardAgentHelper/1.0"

    def do_GET(self) -> None:
        requested = "session.html" if self.path in ("", "/") else self.path.split("?", 1)[0].lstrip("/")
        candidate = (HELPER_STATIC_DIR / requested).resolve()
        if not str(candidate).startswith(str(HELPER_STATIC_DIR.resolve())) or not candidate.exists():
            self.send_error(HTTPStatus.NOT_FOUND, "Not Found")
            return
        body = candidate.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", guess_content_type(candidate.suffix))
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: Any) -> None:
        return


def guess_content_type(suffix: str) -> str:
    return {
        ".html": "text/html; charset=utf-8",
        ".css": "text/css; charset=utf-8",
        ".js": "text/javascript; charset=utf-8",
        ".json": "application/json; charset=utf-8",
        ".png": "image/png",
        ".svg": "image/svg+xml",
    }.get(suffix, "application/octet-stream")


def start_helper_server(config: AgentConfig) -> ThreadingHTTPServer | None:
    if not config.helper_enabled:
        return None
    try:
        server = ThreadingHTTPServer((config.helper_host, config.helper_port), HelperStaticHandler)
    except OSError as exc:
        print(
            f"switchboard-agent warning: helper server unavailable on {config.helper_host}:{config.helper_port}: {exc}",
            file=sys.stderr,
            flush=True,
        )
        return None
    thread = threading.Thread(target=server.serve_forever, name="switchboard-agent-helper", daemon=True)
    thread.start()
    return server


def run_once(
    conn: sqlite3.Connection,
    config: AgentConfig,
    *,
    print_snapshot: bool = False,
) -> bool:
    identity = detect_machine_identity(config)
    snapshot = build_snapshot(conn, config, identity)
    if print_snapshot:
        print(json.dumps(snapshot, indent=2, ensure_ascii=True))
    current_hash = snapshot_hash(snapshot)
    if not should_send_snapshot(conn, current_hash, config.heartbeat_seconds):
        return False

    post_snapshot(config, snapshot)
    now = str(time.time())
    set_agent_state(conn, "last_snapshot_hash", current_hash)
    set_agent_state(conn, "last_sent_at", now)
    conn.commit()
    return True


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    config = load_config(args.config.expanduser())
    conn = init_db(config.state_dir)
    helper_server = start_helper_server(config) if args.loop else None
    try:
        while True:
            changed = run_once(conn, config, print_snapshot=args.print_snapshot)
            if not args.loop:
                return 0
            if changed:
                print(f"switchboard-agent: reported snapshot to {config.backend_url}", flush=True)
            time.sleep(config.interval_seconds)
    except KeyboardInterrupt:
        return 0
    except error.URLError as exc:
        print(f"switchboard-agent error: {exc}", file=sys.stderr, flush=True)
        return 1
    finally:
        if helper_server is not None:
            helper_server.shutdown()
            helper_server.server_close()
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
