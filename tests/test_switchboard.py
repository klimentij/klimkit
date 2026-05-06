import json
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib import error, request
from unittest import mock

from klimkit.apps.switchboard import daemon as MODULE


def build_config(
    state_dir: Path,
    *,
    base_path: str = "/switchboard",
    port: int = 0,
    trusted_bypass: bool = True,
) -> object:
    return MODULE.AppConfig(
        state_dir=state_dir,
        sessions_root=state_dir / "sessions",
        session_index=state_dir / "session_index.jsonl",
        hooks_events_path=state_dir / "hooks_events.jsonl",
        server_enabled=True,
        host="127.0.0.1",
        port=port,
        base_path=base_path,
        secure_auth_cookie=False,
        tls_cert_file=Path(""),
        tls_key_file=Path(""),
        backend_url="",
        backend_timeout_seconds=5,
        backend_auth_token="",
        collector_enabled=False,
        collector_interval_seconds=0.5,
        heartbeat_seconds=15,
        max_session_age_days=3650,
        stale_after_seconds=180,
        max_loaded_tabs=5,
        machine_id="workstation",
        machine_dns="workstation.example.ts.net",
        trusted_codex_launch_bypass_sandbox=trusted_bypass,
    )


class RunningServer:
    def __init__(self, app: object, server: object, thread: threading.Thread) -> None:
        self.app = app
        self.server = server
        self.thread = thread
        self.base_url = f"http://127.0.0.1:{self.server.server_address[1]}{self.app.config.base_path}"

    def close(self) -> None:
        self.app.close()
        self.thread.join(timeout=2)


class CaptureHandler(BaseHTTPRequestHandler):
    requests: list[dict[str, object]] = []

    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(length).decode("utf-8")
        self.__class__.requests.append(
            {
                "path": self.path,
                "headers": dict(self.headers.items()),
                "body": body,
            }
        )
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", "2")
        self.end_headers()
        self.wfile.write(b"{}")

    def log_message(self, format: str, *args: object) -> None:  # noqa: A003
        return


class RunningCaptureServer:
    def __init__(self, server: ThreadingHTTPServer, thread: threading.Thread) -> None:
        self.server = server
        self.thread = thread
        self.base_url = f"http://127.0.0.1:{self.server.server_address[1]}"

    def close(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)


def start_server(config: object) -> RunningServer:
    app = MODULE.SwitchboardApp(config)
    server = MODULE.ThreadingHTTPServer((config.host, config.port), MODULE.SwitchboardHandler)
    server.app = app
    app._server = server
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return RunningServer(app, server, thread)


