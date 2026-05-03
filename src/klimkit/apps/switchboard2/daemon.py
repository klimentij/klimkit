#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import ipaddress
import json
import os
import queue
import re
import socket
import sqlite3
import ssl
import subprocess
import sys
import threading
import time
import traceback
from dataclasses import asdict, dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from http.cookies import SimpleCookie
from pathlib import Path
from typing import Any
from urllib import error, parse, request
from urllib.parse import urlparse

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib


DEFAULT_CONFIG_PATH = Path(__file__).with_name("switchboard2.toml")
STATIC_DIR = Path(__file__).with_name("static")
CACHE_VERSION = 2
DEFAULT_BASE_PATH = "/switchboard2"
AUTH_COOKIE_NAME = "switchboard2_token"
MAX_JSON_BODY_BYTES = 1024 * 1024
MAX_SSE_SUBSCRIBERS = 16
SOCKET_TIMEOUT_SECONDS = 15
UI_VERSION_FILES = (
    "index.html",
    "styles.css",
    "app.js",
    "service-worker.js",
    "manifest.webmanifest",
)
QUESTION_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\?\s*$",
        r"\b(clarify|which|what|how would you like|do you want|please provide|let me know)\b",
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
ACTIVE_STATES = {"starting", "planning", "working", "needs_input", "awaiting_approval"}


@dataclass(frozen=True)
class AppConfig:
    state_dir: Path
    sessions_root: Path
    session_index: Path
    hooks_events_path: Path
    server_enabled: bool
    host: str
    port: int
    base_path: str
    tls_cert_file: Path
    tls_key_file: Path
    backend_url: str
    backend_timeout_seconds: int
    backend_auth_token: str
    collector_enabled: bool
    collector_interval_seconds: float
    heartbeat_seconds: int
    max_session_age_days: int
    stale_after_seconds: int
    machine_id: str
    machine_dns: str


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
    latest_user_message: str
    last_event_at: str
    latest_completion_id: str
    latest_completion_at: str
    latest_completion_message: str
    latest_error_id: str
    latest_error_at: str
    latest_error_message: str
    latest_assistant_message: str
    latest_agent_message: str
    latest_plan_id: str
    latest_plan_at: str
    latest_plan_message: str
    pending_input_request_id: str
    pending_input_request_at: str
    pending_input_request_message: str
    pending_approval_request_id: str
    pending_approval_request_at: str
    pending_approval_request_message: str
    pending_approval_kind: str
    current_turn_id: str
    current_turn_started_at: str
    saw_action_in_current_turn: bool
    approval_policy: str


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Switchboard2 daemon: collector + backend + UI host."
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path(os.environ.get("SWITCHBOARD2_CONFIG", DEFAULT_CONFIG_PATH)),
        help="Path to the switchboard2 TOML config.",
    )
    parser.add_argument(
        "--print-projections",
        action="store_true",
        help="Print current local projections and exit.",
    )
    return parser.parse_args(argv)


def load_config(path: Path) -> AppConfig:
    defaults = {
        "paths": {
            "state_dir": str(Path.home() / ".local" / "state" / "klimkit" / "switchboard2"),
            "sessions_root": str(Path.home() / ".codex" / "sessions"),
            "session_index": str(Path.home() / ".codex" / "session_index.jsonl"),
            "hooks_events": str(Path.home() / ".codex" / "switchboard" / "events.jsonl"),
        },
        "server": {
            "enabled": True,
            "host": "127.0.0.1",
            "port": 4721,
            "base_path": DEFAULT_BASE_PATH,
            "tls_cert_file": "",
            "tls_key_file": "",
        },
        "backend": {
            "base_url": "",
            "timeout_seconds": 10,
            "auth_token": "",
        },
        "collector": {
            "enabled": True,
            "interval_seconds": 0.5,
            "heartbeat_seconds": 15,
            "max_session_age_days": 14,
            "stale_after_seconds": 180,
        },
        "machine": {
            "id": "",
            "dns_name": "",
        },
    }

    raw = tomllib.loads(path.read_text(encoding="utf-8")) if path.exists() else {}

    def nested(section: str, key: str) -> Any:
        return raw.get(section, {}).get(key, defaults[section][key])

    base_path = str(nested("server", "base_path")).strip() or DEFAULT_BASE_PATH
    if not base_path.startswith("/"):
        base_path = "/" + base_path
    base_path = base_path.rstrip("/") or DEFAULT_BASE_PATH

    return AppConfig(
        state_dir=Path(str(nested("paths", "state_dir"))).expanduser(),
        sessions_root=Path(str(nested("paths", "sessions_root"))).expanduser(),
        session_index=Path(str(nested("paths", "session_index"))).expanduser(),
        hooks_events_path=Path(str(nested("paths", "hooks_events"))).expanduser(),
        server_enabled=bool(nested("server", "enabled")),
        host=str(nested("server", "host")).strip(),
        port=max(1, int(nested("server", "port"))),
        base_path=base_path,
        tls_cert_file=optional_path(nested("server", "tls_cert_file")),
        tls_key_file=optional_path(nested("server", "tls_key_file")),
        backend_url=str(nested("backend", "base_url")).strip().rstrip("/"),
        backend_timeout_seconds=max(1, int(nested("backend", "timeout_seconds"))),
        backend_auth_token=str(nested("backend", "auth_token")).strip(),
        collector_enabled=bool(nested("collector", "enabled")),
        collector_interval_seconds=max(0.1, float(nested("collector", "interval_seconds"))),
        heartbeat_seconds=max(5, int(nested("collector", "heartbeat_seconds"))),
        max_session_age_days=max(1, int(nested("collector", "max_session_age_days"))),
        stale_after_seconds=max(30, int(nested("collector", "stale_after_seconds"))),
        machine_id=str(nested("machine", "id")).strip(),
        machine_dns=str(nested("machine", "dns_name")).strip(),
    )


def iso_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def optional_path(value: Any) -> Path:
    text = str(value or "").strip()
    if not text:
        return Path("")
    return Path(text).expanduser()


def parse_iso_timestamp(value: str | None) -> dt.datetime | None:
    if not value:
        return None
    text = value.strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = dt.datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return parsed.astimezone(dt.timezone.utc)


def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def clip_text(text: str, limit: int) -> str:
    normalized = normalize_whitespace(text)
    if len(normalized) <= limit:
        return normalized
    if limit <= 3:
        return normalized[:limit]
    return normalized[: limit - 3].rstrip() + "..."


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


def earliest_timestamp(*values: str) -> str:
    filtered = [value for value in values if value]
    return min(filtered) if filtered else ""


def latest_timestamp(*values: str) -> str:
    filtered = [value for value in values if value]
    return max(filtered) if filtered else ""


def fallback_title_from_context(cwd: str, session_id: str) -> str:
    return folder_name_from_path(cwd) or session_id or "Untitled"


def folder_name_from_path(path: str) -> str:
    normalized = str(path or "").rstrip("/")
    if not normalized:
        return ""
    return normalized.rsplit("/", 1)[-1] or normalized


def stable_json_hash(payload: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=True).encode("utf-8")).hexdigest()


def detect_machine_identity(config: AppConfig) -> MachineIdentity:
    machine = config.machine_id or socket.gethostname()
    dns_name = config.machine_dns
    if config.machine_id and config.machine_dns:
        return MachineIdentity(machine=config.machine_id, dns_name=config.machine_dns.rstrip("."))
    try:
        result = subprocess.run(
            ["tailscale", "status", "--json"],
            capture_output=True,
            text=True,
            check=True,
        )
        payload = json.loads(result.stdout)
        self_info = payload.get("Self") or {}
        machine = str(self_info.get("HostName") or machine).strip() or machine
        dns_name = str(self_info.get("DNSName") or dns_name).strip().rstrip(".")
    except Exception:
        pass
    return MachineIdentity(machine=machine, dns_name=dns_name)


def build_code_server_url(identity: MachineIdentity, cwd: str) -> str:
    if not identity.dns_name or not cwd:
        return ""
    return f"https://{identity.dns_name}/?folder={parse.quote(cwd, safe='/')}"


def is_recent(value: str, max_age_seconds: int) -> bool:
    parsed = parse_iso_timestamp(value)
    if parsed is None:
        return False
    return (dt.datetime.now(dt.timezone.utc) - parsed).total_seconds() <= max_age_seconds


def classify_done_message(message: str) -> str:
    text = normalize_whitespace(message)
    lower = text.lower()
    if not text:
        return "done"
    if lower in TRIVIAL_MESSAGES:
        return "done"
    if any(pattern.search(text) for pattern in QUESTION_PATTERNS):
        return "needs_input"
    return "done"


def normalize_hook_status(status: str) -> str:
    normalized = normalize_whitespace(status).lower().replace(" ", "_")
    if normalized == "errored":
        return "error"
    if normalized in {"needs_input", "awaiting_approval", "error", "done", "working", "planning", "starting", "idle"}:
        return normalized
    return ""


def hook_status_to_activity(status: str) -> tuple[str, str, bool]:
    normalized = normalize_hook_status(status)
    if normalized == "needs_input":
        return ("needs_input", "needs_input", True)
    if normalized == "awaiting_approval":
        return ("awaiting_approval", "awaiting_approval", True)
    if normalized == "error":
        return ("errored", "error", True)
    if normalized == "done":
        return ("done", "completion_unseen", True)
    if normalized in {"working", "planning", "starting", "idle"}:
        return (normalized, "", False)
    return ("idle", "", False)


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
    texts = [
        normalize_whitespace(str(question.get("question") or ""))
        for question in questions
        if isinstance(question, dict)
    ]
    texts = [text for text in texts if text]
    if len(texts) == 1:
        return texts[0]
    if texts:
        return f"Asked {len(texts)} questions. {texts[0]}"
    return f"Asked {len(questions)} questions."


