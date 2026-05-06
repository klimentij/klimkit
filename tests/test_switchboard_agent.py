import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from klimkit.tools.switchboard_agent import switchboard_agent as MODULE


class SwitchboardAgentTests(unittest.TestCase):
    def test_load_config_reads_agent_from_klimkit_toml(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            config_path = root / "klimkit.toml"
            config_path.write_text(
                "\n".join(
                    [
                        "[paths]",
                        f'state_dir = "{root / "state"}"',
                        "",
                        "[switchboard.agent]",
                        "enabled = true",
                        'backend_url = "https://server.example.ts.net/switchboard"',
                        'auth_token = "secret"',
                        "interval_seconds = 7",
                        "heartbeat_seconds = 70",
                        "helper_host = \"127.0.0.1\"",
                        "helper_port = 4633",
                        "",
                    ]
                ),
                encoding="utf-8",
            )

            config = MODULE.load_config(config_path)

        self.assertEqual(config.state_dir, root / "state" / "switchboard-agent")
        self.assertEqual(config.backend_url, "https://server.example.ts.net/switchboard")
        self.assertEqual(config.backend_auth_token, "secret")
        self.assertEqual(config.interval_seconds, 7)
        self.assertEqual(config.helper_host, "127.0.0.1")
        self.assertEqual(config.helper_port, 4633)

    def test_load_config_defaults_first_vm_agent_to_local_switchboard(self):
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
                        "port = 4999",
                        'base_path = "/switchboard"',
                        "",
                        "[switchboard.agent]",
                        "enabled = true",
                        'backend_url = ""',
                        "",
                    ]
                ),
                encoding="utf-8",
            )

            config = MODULE.load_config(config_path)

        self.assertEqual(config.backend_url, "http://127.0.0.1:4999/switchboard")

    def test_detect_machine_identity_infers_dns_when_tailscale_omits_self_dns(self):
        with (
            mock.patch.object(MODULE.socket, "gethostname", return_value="MacBook-Air-8.local"),
            mock.patch.object(
                MODULE,
                "load_tailscale_status_payload",
                return_value={
                    "MagicDNSSuffix": "tail11c448.ts.net",
                    "Self": {
                        "HostName": "MacBook-Air-8.local",
                        "DNSName": "",
                    },
                },
            ),
        ):
            identity = MODULE.detect_machine_identity()

        self.assertEqual(identity.machine, "MacBook-Air-8")
        self.assertEqual(identity.dns_name, "macbook-air-8.tail11c448.ts.net")

    def test_load_config_keeps_standalone_agent_paths_exact(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            config_path = root / "switchboard-agent.toml"
            config_path.write_text(
                "\n".join(
                    [
                        "[paths]",
                        f'state_dir = "{root / "state" / "switchboard-agent"}"',
                        f'sessions_root = "{root / "sessions"}"',
                        f'session_index = "{root / "session_index.jsonl"}"',
                        "",
                        "[backend]",
                        'base_url = "https://server.example.ts.net/switchboard"',
                    ]
                ),
                encoding="utf-8",
            )

            config = MODULE.load_config(config_path)

        self.assertEqual(config.state_dir, root / "state" / "switchboard-agent")
        self.assertEqual(config.sessions_root, root / "sessions")
        self.assertEqual(config.session_index, root / "session_index.jsonl")

    def test_build_snapshot_summarizes_sessions(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            sessions_root = root / "sessions"
            sessions_root.mkdir(parents=True)
            session_index = root / "session_index.jsonl"
            session_index.write_text(
                json.dumps(
                    {
                        "id": "thread-1",
                        "thread_name": "Build Switchboard",
                        "created_at": "2026-04-15T09:45:00Z",
                        "updated_at": "2026-04-15T10:02:00Z",
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            rollout = sessions_root / "rollout-2026-04-15T10-00-00-thread-1.jsonl"
            rollout.write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "timestamp": "2026-04-15T10:00:00Z",
                                "type": "session_meta",
                                "payload": {
                                    "id": "thread-1",
                                    "cwd": "/home/user/klimkit",
                                    "git": {"branch": "main"},
                                },
                            }
                        ),
                        json.dumps(
                            {
                                "timestamp": "2026-04-15T10:00:01Z",
                                "type": "event_msg",
                                "payload": {
                                    "type": "task_complete",
                                    "turn_id": "turn-1",
                                    "last_agent_message": "Which deployment target should I use?",
                                },
                            }
                        ),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            conn = MODULE.init_db(root / "agent-state")
            config = MODULE.AgentConfig(
                sessions_root=sessions_root,
                session_index=session_index,
                state_dir=root / "agent-state",
                backend_url="https://example.com",
                backend_auth_token="",
                timeout_seconds=5,
                interval_seconds=5,
                heartbeat_seconds=60,
                max_session_age_days=3650,
                helper_enabled=True,
                helper_host="127.0.0.1",
                helper_port=4632,
            )
            identity = MODULE.MachineIdentity(machine="workstation", dns_name="workstation.example.ts.net")
            try:
                snapshot = MODULE.build_snapshot(conn, config, identity)
            finally:
                conn.close()

            self.assertEqual(snapshot["machine"], "workstation")
            self.assertEqual(len(snapshot["sessions"]), 1)
            session = snapshot["sessions"][0]
            self.assertEqual(session["title"], "Build Switchboard")
            self.assertEqual(session["branch"], "main")
            self.assertEqual(session["created_at"], "2026-04-15T09:45:00Z")
            self.assertEqual(session["activity_state"], "needs_input")
            self.assertTrue(session["needs_attention"])
            self.assertEqual(session["attention_kind"], "needs_input")
            self.assertEqual(session["latest_event_id"], "turn-1")
            self.assertEqual(
                session["code_server_url"],
                "https://workstation.example.ts.net/?folder=/home/user/klimkit",
            )
            self.assertEqual(
                session["same_origin_helper_url"],
                "https://workstation.example.ts.net/proxy/4632/session.html?folder=%2Fhome%2Fuser%2Fklimkit&session_id=thread-1&title=Build+Switchboard&code_server_url=https%3A%2F%2Fworkstation.example.ts.net%2F%3Ffolder%3D%2Fhome%2Fuser%2Fklimkit",
            )

    def test_parse_rollout_backfills_created_at_from_earliest_event(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            rollout = root / "rollout-2026-04-15T10-00-00-thread-2.jsonl"
            rollout.write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "timestamp": "2026-04-15T09:00:00Z",
                                "type": "session_meta",
                                "payload": {
                                    "id": "thread-2",
                                    "cwd": "/home/user/archive",
                                    "git": {"branch": "feature/ui"},
                                },
                            }
                        ),
                        json.dumps(
                            {
                                "timestamp": "2026-04-15T10:30:00Z",
                                "type": "event_msg",
                                "payload": {
                                    "type": "task_complete",
                                    "turn_id": "turn-9",
                                    "last_agent_message": "Implemented and verified.",
                                },
                            }
                        ),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            summary = MODULE.parse_rollout(rollout, {})
            self.assertEqual(summary.created_at, "2026-04-15T09:00:00Z")
            self.assertEqual(summary.updated_at, "2026-04-15T10:30:00Z")

    def test_parse_rollout_marks_open_request_user_input_as_needs_input(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            rollout = root / "rollout-2026-04-16T22-48-38-thread-3.jsonl"
            rollout.write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "timestamp": "2026-04-16T22:48:38Z",
                                "type": "session_meta",
                                "payload": {
                                    "id": "thread-3",
                                    "cwd": "/home/user/klimkit",
                                    "git": {"branch": "main"},
                                },
                            }
                        ),
                        json.dumps(
                            {
                                "timestamp": "2026-04-16T22:48:39Z",
                                "type": "event_msg",
                                "payload": {"type": "task_started", "turn_id": "turn-3"},
                            }
                        ),
                        json.dumps(
                            {
                                "timestamp": "2026-04-16T22:48:40Z",
                                "type": "response_item",
                                "payload": {
                                    "type": "function_call",
                                    "name": "request_user_input",
                                    "call_id": "call-123",
                                    "arguments": json.dumps(
                                        {
                                            "questions": [
                                                {
                                                    "id": "mode",
                                                    "header": "Mode",
                                                    "question": "Implement this plan?",
                                                    "options": [],
                                                }
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
            payload = MODULE.summarize_session(
                MODULE.MachineIdentity(machine="workstation", dns_name="workstation.example.ts.net"),
                summary,
                4632,
            )

            self.assertEqual(summary.pending_input_request_id, "call-123")
            self.assertEqual(payload["activity_state"], "needs_input")
            self.assertEqual(payload["latest_event_status"], "needs_input")
            self.assertEqual(payload["latest_event_id"], "call-123")
            self.assertEqual(payload["latest_event_message"], "Implement this plan?")
            self.assertTrue(payload["needs_attention"])
            self.assertEqual(payload["attention_kind"], "needs_input")

    def test_completed_session_requests_completion_notification(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            rollout = root / "rollout-2026-04-16T23-00-00-thread-4.jsonl"
            rollout.write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "timestamp": "2026-04-16T23:00:00Z",
                                "type": "session_meta",
                                "payload": {
                                    "id": "thread-4",
                                    "cwd": "/Users/klim",
                                    "git": {"branch": "main"},
                                },
                            }
                        ),
                        json.dumps(
                            {
                                "timestamp": "2026-04-16T23:00:05Z",
                                "type": "event_msg",
                                "payload": {
                                    "type": "task_complete",
                                    "turn_id": "turn-done",
                                    "last_agent_message": "hi43",
                                },
                            }
                        ),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            summary = MODULE.parse_rollout(rollout, {})
            payload = MODULE.summarize_session(
                MODULE.MachineIdentity(machine="MacBook-Air-8", dns_name="macbook-air-8.tail11c448.ts.net"),
                summary,
                4632,
            )

            self.assertEqual(payload["activity_state"], "done")
            self.assertEqual(payload["latest_event_status"], "done")
            self.assertTrue(payload["needs_attention"])
            self.assertEqual(payload["attention_kind"], "completion_unseen")

    def test_subagent_done_does_not_request_completion_notification(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            rollout = root / "rollout-2026-05-06T00-43-27-thread-subagent.jsonl"
            rollout.write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "timestamp": "2026-05-06T00:43:29Z",
                                "type": "session_meta",
                                "payload": {
                                    "id": "thread-subagent",
                                    "cwd": "/home/user/repo",
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
            payload = MODULE.summarize_session(
                MODULE.MachineIdentity(machine="workstation", dns_name="workstation.example.ts.net"),
                summary,
                4632,
            )

            self.assertTrue(summary.is_subagent)
            self.assertEqual(payload["activity_state"], "done")
            self.assertEqual(payload["latest_event_status"], "done")
            self.assertFalse(payload["needs_attention"])
            self.assertEqual(payload["attention_kind"], "")

    def test_completed_summary_with_what_changed_is_done_unseen(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            rollout = root / "rollout-2026-05-06T04-10-00-thread-done-summary.jsonl"
            rollout.write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "timestamp": "2026-05-06T04:00:00Z",
                                "type": "session_meta",
                                "payload": {
                                    "id": "thread-done-summary",
                                    "cwd": "/home/user/klimkit",
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
            payload = MODULE.summarize_session(
                MODULE.MachineIdentity(machine="workstation", dns_name="workstation.example.ts.net"),
                summary,
                4632,
            )

            self.assertEqual(payload["activity_state"], "done")
            self.assertEqual(payload["latest_event_status"], "done")
            self.assertTrue(payload["needs_attention"])
            self.assertEqual(payload["attention_kind"], "completion_unseen")

    def test_should_send_snapshot_respects_hash_and_heartbeat(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            conn = MODULE.init_db(Path(tmpdir))
            try:
                self.assertTrue(MODULE.should_send_snapshot(conn, "hash-1", 60, now=100.0))
                MODULE.set_agent_state(conn, "last_snapshot_hash", "hash-1")
                MODULE.set_agent_state(conn, "last_sent_at", "100.0")
                conn.commit()
                self.assertFalse(MODULE.should_send_snapshot(conn, "hash-1", 60, now=120.0))
                self.assertTrue(MODULE.should_send_snapshot(conn, "hash-1", 60, now=161.0))
                self.assertTrue(MODULE.should_send_snapshot(conn, "hash-2", 60, now=120.0))
            finally:
                conn.close()

    def test_cached_summary_accepts_legacy_payload_without_created_at(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            rollout = root / "rollout-legacy.jsonl"
            rollout.write_text("{}", encoding="utf-8")
            stat = rollout.stat()
            conn = MODULE.init_db(root / "agent-state")
            try:
                legacy_payload = {
                    "_parser_version": MODULE.CACHE_VERSION,
                    "session_id": "thread-legacy",
                    "cwd": "/home/user/klimkit",
                    "branch": "main",
                    "updated_at": "2026-04-15T10:30:00Z",
                    "title": "Legacy cache",
                    "last_event_at": "2026-04-15T10:00:00Z",
                    "last_assistant_message": "",
                    "last_agent_message": "",
                    "last_task_message": "",
                    "last_task_turn_id": "",
                    "last_task_completed_at": "",
                    "pending_input_request_id": "",
                    "pending_input_request_at": "",
                    "pending_input_request_message": "",
                    "in_progress": False,
                    "current_turn_id": "",
                }
                conn.execute(
                    """
                    INSERT INTO rollout_cache(path, size, mtime_ns, summary_json)
                    VALUES(?, ?, ?, ?)
                    """,
                    (str(rollout), stat.st_size, stat.st_mtime_ns, json.dumps(legacy_payload)),
                )
                conn.commit()

                summary = MODULE.cached_summary(conn, rollout, stat)
            finally:
                conn.close()

            self.assertIsNotNone(summary)
            assert summary is not None
            self.assertEqual(summary.created_at, "2026-04-15T10:00:00Z")

    def test_cached_summary_ignores_stale_parser_version(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            rollout = root / "rollout-stale-cache.jsonl"
            rollout.write_text("{}", encoding="utf-8")
            stat = rollout.stat()
            conn = MODULE.init_db(root / "agent-state")
            try:
                stale_payload = {
                    "_parser_version": MODULE.CACHE_VERSION - 1,
                    "session_id": "thread-stale",
                    "cwd": "/home/user/klimkit",
                    "branch": "main",
                    "created_at": "2026-04-15T10:00:00Z",
                    "updated_at": "2026-04-15T10:30:00Z",
                    "title": "Stale cache",
                    "last_event_at": "2026-04-15T10:00:00Z",
                    "last_assistant_message": "",
                    "last_agent_message": "",
                    "last_task_message": "",
                    "last_task_turn_id": "",
                    "last_task_completed_at": "",
                    "pending_input_request_id": "",
                    "pending_input_request_at": "",
                    "pending_input_request_message": "",
                    "is_subagent": False,
                    "in_progress": False,
                    "current_turn_id": "",
                }
                conn.execute(
                    """
                    INSERT INTO rollout_cache(path, size, mtime_ns, summary_json)
                    VALUES(?, ?, ?, ?)
                    """,
                    (str(rollout), stat.st_size, stat.st_mtime_ns, json.dumps(stale_payload)),
                )
                conn.commit()

                summary = MODULE.cached_summary(conn, rollout, stat)
            finally:
                conn.close()

            self.assertIsNone(summary)

    def test_build_snapshot_sorts_by_latest_state_change_not_created_at(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            sessions_root = root / "sessions"
            sessions_root.mkdir(parents=True)
            session_index = root / "session_index.jsonl"
            session_index.write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "id": "thread-newer-created",
                                "thread_name": "Created later",
                                "created_at": "2026-04-15T09:55:00Z",
                                "updated_at": "2026-04-15T10:00:00Z",
                            }
                        ),
                        json.dumps(
                            {
                                "id": "thread-state-changed",
                                "thread_name": "Changed later",
                                "created_at": "2026-04-15T09:40:00Z",
                                "updated_at": "2026-04-15T10:06:00Z",
                            }
                        ),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            first_rollout = sessions_root / "rollout-2026-04-15T10-00-00-thread-newer-created.jsonl"
            first_rollout.write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "timestamp": "2026-04-15T09:55:00Z",
                                "type": "session_meta",
                                "payload": {
                                    "id": "thread-newer-created",
                                    "cwd": "/home/user/a",
                                    "git": {"branch": "main"},
                                },
                            }
                        ),
                        json.dumps(
                            {
                                "timestamp": "2026-04-15T10:00:00Z",
                                "type": "event_msg",
                                "payload": {
                                    "type": "agent_message",
                                    "last_agent_message": "Idle.",
                                },
                            }
                        ),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            second_rollout = sessions_root / "rollout-2026-04-15T10-06-00-thread-state-changed.jsonl"
            second_rollout.write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "timestamp": "2026-04-15T09:40:00Z",
                                "type": "session_meta",
                                "payload": {
                                    "id": "thread-state-changed",
                                    "cwd": "/home/user/b",
                                    "git": {"branch": "main"},
                                },
                            }
                        ),
                        json.dumps(
                            {
                                "timestamp": "2026-04-15T10:06:00Z",
                                "type": "event_msg",
                                "payload": {
                                    "type": "task_started",
                                    "turn_id": "turn-working",
                                },
                            }
                        ),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            conn = MODULE.init_db(root / "agent-state")
            config = MODULE.AgentConfig(
                sessions_root=sessions_root,
                session_index=session_index,
                state_dir=root / "agent-state",
                backend_url="https://example.com",
                backend_auth_token="",
                timeout_seconds=5,
                interval_seconds=5,
                heartbeat_seconds=60,
                max_session_age_days=3650,
                helper_enabled=True,
                helper_host="127.0.0.1",
                helper_port=4632,
            )
            identity = MODULE.MachineIdentity(machine="workstation", dns_name="workstation.example.ts.net")
            try:
                snapshot = MODULE.build_snapshot(conn, config, identity)
            finally:
                conn.close()

            self.assertEqual(
                [session["session_id"] for session in snapshot["sessions"]],
                ["thread-state-changed", "thread-newer-created"],
            )
            self.assertEqual(snapshot["sessions"][0]["activity_state"], "working")


if __name__ == "__main__":
    unittest.main()
