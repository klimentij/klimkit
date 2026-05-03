from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

from klimkit import cli
from klimkit.install import build_plan, default_config, format_plan


class KlimkitCliTests(unittest.TestCase):
    def test_help_lists_agent_testable_commands(self) -> None:
        parser = cli.build_parser()

        help_text = parser.format_help()

        for command in ["setup", "preview", "apply", "doctor", "daemon", "sync-live", "update", "serve", "uninstall"]:
            self.assertIn(command, help_text)

    def test_each_command_help_has_examples(self) -> None:
        for command in ["setup", "preview", "apply", "doctor", "daemon", "sync-live", "update", "serve", "uninstall"]:
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
        self.assertIn("kk apply --yes", stdout.getvalue())
        self.assertIn("kk update", stdout.getvalue())

    def test_preview_refuses_to_create_missing_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "klimkit.toml"
            stderr = io.StringIO()

            with redirect_stderr(stderr):
                result = cli.main(["--config", str(config_path), "preview"])

            self.assertEqual(result, 1)
            self.assertFalse(config_path.exists())
            self.assertIn("Config is missing", stderr.getvalue())

    def test_setup_creates_config_without_applying_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "klimkit.toml"
            stdout = io.StringIO()

            with redirect_stdout(stdout):
                result = cli.main(["--config", str(config_path), "setup", "--profile", "client", "--skip-services"])

            self.assertEqual(result, 0)
            self.assertTrue(config_path.exists())
            self.assertIn("No changes applied", stdout.getvalue())

    def test_plan_uses_klimkit_paths_and_no_private_defaults(self) -> None:
        config = default_config("client")
        rendered = format_plan(build_plan(config, skip_services=True), config_path=Path("/tmp/klimkit.toml"))

        self.assertIn(".config/klimkit", rendered)
        self.assertIn(".local/state/klimkit", rendered)
        self.assertNotIn("tail11" + "c448", rendered)
        self.assertNotIn("od" + "ev", rendered)


if __name__ == "__main__":
    unittest.main()