def summarize_approval_request(arguments: str) -> str:
    if not arguments:
        return "Waiting for approval."
    try:
        payload = json.loads(arguments)
    except json.JSONDecodeError:
        return "Waiting for approval."
    justification = normalize_whitespace(str(payload.get("justification") or ""))
    if justification:
        return justification
    cmd = normalize_whitespace(str(payload.get("cmd") or ""))
    if cmd:
        return cmd[:180]
    return "Waiting for approval."


def is_exec_command_approval(arguments: str) -> bool:
    try:
        payload = json.loads(arguments or "{}")
    except json.JSONDecodeError:
        return False
    return str(payload.get("sandbox_permissions") or "").strip() == "require_escalated"


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


def parse_rollout(path: Path, index: dict[str, dict[str, Any]]) -> SessionSummary:
    session_id = ""
    cwd = ""
    branch = ""
    created_at = ""
    updated_at = ""
    title = ""
    latest_user_message = ""
    first_event_at = ""
    last_event_at = ""
    latest_completion_id = ""
    latest_completion_at = ""
    latest_completion_message = ""
    latest_error_id = ""
    latest_error_at = ""
    latest_error_message = ""
    latest_assistant_message = ""
    latest_agent_message = ""
    latest_plan_id = ""
    latest_plan_at = ""
    latest_plan_message = ""
    pending_input_request_id = ""
    pending_input_request_at = ""
    pending_input_request_message = ""
    pending_approval_request_id = ""
    pending_approval_request_at = ""
    pending_approval_request_message = ""
    pending_approval_kind = ""
    current_turn_id = ""
    current_turn_started_at = ""
    saw_action_in_current_turn = False
    approval_policy = ""
    open_input_requests: dict[str, tuple[str, str]] = {}
    open_approval_requests: dict[str, tuple[str, str, str]] = {}

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
            created_at = created_at or timestamp
            updated_at = timestamp or updated_at
            continue

        if row_type == "turn_context":
            git = payload.get("git") or {}
            branch = str(git.get("branch") or branch)
            approval_policy = str(payload.get("approval_policy") or approval_policy)
            continue

        if row_type == "event_msg":
            event_type = str(payload.get("type") or "")
            if event_type == "task_started":
                current_turn_id = str(payload.get("turn_id") or current_turn_id)
                current_turn_started_at = timestamp or current_turn_started_at
                saw_action_in_current_turn = False
                latest_plan_id = ""
                latest_plan_at = ""
                latest_plan_message = ""
            elif event_type in {"task_complete", "turn_aborted"}:
                latest_completion_id = str(payload.get("turn_id") or current_turn_id or latest_completion_id)
                latest_completion_at = timestamp or latest_completion_at
                latest_completion_message = str(
                    payload.get("last_agent_message")
                    or latest_agent_message
                    or latest_assistant_message
                    or latest_plan_message
                    or latest_completion_message
                )
                if current_turn_id == latest_completion_id:
                    current_turn_id = ""
                    current_turn_started_at = ""
                open_input_requests.clear()
                open_approval_requests.clear()
            elif event_type == "agent_message":
                latest_agent_message = str(payload.get("message") or payload.get("last_agent_message") or latest_agent_message)
                if current_turn_id and not saw_action_in_current_turn:
                    latest_plan_id = current_turn_id or latest_plan_id
                    latest_plan_at = timestamp or latest_plan_at
                    latest_plan_message = latest_agent_message or latest_plan_message
            elif event_type == "user_message":
                latest_user_message = str(payload.get("message") or latest_user_message)
            elif event_type in {"plan_update", "plan_delta"}:
                latest_plan_id = str(payload.get("turn_id") or current_turn_id or latest_plan_id or timestamp)
                latest_plan_at = timestamp or latest_plan_at
                latest_plan_message = str(payload.get("message") or payload.get("summary") or latest_plan_message)
            elif event_type in {"exec_command_begin", "mcp_tool_call_begin", "patch_apply_begin", "item_started"}:
                if current_turn_id:
                    saw_action_in_current_turn = True
            elif event_type in {"exec_command_end", "mcp_tool_call_end", "patch_apply_end", "item_completed"}:
                call_id = str(payload.get("call_id") or "")
                if call_id:
                    open_input_requests.pop(call_id, None)
                    open_approval_requests.pop(call_id, None)
                if current_turn_id:
                    saw_action_in_current_turn = True
            elif event_type in {"exec_approval_request", "apply_patch_approval_request"}:
                synthetic_id = str(payload.get("call_id") or payload.get("request_id") or current_turn_id or timestamp)
                open_approval_requests[synthetic_id] = (
                    timestamp,
                    str(payload.get("justification") or payload.get("command") or "Waiting for approval."),
                    "patch" if event_type == "apply_patch_approval_request" else "tool",
                )
            elif event_type in {"error", "stream_error"}:
                latest_error_id = str(payload.get("turn_id") or current_turn_id or latest_error_id or timestamp)
                latest_error_at = timestamp or latest_error_at
                latest_error_message = str(payload.get("message") or payload.get("error") or latest_error_message)
            continue

        if row_type != "response_item":
            continue

        payload_type = str(payload.get("type") or "")
        if payload_type == "message" and payload.get("role") == "assistant":
            message_text = extract_message_text(payload.get("content") or [])
            if message_text:
                latest_assistant_message = message_text
                if current_turn_id and not saw_action_in_current_turn and payload.get("phase") == "commentary":
                    latest_plan_id = current_turn_id or latest_plan_id
                    latest_plan_at = timestamp or latest_plan_at
                    latest_plan_message = message_text
        elif payload_type == "reasoning":
            if current_turn_id and not saw_action_in_current_turn:
                latest_plan_id = current_turn_id or latest_plan_id
                latest_plan_at = timestamp or latest_plan_at
        elif payload_type == "function_call":
            name = str(payload.get("name") or "")
            call_id = str(payload.get("call_id") or "")
            arguments = str(payload.get("arguments") or "")
            if name == "request_user_input" and call_id:
                open_input_requests[call_id] = (
                    timestamp,
                    summarize_request_user_input(arguments),
                )
            else:
                if current_turn_id:
                    saw_action_in_current_turn = True
                if name == "exec_command" and call_id and is_exec_command_approval(arguments):
                    open_approval_requests[call_id] = (
                        timestamp,
                        summarize_approval_request(arguments),
                        "tool",
                    )
        elif payload_type == "function_call_output":
            call_id = str(payload.get("call_id") or "")
            if call_id:
                open_input_requests.pop(call_id, None)
                open_approval_requests.pop(call_id, None)
            if current_turn_id:
                saw_action_in_current_turn = True

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
    updated_at = latest_timestamp(
        thread_updated_at,
        updated_at,
        last_event_at,
        latest_completion_at,
        latest_error_at,
        latest_plan_at,
        current_turn_started_at,
    )
    if not title:
        title = fallback_title_from_context(cwd, session_id)
    if not branch:
        branch = folder_name_from_path(cwd) or "unknown"
    if open_input_requests:
        pending_input_request_id, (pending_input_request_at, pending_input_request_message) = max(
            open_input_requests.items(),
            key=lambda item: item[1][0] or "",
        )
    if open_approval_requests:
        pending_approval_request_id, (
            pending_approval_request_at,
            pending_approval_request_message,
            pending_approval_kind,
        ) = max(
            open_approval_requests.items(),
            key=lambda item: item[1][0] or "",
        )

    return SessionSummary(
        session_id=session_id,
        cwd=cwd,
        branch=branch,
        created_at=created_at or earliest_timestamp(updated_at, last_event_at),
        updated_at=updated_at or last_event_at,
        title=title,
        latest_user_message=latest_user_message,
        last_event_at=last_event_at,
        latest_completion_id=latest_completion_id,
        latest_completion_at=latest_completion_at,
        latest_completion_message=latest_completion_message,
        latest_error_id=latest_error_id,
        latest_error_at=latest_error_at,
        latest_error_message=latest_error_message,
        latest_assistant_message=latest_assistant_message,
        latest_agent_message=latest_agent_message,
        latest_plan_id=latest_plan_id,
        latest_plan_at=latest_plan_at,
        latest_plan_message=latest_plan_message,
        pending_input_request_id=pending_input_request_id,
        pending_input_request_at=pending_input_request_at,
        pending_input_request_message=pending_input_request_message,
        pending_approval_request_id=pending_approval_request_id,
        pending_approval_request_at=pending_approval_request_at,
        pending_approval_request_message=pending_approval_request_message,
        pending_approval_kind=pending_approval_kind,
        current_turn_id=current_turn_id,
        current_turn_started_at=current_turn_started_at,
        saw_action_in_current_turn=saw_action_in_current_turn,
        approval_policy=approval_policy,
    )


