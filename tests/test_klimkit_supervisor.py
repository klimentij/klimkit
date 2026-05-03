import tempfile
import unittest
from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path
from unittest import mock

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
            switchboard_agent_config_path=Path("/tmp/private-agent.toml"),
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
        load_config_mock.assert_called_once_with(Path("/tmp/private-agent.toml"))
        conn.close.assert_called_once()
        self.assertEqual(result, "switchboard-agent: reported snapshot")

    def test_load_machine_config_accepts_legacy_switchboard_key(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "machine.toml"
            config_path.write_text(
                "\n".join(
                    [
                        "[machine]",
                        'profile = "server"',
                        "",
                        "[components]",
                        "switchboard = true",
                        "",
                    ]
                ),
                encoding="utf-8",
            )

            config = MODULE.load_machine_config(config_path)

        self.assertTrue(config.manage_switchboard)
        self.assertEqual(config.switchboard_config_path, config_path.parent / "switchboard.toml")

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

    def test_load_machine_config_uses_local_switchboard_agent_config_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "machine.toml"
            agent_config_path = Path(tmpdir) / "private-agent.toml"
            config_path.write_text(
                "\n".join(
                    [
                        "[components]",
                        "client = true",
                        "server = false",
                        "",
                        "[workers]",
                        "switchboard_agent = true",
                        "",
                        "[switchboard]",
                        f'agent_config_path = "{agent_config_path}"',
                        "",
                    ]
                ),
                encoding="utf-8",
            )

            config = MODULE.load_machine_config(config_path)

        self.assertEqual(config.profile, "client")
        self.assertTrue(config.switchboard_agent_enabled)
        self.assertEqual(config.switchboard_agent_config_path, agent_config_path)

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
            switchboard_config_path=Path("/tmp/private-switchboard.toml"),
        )

        with mock.patch.object(MODULE, "start_process", return_value=mock.Mock()) as start_mock:
            MODULE.ensure_central_processes(config, {})

        command = start_mock.call_args.kwargs["command"]
        self.assertEqual(command, ["/tmp/klimkit/klimkit", "serve", "--config", "/tmp/private-switchboard.toml"])


if __name__ == "__main__":
    unittest.main()