def start_capture_server() -> RunningCaptureServer:
    CaptureHandler.requests = []
    server = ThreadingHTTPServer(("127.0.0.1", 0), CaptureHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return RunningCaptureServer(server, thread)


def same_origin_headers(running: RunningServer) -> dict[str, str]:
    return {
        "Content-Type": "application/json",
        "Origin": f"http://127.0.0.1:{running.server.server_address[1]}",
    }


class SwitchboardTests(unittest.TestCase):
    def test_load_config_reads_server_from_klimkit_toml(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            config_path = root / "klimkit.toml"
            config_path.write_text(
                "\n".join(
                    [
                        "[paths]",
                        f'state_dir = "{root / "state"}"',
                        "",
                        "[switchboard.server]",
                        "enabled = true",
                        'host = "127.0.0.1"',
                        "port = 4876",
                        'base_path = "/switchboard"',
                        "secure_auth_cookie = true",
                        'auth_token = "secret"',
                        "collector_interval_seconds = 1.5",
                        "",
                        "[trusted_local_agent_launch]",
                        "bypass_codex_approvals_and_sandbox = false",
                        "",
                    ]
                ),
                encoding="utf-8",
            )

            config = MODULE.load_config(config_path)

        self.assertEqual(config.state_dir, root / "state" / "switchboard")
        self.assertEqual(config.hooks_events_path, root / "state" / "switchboard" / "events.jsonl")
        self.assertEqual(config.port, 4876)
        self.assertTrue(config.secure_auth_cookie)
        self.assertEqual(config.backend_auth_token, "secret")
        self.assertEqual(config.collector_interval_seconds, 1.5)
        self.assertFalse(config.trusted_codex_launch_bypass_sandbox)

    def test_load_config_keeps_standalone_switchboard_paths_exact(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            config_path = root / "switchboard.toml"
            config_path.write_text(
                "\n".join(
                    [
                        "[paths]",
                        f'state_dir = "{root / "state" / "switchboard"}"',
                        f'hooks_events = "{root / "events.jsonl"}"',
                        "",
                        "[server]",
                        "enabled = true",
                        'host = "127.0.0.1"',
                        "port = 4877",
                    ]
                ),
                encoding="utf-8",
            )

            config = MODULE.load_config(config_path)

        self.assertEqual(config.state_dir, root / "state" / "switchboard")
        self.assertEqual(config.hooks_events_path, root / "events.jsonl")

    def test_non_loopback_server_requires_auth_token(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config = build_config(Path(tmpdir))
            config = MODULE.AppConfig(**{**config.__dict__, "host": "0.0.0.0", "backend_auth_token": ""})

            with self.assertRaises(ValueError):
                MODULE.validate_server_auth_config(config)

            secured = MODULE.AppConfig(**{**config.__dict__, "backend_auth_token": "secret"})

            MODULE.validate_server_auth_config(secured)

    def test_secure_auth_cookie_flag_is_configurable(self) -> None:
        plain = MODULE.build_auth_cookie("token", "/switchboard")
        secure = MODULE.build_auth_cookie("token", "/switchboard", secure=True)

        self.assertNotIn("Secure", plain)
        self.assertIn("Secure", secure)

    def test_app_state_includes_self_machine_before_collector_heartbeat(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            app = MODULE.SwitchboardApp(build_config(Path(tmpdir)))
            try:
                state = app.build_state()
            finally:
                app.close()

        self.assertEqual(len(state["machines"]), 1)
        self.assertEqual(state["machines"][0]["machine"], "workstation")
        self.assertEqual(state["machines"][0]["machine_dns"], "workstation.example.ts.net")
        self.assertEqual(state["machines"][0]["session_count"], 0)
        self.assertTrue(state["machines"][0]["online"])
        self.assertEqual(state["max_loaded_tabs"], 5)

    def test_app_state_includes_configured_loaded_tab_limit(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config = MODULE.AppConfig(**{**build_config(Path(tmpdir)).__dict__, "max_loaded_tabs": 7})
            app = MODULE.SwitchboardApp(config)
            try:
                state = app.build_state()
            finally:
                app.close()

        self.assertEqual(state["max_loaded_tabs"], 7)

    def test_parse_rollout_marks_planning_before_action(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            rollout = root / "rollout-1.jsonl"
            rollout.write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "timestamp": "2026-04-17T09:00:00Z",
                                "type": "session_meta",
                                "payload": {
                                    "id": "thread-plan",
                                    "cwd": "/repo",
                                    "git": {"branch": "main"},
                                },
                            }
                        ),
                        json.dumps(
                            {
                                "timestamp": "2026-04-17T09:00:01Z",
                                "type": "event_msg",
                                "payload": {"type": "task_started", "turn_id": "turn-1"},
                            }
                        ),
                        json.dumps(
                            {
                                "timestamp": "2026-04-17T09:00:02Z",
                                "type": "response_item",
                                "payload": {
                                    "type": "message",
                                    "role": "assistant",
                                    "phase": "commentary",
                                    "content": [{"type": "output_text", "text": "I’m checking the architecture first."}],
                                },
                            }
                        ),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            summary = MODULE.parse_rollout(rollout, {})
            projection = MODULE.summarize_session(
                MODULE.MachineIdentity(machine="workstation", dns_name="workstation.example.ts.net"),
                summary,
            )

            self.assertEqual(projection["activity_state"], "planning")
            self.assertEqual(projection["latest_event_id"], "turn-1")

    def test_parse_rollout_marks_exec_command_approval_wait(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            rollout = root / "rollout-2.jsonl"
            rollout.write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "timestamp": "2026-04-17T09:10:00Z",
                                "type": "session_meta",
                                "payload": {
                                    "id": "thread-approval",
                                    "cwd": "/repo",
                                    "git": {"branch": "main"},
                                },
                            }
                        ),
                        json.dumps(
                            {
                                "timestamp": "2026-04-17T09:10:01Z",
                                "type": "event_msg",
                                "payload": {"type": "task_started", "turn_id": "turn-2"},
                            }
                        ),
                        json.dumps(
                            {
                                "timestamp": "2026-04-17T09:10:02Z",
                                "type": "response_item",
                                "payload": {
                                    "type": "function_call",
                                    "name": "exec_command",
                                    "call_id": "call-123",
                                    "arguments": json.dumps(
                                        {
                                            "cmd": "git pull",
                                            "sandbox_permissions": "require_escalated",
                                            "justification": "Need network to fetch updates.",
                                        }
                                    ),
                                },
                            }
                        ),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            summary = MODULE.parse_rollout(rollout, {})
            projection = MODULE.summarize_session(
                MODULE.MachineIdentity(machine="workstation", dns_name="workstation.example.ts.net"),
                summary,
            )

            self.assertEqual(projection["activity_state"], "awaiting_approval")
            self.assertEqual(projection["attention_kind"], "awaiting_approval")
            self.assertEqual(projection["latest_event_id"], "call-123")

    def test_request_user_input_beats_done(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            rollout = root / "rollout-3.jsonl"
            rollout.write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "timestamp": "2026-04-17T09:20:00Z",
                                "type": "session_meta",
                                "payload": {
                                    "id": "thread-input",
                                    "cwd": "/repo",
                                    "git": {"branch": "main"},
                                },
                            }
                        ),
                        json.dumps(
                            {
                                "timestamp": "2026-04-17T09:20:01Z",
                                "type": "event_msg",
                                "payload": {"type": "task_started", "turn_id": "turn-3"},
                            }
                        ),
                        json.dumps(
                            {
                                "timestamp": "2026-04-17T09:20:02Z",
                                "type": "response_item",
                                "payload": {
                                    "type": "function_call",
                                    "name": "request_user_input",
                                    "call_id": "call-ask",
                                    "arguments": json.dumps(
                                        {
                                            "questions": [
                                                {"question": "Which target should I use?"}
                                            ]
                                        }
                                    ),
                                },
                            }
                        ),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            summary = MODULE.parse_rollout(rollout, {})
            projection = MODULE.summarize_session(
                MODULE.MachineIdentity(machine="workstation", dns_name="workstation.example.ts.net"),
                summary,
            )

            self.assertEqual(projection["activity_state"], "needs_input")
            self.assertEqual(projection["attention_kind"], "needs_input")
            self.assertEqual(projection["latest_event_message"], "Which target should I use?")

    def test_subagent_done_does_not_request_completion_notification(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            rollout = root / "rollout-subagent.jsonl"
            rollout.write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "timestamp": "2026-05-06T00:43:29Z",
                                "type": "session_meta",
                                "payload": {
                                    "id": "thread-subagent",
                                    "cwd": "/repo",
                                    "source": {
                                        "subagent": {
                                            "thread_spawn": {
                                                "parent_thread_id": "thread-main",
                                                "depth": 1,
                                                "agent_role": "final_reviewer",
                                            }
                                        }
                                    },
                                },
                            }
                        ),
                        json.dumps(
                            {
                                "timestamp": "2026-05-06T00:45:15Z",
                                "type": "event_msg",
                                "payload": {
                                    "type": "task_complete",
                                    "turn_id": "turn-subagent",
                                    "last_agent_message": "PASS",
                                },
                            }
                        ),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            summary = MODULE.parse_rollout(rollout, {})
            projection = MODULE.summarize_session(
                MODULE.MachineIdentity(machine="workstation", dns_name="workstation.example.ts.net"),
                summary,
            )

            self.assertTrue(summary.is_subagent)
            self.assertEqual(projection["activity_state"], "done")
            self.assertEqual(projection["latest_event_status"], "done")
            self.assertFalse(projection["needs_attention"])
            self.assertEqual(projection["attention_kind"], "")

    def test_completed_summary_with_what_changed_is_done_unseen(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            rollout = root / "rollout-done-summary.jsonl"
            rollout.write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "timestamp": "2026-05-06T04:00:00Z",
                                "type": "session_meta",
                                "payload": {
                                    "id": "thread-done-summary",
                                    "cwd": "/repo",
                                    "git": {"branch": "main"},
                                },
                            }
                        ),
                        json.dumps(
                            {
                                "timestamp": "2026-05-06T04:10:00Z",
                                "type": "event_msg",
                                "payload": {
                                    "type": "task_complete",
                                    "turn_id": "turn-done",
                                    "last_agent_message": (
                                        "What changed:\n"
                                        "- Updated Switchboard.\n\n"
                                        "How Klim can check this:\n"
                                        "1. Run kk pull."
                                    ),
                                },
                            }
                        ),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            summary = MODULE.parse_rollout(rollout, {})
            projection = MODULE.summarize_session(
                MODULE.MachineIdentity(machine="workstation", dns_name="workstation.example.ts.net"),
                summary,
            )

            self.assertEqual(projection["activity_state"], "done")
            self.assertEqual(projection["latest_event_status"], "done")
            self.assertIn("What changed:", projection["latest_event_notification_message"])
            self.assertTrue(projection["needs_attention"])
            self.assertEqual(projection["attention_kind"], "completion_unseen")

    def test_parse_rollout_uses_folder_name_when_thread_title_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            rollout = root / "rollout-untitled.jsonl"
            rollout.write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "timestamp": "2026-04-17T09:30:00Z",
                                "type": "session_meta",
                                "payload": {
                                    "id": "thread-untitled",
                                    "cwd": "/repo/switchboard",
                                    "git": {"branch": "main"},
                                },
                            }
                        ),
                        json.dumps(
                            {
                                "timestamp": "2026-04-17T09:30:01Z",
                                "type": "response_item",
                                "payload": {
                                    "type": "message",
                                    "role": "assistant",
                                    "phase": "commentary",
                                    "content": [{"type": "output_text", "text": "This should not become the thread title."}],
                                },
                            }
                        ),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            summary = MODULE.parse_rollout(rollout, {})
            projection = MODULE.summarize_session(
                MODULE.MachineIdentity(machine="workstation", dns_name="workstation.example.ts.net"),
                summary,
            )

            self.assertEqual(summary.title, "switchboard")
            self.assertEqual(projection["title"], "switchboard")

    def test_parse_rollout_tracks_latest_user_message(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            rollout = root / "rollout-user-message.jsonl"
            rollout.write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "timestamp": "2026-04-17T09:31:00Z",
                                "type": "session_meta",
                                "payload": {
                                    "id": "thread-user-msg",
                                    "cwd": "/repo/switchboard",
                                    "git": {"branch": "main"},
                                },
                            }
                        ),
                        json.dumps(
                            {
                                "timestamp": "2026-04-17T09:31:01Z",
                                "type": "event_msg",
                                "payload": {
                                    "type": "user_message",
                                    "message": "Show folder, machine, status, and my last message in the tabs.",
                                },
                            }
                        ),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            summary = MODULE.parse_rollout(rollout, {})
            projection = MODULE.summarize_session(
                MODULE.MachineIdentity(machine="workstation", dns_name="workstation.example.ts.net"),
                summary,
            )

            self.assertEqual(summary.latest_user_message, "Show folder, machine, status, and my last message in the tabs.")
            self.assertEqual(projection["latest_user_message"], "Show folder, machine, status, and my last message in the tabs.")

    def test_store_acknowledge_completion_changes_display_state_to_seen(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            store = MODULE.StateStore(Path(tmpdir))
            try:
                store.apply_event_batch(
                    [
                        {
                            "event_id": "workstation:heartbeat:1",
                            "type": "machine_heartbeat",
                            "machine": "workstation",
                            "machine_dns": "workstation.example.ts.net",
                            "generated_at": "2026-04-17T10:00:00Z",
                            "session_count": 1,
                        },
                        {
                            "event_id": "workstation:thread-1:turn-1",
                            "type": "session_upsert",
                            "machine": "workstation",
                            "machine_dns": "workstation.example.ts.net",
                            "generated_at": "2026-04-17T10:00:00Z",
                            "session": {
                                "session_id": "thread-1",
                                "cwd": "/repo",
                                "folder_name": "repo",
                                "branch": "main",
                                "title": "Test completion",
                                "detail": "Implemented and verified.",
                                "activity_state": "done",
                                "created_at": "2026-04-17T09:00:00Z",
                                "updated_at": "2026-04-17T10:00:00Z",
                                "latest_event_id": "turn-1",
                                "latest_event_status": "done",
                                "latest_event_message": "Implemented and verified.",
                                "latest_event_created_at": "2026-04-17T10:00:00Z",
                                "needs_attention": True,
                                "attention_kind": "completion_unseen",
                                "approval_policy": "never",
                                "code_server_url": "https://workstation.example.ts.net/?folder=/repo",
                                "same_origin_helper_url": "",
                            },
                        },
                    ]
                )

                state = store.build_state("workstation", stale_after_seconds=180, retention_days=3650)
                self.assertEqual(state["workspaces"][0]["display_state"], "done")
                self.assertTrue(state["workspaces"][0]["needs_attention"])

                store.acknowledge_completion("thread-1", "turn-1")

                state = store.build_state("workstation", stale_after_seconds=180, retention_days=3650)
                self.assertEqual(state["workspaces"][0]["display_state"], "seen")
                self.assertFalse(state["workspaces"][0]["needs_attention"])
            finally:
                store.close()

    def test_build_state_marks_active_session_stale_when_reporting_stops(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            store = MODULE.StateStore(Path(tmpdir))
            try:
                store.apply_event_batch(
                    [
                        {
                            "event_id": "workstation:heartbeat:stale",
                            "type": "machine_heartbeat",
                            "machine": "workstation",
                            "machine_dns": "workstation.example.ts.net",
                            "generated_at": "2026-04-17T09:00:00Z",
                            "session_count": 1,
                        },
                        {
                            "event_id": "workstation:thread-stale:turn-2",
                            "type": "session_upsert",
                            "machine": "workstation",
                            "machine_dns": "workstation.example.ts.net",
                            "generated_at": "2026-04-17T09:00:00Z",
                            "session": {
                                "session_id": "thread-stale",
                                "cwd": "/repo",
                                "folder_name": "repo",
                                "branch": "main",
                                "title": "Still running",
                                "detail": "Working.",
                                "activity_state": "working",
                                "created_at": "2026-04-17T08:30:00Z",
                                "updated_at": "2026-04-17T09:00:00Z",
                                "latest_event_id": "turn-2",
                                "latest_event_status": "",
                                "latest_event_message": "",
                                "latest_event_created_at": "2026-04-17T09:00:00Z",
                                "needs_attention": False,
                                "attention_kind": "",
                                "approval_policy": "never",
                                "code_server_url": "https://workstation.example.ts.net/?folder=/repo",
                                "same_origin_helper_url": "",
                            },
                        },
                    ]
                )

                original_parse = MODULE.parse_iso_timestamp
                try:
                    def fake_parse(value):
                        parsed = original_parse(value)
                        if parsed is None:
                            return None
                        return parsed - MODULE.dt.timedelta(minutes=10)

                    MODULE.parse_iso_timestamp = fake_parse
                    state = store.build_state("workstation", stale_after_seconds=180, retention_days=3650)
                finally:
                    MODULE.parse_iso_timestamp = original_parse

                self.assertEqual(state["workspaces"][0]["display_state"], "stale")
            finally:
                store.close()

    def test_build_state_keeps_creation_order_and_archives_last(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            store = MODULE.StateStore(Path(tmpdir))
            try:
                now = MODULE.dt.datetime.now(MODULE.dt.UTC).replace(microsecond=0)
                latest_update = now.strftime("%Y-%m-%dT%H:%M:%SZ")
                mid_update = (now - MODULE.dt.timedelta(minutes=2)).strftime("%Y-%m-%dT%H:%M:%SZ")
                earlier_update = (now - MODULE.dt.timedelta(minutes=4)).strftime("%Y-%m-%dT%H:%M:%SZ")
                newest_created = (now - MODULE.dt.timedelta(minutes=10)).strftime("%Y-%m-%dT%H:%M:%SZ")
                middle_created = (now - MODULE.dt.timedelta(minutes=20)).strftime("%Y-%m-%dT%H:%M:%SZ")
                oldest_created = (now - MODULE.dt.timedelta(minutes=30)).strftime("%Y-%m-%dT%H:%M:%SZ")
                store.apply_event_batch(
                    [
                        {
                            "event_id": "workstation:heartbeat:sort",
                            "type": "machine_heartbeat",
                            "machine": "workstation",
                            "machine_dns": "workstation.example.ts.net",
                            "generated_at": latest_update,
                            "session_count": 3,
                        },
                        {
                            "event_id": "workstation:thread-newest:turn-3",
                            "type": "session_upsert",
                            "machine": "workstation",
                            "machine_dns": "workstation.example.ts.net",
                            "generated_at": earlier_update,
                            "session": {
                                "session_id": "thread-newest",
                                "cwd": "/repo/newest",
                                "folder_name": "newest",
                                "branch": "main",
                                "title": "Newest created",
                                "detail": "Created last, but archived.",
                                "activity_state": "done",
                                "created_at": newest_created,
                                "updated_at": earlier_update,
                                "latest_event_id": "turn-3",
                                "latest_event_status": "done",
                                "latest_event_message": "",
                                "latest_event_created_at": earlier_update,
                                "needs_attention": True,
                                "attention_kind": "completion_unseen",
                                "approval_policy": "never",
                                "code_server_url": "https://workstation.example.ts.net/?folder=/repo/newest",
                                "same_origin_helper_url": "",
                            },
                        },
                        {
                            "event_id": "workstation:thread-middle:turn-2",
                            "type": "session_upsert",
                            "machine": "workstation",
                            "machine_dns": "workstation.example.ts.net",
                            "generated_at": mid_update,
                            "session": {
                                "session_id": "thread-middle",
                                "cwd": "/repo/middle",
                                "folder_name": "middle",
                                "branch": "main",
                                "title": "Middle created",
                                "detail": "Created second and updated midstream.",
                                "activity_state": "working",
                                "created_at": middle_created,
                                "updated_at": mid_update,
                                "latest_event_id": "turn-2",
                                "latest_event_status": "",
                                "latest_event_message": "",
                                "latest_event_created_at": mid_update,
                                "needs_attention": False,
                                "attention_kind": "",
                                "approval_policy": "never",
                                "code_server_url": "https://workstation.example.ts.net/?folder=/repo/middle",
                                "same_origin_helper_url": "",
                            },
                        },
                        {
                            "event_id": "workstation:thread-oldest:turn-1",
                            "type": "session_upsert",
                            "machine": "workstation",
                            "machine_dns": "workstation.example.ts.net",
                            "generated_at": latest_update,
                            "session": {
                                "session_id": "thread-oldest",
                                "cwd": "/repo/oldest",
                                "folder_name": "oldest",
                                "branch": "main",
                                "title": "Oldest created",
                                "detail": "Got the newest status update.",
                                "activity_state": "needs_input",
                                "created_at": oldest_created,
                                "updated_at": latest_update,
                                "latest_event_id": "turn-1",
                                "latest_event_status": "needs_input",
                                "latest_event_message": "",
                                "latest_event_created_at": latest_update,
                                "needs_attention": True,
                                "attention_kind": "needs_input",
                                "approval_policy": "never",
                                "code_server_url": "https://workstation.example.ts.net/?folder=/repo/oldest",
                                "same_origin_helper_url": "",
                            },
                        },
                    ]
                )
                store.set_archive_state("thread-newest", True)

                state = store.build_state("workstation", stale_after_seconds=180, retention_days=3650)

                self.assertEqual(
                    [item["title"] for item in state["workspaces"][:3]],
                    ["Middle created", "Oldest created", "Newest created"],
                )
                self.assertFalse(state["workspaces"][0]["archived"])
                self.assertFalse(state["workspaces"][1]["archived"])
                self.assertTrue(state["workspaces"][2]["archived"])
            finally:
                store.close()

    def test_upsert_derives_code_server_url_from_machine_dns_and_cwd(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            store = MODULE.StateStore(Path(tmpdir))
            try:
                store.apply_event_batch(
                    [
                        {
                            "event_id": "workstation:thread-safe:url",
                            "type": "session_upsert",
                            "machine": "workstation",
                            "machine_dns": "workstation.example.ts.net",
                            "generated_at": "2026-04-17T10:00:00Z",
                            "session": {
                                "session_id": "thread-safe",
                                "cwd": "/repo",
                                "folder_name": "repo",
                                "branch": "main",
                                "title": "Safe URL",
                                "detail": "Working.",
                                "activity_state": "working",
                                "created_at": "2026-04-17T09:00:00Z",
                                "updated_at": "2026-04-17T10:00:00Z",
                                "latest_event_id": "turn-safe",
                                "latest_event_status": "",
                                "latest_event_message": "",
                                "latest_event_created_at": "2026-04-17T10:00:00Z",
                                "needs_attention": False,
                                "attention_kind": "",
                                "approval_policy": "never",
                                "code_server_url": "https://evil.invalid/phish",
                                "same_origin_helper_url": "",
                            },
                        },
                    ]
                )

                state = store.build_state("workstation", stale_after_seconds=180, retention_days=3650)
                self.assertEqual(
                    state["workspaces"][0]["code_server_url"],
                    "https://workstation.example.ts.net/?folder=/repo",
                )
            finally:
                store.close()

    def test_upsert_resolves_missing_machine_dns_from_tailscale_peer(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            store = MODULE.StateStore(Path(tmpdir))
            try:
                with mock.patch.object(
                    MODULE,
                    "load_tailscale_status_payload",
                    return_value={
                        "MagicDNSSuffix": "tail11c448.ts.net",
                        "Peer": {
                            "peer-1": {
                                "HostName": "MacBook Air (23)",
                                "DNSName": "macbook-air-23.tail11c448.ts.net.",
                            }
                        },
                    },
                ):
                    store.apply_snapshot(
                        {
                            "machine": "MacBook-Air-8.local",
                            "machine_dns": "",
                            "generated_at": "2026-04-17T10:00:00Z",
                            "sessions": [
                                {
                                    "session_id": "thread-mac",
                                    "cwd": "/Users/klim/coding-ops",
                                    "folder_name": "coding-ops",
                                    "branch": "main",
                                    "title": "Mac session",
                                    "detail": "Working.",
                                    "activity_state": "working",
                                    "created_at": "2026-04-17T09:00:00Z",
                                    "updated_at": "2026-04-17T10:00:00Z",
                                    "latest_event_id": "turn-mac",
                                    "latest_event_status": "working",
                                    "latest_event_message": "",
                                    "latest_event_created_at": "2026-04-17T10:00:00Z",
                                    "needs_attention": False,
                                    "attention_kind": "",
                                    "approval_policy": "never",
                                }
                            ],
                        }
                    )

                state = store.build_state("workstation", stale_after_seconds=180, retention_days=3650)
                self.assertEqual(state["machines"][0]["machine_dns"], "macbook-air-23.tail11c448.ts.net")
                self.assertEqual(
                    state["workspaces"][0]["code_server_url"],
                    "https://macbook-air-23.tail11c448.ts.net/?folder=/Users/klim/coding-ops",
                )
            finally:
                store.close()

    def test_archive_endpoint_returns_400_for_malformed_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            running = start_server(build_config(Path(tmpdir)))
            try:
                req = request.Request(
                    running.base_url + "/api/workspaces/archive",
                    data=b"{",
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with self.assertRaises(error.HTTPError) as raised:
                    request.urlopen(req, timeout=5)
                self.assertEqual(raised.exception.code, 400)
                payload = json.loads(raised.exception.read().decode("utf-8"))
                self.assertEqual(payload["status"], "error")
                self.assertIn("error", payload)
            finally:
                running.close()

    def test_local_workspace_bootstrap_writes_codex_task_and_settings(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            running = start_server(build_config(Path(tmpdir)))
            try:
                workspace = Path(tmpdir) / "created" / "repo"
                req = request.Request(
                    running.base_url + "/api/local-workspaces/bootstrap",
                    data=json.dumps(
                        {
                            "cwd": str(workspace),
                            "codex_command": "touch /tmp/klimkit-bootstrap-injected",
                        }
                    ).encode("utf-8"),
                    headers=same_origin_headers(running),
                    method="POST",
                )
                with request.urlopen(req, timeout=5) as response:
                    payload = json.loads(response.read().decode("utf-8"))

                self.assertEqual(payload["status"], "ok")
                tasks = json.loads((workspace / ".vscode" / "tasks.json").read_text(encoding="utf-8"))
                settings = json.loads((workspace / ".vscode" / "settings.json").read_text(encoding="utf-8"))
                klimkit_tasks = [
                    task for task in tasks["tasks"] if task.get("label") == MODULE.LOCAL_CODEX_TASK_LABEL
                ]
                self.assertEqual(len(klimkit_tasks), 1)
                self.assertEqual(klimkit_tasks[0]["runOptions"]["runOn"], "folderOpen")
                self.assertIn("check_for_update_on_startup=false", klimkit_tasks[0]["command"])
                self.assertIn("--dangerously-bypass-approvals-and-sandbox", klimkit_tasks[0]["command"])
                self.assertIn(str(workspace), klimkit_tasks[0]["command"])
                self.assertNotIn("klimkit-bootstrap-injected", klimkit_tasks[0]["command"])
                self.assertEqual(settings["task.allowAutomaticTasks"], "on")
                self.assertEqual(settings["workbench.startupEditor"], "none")
                self.assertFalse(settings["security.workspace.trust.enabled"])
            finally:
                running.close()

    def test_local_workspace_bootstrap_respects_disabled_trusted_bypass(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            running = start_server(build_config(Path(tmpdir), trusted_bypass=False))
            try:
                workspace = Path(tmpdir) / "safe" / "repo"
                req = request.Request(
                    running.base_url + "/api/local-workspaces/bootstrap",
                    data=json.dumps({"cwd": str(workspace)}).encode("utf-8"),
                    headers=same_origin_headers(running),
                    method="POST",
                )
                with request.urlopen(req, timeout=5):
                    pass

                tasks = json.loads((workspace / ".vscode" / "tasks.json").read_text(encoding="utf-8"))
                klimkit_tasks = [
                    task for task in tasks["tasks"] if task.get("label") == MODULE.LOCAL_CODEX_TASK_LABEL
                ]
                self.assertEqual(len(klimkit_tasks), 1)
                self.assertIn("check_for_update_on_startup=false", klimkit_tasks[0]["command"])
                self.assertNotIn("--dangerously-bypass-approvals-and-sandbox", klimkit_tasks[0]["command"])
            finally:
                running.close()

    def test_tokenless_loopback_rejects_untrusted_host_header(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            running = start_server(build_config(Path(tmpdir)))
            try:
                req = request.Request(
                    running.base_url + "/api/state",
                    headers={"Host": "attacker.example"},
                    method="GET",
                )
                with self.assertRaises(error.HTTPError) as raised:
                    request.urlopen(req, timeout=5)
                self.assertEqual(raised.exception.code, 401)
            finally:
                running.close()

    def test_tokenless_loopback_allows_self_tailscale_host_header(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            running = start_server(build_config(Path(tmpdir)))
            try:
                req = request.Request(
                    running.base_url + "/api/state",
                    headers={"Host": "workstation.example.ts.net"},
                    method="GET",
                )
                with request.urlopen(req, timeout=5) as response:
                    payload = json.loads(response.read().decode("utf-8"))
                self.assertEqual(payload["machines"][0]["machine"], "workstation")
            finally:
                running.close()

    def test_state_exposes_effective_codex_launch_flags(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            running = start_server(build_config(Path(tmpdir), trusted_bypass=False))
            try:
                with request.urlopen(running.base_url + "/api/state", timeout=5) as response:
                    payload = json.loads(response.read().decode("utf-8"))
                self.assertIn("check_for_update_on_startup=false", payload["codex_launch_flags"])
                self.assertNotIn("--dangerously-bypass-approvals-and-sandbox", payload["codex_launch_flags"])
            finally:
                running.close()

    def test_local_workspace_bootstrap_rejects_relative_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            running = start_server(build_config(Path(tmpdir)))
            try:
                req = request.Request(
                    running.base_url + "/api/local-workspaces/bootstrap",
                    data=json.dumps({"cwd": "relative/path"}).encode("utf-8"),
                    headers=same_origin_headers(running),
                    method="POST",
                )
                with self.assertRaises(error.HTTPError) as raised:
                    request.urlopen(req, timeout=5)
                self.assertEqual(raised.exception.code, 400)
                payload = json.loads(raised.exception.read().decode("utf-8"))
                self.assertEqual(payload["status"], "error")
                self.assertIn("absolute path", payload["error"])
            finally:
                running.close()

    def test_local_workspace_bootstrap_requires_same_origin_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            running = start_server(build_config(Path(tmpdir)))
            try:
                workspace = Path(tmpdir) / "cross-site" / "repo"
                cross_site = request.Request(
                    running.base_url + "/api/local-workspaces/bootstrap",
                    data=json.dumps({"cwd": str(workspace)}).encode("utf-8"),
                    headers={"Content-Type": "application/json", "Origin": "https://example.invalid"},
                    method="POST",
                )
                with self.assertRaises(error.HTTPError) as cross_site_error:
                    request.urlopen(cross_site, timeout=5)
                self.assertEqual(cross_site_error.exception.code, 403)
                self.assertFalse((workspace / ".vscode" / "tasks.json").exists())

                text_plain = request.Request(
                    running.base_url + "/api/local-workspaces/bootstrap",
                    data=json.dumps({"cwd": str(workspace)}).encode("utf-8"),
                    headers={"Content-Type": "text/plain", "Origin": same_origin_headers(running)["Origin"]},
                    method="POST",
                )
                with self.assertRaises(error.HTTPError) as text_plain_error:
                    request.urlopen(text_plain, timeout=5)
                self.assertEqual(text_plain_error.exception.code, 415)
                self.assertFalse((workspace / ".vscode" / "tasks.json").exists())
            finally:
                running.close()

    def test_events_batch_endpoint_ingests_forwarded_satellite_events(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            running = start_server(build_config(Path(tmpdir)))
            try:
                payload = {
                    "events": [
                        {
                            "event_id": "satellite:heartbeat:1",
                            "type": "machine_heartbeat",
                            "machine": "satellite",
                            "machine_dns": "satellite.example.ts.net",
                            "generated_at": "2026-04-18T10:00:00Z",
                            "created_at": "2026-04-18T10:00:00Z",
                            "session_count": 1,
                        },
                        {
                            "event_id": "satellite:thread-1:turn-1",
                            "type": "session_upsert",
                            "machine": "satellite",
                            "machine_dns": "satellite.example.ts.net",
                            "generated_at": "2026-04-18T10:00:00Z",
                            "created_at": "2026-04-18T10:00:00Z",
                            "session": {
                                "session_id": "thread-1",
                                "cwd": "/work/repo",
                                "folder_name": "repo",
                                "branch": "main",
                                "title": "Forwarded session",
                                "detail": "Forwarded from another VM.",
                                "activity_state": "working",
                                "created_at": "2026-04-18T09:55:00Z",
                                "updated_at": "2026-04-18T10:00:00Z",
                                "latest_event_id": "turn-1",
                                "latest_event_status": "working",
                                "latest_event_message": "Still running",
                                "latest_event_created_at": "2026-04-18T10:00:00Z",
                                "latest_user_message": "check this repo",
                                "needs_attention": False,
                                "attention_kind": "",
                                "approval_policy": "never",
                                "code_server_url": "https://satellite.example.ts.net/?folder=/work/repo",
                                "same_origin_helper_url": "",
                            },
                        },
                    ]
                }
                req = request.Request(
                    running.base_url + "/api/events/batch",
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with request.urlopen(req, timeout=5) as response:
                    accepted = json.loads(response.read().decode("utf-8"))
                self.assertEqual(accepted["status"], "accepted")
                self.assertEqual(accepted["applied"], 2)

                with request.urlopen(running.base_url + "/api/state", timeout=5) as response:
                    state = json.loads(response.read().decode("utf-8"))
                self.assertEqual(state["machines"][0]["machine"], "satellite")
                self.assertEqual(state["workspaces"][0]["machine"], "satellite")
                self.assertEqual(state["workspaces"][0]["folder_name"], "repo")
                self.assertEqual(state["workspaces"][0]["latest_user_message"], "check this repo")
            finally:
                running.close()

    def test_collect_once_surfaces_needs_input_from_hook_stream(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config = build_config(Path(tmpdir))
            now = MODULE.dt.datetime.now(MODULE.dt.UTC).replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")
            config.hooks_events_path.parent.mkdir(parents=True, exist_ok=True)
            config.hooks_events_path.write_text(
                json.dumps(
                    {
                        "event_id": "pws:thread-hook:turn-1",
                        "session_id": "thread-hook",
                        "machine": "pws",
                        "cwd": "/home/user/pantera",
                        "workspace": "pantera",
                        "status": "needs_input",
                        "title": "pantera",
                        "branch": "main",
                        "message": "Which deploy target should I use?",
                        "created_at": now,
                        "source": "codex_stop_hook",
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            app = MODULE.SwitchboardApp(config)
            try:
                changed = app.collect_once()
                self.assertTrue(changed)

                state = app.build_state()
                self.assertEqual(len(state["workspaces"]), 1)
                workspace = state["workspaces"][0]
                self.assertEqual(workspace["machine"], "pws")
                self.assertEqual(workspace["display_state"], "needs_input")
                self.assertEqual(workspace["attention_kind"], "needs_input")
                self.assertEqual(workspace["latest_event_message"], "Which deploy target should I use?")
            finally:
                app.close()

    def test_collect_once_enqueues_hook_events_for_satellite_mode(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = build_config(Path(tmpdir))
            now = MODULE.dt.datetime.now(MODULE.dt.UTC).replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")
            config = MODULE.AppConfig(
                **{
                    **base.__dict__,
                    "server_enabled": False,
                    "backend_url": "http://127.0.0.1:9999/switchboard",
                }
            )
            config.hooks_events_path.parent.mkdir(parents=True, exist_ok=True)
            config.hooks_events_path.write_text(
                json.dumps(
                    {
                        "event_id": "pws:thread-hook:turn-2",
                        "session_id": "thread-hook",
                        "machine": "pws",
                        "cwd": "/home/user/pantera",
                        "workspace": "pantera",
                        "status": "needs_input",
                        "title": "pantera",
                        "branch": "main",
                        "message": "Pick a deployment target.",
                        "created_at": now,
                        "source": "codex_stop_hook",
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            app = MODULE.SwitchboardApp(config)
            try:
                changed = app.collect_once()
                self.assertTrue(changed)

                queued = app.store.next_outbound_batch(limit=10)
                payloads = [json.loads(str(row["payload_json"])) for row in queued]
                hook_events = [payload for payload in payloads if payload.get("type") == "hook_hint"]
                self.assertEqual(len(hook_events), 1)
                self.assertEqual(hook_events[0]["status"], "needs_input")
                self.assertEqual(hook_events[0]["machine"], "pws")
            finally:
                app.close()

    def test_newer_hook_hint_overrides_older_projection(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            store = MODULE.StateStore(Path(tmpdir))
            try:
                base = MODULE.dt.datetime.now(MODULE.dt.UTC).replace(microsecond=0)
                created = (base - MODULE.dt.timedelta(minutes=7)).strftime("%Y-%m-%dT%H:%M:%SZ")
                working_at = (base - MODULE.dt.timedelta(minutes=2)).strftime("%Y-%m-%dT%H:%M:%SZ")
                hook_at = (base - MODULE.dt.timedelta(minutes=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
                store.apply_event_batch(
                    [
                        {
                            "event_id": "pws:thread-hook:turn-working",
                            "type": "session_upsert",
                            "machine": "pws",
                            "machine_dns": "pws.example.ts.net",
                            "generated_at": working_at,
                            "session": {
                                "session_id": "thread-hook",
                                "cwd": "/home/user/pantera",
                                "folder_name": "pantera",
                                "branch": "main",
                                "title": "pantera",
                                "detail": "Still working.",
                                "activity_state": "working",
                                "created_at": created,
                                "updated_at": working_at,
                                "latest_event_id": "turn-working",
                                "latest_event_status": "working",
                                "latest_event_message": "Still working.",
                                "latest_event_created_at": working_at,
                                "needs_attention": False,
                                "attention_kind": "",
                                "approval_policy": "never",
                                "code_server_url": "https://pws.example.ts.net/?folder=/home/user/pantera",
                                "same_origin_helper_url": "",
                            },
                        },
                        {
                            "event_id": "pws:thread-hook:turn-needs-input",
                            "type": "hook_hint",
                            "machine": "pws",
                            "machine_dns": "pws.example.ts.net",
                            "session_id": "thread-hook",
                            "cwd": "/home/user/pantera",
                            "workspace": "pantera",
                            "title": "pantera",
                            "branch": "main",
                            "status": "needs_input",
                            "message": "Choose the deploy target.",
                            "created_at": hook_at,
                            "generated_at": hook_at,
                        },
                    ]
                )

                state = store.build_state("workstation", stale_after_seconds=180, retention_days=3650)
                workspace = state["workspaces"][0]
                self.assertEqual(workspace["display_state"], "needs_input")
                self.assertEqual(workspace["attention_kind"], "needs_input")
                self.assertEqual(workspace["latest_event_message"], "Choose the deploy target.")
            finally:
                store.close()

    def test_older_hook_hint_does_not_override_newer_projection(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            store = MODULE.StateStore(Path(tmpdir))
            try:
                base = MODULE.dt.datetime.now(MODULE.dt.UTC).replace(microsecond=0)
                created = (base - MODULE.dt.timedelta(minutes=10)).strftime("%Y-%m-%dT%H:%M:%SZ")
                hook_at = (base - MODULE.dt.timedelta(minutes=5)).strftime("%Y-%m-%dT%H:%M:%SZ")
                working_at = (base - MODULE.dt.timedelta(minutes=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
                store.apply_event_batch(
                    [
                        {
                            "event_id": "pws:thread-hook:turn-working",
                            "type": "session_upsert",
                            "machine": "pws",
                            "machine_dns": "pws.example.ts.net",
                            "generated_at": working_at,
                            "session": {
                                "session_id": "thread-hook",
                                "cwd": "/home/user/pantera",
                                "folder_name": "pantera",
                                "branch": "main",
                                "title": "pantera",
                                "detail": "Still working.",
                                "activity_state": "working",
                                "created_at": created,
                                "updated_at": working_at,
                                "latest_event_id": "turn-working",
                                "latest_event_status": "working",
                                "latest_event_message": "Still working.",
                                "latest_event_created_at": working_at,
                                "needs_attention": False,
                                "attention_kind": "",
                                "approval_policy": "never",
                                "code_server_url": "https://pws.example.ts.net/?folder=/home/user/pantera",
                                "same_origin_helper_url": "",
                            },
                        },
                        {
                            "event_id": "pws:thread-hook:turn-needs-input-old",
                            "type": "hook_hint",
                            "machine": "pws",
                            "machine_dns": "pws.example.ts.net",
                            "session_id": "thread-hook",
                            "cwd": "/home/user/pantera",
                            "workspace": "pantera",
                            "title": "pantera",
                            "branch": "main",
                            "status": "needs_input",
                            "message": "Choose the deploy target.",
                            "created_at": hook_at,
                            "generated_at": hook_at,
                        },
                    ]
                )

                state = store.build_state("workstation", stale_after_seconds=180, retention_days=3650)
                workspace = state["workspaces"][0]
                self.assertEqual(workspace["display_state"], "working")
                self.assertEqual(workspace["attention_kind"], "")
                self.assertEqual(workspace["latest_event_message"], "Still working.")
            finally:
                store.close()

    def test_sender_posts_to_backend_batch_endpoint_with_token(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            capture = start_capture_server()
            try:
                config = build_config(Path(tmpdir))
                config = MODULE.AppConfig(
                    **{
                        **config.__dict__,
                        "server_enabled": False,
                        "backend_url": capture.base_url + "/switchboard",
                        "backend_auth_token": "secret-token",
                    }
                )
                app = MODULE.SwitchboardApp(config)
                try:
                    app._post_event_batch(
                        [
                            {
                                "event_id": "satellite:heartbeat:1",
                                "type": "machine_heartbeat",
                                "machine": "satellite",
                                "machine_dns": "satellite.example.ts.net",
                                "generated_at": "2026-04-18T10:00:00Z",
                                "created_at": "2026-04-18T10:00:00Z",
                                "session_count": 1,
                            }
                        ]
                    )
                finally:
                    app.close()

                self.assertEqual(len(CaptureHandler.requests), 1)
                captured = CaptureHandler.requests[0]
                self.assertEqual(captured["path"], "/switchboard/api/events/batch")
                self.assertEqual(captured["headers"]["X-Switchboard-Token"], "secret-token")
                body = json.loads(str(captured["body"]))
                self.assertEqual(body["events"][0]["machine"], "satellite")
            finally:
                capture.close()

    def test_token_protects_state_and_mutations(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config = build_config(Path(tmpdir))
            config = MODULE.AppConfig(**{**config.__dict__, "backend_auth_token": "secret-token"})
            running = start_server(config)
            try:
                with self.assertRaises(error.HTTPError) as raised:
                    request.urlopen(running.base_url + "/api/state", timeout=5)
                self.assertEqual(raised.exception.code, 401)

                authorized = request.Request(
                    running.base_url + "/api/state",
                    headers={"X-Switchboard-Token": "secret-token"},
                    method="GET",
                )
                with request.urlopen(authorized, timeout=5) as response:
                    payload = json.loads(response.read().decode("utf-8"))
                self.assertIn("workspaces", payload)

                unauthorized_post = request.Request(
                    running.base_url + "/api/workspaces/archive",
                    data=json.dumps({"session_id": "missing", "archived": True}).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with self.assertRaises(error.HTTPError) as post_raised:
                    request.urlopen(unauthorized_post, timeout=5)
                self.assertEqual(post_raised.exception.code, 401)
            finally:
                running.close()

    def test_custom_base_path_serves_relative_manifest_and_scope_safe_worker(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            running = start_server(build_config(Path(tmpdir), base_path="/board"))
            try:
                with request.urlopen(running.base_url + "/manifest.webmanifest", timeout=5) as response:
                    manifest = json.loads(response.read().decode("utf-8"))
                self.assertEqual(manifest["start_url"], "./")
                self.assertEqual(manifest["scope"], "./")
                self.assertTrue(all(not icon["src"].startswith("/switchboard/") for icon in manifest["icons"]))

                with request.urlopen(running.base_url + "/service-worker.js", timeout=5) as response:
                    worker = response.read().decode("utf-8")
                self.assertNotIn('"/switchboard/', worker)
                self.assertIn("pathWithinScope", worker)
            finally:
                running.close()

    def test_ui_version_endpoint_reports_static_revision(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            running = start_server(build_config(Path(tmpdir)))
            try:
                with request.urlopen(running.base_url + "/api/ui-version", timeout=5) as response:
                    payload = json.loads(response.read().decode("utf-8"))
                self.assertIn("version", payload)
                self.assertRegex(str(payload["version"]), r"^\d+$")
            finally:
                running.close()

    def test_index_uses_create_tab_copy_and_folder_combobox(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            running = start_server(build_config(Path(tmpdir)))
            try:
                with request.urlopen(running.base_url + "/", timeout=5) as response:
                    html = response.read().decode("utf-8")
                self.assertIn("Create Workspace", html)
                self.assertIn(">Create tab<", html)
                self.assertIn('role="combobox"', html)
                self.assertIn('id="new-workspace-folder-options"', html)
                self.assertNotIn("new-workspace-folder-suggestions", html)
            finally:
                running.close()

    def test_app_script_creates_unique_local_workspace_ids_keeps_fresh_tabs_and_syncs_window_title(self) -> None:
        script = (
            Path(__file__).resolve().parents[1]
            / "src"
            / "klimkit"
            / "apps"
            / "switchboard"
            / "static"
            / "app.js"
        ).read_text(encoding="utf-8")
        self.assertIn("createLocalWorkspaceId", script)
        self.assertIn("LOCAL_WORKSPACE_SEQUENCE_KEY", script)
        self.assertNotIn("activate(existing.id", script)
        self.assertIn("Create fresh tab for new folder path", script)
        self.assertIn("buildLocalCodeServerUrl", script)
        self.assertIn("bootstrapLocalWorkspace", script)
        self.assertIn("check_for_update_on_startup=false", script)
        self.assertIn("codexLaunchFlags", script)
        self.assertIn("tmuxSessionName", script)
        self.assertIn("tmux new-session -A -s", script)
        self.assertNotIn("TRUSTED_LOCAL_CODEX_LAUNCH_FLAGS", script)
        self.assertNotIn("--dangerously-bypass-approvals-and-sandbox", script)
        self.assertIn("resolveNotificationTargetWorkspace", script)
        self.assertIn("syncLoadedFrames", script)
        self.assertIn("DEFAULT_MAX_LOADED_FRAMES = 5", script)
        self.assertIn("ui.maxLoadedFrames = sanitizeMaxLoadedFrames(payload.max_loaded_tabs)", script)
        self.assertIn("loadedFrameRecency", script)
        self.assertIn("desired.size >= ui.maxLoadedFrames", script)
        self.assertNotIn("preloadNonArchivedFrames", script)
        self.assertNotIn("!machine || !machine.machine_dns || !folder", script)
        self.assertIn("buildWindowTitle", script)
        self.assertIn("syncDocumentTitle", script)
        self.assertIn("notificationStatusForWorkspace", script)
        self.assertIn("notificationMemoryKeyForWorkspace", script)
        self.assertIn("notificationSignatureForWorkspace", script)
        self.assertIn("materializeManualWorkspaces", script)
        self.assertIn("mergeWorkspaceStatus", script)
        self.assertIn("findServerWorkspaceForLocal", script)
        self.assertIn("machineIdentityKey", script)
        self.assertIn("setLocalArchiveStates", script)
        self.assertIn("tabBarWorkspaces", script)
        self.assertIn("tabBarWorkspaceCount", script)
        self.assertIn("return tabBarWorkspaces(workspaces).filter", script)
        self.assertIn("ui.orderedWorkspaceIds = tabBarWorkspaces(allWorkspaces).map", script)
        self.assertIn('const actionLabel = workspace.archived ? "Unarchive" : "Archive";', script)
        self.assertIn("setArchiveStates(serverSessionIds, archived)", script)
        self.assertIn("const visibleArchivableIds = visible.map((workspace) => workspace.id);", script)
        self.assertIn("workspaceSortStamp(right).localeCompare(workspaceSortStamp(left))", script)
        self.assertIn('event.code === "Digit0" || event.key === "0"', script)
        self.assertIn('toggleDrawer("catalog");', script)
        self.assertIn('tag: signature', script)
        self.assertIn('console.warn("Failed to show Switchboard notification"', script)
        self.assertIn('panel.setAttribute("aria-hidden", String(!active))', script)
        self.assertIn("ensurePanel(workspace);", script)
        self.assertIn("workspace.archived || !workspace.needs_attention", script)
        self.assertIn('const uiVersionUrl = "./api/ui-version";', script)
        self.assertNotIn('document.title = error instanceof Error ? error.message', script)
        self.assertNotIn('panel.toggleAttribute("hidden", !active)', script)
        self.assertNotIn("ui.notificationMemory[workspace.id] = eventId", script)
        self.assertNotIn('workspace.is_local ? "Close"', script)
        self.assertNotIn("closeLocalWorkspace(workspace.id)", script)
        self.assertNotIn("checkbox.disabled = Boolean(workspace.is_local)", script)
        self.assertNotIn('["__archive_separator__"]', script)

    def test_ingest_snapshot_sends_telegram_for_client_attention_once(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = build_config(Path(tmpdir))
            config = MODULE.AppConfig(
                **{
                    **base.__dict__,
                    "telegram_enabled": True,
                    "telegram_bot_token": "token",
                    "telegram_chat_id": "chat",
                }
            )
            app = MODULE.SwitchboardApp(config)
            full_completion_message = (
                "What changed:\n"
                "- Fixed the Switchboard done status classifier.\n"
                "- Updated the Tailscale Serve permission skip report.\n\n"
                "Verification:\n"
                "- The full completion body reached Telegram, including this tail sentinel."
            )
            payload = {
                "machine": "MacBook-Air-8",
                "machine_dns": "macbook-air-8.tail11c448.ts.net",
                "generated_at": "2026-05-04T12:34:50Z",
                "sessions": [
                    {
                        "session_id": "thread-mac",
                        "cwd": "/Users/klim",
                        "folder_name": "klim",
                        "branch": "klim",
                        "title": "hi43",
                        "detail": "hi43",
                        "activity_state": "done",
                        "created_at": "2026-05-04T12:34:43Z",
                        "updated_at": "2026-05-04T12:34:48Z",
                        "latest_event_id": "turn-done",
                        "latest_event_status": "done",
                        "latest_event_message": full_completion_message,
                        "latest_event_created_at": "2026-05-04T12:34:48Z",
                        "needs_attention": True,
                        "attention_kind": "completion_unseen",
                        "approval_policy": "never",
                    }
                ],
            }
            try:
                with mock.patch.object(MODULE, "send_telegram_message", return_value=True) as telegram:
                    app.ingest_snapshot(payload)
                    app.ingest_snapshot(payload)

                telegram.assert_called_once()
                text = telegram.call_args.args[1]
                self.assertEqual(telegram.call_args.kwargs["parse_mode"], "HTML")
                self.assertIn("<b>Codex finished</b>", text)
                self.assertIn("<code>MacBook-Air-8</code>", text)
                self.assertIn("/Users/klim", text)
                self.assertIn(full_completion_message, text)
                self.assertIn("https://workstation.example.ts.net/switchboard/#", text)
            finally:
                app.close()

    def test_long_done_message_flows_from_rollout_to_telegram_notification(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            tail_sentinel = "TAIL_SENTINEL_FULL_DONE_MESSAGE"
            full_completion_message = (
                "What changed:\n"
                "- Fixed the status classifier for completed Switchboard sessions.\n"
                "- Kept the compact UI event summary clipped for tab rendering.\n"
                "- Carried the full done body separately for notification delivery.\n"
                "- Added this deliberately long verification sentence so the sentinel sits past the old two hundred forty character projection clip boundary.\n"
                f"Verification tail: {tail_sentinel}"
            )
            self.assertGreater(len(full_completion_message), 300)
            rollout = root / "rollout-long-done-message.jsonl"
            rollout.write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "timestamp": "2026-05-06T04:00:00Z",
                                "type": "session_meta",
                                "payload": {
                                    "id": "thread-long-done",
                                    "cwd": "/repo",
                                    "git": {"branch": "main"},
                                },
                            }
                        ),
                        json.dumps(
                            {
                                "timestamp": "2026-05-06T04:10:00Z",
                                "type": "event_msg",
                                "payload": {
                                    "type": "task_complete",
                                    "turn_id": "turn-long-done",
                                    "last_agent_message": full_completion_message,
                                },
                            }
                        ),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            summary = MODULE.parse_rollout(rollout, {})
            projection = MODULE.summarize_session(
                MODULE.MachineIdentity(machine="workstation", dns_name="workstation.example.ts.net"),
                summary,
            )
            self.assertEqual(projection["activity_state"], "done")
            self.assertEqual(projection["latest_event_status"], "done")
            self.assertNotIn(tail_sentinel, projection["latest_event_message"])
            self.assertEqual(projection["latest_event_notification_message"], full_completion_message)

            base = build_config(root)
            config = MODULE.AppConfig(
                **{
                    **base.__dict__,
                    "telegram_enabled": True,
                    "telegram_bot_token": "token",
                    "telegram_chat_id": "chat",
                }
            )
            app = MODULE.SwitchboardApp(config)
            try:
                payload = {
                    "machine": "workstation",
                    "machine_dns": "workstation.example.ts.net",
                    "generated_at": "2026-05-06T04:10:01Z",
                    "sessions": [projection],
                }
                with mock.patch.object(MODULE, "send_telegram_message", return_value=True) as telegram:
                    app.ingest_snapshot(payload)

                telegram.assert_called_once()
                text = telegram.call_args.args[1]
                self.assertIn(full_completion_message, text)
                self.assertIn(tail_sentinel, text)
            finally:
                app.close()

    def test_recent_attention_snapshot_sends_after_telegram_is_enabled(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = build_config(Path(tmpdir))
            app = MODULE.SwitchboardApp(base)
            payload = {
                "machine": "MacBook-Air-8",
                "machine_dns": "macbook-air-8.tail11c448.ts.net",
                "generated_at": "2026-05-04T12:34:50Z",
                "sessions": [
                    {
                        "session_id": "thread-mac",
                        "cwd": "/Users/klim",
                        "folder_name": "klim",
                        "activity_state": "done",
                        "latest_event_id": "turn-done",
                        "latest_event_status": "done",
                        "latest_event_message": "hi43",
                        "latest_event_created_at": MODULE.iso_now(),
                        "needs_attention": True,
                        "attention_kind": "completion_unseen",
                    }
                ],
            }
            try:
                app.ingest_snapshot(payload)
                app.config = MODULE.AppConfig(
                    **{
                        **base.__dict__,
                        "telegram_enabled": True,
                        "telegram_bot_token": "token",
                        "telegram_chat_id": "chat",
                    }
                )
                with mock.patch.object(MODULE, "send_telegram_message", return_value=True) as telegram:
                    app.ingest_snapshot(payload)
                    app.ingest_snapshot(payload)

                telegram.assert_called_once()
            finally:
                app.close()


if __name__ == "__main__":
    unittest.main()
