from __future__ import annotations

import io
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

        for command in ["setup", "preview", "apply", "doctor", "daemon", "sync-live", "update", "pull", "serve", "uninstall"]:
            self.assertIn(command, help_text)

    def test_each_command_help_has_examples(self) -> None:
        for command in ["setup", "preview", "apply", "doctor", "daemon", "sync-live", "update", "pull", "serve", "uninstall"]:
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
        self.assertIn("Agentic engineering across machines, under control.", stdout.getvalue())
        self.assertIn("kk setup", stdout.getvalue())
        self.assertIn("kk apply", stdout.getvalue())
        self.assertIn("kk update", stdout.getvalue())
        self.assertIn("kk pull", stdout.getvalue())

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
            apply_plan_mock.assert_called_once_with([])
            self.assertIn("actions    0", stdout.getvalue())

    def test_uninstall_without_confirmation_flag_uninstalls(self) -> None:
        stdout = io.StringIO()

        with redirect_stdout(stdout), mock.patch.object(cli, "uninstall_from_manifest", return_value=3) as uninstall_mock:
            result = cli.main(["uninstall"])

        self.assertEqual(result, 0)
        uninstall_mock.assert_called_once_with()
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
            config_path.write_text("[components]\nclient = true\nserver = false\n", encoding="utf-8")
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
            apply_plan_mock.assert_called_once_with([])
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
            self.assertIn("Switchboard TOML config", stdout.getvalue())
            config = parse_config(config_path.read_text(encoding="utf-8"))
            self.assertTrue(config.server_enabled)

    def test_plan_uses_klimkit_paths_and_no_private_defaults(self) -> None:
        config = default_config("client")
        rendered = format_plan(build_plan(config, skip_services=True), config_path=Path("/tmp/klimkit.toml"))

        self.assertIn(".config/klimkit", rendered)
        self.assertIn(".local/state/klimkit", rendered)
        self.assertNotIn("tail11" + "c448", rendered)
        self.assertNotIn("od" + "ev", rendered)


if __name__ == "__main__":
    unittest.main()
