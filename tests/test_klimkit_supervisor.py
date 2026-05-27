import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from urllib.parse import unquote_plus
from unittest import mock

from klimkit import notifications
from klimkit.tools.supervisor import supervisor as MODULE


class StopLoop(Exception):
    pass


class KlimkitSupervisorTests(unittest.TestCase):
    def test_daemon_loop_starts_central_services_before_worker_failures(self) -> None:
        config = MODULE.SupervisorConfig(
            profile="server",
            repo_root=Path("/tmp/klimkit"),
            machine_config_path=Path("/tmp/machine.toml"),
            live_sync_enabled=False,
            live_sync_interval_seconds=60,
            fetch_ref="origin/main",
            switchboard_agent_enabled=True,
            manage_switchboard=True,
        )
        events: list[str] = []

        def fake_ensure_central_processes(*_args: object, **_kwargs: object) -> None:
            events.append("central")

        def fake_run_switchboard_agent_once(*_args: object, **_kwargs: object) -> str:
            events.append("switchboard-agent")
            raise RuntimeError("backend unavailable")

        with (
            redirect_stderr(StringIO()),
            mock.patch.object(MODULE, "load_supervisor_state", return_value={"live_sync": {}}),
            mock.patch.object(MODULE.signal, "signal"),
            mock.patch.object(MODULE.time, "time", return_value=0.0),
            mock.patch.object(MODULE.time, "sleep", side_effect=StopLoop),
            mock.patch.object(MODULE, "ensure_central_processes", side_effect=fake_ensure_central_processes),
            mock.patch.object(MODULE, "run_switchboard_agent_once", side_effect=fake_run_switchboard_agent_once),
        ):
            with self.assertRaises(StopLoop):
                MODULE.daemon_loop(config)

        self.assertEqual(events, ["central", "switchboard-agent"])

    def test_run_switchboard_agent_once_starts_helper_server_when_enabled(self) -> None:
        config = MODULE.SupervisorConfig(
            profile="server",
            repo_root=Path("/tmp/klimkit"),
            machine_config_path=Path("/tmp/machine.toml"),
            live_sync_enabled=False,
            live_sync_interval_seconds=60,
            fetch_ref="origin/main",
            switchboard_agent_enabled=True,
            manage_switchboard=True,
        )
        agent_config = mock.Mock()
        agent_config.state_dir = Path("/tmp/agent-state")
        agent_config.helper_enabled = True

        with (
            mock.patch.object(MODULE, "_SWITCHBOARD_HELPER_SERVER", None),
            mock.patch.object(MODULE, "load_switchboard_config", return_value=agent_config) as load_config_mock,
            mock.patch.object(MODULE, "start_switchboard_helper_server", return_value=object()) as helper_mock,
            mock.patch.object(MODULE, "init_switchboard_db", return_value=mock.Mock()) as db_mock,
            mock.patch.object(MODULE, "run_switchboard_report", return_value=True),
        ):
            conn = db_mock.return_value
            result = MODULE.run_switchboard_agent_once(config)

        helper_mock.assert_called_once_with(agent_config)
        load_config_mock.assert_called_once_with(Path("/tmp/machine.toml"))
        conn.close.assert_called_once()
        self.assertEqual(result, "switchboard-agent: reported snapshot")

    def test_load_machine_config_uses_single_switchboard_server_section(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "machine.toml"
            config_path.write_text(
                "\n".join(
                    [
                        "[paths]",
                        f'repo_root = "{tmpdir}"',
                        "",
                        "[components]",
                        "client = true",
                        "server = true",
                        "",
                        "[switchboard.server]",
                        "enabled = true",
                        "",
                    ]
                ),
                encoding="utf-8",
            )

            config = MODULE.load_machine_config(config_path)

        self.assertTrue(config.manage_switchboard)
        self.assertEqual(config.machine_config_path, config_path)

    def test_load_machine_config_uses_component_server_without_profile(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "machine.toml"
            config_path.write_text(
                "\n".join(
                    [
                        "[components]",
                        "client = true",
                        "server = true",
                        "",
                    ]
                ),
                encoding="utf-8",
            )

            config = MODULE.load_machine_config(config_path)

        self.assertEqual(config.profile, "server")
        self.assertTrue(config.manage_switchboard)
        self.assertFalse(config.live_sync_enabled)
        self.assertEqual(config.live_sync_interval_seconds, 5)
        self.assertEqual(config.fetch_ref, "origin/main")

    def test_load_machine_config_allows_autosync_interval_override(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "machine.toml"
            config_path.write_text(
                "\n".join(
                    [
                        "[workers]",
                        "auto_sync = false",
                        "auto_sync_interval_seconds = 17",
                        'auto_sync_ref = "origin/release"',
                        "",
                    ]
                ),
                encoding="utf-8",
            )

            config = MODULE.load_machine_config(config_path)

        self.assertFalse(config.live_sync_enabled)
        self.assertEqual(config.live_sync_interval_seconds, 17)
        self.assertEqual(config.fetch_ref, "origin/release")

    def test_load_machine_config_uses_single_switchboard_agent_section(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "machine.toml"
            config_path.write_text(
                "\n".join(
                    [
                        "[components]",
                        "client = true",
                        "server = false",
                        "",
                        "[switchboard.agent]",
                        "enabled = true",
                        'backend_url = "https://server.example.ts.net/switchboard"',
                        "",
                    ]
                ),
                encoding="utf-8",
            )

            config = MODULE.load_machine_config(config_path)

        self.assertEqual(config.profile, "client")
        self.assertTrue(config.switchboard_agent_enabled)
        self.assertEqual(config.machine_config_path, config_path)

    def test_ensure_central_processes_uses_local_switchboard_config(self) -> None:
        config = MODULE.SupervisorConfig(
            profile="server",
            repo_root=Path("/tmp/klimkit"),
            machine_config_path=Path("/tmp/machine.toml"),
            live_sync_enabled=False,
            live_sync_interval_seconds=60,
            fetch_ref="origin/main",
            switchboard_agent_enabled=False,
            manage_switchboard=True,
        )

        with mock.patch.object(MODULE, "start_process", return_value=mock.Mock()) as start_mock:
            MODULE.ensure_central_processes(config, {})

        command = start_mock.call_args.kwargs["command"]
        self.assertEqual(command, ["/tmp/klimkit/klimkit", "serve", "--config", "/tmp/machine.toml"])

    def test_live_mappings_match_codex_harness_registry(self) -> None:
        mappings = MODULE.live_mappings()

        self.assertEqual(mappings[0].repo_path, "packs/codex/AGENTS.md")
        self.assertEqual(mappings[0].target_path, Path.home() / ".codex" / "AGENTS.md")
        self.assertFalse(any(mapping.repo_path == "packs/codex/hooks.json" for mapping in mappings))
        skills = next(mapping for mapping in mappings if mapping.repo_path == "packs/codex/skills")
        self.assertEqual(skills.exclude_prefixes, (".system/",))

    def test_auto_sync_once_fast_forwards_applies_and_restarts(self) -> None:
        config = MODULE.SupervisorConfig(
            profile="server",
            repo_root=Path("/tmp/klimkit"),
            machine_config_path=Path("/tmp/machine.toml"),
            live_sync_enabled=True,
            live_sync_interval_seconds=5,
            fetch_ref="origin/main",
            switchboard_agent_enabled=False,
            manage_switchboard=True,
        )
        git_calls: list[tuple[str, ...]] = []

        def fake_git_output(_repo_root: Path, *args: str) -> str:
            git_calls.append(args)
            if args == ("rev-parse", "HEAD"):
                return "oldrevision"
            if args == ("status", "--porcelain"):
                return ""
            if args == ("diff", "--name-only", "oldrevision", "newrevision"):
                return "packs/codex/AGENTS.md\nsrc/klimkit/apps/switchboard/daemon.py\n"
            if args == ("merge", "--ff-only", "newrevision"):
                return ""
            raise AssertionError(args)

        state: dict[str, object] = {}
        stdout = StringIO()
        with (
            redirect_stdout(stdout),
            mock.patch.object(MODULE, "fetch_remote", return_value="newrevision"),
            mock.patch.object(MODULE, "git_output", side_effect=fake_git_output),
            mock.patch.object(MODULE, "is_ancestor", return_value=True) as ancestor_mock,
            mock.patch.object(MODULE, "save_supervisor_state") as save_mock,
            mock.patch.object(MODULE, "run_apply_for_autosync", return_value="apply ok") as apply_mock,
            mock.patch.object(MODULE, "send_telegram_notification", return_value=True) as telegram_mock,
            mock.patch.object(MODULE, "tailscale_dns_name", return_value="vm-1.tailnet.ts.net"),
            mock.patch.object(MODULE, "restart_managed_service", return_value="restarted systemd user service") as restart_mock,
        ):
            summary = MODULE.auto_sync_once(config, state)

        ancestor_mock.assert_called_once_with(Path("/tmp/klimkit"), "oldrevision", "newrevision")
        apply_mock.assert_called_once_with(config)
        telegram_mock.assert_called_once()
        notification_text = telegram_mock.call_args.args[1]
        self.assertIn("oldrevi -> newrevi", notification_text)
        self.assertIn("Switchboard", notification_text)
        restart_mock.assert_called_once_with()
        save_mock.assert_called_once()
        self.assertIn(("merge", "--ff-only", "newrevision"), git_calls)
        self.assertIn("oldrevi..newrevi", summary)
        self.assertIn("2 changed files", summary)
        self.assertEqual(state["auto_sync"]["changed_files"], [
            "packs/codex/AGENTS.md",
            "src/klimkit/apps/switchboard/daemon.py",
        ])

    def test_fetch_remote_updates_remote_tracking_ref(self) -> None:
        completed = mock.Mock()
        completed.returncode = 0
        completed.stdout = ""
        completed.stderr = ""

        with (
            mock.patch.object(MODULE.subprocess, "run", return_value=completed) as run_mock,
            mock.patch.object(MODULE, "git_output", return_value="newrevision") as git_output_mock,
        ):
            revision = MODULE.fetch_remote(Path("/tmp/klimkit"), "origin/main")

        self.assertEqual(revision, "newrevision")
        self.assertEqual(
            run_mock.call_args.args[0],
            ["git", "fetch", "--quiet", "origin", "main:refs/remotes/origin/main"],
        )
        git_output_mock.assert_called_once_with(
            Path("/tmp/klimkit"),
            "rev-parse",
            "refs/remotes/origin/main",
        )

    def test_autosync_telegram_sender_posts_short_summary(self) -> None:
        config = MODULE.SupervisorConfig(
            profile="client",
            repo_root=Path("/tmp/klimkit"),
            machine_config_path=Path("/tmp/machine.toml"),
            live_sync_enabled=True,
            live_sync_interval_seconds=5,
            fetch_ref="origin/main",
            switchboard_agent_enabled=False,
            manage_switchboard=False,
            telegram_enabled=True,
            telegram_bot_token="bot-token",
            telegram_chat_id="chat-id",
            code_server_enabled=True,
            switchboard_backend_url="https://server.example.ts.net/switchboard",
        )
        update = MODULE.CheckoutUpdate(
            previous_revision="abcdef123456",
            new_revision="123456abcdef",
            changed_files=("packs/codex/AGENTS.md", "README.md"),
        )

        with (
            mock.patch.object(MODULE.socket, "gethostname", return_value="vm-1"),
            mock.patch.object(MODULE, "tailscale_dns_name", return_value="vm-1.tailnet.ts.net"),
            mock.patch.object(notifications.request, "urlopen") as urlopen_mock,
        ):
            urlopen_mock.return_value.__enter__.return_value.read.return_value = b'{"ok":true}'
            sent = MODULE.send_telegram_notification(config, MODULE.autosync_notification_text(config, update))

        self.assertTrue(sent)
        req = urlopen_mock.call_args.args[0]
        self.assertIn("botbot-token/sendMessage", req.full_url)
        body = req.data.decode("utf-8")
        self.assertIn("chat_id=chat-id", body)
        self.assertIn("vm-1", body)
        self.assertIn("Codex+pack", body)
        decoded_body = unquote_plus(body)
        self.assertIn("Switchboard: https://server.example.ts.net/switchboard", decoded_body)
        self.assertIn("Code-server direct: https://vm-1.tailnet.ts.net/?folder=/tmp/klimkit", decoded_body)

    def test_restart_managed_service_treats_self_restart_sigterm_as_success(self) -> None:
        with mock.patch.object(
            MODULE.subprocess,
            "run",
            side_effect=MODULE.subprocess.CalledProcessError(-MODULE.signal.SIGTERM, ["systemctl"]),
        ):
            summary = MODULE.restart_managed_service()

        self.assertIn("restarted", summary)

    def test_auto_sync_once_does_not_apply_when_main_is_unchanged(self) -> None:
        config = MODULE.SupervisorConfig(
            profile="server",
            repo_root=Path("/tmp/klimkit"),
            machine_config_path=Path("/tmp/machine.toml"),
            live_sync_enabled=True,
            live_sync_interval_seconds=5,
            fetch_ref="origin/main",
            switchboard_agent_enabled=False,
            manage_switchboard=True,
        )
        state: dict[str, object] = {"auto_sync": {"current_revision": "samerevision"}}

        with (
            mock.patch.object(MODULE, "fetch_remote", return_value="samerevision"),
            mock.patch.object(MODULE, "git_output", return_value="samerevision"),
            mock.patch.object(MODULE, "save_supervisor_state") as save_mock,
            mock.patch.object(MODULE, "run_apply_for_autosync") as apply_mock,
            mock.patch.object(MODULE, "restart_managed_service") as restart_mock,
        ):
            summary = MODULE.auto_sync_once(config, state)

        self.assertEqual(summary, "autosync: main unchanged")
        save_mock.assert_called_once()
        apply_mock.assert_not_called()
        restart_mock.assert_not_called()

    def test_auto_sync_once_applies_local_head_change_after_same_vm_push(self) -> None:
        config = MODULE.SupervisorConfig(
            profile="server",
            repo_root=Path("/tmp/klimkit"),
            machine_config_path=Path("/tmp/machine.toml"),
            live_sync_enabled=True,
            live_sync_interval_seconds=5,
            fetch_ref="origin/main",
            switchboard_agent_enabled=False,
            manage_switchboard=True,
        )

        def fake_git_output(_repo_root: Path, *args: str) -> str:
            if args == ("rev-parse", "HEAD"):
                return "newrevision"
            if args == ("diff", "--name-only", "oldrevision", "newrevision"):
                return "packs/codex/AGENTS.md\n"
            raise AssertionError(args)

        state: dict[str, object] = {"auto_sync": {"current_revision": "oldrevision"}}
        with (
            mock.patch.object(MODULE, "fetch_remote", return_value="newrevision"),
            mock.patch.object(MODULE, "git_output", side_effect=fake_git_output),
            mock.patch.object(MODULE, "save_supervisor_state") as save_mock,
            mock.patch.object(MODULE, "run_apply_for_autosync", return_value="apply ok") as apply_mock,
            mock.patch.object(MODULE, "send_telegram_notification", return_value=True) as telegram_mock,
            mock.patch.object(MODULE, "tailscale_dns_name", return_value="vm-1.tailnet.ts.net"),
            mock.patch.object(MODULE, "restart_managed_service", return_value="restarted systemd user service") as restart_mock,
        ):
            summary = MODULE.auto_sync_once(config, state)

        apply_mock.assert_called_once_with(config)
        telegram_mock.assert_called_once()
        restart_mock.assert_called_once_with()
        save_mock.assert_called_once()
        self.assertIn("oldrevi..newrevi", summary)
        self.assertEqual(state["auto_sync"]["current_revision"], "newrevision")
        self.assertEqual(state["auto_sync"]["changed_files"], ["packs/codex/AGENTS.md"])

    def test_auto_sync_once_does_not_mark_revision_applied_when_apply_fails(self) -> None:
        config = MODULE.SupervisorConfig(
            profile="server",
            repo_root=Path("/tmp/klimkit"),
            machine_config_path=Path("/tmp/machine.toml"),
            live_sync_enabled=True,
            live_sync_interval_seconds=5,
            fetch_ref="origin/main",
            switchboard_agent_enabled=False,
            manage_switchboard=True,
        )

        def fake_git_output(_repo_root: Path, *args: str) -> str:
            if args == ("rev-parse", "HEAD"):
                return "newrevision"
            if args == ("diff", "--name-only", "oldrevision", "newrevision"):
                return "packs/codex/AGENTS.md\n"
            raise AssertionError(args)

        state: dict[str, object] = {"auto_sync": {"current_revision": "oldrevision"}}
        with (
            mock.patch.object(MODULE, "fetch_remote", return_value="newrevision"),
            mock.patch.object(MODULE, "git_output", side_effect=fake_git_output),
            mock.patch.object(MODULE, "save_supervisor_state") as save_mock,
            mock.patch.object(MODULE, "run_apply_for_autosync", side_effect=RuntimeError("apply failed")),
            mock.patch.object(MODULE, "send_telegram_notification") as telegram_mock,
            mock.patch.object(MODULE, "restart_managed_service") as restart_mock,
        ):
            with self.assertRaisesRegex(RuntimeError, "apply failed"):
                MODULE.auto_sync_once(config, state)

        save_mock.assert_not_called()
        telegram_mock.assert_not_called()
        restart_mock.assert_not_called()


if __name__ == "__main__":
    unittest.main()