def summarize_session(identity: MachineIdentity, summary: SessionSummary) -> dict[str, Any]:
    folder_name = folder_name_from_path(summary.cwd) or "workspace"
    detail = clip_text(
        summary.latest_agent_message
        or summary.latest_assistant_message
        or summary.latest_completion_message
        or summary.latest_plan_message
        or summary.latest_error_message,
        320,
    )

    attention_kind = ""
    latest_event_status = ""
    latest_event_id = ""
    latest_event_message = ""
    latest_event_created_at = ""
    activity_state = "idle"

    if summary.latest_error_at and summary.latest_error_at >= latest_timestamp(summary.latest_completion_at, summary.updated_at):
        activity_state = "errored"
        attention_kind = "error"
        latest_event_status = "error"
        latest_event_id = summary.latest_error_id or summary.current_turn_id or summary.session_id
        latest_event_message = clip_text(summary.latest_error_message or detail or "Agent errored.", 240)
        latest_event_created_at = summary.latest_error_at
    elif summary.pending_approval_request_id:
        activity_state = "awaiting_approval"
        attention_kind = "awaiting_approval"
        latest_event_status = "awaiting_approval"
        latest_event_id = summary.pending_approval_request_id
        latest_event_message = clip_text(
            summary.pending_approval_request_message or "Waiting for approval.",
            240,
        )
        latest_event_created_at = summary.pending_approval_request_at
    elif summary.pending_input_request_id:
        activity_state = "needs_input"
        attention_kind = "needs_input"
        latest_event_status = "needs_input"
        latest_event_id = summary.pending_input_request_id
        latest_event_message = clip_text(
            summary.pending_input_request_message or "Waiting for user input.",
            240,
        )
        latest_event_created_at = summary.pending_input_request_at
    elif summary.current_turn_id:
        latest_event_id = summary.current_turn_id
        latest_event_message = clip_text(detail, 240)
        latest_event_created_at = latest_timestamp(summary.latest_plan_at, summary.current_turn_started_at, summary.updated_at)
        if summary.saw_action_in_current_turn:
            activity_state = "working"
        elif summary.latest_plan_at or detail:
            activity_state = "planning"
        else:
            activity_state = "starting"
    elif summary.latest_completion_at:
        completion_status = classify_done_message(
            summary.latest_completion_message or summary.latest_agent_message or summary.latest_assistant_message
        )
        if completion_status == "needs_input":
            activity_state = "needs_input"
            attention_kind = "needs_input"
            latest_event_status = "needs_input"
        else:
            activity_state = "done"
            attention_kind = "completion_unseen"
            latest_event_status = "done"
        latest_event_id = summary.latest_completion_id or summary.session_id
        latest_event_message = clip_text(
            summary.latest_completion_message
            or summary.latest_agent_message
            or summary.latest_assistant_message
            or "Completed.",
            240,
        )
        latest_event_created_at = summary.latest_completion_at
    else:
        activity_state = "idle"
        latest_event_message = clip_text(detail, 240)
        latest_event_created_at = latest_timestamp(summary.updated_at, summary.last_event_at)

    return {
        "session_id": summary.session_id,
        "cwd": summary.cwd,
        "folder_name": folder_name,
        "branch": summary.branch or folder_name,
        "title": clip_text(summary.title or folder_name, 120),
        "latest_user_message": clip_text(summary.latest_user_message, 240),
        "detail": detail,
        "activity_state": activity_state,
        "created_at": summary.created_at or earliest_timestamp(summary.updated_at, latest_event_created_at),
        "updated_at": summary.updated_at or summary.last_event_at or iso_now(),
        "latest_event_id": latest_event_id,
        "latest_event_status": latest_event_status,
        "latest_event_message": latest_event_message,
        "latest_event_created_at": latest_event_created_at,
        "needs_attention": bool(attention_kind),
        "attention_kind": attention_kind,
        "approval_policy": summary.approval_policy,
        "code_server_url": build_code_server_url(identity, summary.cwd),
        "same_origin_helper_url": "",
    }


def session_sort_stamp(item: dict[str, Any]) -> str:
    return str(
        item.get("latest_event_created_at")
        or item.get("updated_at")
        or item.get("created_at")
        or item.get("reported_at")
        or ""
    )


def session_creation_sort_stamp(item: dict[str, Any]) -> str:
    return str(
        item.get("created_at")
        or item.get("reported_at")
        or item.get("updated_at")
        or item.get("latest_event_created_at")
        or ""
    )


def display_state_for_row(row: sqlite3.Row | dict[str, Any], stale_after_seconds: int) -> str:
    activity_state = str(row["activity_state"])
    reported_at = str(row["reported_at"])
    latest_event_id = str(row["latest_event_id"])
    last_seen_event_id = str(row["last_seen_event_id"])
    attention_kind = str(row["attention_kind"])
    if activity_state in ACTIVE_STATES and not is_recent(reported_at, stale_after_seconds):
        return "stale"
    if activity_state == "done" and latest_event_id and latest_event_id == last_seen_event_id and attention_kind == "":
        return "seen"
    return activity_state


def is_newer_timestamp(candidate: str, reference: str) -> bool:
    candidate_parsed = parse_iso_timestamp(candidate)
    reference_parsed = parse_iso_timestamp(reference)
    if candidate_parsed is None:
        return False
    if reference_parsed is None:
        return True
    return candidate_parsed > reference_parsed


class EventBroadcaster:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._subscribers: set[queue.Queue[str]] = set()
        self._sequence = 0

    def subscribe(self) -> queue.Queue[str] | None:
        subscriber: queue.Queue[str] = queue.Queue(maxsize=32)
        with self._lock:
            if len(self._subscribers) >= MAX_SSE_SUBSCRIBERS:
                return None
            self._subscribers.add(subscriber)
            self._sequence += 1
            payload = json.dumps({"sequence": self._sequence, "reason": "connected"}, ensure_ascii=True)
            subscriber.put_nowait(f"event: invalidate\ndata: {payload}\n\n")
        return subscriber

    def unsubscribe(self, subscriber: queue.Queue[str]) -> None:
        with self._lock:
            self._subscribers.discard(subscriber)

    def publish_invalidate(self, reason: str) -> None:
        with self._lock:
            self._sequence += 1
            payload = json.dumps({"sequence": self._sequence, "reason": reason}, ensure_ascii=True)
            dead: list[queue.Queue[str]] = []
            for subscriber in self._subscribers:
                try:
                    subscriber.put_nowait(f"event: invalidate\ndata: {payload}\n\n")
                except queue.Full:
                    dead.append(subscriber)
            for subscriber in dead:
                self._subscribers.discard(subscriber)


