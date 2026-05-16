from __future__ import annotations

import io
import os
import shlex
import subprocess
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

from klimkit import cli
from klimkit.install import build_plan, default_config, format_plan, parse_config


class KlimkitCliTests(unittest.TestCase):
    def test_help_lists_agent_testable_commands(self) -> None:
        parser = cli.build_parser()

        help_text = parser.format_help()

        for command in ["setup", "preview", "apply", "doctor", "daemon", "sync-live", "update", "pull", "migrate", "serve", "code-server", "uninstall"]:
            self.assertIn(command, help_text)

    def test_each_command_help_has_examples(self) -> None:
        for command in ["setup", "preview", "apply", "doctor", "daemon", "sync-live", "update", "pull", "migrate", "serve", "code-server", "uninstall"]:
            stdout = io.StringIO()
            with self.subTest(command=command), redirect_stdout(stdout), self.assertRaises(SystemExit) as raised:
                cli.build_parser().parse_args([command, "--help"])

            self.assertEqual(raised.exception.code, 0)
            self.assertIn("examples:", stdout.getvalue())

    def test_kk_alias_can_show_kk_usage(self) -> None:
        with mock.patch.dict("os.environ", {"KLIMKIT_PROG": "kk"}):
            help_text = cli.build_parser().format_help()

        self.assertIn("usage: kk", help_text)

    def test_no_args_prints_getting_started(self) -> None:
        stdout = io.StringIO()

        with redirect_stdout(stdout):
            result = cli.main([])

        self.assertEqual(result, 0)
        self.assertIn("Keep an agent-ready machine reproducible from one repo.", stdout.getvalue())
        self.assertIn("kk setup", stdout.getvalue())
        self.assertIn("kk apply", stdout.getvalue())
        self.assertIn("kk update", stdout.getvalue())
        self.assertIn("kk pull", stdout.getvalue())
        self.assertIn("kk migrate team-workflow", stdout.getvalue())

    def test_migrate_team_workflow_dry_run_and_apply(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            config_path = root / ".klimkit" / "local" / "klimkit.toml"
            config_path.parent.mkdir(parents=True)
            (root / ".klimkit" / "tasks" / "feature").mkdir(parents=True)
            (root / ".klimkit" / "memory.md").write_text("# Memory\n", encoding="utf-8")
            (root / ".klimkit" / "tasks" / "feature" / "01-a.md").write_text("task\n", encoding="utf-8")
            config_path.write_text(
                "\n".join(
                    [
                        "[operator]",
                        'human_name = "Alice"',
                        "",
                        "[paths]",
                        f'repo_root = "{root}"',
                        "",
                    ]
                ),
                encoding="utf-8",
            )
            dry_stdout = io.StringIO()

            with redirect_stdout(dry_stdout):
                dry_result = cli.main(["--config", str(config_path), "migrate", "team-workflow", "--dry-run"])

            self.assertEqual(dry_result, 0)
            self.assertIn("would move", dry_stdout.getvalue())
            self.assertTrue((root / ".klimkit" / "memory.md").exists())

            apply_stdout = io.StringIO()
            with redirect_stdout(apply_stdout):
                apply_result = cli.main(["--config", str(config_path), "migrate", "team-workflow"])

            self.assertEqual(apply_result, 0)
            self.assertIn("moved", apply_stdout.getvalue())
            self.assertFalse((root / ".klimkit" / "memory.md").exists())
            self.assertTrue((root / ".klimkit" / "Alice" / "memory.md").exists())
            self.assertTrue((root / ".klimkit" / "Alice" / "tasks" / "feature" / "01-a.md").exists())
            self.assertIn('workflow = "team"', config_path.read_text(encoding="utf-8"))

    def test_migrate_team_workflow_explicit_configured_repo_updates_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            config_path = root / ".klimkit" / "local" / "klimkit.toml"
            config_path.parent.mkdir(parents=True)
            (root / ".klimkit" / "memory.md").write_text("# Memory\n", encoding="utf-8")
            config_path.write_text(
                "\n".join(
                    [
                        "[operator]",
                        'human_name = "Alice"',
                        'workflow = "solo"',
                        "",
                        "[paths]",
                        f'repo_root = "{root}"',
                        "",
                    ]
                ),
                encoding="utf-8",
            )
            stdout = io.StringIO()

            with redirect_stdout(stdout):
                result = cli.main(["--config", str(config_path), "migrate", "team-workflow", "--repo", str(root)])

            self.assertEqual(result, 0)
            self.assertIn("moved", stdout.getvalue())
            self.assertNotIn("(not updated for project migration)", stdout.getvalue())
            self.assertTrue((root / ".klimkit" / "Alice" / "memory.md").exists())
            self.assertIn('workflow = "team"', config_path.read_text(encoding="utf-8"))

    def test_migrate_team_workflow_uses_current_project_when_config_is_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            harness = root / "harness"
            project = root / "project"
            config_path = harness / ".klimkit" / "local" / "klimkit.toml"
            config_path.parent.mkdir(parents=True)
            project_klimkit = project / ".klimkit"
            project_klimkit.mkdir(parents=True)
            (project_klimkit / "memory.md").write_text("# Project Memory\n", encoding="utf-8")
            config_path.write_text(
                "\n".join(
                    [
                        "[operator]",
                        'human_name = "Dominik"',
                        'workflow = "solo"',
                        "",
                        "[paths]",
                        f'repo_root = "{harness}"',
                        "",
                    ]
                ),
                encoding="utf-8",
            )
            old_cwd = Path.cwd()
            stdout = io.StringIO()
            try:
                os.chdir(project)
                with mock.patch.dict("os.environ", {"KLIMKIT_CONFIG": str(config_path)}), redirect_stdout(stdout):
                    result = cli.main(["migrate", "team-workflow"])
            finally:
                os.chdir(old_cwd)

            self.assertEqual(result, 0)
            self.assertIn(str(project), stdout.getvalue())
            self.assertIn("(not updated for project migration)", stdout.getvalue())
            self.assertFalse((project_klimkit / "memory.md").exists())
            self.assertTrue((project_klimkit / "Dominik" / "memory.md").exists())
            rendered_config = config_path.read_text(encoding="utf-8")
            self.assertIn(f'repo_root = "{harness}"', rendered_config)
            self.assertIn('workflow = "solo"', rendered_config)

    def test_migrate_team_workflow_dry_run_next_command_preserves_implicit_context(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            harness = root / "harness"
            project = root / "project"
            config_path = harness / ".klimkit" / "local" / "klimkit.toml"
            config_path.parent.mkdir(parents=True)
            project_klimkit = project / ".klimkit"
            project_klimkit.mkdir(parents=True)
            (project_klimkit / "memory.md").write_text("# Project Memory\n", encoding="utf-8")
            config_path.write_text(
                "\n".join(
                    [
                        "[operator]",
                        'human_name = "Dominik"',
                        'workflow = "solo"',
                        "",
                        "[paths]",
                        f'repo_root = "{harness}"',
                        "",
                    ]
                ),
                encoding="utf-8",
            )
            old_cwd = Path.cwd()
            stdout = io.StringIO()
            try:
                os.chdir(project)
                with mock.patch.dict("os.environ", {"KLIMKIT_CONFIG": str(config_path)}), redirect_stdout(stdout):
                    result = cli.main(["migrate", "team-workflow", "--dry-run"])
            finally:
                os.chdir(old_cwd)

            self.assertEqual(result, 0)
            command_line = next(
                line.strip()
                for line in stdout.getvalue().splitlines()
                if line.strip().startswith("kk ")
            )
            self.assertEqual(
                shlex.split(command_line),
                [
                    "kk",
                    "--config",
                    str(config_path),
                    "migrate",
                    "team-workflow",
                    "--repo",
                    str(project),
                    "--human-name",
                    "Dominik",
                ],
            )
            self.assertTrue((project_klimkit / "memory.md").exists())

    def test_migrate_team_workflow_supports_explicit_repo_and_human_name_without_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            project = root / "project"
            project_klimkit = project / ".klimkit"
            config_path = root / "missing" / "klimkit.toml"
            project_klimkit.mkdir(parents=True)
            (project_klimkit / "log.md").write_text("# Project Log\n", encoding="utf-8")
            stdout = io.StringIO()

            with redirect_stdout(stdout):
                result = cli.main(
                    [
                        "--config",
                        str(config_path),
                        "migrate",
                        "team-workflow",
                        "--repo",
                        str(project),
                        "--human-name",
                        "Dominik",
                    ]
                )

            self.assertEqual(result, 0)
            self.assertIn(str(project), stdout.getvalue())
            self.assertFalse(config_path.exists())
            self.assertFalse((project_klimkit / "log.md").exists())
            self.assertTrue((project_klimkit / "Dominik" / "log.md").exists())

    def test_migrate_team_workflow_dry_run_next_command_preserves_and_quotes_context(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            project = root / "project with spaces"
            config_path = root / "config dir" / "klimkit.toml"
            project_klimkit = project / ".klimkit"
            project_klimkit.mkdir(parents=True)
            (project_klimkit / "memory.md").write_text("# Project Memory\n", encoding="utf-8")
            human_name = "Alice O'Connor; rm -rf nope"
            stdout = io.StringIO()

            with redirect_stdout(stdout):
                result = cli.main(
                    [
                        "--config",
                        str(config_path),
                        "migrate",
                        "team-workflow",
                        "--repo",
                        str(project),
                        "--human-name",
                        human_name,
                        "--dry-run",
                    ]
                )

            self.assertEqual(result, 0)
            command_line = next(
                line.strip()
                for line in stdout.getvalue().splitlines()
                if line.strip().startswith("kk ")
            )
            self.assertEqual(
                shlex.split(command_line),
                [
                    "kk",
                    "--config",
                    str(config_path),
                    "migrate",
                    "team-workflow",
                    "--repo",
                    str(project),
                    "--human-name",
                    human_name,
                ],
            )
            self.assertFalse(config_path.exists())
            self.assertTrue((project_klimkit / "memory.md").exists())

    def test_code_server_capture_writes_repo_profile(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            config_path = root / "klimkit.toml"
            user_dir = root / "live" / "User"
            extensions_dir = root / "live" / "extensions"
            user_dir.mkdir(parents=True)
            extensions_dir.mkdir(parents=True)
            config_path.write_text(
                "\n".join(
                    [
                        "[paths]",
                        f'repo_root = "{root}"',
                        "",
                        "[components]",
                        "client = true",
                        "server = false",
                        "",
                        "[workers]",
                        "switchboard_agent = false",
                    ]
                ),
                encoding="utf-8",
            )
            (user_dir / "settings.json").write_text('{"workbench.colorTheme": "Dark 2026"}\n', encoding="utf-8")
            (user_dir / "keybindings.json").write_text("[]\n", encoding="utf-8")
            package = extensions_dir / "publisher.example-1.0.0" / "package.json"
            package.parent.mkdir()
            package.write_text('{"publisher": "publisher", "name": "example"}\n', encoding="utf-8")
            stdout = io.StringIO()

            with redirect_stdout(stdout):
                result = cli.main(
                    [
                        "--config",
                        str(config_path),
                        "code-server",
                        "capture",
                        "--user-dir",
                        str(user_dir),
                        "--extensions-dir",
                        str(extensions_dir),
                    ]
                )

            self.assertEqual(result, 0)
            self.assertIn("Managed profile captured.", stdout.getvalue())
            self.assertEqual(
                (root / "templates" / "code-server" / "extensions.txt").read_text(encoding="utf-8"),
                "publisher.example\n",
            )

    def test_preview_refuses_to_create_missing_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "klimkit.toml"
            stderr = io.StringIO()

            with redirect_stderr(stderr):
                result = cli.main(["--config", str(config_path), "preview"])

            self.assertEqual(result, 1)
            self.assertFalse(config_path.exists())
            self.assertIn("Config is missing", stderr.getvalue())

    def test_apply_without_confirmation_flag_applies_plan(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "klimkit.toml"
            stdout = io.StringIO()

            with (
                redirect_stdout(stdout),
                mock.patch.object(cli, "build_plan", return_value=[]) as build_plan_mock,
                mock.patch.object(cli, "apply_plan", return_value={"actions": []}) as apply_plan_mock,
            ):
                result = cli.main(["--config", str(config_path), "apply", "--skip-services"])

            self.assertEqual(result, 0)
            build_plan_mock.assert_called_once()
            self.assertTrue(build_plan_mock.call_args.kwargs["skip_services"])
            apply_plan_mock.assert_called_once()
            self.assertEqual(apply_plan_mock.call_args.args, ([],))
            self.assertEqual(apply_plan_mock.call_args.kwargs["manifest_path"], cli.KLIMKIT_MANIFEST_FILE)
            self.assertIn("actions    0", stdout.getvalue())

    def test_apply_can_defer_service_restart_for_daemon_autosync(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "klimkit.toml"
            stdout = io.StringIO()

            with (
                redirect_stdout(stdout),
                mock.patch.object(cli, "build_plan", return_value=[]) as build_plan_mock,
                mock.patch.object(cli, "apply_plan", return_value={"actions": [], "changed": []}),
            ):
                result = cli.main(["--config", str(config_path), "apply", "--defer-service-restart"])

            self.assertEqual(result, 0)
            build_plan_mock.assert_called_once()
            self.assertFalse(build_plan_mock.call_args.kwargs["restart_services"])

    def test_uninstall_without_confirmation_flag_uninstalls(self) -> None:
        stdout = io.StringIO()

        with redirect_stdout(stdout), mock.patch.object(cli, "uninstall_from_manifest", return_value=3) as uninstall_mock:
            result = cli.main(["uninstall"])

        self.assertEqual(result, 0)
        uninstall_mock.assert_called_once_with(manifest_path=cli.KLIMKIT_MANIFEST_FILE)
        self.assertIn("removed    3", stdout.getvalue())

    def test_pull_refuses_missing_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "klimkit.toml"
            stderr = io.StringIO()

            with redirect_stderr(stderr):
                result = cli.main(["--config", str(config_path), "pull"])

            self.assertEqual(result, 1)
            self.assertFalse(config_path.exists())
            self.assertIn("Config is missing", stderr.getvalue())

    def test_pull_updates_from_git_upstream_and_applies(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "klimkit.toml"
            config_path.write_text(
                "[components]\nclient = true\nserver = false\n\n[workers]\nswitchboard_agent = false\n",
                encoding="utf-8",
            )
            stdout = io.StringIO()
            git_calls: list[list[str]] = []

            def fake_subprocess_run(command: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
                del cwd
                git_calls.append(command)
                stdout_text = ""
                if command == ["git", "branch", "--show-current"]:
                    stdout_text = "main\n"
                elif command == ["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"]:
                    stdout_text = "origin/main\n"
                return subprocess.CompletedProcess(command, 0, stdout_text, "")

            with (
                redirect_stdout(stdout),
                mock.patch.object(cli, "subprocess_run", side_effect=fake_subprocess_run),
                mock.patch.object(cli, "build_plan", return_value=[]) as build_plan_mock,
                mock.patch.object(cli, "apply_plan", return_value={"actions": []}) as apply_plan_mock,
            ):
                result = cli.main(["--config", str(config_path), "pull", "--skip-services"])

            self.assertEqual(result, 0)
            self.assertIn(["git", "fetch", "origin", "main"], git_calls)
            self.assertIn(["git", "pull", "--ff-only", "origin", "main"], git_calls)
            build_plan_mock.assert_called_once()
            self.assertTrue(build_plan_mock.call_args.kwargs["skip_services"])
            apply_plan_mock.assert_called_once()
            self.assertEqual(apply_plan_mock.call_args.args, ([],))
            self.assertEqual(apply_plan_mock.call_args.kwargs["manifest_path"], cli.KLIMKIT_MANIFEST_FILE)
            self.assertIn("actions    0", stdout.getvalue())

    def test_setup_creates_config_without_applying_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "klimkit.toml"
            stdout = io.StringIO()

            with redirect_stdout(stdout):
                result = cli.main(["--config", str(config_path), "setup", "--skip-services"])

            self.assertEqual(result, 0)
            self.assertTrue(config_path.exists())
            self.assertIn("Config prepared; no files were applied.", stdout.getvalue())
            config = parse_config(config_path.read_text(encoding="utf-8"))
            self.assertTrue(config.client_enabled)
            self.assertTrue(config.server_enabled)

    def test_setup_client_only_creates_second_vm_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "klimkit.toml"

            with redirect_stdout(io.StringIO()):
                result = cli.main(["--config", str(config_path), "setup", "--client-only", "--skip-services"])

            self.assertEqual(result, 0)
            config = parse_config(config_path.read_text(encoding="utf-8"))
            self.assertTrue(config.client_enabled)
            self.assertFalse(config.server_enabled)
            self.assertFalse(config.switchboard_enabled)
            self.assertTrue(config.switchboard_agent_enabled)

    def test_apply_blocks_client_agent_without_backend_url(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "klimkit.toml"
            with redirect_stdout(io.StringIO()):
                cli.main(["--config", str(config_path), "setup", "--client-only", "--skip-services"])
            stderr = io.StringIO()

            with redirect_stderr(stderr):
                result = cli.main(["--config", str(config_path), "apply", "--skip-services"])

            self.assertEqual(result, 1)
            self.assertIn("Apply is blocked", stderr.getvalue())
            self.assertIn("backend_url", stderr.getvalue())

    def test_apply_reports_only_changed_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "klimkit.toml"
            config_path.write_text(
                "[components]\nclient = true\nserver = false\n\n[workers]\nswitchboard_agent = false\n",
                encoding="utf-8",
            )
            stdout = io.StringIO()

            with (
                redirect_stdout(stdout),
                mock.patch.object(cli, "build_plan", return_value=[]) as build_plan_mock,
                mock.patch.object(
                    cli,
                    "apply_plan",
                    return_value={
                        "actions": [{"id": "same"}],
                        "changed": [{"status": "updated", "target": "/tmp/changed.txt"}],
                    },
                ) as apply_plan_mock,
            ):
                result = cli.main(["--config", str(config_path), "apply", "--skip-services"])

            self.assertEqual(result, 0)
            build_plan_mock.assert_called_once()
            apply_plan_mock.assert_called_once()
            self.assertEqual(apply_plan_mock.call_args.args, ([],))
            self.assertEqual(apply_plan_mock.call_args.kwargs["manifest_path"], cli.KLIMKIT_MANIFEST_FILE)
            self.assertIn("changed    1", stdout.getvalue())
            self.assertIn("Changed Files", stdout.getvalue())
            self.assertIn("/tmp/changed.txt", stdout.getvalue())

    def test_apply_reports_live_service_restart_and_urls(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "klimkit.toml"
            config_path.write_text(
                "\n".join(
                    [
                        "[components]",
                        "client = true",
                        "server = true",
                        "",
                        "[switchboard.server]",
                        "enabled = true",
                        'host = "127.0.0.1"',
                        "port = 4721",
                        'base_path = "/switchboard"',
                        "",
                    ]
                ),
                encoding="utf-8",
            )
            stdout = io.StringIO()

            with (
                redirect_stdout(stdout),
                mock.patch.object(cli, "build_plan", return_value=[]),
                mock.patch.object(cli, "_tailscale_dns_name", return_value="odev.tail11c448.ts.net"),
                mock.patch.object(
                    cli,
                    "apply_plan",
                    return_value={
                        "actions": [
                            {
                                "id": "tailscale-serve-code-server",
                                "kind": "run_command",
                                "description": "configure Tailscale Serve for code-server",
                                "status": "ran",
                            },
                            {
                                "id": "systemd-restart-klimkit",
                                "kind": "run_command",
                                "description": "restart Klimkit user service",
                                "status": "ran",
                            }
                        ],
                        "changed": [],
                    },
                ),
            ):
                result = cli.main(["--config", str(config_path), "apply"])

            self.assertEqual(result, 0)
            output = stdout.getvalue()
            self.assertIn("Live", output)
            self.assertIn("served", output)
            self.assertIn("configure Tailscale Serve for code-server", output)
            self.assertIn("restarted", output)
            self.assertIn("restart Klimkit user service", output)
            self.assertIn("Switchboard: http://127.0.0.1:4721/switchboard/", output)
            self.assertIn("Switchboard proxy: https://odev.tail11c448.ts.net/proxy/4721/", output)
            self.assertIn("Switchboard serve: https://odev.tail11c448.ts.net/switchboard/", output)
            self.assertIn("Proof reports: https://odev.tail11c448.ts.net/reports/", output)
            self.assertIn("Codex projection:", output)
            self.assertIn("code-server settings:", output)
            expected_check = (
                "launchctl print gui/$(id -u)/com.klim.klimkit"
                if cli.platform.system() == "Darwin"
                else "systemctl --user status klimkit.service --no-pager"
            )
            self.assertIn(expected_check, output)

    def test_apply_reports_tailscale_serve_permission_skip(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "klimkit.toml"
            config_path.write_text(
                "\n".join(
                    [
                        "[components]",
                        "client = true",
                        "server = true",
                        "",
                        "[switchboard.server]",
                        "enabled = true",
                        'host = "127.0.0.1"',
                        "port = 4721",
                        'base_path = "/switchboard"',
                        "",
                    ]
                ),
                encoding="utf-8",
            )
            stdout = io.StringIO()

            with (
                redirect_stdout(stdout),
                mock.patch.object(cli, "build_plan", return_value=[]),
                mock.patch.object(cli, "_tailscale_dns_name", return_value="odev.tail11c448.ts.net"),
                mock.patch.object(
                    cli,
                    "apply_plan",
                    return_value={
                        "actions": [
                            {
                                "id": "tailscale-serve-code-server",
                                "kind": "run_command",
                                "description": "configure Tailscale Serve for code-server",
                                "component": "tailscale",
                                "status": "skipped",
                                "reason": "tailscale serve operator permission required",
                                "message": (
                                    "configure Tailscale Serve for code-server skipped; "
                                    "run sudo tailscale set --operator=$USER"
                                ),
                            }
                        ],
                        "changed": [],
                    },
                ),
            ):
                result = cli.main(["--config", str(config_path), "apply"])

            self.assertEqual(result, 0)
            output = stdout.getvalue()
            self.assertIn("skipped", output)
            self.assertIn("configure Tailscale Serve for code-server skipped", output)
            self.assertIn("sudo tailscale set --operator=$USER", output)
            self.assertNotIn("served", output)

    def test_apply_sends_telegram_summary_when_enabled(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "klimkit.toml"
            config_path.write_text(
                "\n".join(
                    [
                        "[components]",
                        "client = true",
                        "server = true",
                        "",
                        "[switchboard.server]",
                        "enabled = true",
                        'host = "127.0.0.1"',
                        "port = 4721",
                        'base_path = "/switchboard"',
                        "",
                        "[notifications.telegram]",
                        "enabled = true",
                        'bot_token = "bot-token"',
                        'chat_id = "chat-id"',
                        "",
                    ]
                ),
                encoding="utf-8",
            )
            stdout = io.StringIO()

            with (
                redirect_stdout(stdout),
                mock.patch.object(cli.socket, "gethostname", return_value="vm-1"),
                mock.patch.object(cli, "_tailscale_dns_name", return_value="odev.tail11c448.ts.net"),
                mock.patch.object(cli, "build_plan", return_value=[]),
                mock.patch.object(
                    cli,
                    "apply_plan",
                    return_value={
                        "actions": [
                            {
                                "id": "systemd-restart-klimkit",
                                "kind": "run_command",
                                "description": "restart Klimkit user service",
                                "status": "ran",
                            }
                        ],
                        "changed": [{"status": "updated", "target": "/tmp/changed.txt"}],
                    },
                ),
                mock.patch.object(cli, "send_telegram_notification", return_value=True) as telegram_mock,
            ):
                result = cli.main(["--config", str(config_path), "apply"])

            self.assertEqual(result, 0)
            telegram_mock.assert_called_once()
            notification = telegram_mock.call_args.args[1]
            self.assertIn("✅ Klimkit apply", notification)
            self.assertIn("🖥 Machine: vm-1", notification)
            self.assertIn("📦 Actions: 1", notification)
            self.assertIn("📝 Changes: 1 files changed", notification)
            self.assertIn("restart Klimkit user service", notification)
            self.assertIn("https://odev.tail11c448.ts.net/proxy/4721/", notification)
            self.assertIn("📄 Reports: https://odev.tail11c448.ts.net/reports/", notification)
            self.assertIn("telegram", stdout.getvalue())
            self.assertIn("sent apply summary to Telegram", stdout.getvalue())

    def test_deferred_apply_skips_telegram_to_avoid_autosync_duplicate(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "klimkit.toml"
            config_path.write_text(
                "\n".join(
                    [
                        "[components]",
                        "client = true",
                        "server = false",
                        "",
                        "[workers]",
                        "switchboard_agent = false",
                        "",
                        "[notifications.telegram]",
                        "enabled = true",
                        'bot_token = "bot-token"',
                        'chat_id = "chat-id"',
                        "",
                    ]
                ),
                encoding="utf-8",
            )
            stdout = io.StringIO()

            with (
                redirect_stdout(stdout),
                mock.patch.object(cli, "build_plan", return_value=[]),
                mock.patch.object(cli, "apply_plan", return_value={"actions": [], "changed": []}),
                mock.patch.object(cli, "send_telegram_notification") as telegram_mock,
            ):
                result = cli.main(["--config", str(config_path), "apply", "--defer-service-restart"])

            self.assertEqual(result, 0)
            telegram_mock.assert_not_called()
            self.assertNotIn("telegram", stdout.getvalue())

    def test_doctor_reports_switchboard_tailnet_urls(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "klimkit.toml"
            config_path.write_text(
                "\n".join(
                    [
                        "[components]",
                        "client = true",
                        "server = true",
                        "",
                        "[switchboard.server]",
                        "enabled = true",
                        'host = "127.0.0.1"',
                        "port = 4721",
                        'base_path = "/switchboard"',
                        "",
                    ]
                ),
                encoding="utf-8",
            )
            stdout = io.StringIO()

            with (
                redirect_stdout(stdout),
                mock.patch.object(cli, "_tailscale_dns_name", return_value="odev.tail11c448.ts.net"),
            ):
                result = cli.main(["--config", str(config_path), "doctor"])

            self.assertEqual(result, 0)
            output = stdout.getvalue()
            self.assertIn("URLs", output)
            self.assertIn("Switchboard: http://127.0.0.1:4721/switchboard/", output)
            self.assertIn("Switchboard proxy: https://odev.tail11c448.ts.net/proxy/4721/", output)
            self.assertIn("Switchboard serve: https://odev.tail11c448.ts.net/switchboard/", output)
            self.assertIn("Proof reports: https://odev.tail11c448.ts.net/reports/", output)

    def test_setup_role_flag_previews_existing_config_conversion(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "klimkit.toml"
            with redirect_stdout(io.StringIO()):
                cli.main(["--config", str(config_path), "setup", "--client-only", "--skip-services"])
            stdout = io.StringIO()

            with redirect_stdout(stdout):
                result = cli.main(["--config", str(config_path), "setup", "--profile", "server", "--skip-services"])

            self.assertEqual(result, 0)
            self.assertIn("(updated)", stdout.getvalue())
            self.assertIn("Klimkit single source config", stdout.getvalue())
            config = parse_config(config_path.read_text(encoding="utf-8"))
            self.assertTrue(config.server_enabled)

    def test_plan_uses_klimkit_paths_and_no_private_defaults(self) -> None:
        config = default_config("client")
        with mock.patch("klimkit.install.shutil.which", return_value=None):
            rendered = format_plan(build_plan(config, skip_services=True), config_path=Path("/tmp/klimkit.toml"))

        self.assertIn(".klimkit/local/klimkit.toml", rendered)
        self.assertIn(".klimkit/state", rendered)
        self.assertIn("External Installers", rendered)
        self.assertNotIn("switchboard.toml", rendered)
        self.assertNotIn("tail11" + "c448", rendered)
        self.assertNotIn("od" + "ev", rendered)


if __name__ == "__main__":
    unittest.main()