class StateStore:
    def __init__(self, state_dir: Path) -> None:
        self.state_dir = state_dir
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.state_dir / "switchboard2.sqlite3"
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        self._lock = threading.Lock()
        self._init_db()

    def close(self) -> None:
        with self._lock:
            self.conn.close()

    def _init_db(self) -> None:
        with self._lock:
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS rollout_cache (
                    path TEXT PRIMARY KEY,
                    parser_version INTEGER NOT NULL DEFAULT 0,
                    size INTEGER NOT NULL,
                    mtime_ns INTEGER NOT NULL,
                    summary_json TEXT NOT NULL
                )
                """
            )
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS collector_state (
                    session_id TEXT PRIMARY KEY,
                    projection_hash TEXT NOT NULL DEFAULT ''
                )
                """
            )
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS runtime_state (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
                """
            )
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS outbound_queue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id TEXT NOT NULL UNIQUE,
                    payload_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    available_at REAL NOT NULL DEFAULT 0,
                    attempts INTEGER NOT NULL DEFAULT 0,
                    last_error TEXT NOT NULL DEFAULT ''
                )
                """
            )
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS machine_heartbeats (
                    machine TEXT PRIMARY KEY,
                    machine_dns TEXT NOT NULL DEFAULT '',
                    generated_at TEXT NOT NULL DEFAULT '',
                    reported_at TEXT NOT NULL DEFAULT '',
                    session_count INTEGER NOT NULL DEFAULT 0
                )
                """
            )
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS session_state (
                    session_id TEXT PRIMARY KEY,
                    machine TEXT NOT NULL DEFAULT '',
                    machine_dns TEXT NOT NULL DEFAULT '',
                    cwd TEXT NOT NULL DEFAULT '',
                    folder_name TEXT NOT NULL DEFAULT '',
                    code_server_url TEXT NOT NULL DEFAULT '',
                    same_origin_helper_url TEXT NOT NULL DEFAULT '',
                    title TEXT NOT NULL DEFAULT '',
                    latest_user_message TEXT NOT NULL DEFAULT '',
                    branch TEXT NOT NULL DEFAULT '',
                    detail TEXT NOT NULL DEFAULT '',
                    activity_state TEXT NOT NULL DEFAULT 'idle',
                    created_at TEXT NOT NULL DEFAULT '',
                    updated_at TEXT NOT NULL DEFAULT '',
                    latest_event_id TEXT NOT NULL DEFAULT '',
                    latest_event_status TEXT NOT NULL DEFAULT '',
                    latest_event_message TEXT NOT NULL DEFAULT '',
                    latest_event_created_at TEXT NOT NULL DEFAULT '',
                    needs_attention INTEGER NOT NULL DEFAULT 0,
                    attention_kind TEXT NOT NULL DEFAULT '',
                    approval_policy TEXT NOT NULL DEFAULT '',
                    archived INTEGER NOT NULL DEFAULT 0,
                    archived_at TEXT NOT NULL DEFAULT '',
                    last_seen_event_id TEXT NOT NULL DEFAULT '',
                    seen_at TEXT NOT NULL DEFAULT '',
                    reported_at TEXT NOT NULL DEFAULT ''
                )
                """
            )
            try:
                self.conn.execute(
                    "ALTER TABLE session_state ADD COLUMN latest_user_message TEXT NOT NULL DEFAULT ''"
                )
            except sqlite3.OperationalError:
                pass
            self.conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_session_state_recent ON session_state(reported_at DESC)"
            )
            self.conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_outbound_queue_available ON outbound_queue(available_at, id)"
            )
            self.conn.commit()

    def get_runtime_state(self, key: str) -> str:
        with self._lock:
            row = self.conn.execute("SELECT value FROM runtime_state WHERE key = ?", (key,)).fetchone()
            return str(row["value"]) if row else ""

    def set_runtime_state(self, key: str, value: str) -> None:
        with self._lock:
            self.conn.execute(
                """
                INSERT INTO runtime_state(key, value)
                VALUES(?, ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
                """,
                (key, value),
            )
            self.conn.commit()

    def get_cached_summary(self, path: Path, stat: os.stat_result) -> SessionSummary | None:
        with self._lock:
            row = self.conn.execute(
                """
                SELECT summary_json FROM rollout_cache
                WHERE path = ? AND parser_version = ? AND size = ? AND mtime_ns = ?
                """,
                (str(path), CACHE_VERSION, stat.st_size, stat.st_mtime_ns),
            ).fetchone()
        if row is None:
            return None
        payload = json.loads(str(row["summary_json"]))
        return SessionSummary(**payload)

    def save_cached_summary(self, path: Path, stat: os.stat_result, summary: SessionSummary) -> None:
        with self._lock:
            self.conn.execute(
                """
                INSERT INTO rollout_cache(path, parser_version, size, mtime_ns, summary_json)
                VALUES(?, ?, ?, ?, ?)
                ON CONFLICT(path) DO UPDATE SET
                  parser_version = excluded.parser_version,
                  size = excluded.size,
                  mtime_ns = excluded.mtime_ns,
                  summary_json = excluded.summary_json
                """,
                (
                    str(path),
                    CACHE_VERSION,
                    stat.st_size,
                    stat.st_mtime_ns,
                    json.dumps(asdict(summary), ensure_ascii=True),
                ),
            )
            self.conn.commit()

    def projection_hash(self, session_id: str) -> str:
        with self._lock:
            row = self.conn.execute(
                "SELECT projection_hash FROM collector_state WHERE session_id = ?",
                (session_id,),
            ).fetchone()
            return str(row["projection_hash"]) if row else ""

    def set_projection_hash(self, session_id: str, projection_hash: str) -> None:
        with self._lock:
            self.conn.execute(
                """
                INSERT INTO collector_state(session_id, projection_hash)
                VALUES(?, ?)
                ON CONFLICT(session_id) DO UPDATE SET projection_hash = excluded.projection_hash
                """,
                (session_id, projection_hash),
            )
            self.conn.commit()

    def enqueue_event(self, event: dict[str, Any]) -> None:
        with self._lock:
            self.conn.execute(
                """
                INSERT OR IGNORE INTO outbound_queue(event_id, payload_json, created_at, available_at)
                VALUES(?, ?, ?, 0)
                """,
                (
                    str(event["event_id"]),
                    json.dumps(event, ensure_ascii=True),
                    str(event.get("created_at") or iso_now()),
                ),
            )
            self.conn.commit()

    def next_outbound_batch(self, limit: int = 100) -> list[sqlite3.Row]:
        now = time.time()
        with self._lock:
            return list(
                self.conn.execute(
                    """
                    SELECT id, event_id, payload_json, attempts
                    FROM outbound_queue
                    WHERE available_at <= ?
                    ORDER BY id ASC
                    LIMIT ?
                    """,
                    (now, limit),
                )
            )

    def mark_outbound_sent(self, ids: list[int]) -> None:
        if not ids:
            return
        placeholders = ",".join("?" for _ in ids)
        with self._lock:
            self.conn.execute(
                f"DELETE FROM outbound_queue WHERE id IN ({placeholders})",
                ids,
            )
            self.conn.commit()

    def backoff_outbound(self, ids: list[int], error_message: str) -> None:
        if not ids:
            return
        with self._lock:
            rows = list(
                self.conn.execute(
                    f"SELECT id, attempts FROM outbound_queue WHERE id IN ({','.join('?' for _ in ids)})",
                    ids,
                )
            )
            for row in rows:
                attempts = int(row["attempts"]) + 1
                delay = min(30.0, 0.5 * (2 ** max(0, attempts - 1)))
                self.conn.execute(
                    """
                    UPDATE outbound_queue
                    SET attempts = ?, last_error = ?, available_at = ?
                    WHERE id = ?
                    """,
                    (attempts, error_message[:800], time.time() + delay, int(row["id"])),
                )
            self.conn.commit()

    def apply_snapshot(self, payload: dict[str, Any]) -> int:
        machine = str(payload.get("machine") or "").strip()
        if not machine:
            raise ValueError("missing required field: machine")
        machine_dns = str(payload.get("machine_dns") or "").strip()
        generated_at = str(payload.get("generated_at") or iso_now()).strip()
        sessions = payload.get("sessions")
        if not isinstance(sessions, list):
            raise ValueError("missing required field: sessions")
        self.upsert_machine_heartbeat(machine, machine_dns, generated_at, len(sessions))
        for session in sessions:
            if not isinstance(session, dict):
                continue
            self.upsert_session_projection(machine, machine_dns, generated_at, session)
        return len(sessions)

    def apply_event_batch(self, events: list[dict[str, Any]]) -> int:
        applied = 0
        for event in events:
            event_type = str(event.get("type") or "")
            if event_type == "machine_heartbeat":
                self.upsert_machine_heartbeat(
                    str(event.get("machine") or ""),
                    str(event.get("machine_dns") or ""),
                    str(event.get("generated_at") or iso_now()),
                    int(event.get("session_count") or 0),
                )
                applied += 1
            elif event_type == "session_upsert":
                session = event.get("session")
                if isinstance(session, dict):
                    self.upsert_session_projection(
                        str(event.get("machine") or ""),
                        str(event.get("machine_dns") or ""),
                    str(event.get("generated_at") or iso_now()),
                    session,
                )
                applied += 1
            elif event_type == "hook_hint":
                if self.upsert_hook_hint(event):
                    applied += 1
        return applied

    def upsert_machine_heartbeat(self, machine: str, machine_dns: str, generated_at: str, session_count: int) -> None:
        if not machine:
            return
        with self._lock:
            self.conn.execute(
                """
                INSERT INTO machine_heartbeats(machine, machine_dns, generated_at, reported_at, session_count)
                VALUES(?, ?, ?, ?, ?)
                ON CONFLICT(machine) DO UPDATE SET
                  machine_dns = excluded.machine_dns,
                  generated_at = excluded.generated_at,
                  reported_at = excluded.reported_at,
                  session_count = excluded.session_count
                """,
                (machine, machine_dns, generated_at, generated_at, session_count),
            )
            self.conn.commit()

    def upsert_session_projection(self, machine: str, machine_dns: str, generated_at: str, session: dict[str, Any]) -> None:
        session_id = str(session.get("session_id") or session.get("id") or "").strip()
        if not session_id:
            return
        with self._lock:
            existing = self.conn.execute(
                "SELECT * FROM session_state WHERE session_id = ?",
                (session_id,),
            ).fetchone()

            archived = int(existing["archived"]) if existing else 0
            archived_at = str(existing["archived_at"]) if existing else ""
            last_seen_event_id = str(existing["last_seen_event_id"]) if existing else ""
            seen_at = str(existing["seen_at"]) if existing else ""

            activity_state = str(session.get("activity_state") or "idle")
            latest_event_id = str(session.get("latest_event_id") or "")
            attention_kind = str(session.get("attention_kind") or "")
            needs_attention = bool(session.get("needs_attention"))

            if activity_state == "done" and latest_event_id and latest_event_id == last_seen_event_id:
                attention_kind = ""
                needs_attention = False
            elif activity_state != "done" and attention_kind == "completion_unseen":
                attention_kind = ""
                needs_attention = False

            created_at = str(session.get("created_at") or "")
            existing_created_at = str(existing["created_at"]) if existing else ""
            if existing_created_at and created_at:
                created_at = min(existing_created_at, created_at)
            elif existing_created_at:
                created_at = existing_created_at

            cwd = str(session.get("cwd") or "")
            resolved_machine_dns = machine_dns or str(session.get("machine_dns") or "")
            derived_code_server_url = build_code_server_url(
                MachineIdentity(machine=machine or str(session.get("machine") or ""), dns_name=resolved_machine_dns),
                cwd,
            )

            payload = {
                "session_id": session_id,
                "machine": machine,
                "machine_dns": resolved_machine_dns,
                "cwd": cwd,
                "folder_name": str(session.get("folder_name") or folder_name_from_path(cwd)),
                "code_server_url": derived_code_server_url,
                "same_origin_helper_url": str(session.get("same_origin_helper_url") or ""),
                "title": str(session.get("title") or folder_name_from_path(cwd) or session_id),
                "latest_user_message": str(session.get("latest_user_message") or ""),
                "branch": str(session.get("branch") or folder_name_from_path(cwd) or "workspace"),
                "detail": str(session.get("detail") or ""),
                "activity_state": activity_state,
                "created_at": created_at,
                "updated_at": str(session.get("updated_at") or generated_at),
                "latest_event_id": latest_event_id,
                "latest_event_status": str(session.get("latest_event_status") or ""),
                "latest_event_message": str(session.get("latest_event_message") or ""),
                "latest_event_created_at": str(session.get("latest_event_created_at") or session.get("updated_at") or generated_at),
                "needs_attention": 1 if needs_attention else 0,
                "attention_kind": attention_kind,
                "approval_policy": str(session.get("approval_policy") or ""),
                "archived": archived,
                "archived_at": archived_at,
                "last_seen_event_id": last_seen_event_id,
                "seen_at": seen_at,
                "reported_at": generated_at,
            }
            self.conn.execute(
                """
                INSERT INTO session_state(
                    session_id, machine, machine_dns, cwd, folder_name, code_server_url,
                    same_origin_helper_url, title, latest_user_message, branch, detail, activity_state, created_at, updated_at,
                    latest_event_id, latest_event_status, latest_event_message, latest_event_created_at,
                    needs_attention, attention_kind, approval_policy, archived, archived_at,
                    last_seen_event_id, seen_at, reported_at
                ) VALUES(
                    :session_id, :machine, :machine_dns, :cwd, :folder_name, :code_server_url,
                    :same_origin_helper_url, :title, :latest_user_message, :branch, :detail, :activity_state, :created_at, :updated_at,
                    :latest_event_id, :latest_event_status, :latest_event_message, :latest_event_created_at,
                    :needs_attention, :attention_kind, :approval_policy, :archived, :archived_at,
                    :last_seen_event_id, :seen_at, :reported_at
                )
                ON CONFLICT(session_id) DO UPDATE SET
                    machine = excluded.machine,
                    machine_dns = excluded.machine_dns,
                    cwd = excluded.cwd,
                    folder_name = excluded.folder_name,
                    code_server_url = excluded.code_server_url,
                    same_origin_helper_url = excluded.same_origin_helper_url,
                    title = excluded.title,
                    latest_user_message = excluded.latest_user_message,
                    branch = excluded.branch,
                    detail = excluded.detail,
                    activity_state = excluded.activity_state,
                    created_at = excluded.created_at,
                    updated_at = excluded.updated_at,
                    latest_event_id = excluded.latest_event_id,
                    latest_event_status = excluded.latest_event_status,
                    latest_event_message = excluded.latest_event_message,
                    latest_event_created_at = excluded.latest_event_created_at,
                    needs_attention = excluded.needs_attention,
                    attention_kind = excluded.attention_kind,
                    approval_policy = excluded.approval_policy,
                    archived = excluded.archived,
                    archived_at = excluded.archived_at,
                    last_seen_event_id = excluded.last_seen_event_id,
                    seen_at = excluded.seen_at,
                    reported_at = excluded.reported_at
                """,
                payload,
            )
            self.conn.commit()

    def upsert_hook_hint(self, event: dict[str, Any]) -> bool:
        session_id = str(event.get("session_id") or "").strip()
        if not session_id:
            return False
        status = normalize_hook_status(str(event.get("status") or ""))
        if not status:
            return False
        hook_created_at = str(event.get("created_at") or event.get("generated_at") or iso_now()).strip()
        if not hook_created_at:
            hook_created_at = iso_now()
        machine = str(event.get("machine") or "").strip()
        if not machine:
            return False
        machine_dns = str(event.get("machine_dns") or "").strip()
        cwd = str(event.get("cwd") or "").strip()
        title = str(event.get("title") or "").strip()
        branch = str(event.get("branch") or "").strip()
        message = clip_text(str(event.get("message") or "").strip(), 240)
        hook_event_id = str(event.get("event_id") or f"{machine}:{session_id}:{hook_created_at}:{status}").strip()

        with self._lock:
            existing = self.conn.execute(
                "SELECT * FROM session_state WHERE session_id = ?",
                (session_id,),
            ).fetchone()

            if existing is not None:
                existing_latest = latest_timestamp(
                    str(existing["latest_event_created_at"]),
                    str(existing["updated_at"]),
                    str(existing["reported_at"]),
                )
                if existing_latest and hook_created_at and is_newer_timestamp(existing_latest, hook_created_at):
                    return False

            archived = int(existing["archived"]) if existing else 0
            archived_at = str(existing["archived_at"]) if existing else ""
            last_seen_event_id = str(existing["last_seen_event_id"]) if existing else ""
            seen_at = str(existing["seen_at"]) if existing else ""

            activity_state, attention_kind, needs_attention = hook_status_to_activity(status)
            if status == "done" and hook_event_id and hook_event_id == last_seen_event_id:
                attention_kind = ""
                needs_attention = False

            existing_created_at = str(existing["created_at"]) if existing else ""
            created_at = earliest_timestamp(existing_created_at, hook_created_at) or hook_created_at
            updated_at = latest_timestamp(
                hook_created_at,
                str(existing["updated_at"]) if existing else "",
            ) or hook_created_at

            resolved_machine = machine or (str(existing["machine"]) if existing else "")
            resolved_machine_dns = machine_dns or (str(existing["machine_dns"]) if existing else "")
            resolved_cwd = cwd or (str(existing["cwd"]) if existing else "")
            resolved_folder = (
                folder_name_from_path(resolved_cwd)
                or str(event.get("workspace") or "").strip()
                or (str(existing["folder_name"]) if existing else "")
                or "workspace"
            )
            resolved_title = title or (str(existing["title"]) if existing else "") or resolved_folder or session_id
            resolved_branch = branch or (str(existing["branch"]) if existing else "") or resolved_folder
            existing_detail = str(existing["detail"]) if existing else ""
            existing_latest_user_message = str(existing["latest_user_message"]) if existing else ""
            resolved_code_server_url = build_code_server_url(
                MachineIdentity(machine=resolved_machine, dns_name=resolved_machine_dns),
                resolved_cwd,
            )

            payload = {
                "session_id": session_id,
                "machine": resolved_machine,
                "machine_dns": resolved_machine_dns,
                "cwd": resolved_cwd,
                "folder_name": resolved_folder,
                "code_server_url": resolved_code_server_url,
                "same_origin_helper_url": str(existing["same_origin_helper_url"]) if existing else "",
                "title": clip_text(resolved_title, 120),
                "latest_user_message": existing_latest_user_message,
                "branch": resolved_branch,
                "detail": clip_text(message or existing_detail, 320),
                "activity_state": activity_state,
                "created_at": created_at,
                "updated_at": updated_at,
                "latest_event_id": hook_event_id,
                "latest_event_status": status,
                "latest_event_message": message,
                "latest_event_created_at": hook_created_at,
                "needs_attention": 1 if needs_attention else 0,
                "attention_kind": attention_kind,
                "approval_policy": str(existing["approval_policy"]) if existing else "",
                "archived": archived,
                "archived_at": archived_at,
                "last_seen_event_id": last_seen_event_id,
                "seen_at": seen_at,
                "reported_at": hook_created_at,
            }
            self.conn.execute(
                """
                INSERT INTO session_state(
                    session_id, machine, machine_dns, cwd, folder_name, code_server_url,
                    same_origin_helper_url, title, latest_user_message, branch, detail, activity_state, created_at, updated_at,
                    latest_event_id, latest_event_status, latest_event_message, latest_event_created_at,
                    needs_attention, attention_kind, approval_policy, archived, archived_at,
                    last_seen_event_id, seen_at, reported_at
                ) VALUES(
                    :session_id, :machine, :machine_dns, :cwd, :folder_name, :code_server_url,
                    :same_origin_helper_url, :title, :latest_user_message, :branch, :detail, :activity_state, :created_at, :updated_at,
                    :latest_event_id, :latest_event_status, :latest_event_message, :latest_event_created_at,
                    :needs_attention, :attention_kind, :approval_policy, :archived, :archived_at,
                    :last_seen_event_id, :seen_at, :reported_at
                )
                ON CONFLICT(session_id) DO UPDATE SET
                    machine = excluded.machine,
                    machine_dns = excluded.machine_dns,
                    cwd = excluded.cwd,
                    folder_name = excluded.folder_name,
                    code_server_url = excluded.code_server_url,
                    same_origin_helper_url = excluded.same_origin_helper_url,
                    title = excluded.title,
                    latest_user_message = excluded.latest_user_message,
                    branch = excluded.branch,
                    detail = excluded.detail,
                    activity_state = excluded.activity_state,
                    created_at = excluded.created_at,
                    updated_at = excluded.updated_at,
                    latest_event_id = excluded.latest_event_id,
                    latest_event_status = excluded.latest_event_status,
                    latest_event_message = excluded.latest_event_message,
                    latest_event_created_at = excluded.latest_event_created_at,
                    needs_attention = excluded.needs_attention,
                    attention_kind = excluded.attention_kind,
                    approval_policy = excluded.approval_policy,
                    archived = excluded.archived,
                    archived_at = excluded.archived_at,
                    last_seen_event_id = excluded.last_seen_event_id,
                    seen_at = excluded.seen_at,
                    reported_at = excluded.reported_at
                """,
                payload,
            )
            self.conn.commit()
        return True

    def build_state(self, hostname: str, stale_after_seconds: int, retention_days: int) -> dict[str, Any]:
        cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=retention_days)
        cutoff_text = cutoff.isoformat().replace("+00:00", "Z")
        with self._lock:
            machine_rows = list(
                self.conn.execute(
                    """
                    SELECT machine, machine_dns, generated_at, reported_at, session_count
                    FROM machine_heartbeats
                    ORDER BY machine ASC
                    """
                )
            )
            session_rows = list(
                self.conn.execute(
                    """
                    SELECT *
                    FROM session_state
                    WHERE reported_at >= ? OR archived = 1
                    """,
                    (cutoff_text,),
                )
            )

        machines = [
            {
                "machine": str(row["machine"]),
                "machine_dns": str(row["machine_dns"]),
                "generated_at": str(row["generated_at"]),
                "reported_at": str(row["reported_at"]),
                "session_count": int(row["session_count"]),
                "online": is_recent(str(row["reported_at"]), stale_after_seconds),
            }
            for row in machine_rows
        ]

        workspaces: list[dict[str, Any]] = []
        for row in session_rows:
            display_state = display_state_for_row(row, stale_after_seconds)
            needs_attention = bool(row["needs_attention"])
            workspace = {
                "id": str(row["session_id"]),
                "session_id": str(row["session_id"]),
                "machine": str(row["machine"]),
                "machine_dns": str(row["machine_dns"]),
                "cwd": str(row["cwd"]),
                "folder_name": str(row["folder_name"]),
                "code_server_url": str(row["code_server_url"]),
                "same_origin_helper_url": str(row["same_origin_helper_url"]),
                "title": str(row["title"]),
                "latest_user_message": str(row["latest_user_message"]),
                "branch": str(row["branch"]),
                "detail": str(row["detail"]),
                "activity_state": str(row["activity_state"]),
                "display_state": display_state,
                "created_at": str(row["created_at"]),
                "updated_at": str(row["updated_at"]),
                "latest_event_id": str(row["latest_event_id"]),
                "latest_event_status": str(row["latest_event_status"]),
                "latest_event_message": str(row["latest_event_message"]),
                "latest_event_created_at": str(row["latest_event_created_at"]),
                "needs_attention": needs_attention,
                "attention_kind": str(row["attention_kind"]),
                "approval_policy": str(row["approval_policy"]),
                "archived": bool(row["archived"]),
                "archived_at": str(row["archived_at"]),
                "seen_at": str(row["seen_at"]),
                "reported_at": str(row["reported_at"]),
                "is_local": False,
            }
            workspaces.append(workspace)

        workspaces.sort(key=lambda item: str(item["id"]))
        workspaces.sort(key=lambda item: session_creation_sort_stamp(item), reverse=True)
        workspaces.sort(key=lambda item: 1 if item["archived"] else 0)

        return {
            "generated_at": iso_now(),
            "hostname": hostname,
            "machines": machines,
            "workspaces": workspaces,
        }

    def acknowledge_completion(self, session_id: str, event_id: str | None = None) -> dict[str, Any]:
        with self._lock:
            row = self.conn.execute(
                "SELECT * FROM session_state WHERE session_id = ?",
                (session_id,),
            ).fetchone()
            if row is None:
                raise KeyError(session_id)
            latest_event_id = str(row["latest_event_id"])
            current_attention = str(row["attention_kind"])
            if not latest_event_id or current_attention != "completion_unseen":
                return self._row_to_workspace(row, stale_after_seconds=999999)
            if event_id and event_id != latest_event_id:
                return self._row_to_workspace(row, stale_after_seconds=999999)
            seen_at = iso_now()
            self.conn.execute(
                """
                UPDATE session_state
                SET needs_attention = 0,
                    attention_kind = '',
                    last_seen_event_id = ?,
                    seen_at = ?
                WHERE session_id = ?
                """,
                (latest_event_id, seen_at, session_id),
            )
            self.conn.commit()
            updated = self.conn.execute(
                "SELECT * FROM session_state WHERE session_id = ?",
                (session_id,),
            ).fetchone()
        assert updated is not None
        return self._row_to_workspace(updated, stale_after_seconds=999999)

    def set_archive_state(self, session_id: str, archived: bool) -> dict[str, Any]:
        return self.set_archive_state_many([session_id], archived)[0]

    def set_archive_state_many(self, session_ids: list[str], archived: bool) -> list[dict[str, Any]]:
        normalized = [str(session_id).strip() for session_id in session_ids if str(session_id).strip()]
        if not normalized:
            return []
        placeholders = ",".join("?" for _ in normalized)
        archived_at = iso_now() if archived else ""
        with self._lock:
            rows = list(
                self.conn.execute(
                    f"SELECT * FROM session_state WHERE session_id IN ({placeholders})",
                    normalized,
                )
            )
            found = {str(row["session_id"]) for row in rows}
            missing = [session_id for session_id in normalized if session_id not in found]
            if missing:
                raise KeyError(missing[0])
            self.conn.execute(
                f"""
                UPDATE session_state
                SET archived = ?, archived_at = ?
                WHERE session_id IN ({placeholders})
                """,
                [1 if archived else 0, archived_at, *normalized],
            )
            self.conn.commit()
            updated = list(
                self.conn.execute(
                    f"SELECT * FROM session_state WHERE session_id IN ({placeholders})",
                    normalized,
                )
            )
        return [self._row_to_workspace(row, stale_after_seconds=999999) for row in updated]

    def _row_to_workspace(self, row: sqlite3.Row, stale_after_seconds: int) -> dict[str, Any]:
        return {
            "id": str(row["session_id"]),
            "session_id": str(row["session_id"]),
            "machine": str(row["machine"]),
            "machine_dns": str(row["machine_dns"]),
            "cwd": str(row["cwd"]),
            "folder_name": str(row["folder_name"]),
            "code_server_url": str(row["code_server_url"]),
            "same_origin_helper_url": str(row["same_origin_helper_url"]),
            "title": str(row["title"]),
            "latest_user_message": str(row["latest_user_message"]),
            "branch": str(row["branch"]),
            "detail": str(row["detail"]),
            "activity_state": str(row["activity_state"]),
            "display_state": display_state_for_row(row, stale_after_seconds),
            "created_at": str(row["created_at"]),
            "updated_at": str(row["updated_at"]),
            "latest_event_id": str(row["latest_event_id"]),
            "latest_event_status": str(row["latest_event_status"]),
            "latest_event_message": str(row["latest_event_message"]),
            "latest_event_created_at": str(row["latest_event_created_at"]),
            "needs_attention": bool(row["needs_attention"]),
            "attention_kind": str(row["attention_kind"]),
            "approval_policy": str(row["approval_policy"]),
            "archived": bool(row["archived"]),
            "archived_at": str(row["archived_at"]),
            "seen_at": str(row["seen_at"]),
            "reported_at": str(row["reported_at"]),
            "is_local": False,
        }


class Switchboard2App:
    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.identity = detect_machine_identity(config)
        self.hostname = socket.gethostname()
        self.store = StateStore(config.state_dir)
        self.broadcaster = EventBroadcaster()
        self._stop_event = threading.Event()
        self._collector_thread: threading.Thread | None = None
        self._sender_thread: threading.Thread | None = None
        self._server: ThreadingHTTPServer | None = None
        self._lock = threading.Lock()

    @property
    def local_primary(self) -> bool:
        return self.config.server_enabled and not self.config.backend_url

    def close(self) -> None:
        self._stop_event.set()
        if self._server is not None:
            self._server.shutdown()
            self._server.server_close()
        if self._collector_thread is not None:
            self._collector_thread.join(timeout=2)
        if self._sender_thread is not None:
            self._sender_thread.join(timeout=2)
        self.store.close()

    def build_state(self) -> dict[str, Any]:
        return self.store.build_state(
            hostname=self.hostname,
            stale_after_seconds=self.config.stale_after_seconds,
            retention_days=self.config.max_session_age_days,
        )

    def ingest_snapshot(self, payload: dict[str, Any]) -> dict[str, Any]:
        count = self.store.apply_snapshot(payload)
        self.broadcaster.publish_invalidate("snapshot")
        return {"status": "accepted", "session_count": count}

    def ingest_events(self, payload: dict[str, Any]) -> dict[str, Any]:
        events = payload.get("events")
        if isinstance(events, list):
            normalized = [event for event in events if isinstance(event, dict)]
        elif isinstance(payload, dict):
            normalized = [payload]
        else:
            raise ValueError("invalid event payload")
        applied = self.store.apply_event_batch(normalized)
        self.broadcaster.publish_invalidate("events")
        return {"status": "accepted", "applied": applied}

    def set_archive_state(self, session_id: str, archived: bool) -> dict[str, Any]:
        workspace = self.store.set_archive_state(session_id, archived)
        self.broadcaster.publish_invalidate("archive")
        return workspace

    def set_archive_state_many(self, session_ids: list[str], archived: bool) -> list[dict[str, Any]]:
        workspaces = self.store.set_archive_state_many(session_ids, archived)
        self.broadcaster.publish_invalidate("archive")
        return workspaces

    def acknowledge_completion(self, session_id: str, event_id: str | None = None) -> dict[str, Any]:
        workspace = self.store.acknowledge_completion(session_id, event_id)
        self.broadcaster.publish_invalidate("acknowledge")
        return workspace

    def start_background_workers(self) -> None:
        if self.config.collector_enabled:
            self._collector_thread = threading.Thread(
                target=self._collector_loop,
                name="switchboard2-collector",
                daemon=True,
            )
            self._collector_thread.start()
        if self.config.backend_url:
            self._sender_thread = threading.Thread(
                target=self._sender_loop,
                name="switchboard2-sender",
                daemon=True,
            )
            self._sender_thread.start()

    def _collector_loop(self) -> None:
        while not self._stop_event.is_set():
            try:
                changed = self.collect_once()
                if changed and self.local_primary:
                    self.broadcaster.publish_invalidate("collector")
            except Exception:
                traceback.print_exc()
            self._stop_event.wait(self.config.collector_interval_seconds)

    def collect_once(self) -> bool:
        projections = self._load_local_projections()
        generated_at = iso_now()
        changed = False
        for projection in projections:
            projection_hash = stable_json_hash(projection)
            previous_hash = self.store.projection_hash(str(projection["session_id"]))
            if projection_hash == previous_hash:
                continue
            self.store.set_projection_hash(str(projection["session_id"]), projection_hash)
            event = {
                "event_id": self._projection_event_id(projection),
                "type": "session_upsert",
                "machine": self.identity.machine,
                "machine_dns": self.identity.dns_name,
                "generated_at": generated_at,
                "created_at": generated_at,
                "session": projection,
            }
            if self.local_primary:
                self.store.apply_event_batch([event])
            else:
                self.store.enqueue_event(event)
            changed = True

        last_heartbeat = self.store.get_runtime_state("last_heartbeat_sent_at")
        heartbeat_due = not last_heartbeat
        if last_heartbeat:
            parsed = parse_iso_timestamp(last_heartbeat)
            heartbeat_due = parsed is None or (dt.datetime.now(dt.timezone.utc) - parsed).total_seconds() >= self.config.heartbeat_seconds
        if heartbeat_due:
            heartbeat_event = {
                "event_id": f"{self.identity.machine}:heartbeat:{int(time.time())}",
                "type": "machine_heartbeat",
                "machine": self.identity.machine,
                "machine_dns": self.identity.dns_name,
                "generated_at": generated_at,
                "created_at": generated_at,
                "session_count": len(projections),
            }
            if self.local_primary:
                self.store.apply_event_batch([heartbeat_event])
            else:
                self.store.enqueue_event(heartbeat_event)
            self.store.set_runtime_state("last_heartbeat_sent_at", generated_at)
            changed = True
        hook_events = self._load_new_hook_events(generated_at)
        for event in hook_events:
            if self.local_primary:
                self.store.apply_event_batch([event])
            else:
                self.store.enqueue_event(event)
            changed = True
        return changed

    def _projection_event_id(self, projection: dict[str, Any]) -> str:
        event_anchor = (
            str(projection.get("latest_event_id") or "")
            or str(projection.get("latest_event_created_at") or "")
            or str(projection.get("updated_at") or "")
        )
        if not event_anchor:
            event_anchor = stable_json_hash(projection)[:12]
        return f"{self.identity.machine}:{projection['session_id']}:{event_anchor}"

    def _sender_loop(self) -> None:
        while not self._stop_event.is_set():
            batch = self.store.next_outbound_batch(limit=100)
            if not batch:
                self._stop_event.wait(0.5)
                continue
            ids = [int(row["id"]) for row in batch]
            events = [json.loads(str(row["payload_json"])) for row in batch]
            try:
                self._post_event_batch(events)
            except Exception as exc:
                self.store.backoff_outbound(ids, str(exc))
                self._stop_event.wait(0.5)
                continue
            self.store.mark_outbound_sent(ids)

    def _post_event_batch(self, events: list[dict[str, Any]]) -> None:
        endpoint = self.config.backend_url + "/api/events/batch"
        body = json.dumps({"events": events}, ensure_ascii=True).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.config.backend_auth_token:
            headers["X-Switchboard2-Token"] = self.config.backend_auth_token
        req = request.Request(endpoint, data=body, headers=headers, method="POST")
        with request.urlopen(req, timeout=self.config.backend_timeout_seconds) as response:
            if response.status not in (HTTPStatus.OK, HTTPStatus.ACCEPTED):
                raise RuntimeError(f"unexpected backend status: {response.status}")
            response.read()

    def _load_local_projections(self) -> list[dict[str, Any]]:
        index = load_thread_index(self.config.session_index)
        projections: list[dict[str, Any]] = []
        cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=self.config.max_session_age_days)
        if not self.config.sessions_root.exists():
            return projections
        for path in sorted(self.config.sessions_root.rglob("rollout-*.jsonl")):
            try:
                stat = path.stat()
            except FileNotFoundError:
                continue
            summary = self.store.get_cached_summary(path, stat)
            if summary is None:
                try:
                    summary = parse_rollout(path, index)
                except Exception:
                    continue
                self.store.save_cached_summary(path, stat, summary)
            if not summary.session_id or not summary.cwd:
                continue
            updated = parse_iso_timestamp(summary.updated_at) or parse_iso_timestamp(summary.last_event_at)
            if updated is not None and updated < cutoff:
                continue
            projections.append(summarize_session(self.identity, summary))
        projections.sort(key=lambda item: str(item["session_id"]))
        projections.sort(key=session_sort_stamp, reverse=True)
        return projections

    def _load_new_hook_events(self, generated_at: str) -> list[dict[str, Any]]:
        path = self.config.hooks_events_path
        if not path.exists():
            return []

        try:
            stat = path.stat()
        except FileNotFoundError:
            return []

        cursor_key = "hooks_events_cursor_offset"
        inode_key = "hooks_events_cursor_inode"
        tail_key = "hooks_events_cursor_tail"

        inode = f"{stat.st_dev}:{stat.st_ino}"
        saved_inode = self.store.get_runtime_state(inode_key)
        saved_offset_text = self.store.get_runtime_state(cursor_key)
        saved_tail = self.store.get_runtime_state(tail_key).encode("utf-8")

        try:
            offset = max(0, int(saved_offset_text or "0"))
        except ValueError:
            offset = 0
        if saved_inode != inode or stat.st_size < offset:
            offset = 0
            saved_tail = b""

        try:
            with path.open("rb") as handle:
                handle.seek(offset)
                chunk = handle.read()
        except FileNotFoundError:
            return []

        if not chunk and saved_inode == inode and not saved_tail:
            return []

        data = saved_tail + chunk
        tail_boundary = len(saved_tail)
        cursor = 0
        last_consumed = 0
        events: list[dict[str, Any]] = []

        while True:
            newline = data.find(b"\n", cursor)
            if newline < 0:
                break
            line_bytes = data[cursor:newline]
            next_cursor = newline + 1
            cursor = next_cursor
            if not line_bytes.strip():
                last_consumed = next_cursor
                continue
            try:
                payload = json.loads(line_bytes.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                break
            event = self._normalize_hook_event(payload, generated_at)
            if event is not None:
                events.append(event)
            last_consumed = next_cursor

        committed_offset = offset + max(0, last_consumed - tail_boundary)
        remaining_tail = data[last_consumed:].decode("utf-8", errors="ignore")
        self.store.set_runtime_state(inode_key, inode)
        self.store.set_runtime_state(cursor_key, str(committed_offset))
        self.store.set_runtime_state(tail_key, remaining_tail)
        return events

    def _normalize_hook_event(self, payload: dict[str, Any], generated_at: str) -> dict[str, Any] | None:
        session_id = str(payload.get("session_id") or "").strip()
        if not session_id:
            return None
        status = normalize_hook_status(str(payload.get("status") or ""))
        if not status:
            return None

        machine = str(payload.get("machine") or self.identity.machine).strip()
        machine_dns = str(payload.get("machine_dns") or "").strip()
        if not machine_dns and machine == self.identity.machine:
            machine_dns = self.identity.dns_name

        cwd = str(payload.get("cwd") or "").strip()
        workspace = str(payload.get("workspace") or "").strip()
        title = str(payload.get("title") or workspace or folder_name_from_path(cwd) or session_id).strip()
        branch = str(payload.get("branch") or workspace or folder_name_from_path(cwd) or "workspace").strip()
        message = normalize_whitespace(str(payload.get("message") or ""))
        created_at = str(payload.get("created_at") or generated_at).strip() or generated_at
        event_id = str(payload.get("event_id") or f"{machine}:{session_id}:{created_at}:{status}").strip()

        return {
            "event_id": event_id,
            "type": "hook_hint",
            "machine": machine,
            "machine_dns": machine_dns,
            "session_id": session_id,
            "cwd": cwd,
            "workspace": workspace,
            "title": title,
            "branch": branch,
            "status": status,
            "message": message,
            "generated_at": generated_at,
            "created_at": created_at,
        }


class Switchboard2Handler(BaseHTTPRequestHandler):
    server_version = "Switchboard2HTTP/1.0"

    @property
    def app(self) -> Switchboard2App:
        return self.server.app  # type: ignore[attr-defined]

    def setup(self) -> None:
        super().setup()
        self.connection.settimeout(SOCKET_TIMEOUT_SECONDS)

    def log_message(self, format: str, *args: Any) -> None:
        return

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if self._maybe_set_auth_cookie(parsed):
            return
        if parsed.path == self.app.config.base_path:
            return self._redirect_to_prefixed_root()
        normalized = normalize_request_path(parsed.path, self.app.config.base_path)
        if normalized == "/api/state":
            if not self._authorize_api_request():
                return
            return self._send_json(self.app.build_state())
        if normalized == "/api/healthz":
            return self._send_json({"status": "ok", "generated_at": iso_now()})
        if normalized == "/api/ui-version":
            return self._send_json({"version": current_ui_version()})
        if normalized == "/api/stream":
            if not self._authorize_api_request():
                return
            return self._handle_stream()
        return self._handle_static(normalized)

    def do_HEAD(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == self.app.config.base_path:
            return self._redirect_to_prefixed_root()
        normalized = normalize_request_path(parsed.path, self.app.config.base_path)
        if normalized in {"/api/state", "/api/stream"} and not self._authorize_api_request():
            return
        if normalized in {"/api/state", "/api/healthz", "/api/ui-version", "/api/stream"}:
            return self._send_headers(HTTPStatus.OK, "application/json; charset=utf-8", 0)
        requested = "index.html" if normalized in ("", "/") else normalized.lstrip("/")
        candidate = (STATIC_DIR / requested).resolve()
        if not is_safe_static_path(candidate, STATIC_DIR.resolve()) or not candidate.exists():
            self.send_error(HTTPStatus.NOT_FOUND, "Not Found")
            return
        body = candidate.read_bytes()
        self._send_headers(HTTPStatus.OK, guess_content_type(candidate.suffix), len(body))

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        normalized = normalize_request_path(parsed.path, self.app.config.base_path)
        if normalized == "/api/events":
            if not self._authorize_api_request():
                return
            payload = self._read_json_body_or_respond()
            if payload is None:
                return
            try:
                result = self.app.ingest_events(payload)
            except ValueError as exc:
                return self._send_json({"status": "error", "error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return self._send_json(result, status=HTTPStatus.ACCEPTED)
        if normalized == "/api/events/batch":
            if not self._authorize_api_request():
                return
            payload = self._read_json_body_or_respond()
            if payload is None:
                return
            try:
                result = self.app.ingest_events(payload)
            except ValueError as exc:
                return self._send_json({"status": "error", "error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return self._send_json(result, status=HTTPStatus.ACCEPTED)
        if normalized == "/api/agent-snapshot":
            if not self._authorize_api_request():
                return
            payload = self._read_json_body_or_respond()
            if payload is None:
                return
            try:
                result = self.app.ingest_snapshot(payload)
            except ValueError as exc:
                return self._send_json({"status": "error", "error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return self._send_json(result, status=HTTPStatus.ACCEPTED)
        if normalized == "/api/workspaces/archive":
            if not self._authorize_api_request():
                return
            payload = self._read_json_body_or_respond()
            if payload is None:
                return
            session_id = str(payload.get("session_id") or "").strip()
            archived = payload.get("archived")
            if not session_id or not isinstance(archived, bool):
                return self._send_json(
                    {"status": "error", "error": "expected session_id:string and archived:boolean"},
                    status=HTTPStatus.BAD_REQUEST,
                )
            try:
                workspace = self.app.set_archive_state(session_id, archived)
            except KeyError:
                return self._send_json(
                    {"status": "error", "error": f"unknown session_id: {session_id}"},
                    status=HTTPStatus.NOT_FOUND,
                )
            return self._send_json({"status": "ok", "workspace": workspace})
        if normalized == "/api/workspaces/archive-batch":
            if not self._authorize_api_request():
                return
            payload = self._read_json_body_or_respond()
            if payload is None:
                return
            session_ids = payload.get("session_ids")
            archived = payload.get("archived")
            if not isinstance(session_ids, list) or not isinstance(archived, bool):
                return self._send_json(
                    {"status": "error", "error": "expected session_ids:string[] and archived:boolean"},
                    status=HTTPStatus.BAD_REQUEST,
                )
            try:
                workspaces = self.app.set_archive_state_many(session_ids, archived)
            except KeyError as exc:
                missing = exc.args[0] if exc.args else "unknown"
                return self._send_json(
                    {"status": "error", "error": f"unknown session_id: {missing}"},
                    status=HTTPStatus.NOT_FOUND,
                )
            return self._send_json({"status": "ok", "workspaces": workspaces})
        if normalized == "/api/workspaces/acknowledge":
            if not self._authorize_api_request():
                return
            payload = self._read_json_body_or_respond()
            if payload is None:
                return
            session_id = str(payload.get("session_id") or "").strip()
            event_id = str(payload.get("event_id") or "").strip()
            if not session_id:
                return self._send_json(
                    {"status": "error", "error": "expected session_id:string"},
                    status=HTTPStatus.BAD_REQUEST,
                )
            try:
                workspace = self.app.acknowledge_completion(session_id, event_id or None)
            except KeyError:
                return self._send_json(
                    {"status": "error", "error": f"unknown session_id: {session_id}"},
                    status=HTTPStatus.NOT_FOUND,
                )
            return self._send_json({"status": "ok", "workspace": workspace})
        self.send_error(HTTPStatus.NOT_FOUND, "Not Found")

    def _authorize_api_request(self) -> bool:
        if self._is_authorized():
            return True
        self._send_json({"status": "error", "error": "unauthorized"}, status=HTTPStatus.UNAUTHORIZED)
        return False

    def _handle_stream(self) -> None:
        subscriber = self.app.broadcaster.subscribe()
        if subscriber is None:
            self._send_json(
                {"status": "error", "error": "too many stream subscribers"},
                status=HTTPStatus.SERVICE_UNAVAILABLE,
            )
            return
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Connection", "keep-alive")
        self.end_headers()
        try:
            self.wfile.write(b"retry: 1000\n\n")
            self.wfile.flush()
            while True:
                try:
                    chunk = subscriber.get(timeout=max(1, SOCKET_TIMEOUT_SECONDS - 5))
                except queue.Empty:
                    chunk = ": keepalive\n\n"
                self.wfile.write(chunk.encode("utf-8"))
                self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError, TimeoutError):
            return
        finally:
            self.app.broadcaster.unsubscribe(subscriber)

    def _handle_static(self, path: str) -> None:
        requested = "index.html" if path in ("", "/") else path.lstrip("/")
        candidate = (STATIC_DIR / requested).resolve()
        if not is_safe_static_path(candidate, STATIC_DIR.resolve()) or not candidate.exists():
            self.send_error(HTTPStatus.NOT_FOUND, "Not Found")
            return
        body = candidate.read_bytes()
        self._send_headers(HTTPStatus.OK, guess_content_type(candidate.suffix), len(body))
        self.wfile.write(body)

    def _redirect_to_prefixed_root(self) -> None:
        self.send_response(HTTPStatus.MOVED_PERMANENTLY)
        self.send_header("Location", f"{self.app.config.base_path}/")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def _read_json_body(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length") or 0)
        if length < 0:
            raise ValueError("invalid content length")
        if length > MAX_JSON_BODY_BYTES:
            raise ValueError("request body too large")
        raw = self.rfile.read(length) if length else b"{}"
        try:
            payload = json.loads(raw.decode("utf-8") or "{}")
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise ValueError(str(exc)) from exc
        if not isinstance(payload, dict):
            raise ValueError("expected JSON object")
        return payload

    def _read_json_body_or_respond(self) -> dict[str, Any] | None:
        try:
            return self._read_json_body()
        except ValueError as exc:
            self._send_json({"status": "error", "error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return None

    def _is_authorized(self) -> bool:
        token = self.app.config.backend_auth_token
        if token:
            return self._presented_token() == token
        return is_loopback_host(self.client_address[0])

    def _presented_token(self) -> str:
        header_token = str(self.headers.get("X-Switchboard2-Token", "")).strip()
        if header_token:
            return header_token
        cookie_header = self.headers.get("Cookie", "")
        if cookie_header:
            cookie = SimpleCookie()
            cookie.load(cookie_header)
            morsel = cookie.get(AUTH_COOKIE_NAME)
            if morsel is not None:
                return morsel.value.strip()
        return ""

    def _maybe_set_auth_cookie(self, parsed: Any) -> bool:
        token = self.app.config.backend_auth_token
        if not token:
            return False
        query = parse.parse_qs(parsed.query or "", keep_blank_values=False)
        presented = "".join(query.get("token", [])).strip()
        if not presented:
            return False
        if presented != token:
            self._send_json({"status": "error", "error": "unauthorized"}, status=HTTPStatus.UNAUTHORIZED)
            return True
        clean_query = parse.urlencode(
            [(key, value) for key, values in query.items() if key != "token" for value in values],
            doseq=True,
        )
        location = parsed.path
        if clean_query:
            location += "?" + clean_query
        self.send_response(HTTPStatus.FOUND)
        self.send_header("Location", location)
        self.send_header("Set-Cookie", build_auth_cookie(token, self.app.config.base_path))
        self.send_header("Content-Length", "0")
        self.end_headers()
        return True

    def _send_json(self, payload: dict[str, Any], status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload, ensure_ascii=True).encode("utf-8")
        self._send_headers(
            status,
            "application/json; charset=utf-8",
            len(body),
            cache_control="no-store",
        )
        self.wfile.write(body)

    def _send_headers(
        self,
        status: HTTPStatus,
        content_type: str,
        content_length: int,
        *,
        cache_control: str | None = None,
    ) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        if cache_control:
            self.send_header("Cache-Control", cache_control)
        self.send_header("Content-Length", str(content_length))
        self.end_headers()


def normalize_request_path(path: str, base_path: str) -> str:
    if path == base_path:
        return "/"
    if path.startswith(base_path + "/"):
        return path[len(base_path):] or "/"
    return path


def is_safe_static_path(candidate: Path, root: Path) -> bool:
    try:
        candidate.relative_to(root)
        return True
    except ValueError:
        return False


def is_loopback_host(host: str) -> bool:
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return host in {"localhost", "::1"}


def build_auth_cookie(token: str, base_path: str) -> str:
    cookie = SimpleCookie()
    cookie[AUTH_COOKIE_NAME] = token
    cookie[AUTH_COOKIE_NAME]["path"] = base_path or "/"
    cookie[AUTH_COOKIE_NAME]["httponly"] = True
    cookie[AUTH_COOKIE_NAME]["samesite"] = "Strict"
    return cookie.output(header="", sep="").strip()


def validate_server_auth_config(config: AppConfig) -> None:
    if config.server_enabled and not is_loopback_host(config.host) and not config.backend_auth_token:
        raise ValueError("backend.auth_token is required when server.host is not loopback")


def path_is_configured(path: Path) -> bool:
    return str(path).strip() not in {"", "."}


def guess_content_type(suffix: str) -> str:
    return {
        ".html": "text/html; charset=utf-8",
        ".css": "text/css; charset=utf-8",
        ".js": "text/javascript; charset=utf-8",
        ".json": "application/json; charset=utf-8",
        ".webmanifest": "application/manifest+json; charset=utf-8",
        ".png": "image/png",
        ".svg": "image/svg+xml",
    }.get(suffix, "application/octet-stream")


def current_ui_version() -> str:
    latest = 0
    for relative_path in UI_VERSION_FILES:
        candidate = STATIC_DIR / relative_path
        try:
            stat = candidate.stat()
        except FileNotFoundError:
            continue
        latest = max(latest, int(stat.st_mtime_ns))
    return str(latest)


def serve_forever(app: Switchboard2App) -> None:
    validate_server_auth_config(app.config)
    server = ThreadingHTTPServer((app.config.host, app.config.port), Switchboard2Handler)
    scheme = "http"
    if path_is_configured(app.config.tls_cert_file) and path_is_configured(app.config.tls_key_file):
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(
            certfile=str(app.config.tls_cert_file),
            keyfile=str(app.config.tls_key_file),
        )
        server.socket = context.wrap_socket(server.socket, server_side=True)
        scheme = "https"
    server.app = app  # type: ignore[attr-defined]
    app._server = server
    print(
        f"switchboard2: serving on {scheme}://{app.config.host}:{app.config.port}{app.config.base_path}/",
        flush=True,
    )
    server.serve_forever()


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    config = load_config(args.config.expanduser())
    app = Switchboard2App(config)
    try:
        if args.print_projections:
            projections = app._load_local_projections()
            print(json.dumps(projections, indent=2, ensure_ascii=True))
            return 0
        app.start_background_workers()
        if config.server_enabled:
            serve_forever(app)
            return 0
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        return 0
    except error.URLError as exc:
        print(f"switchboard2 error: {exc}", file=sys.stderr, flush=True)
        return 1
    except ValueError as exc:
        print(f"switchboard2 error: {exc}", file=sys.stderr, flush=True)
        return 1
    finally:
        app.close()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
