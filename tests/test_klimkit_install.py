from __future__ import annotations

import subprocess
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest import mock

from klimkit.install import (
    Action,
    apply_plan,
    build_plan,
    default_config,
    parse_config,
    render_config,
    uninstall_from_manifest,
)


ROOT = Path(__file__).resolve().parents[1]


class KlimkitInstallTests(unittest.TestCase):
    def test_config_render_parse_roundtrip(self) -> None:
        config = replace(default_config("server"), repo_root=Path("/tmp/klimkit"))

        parsed = parse_config(render_config(config))

        self.assertEqual(parsed.profile, "server")
        self.assertEqual(parsed.repo_root, Path("/tmp/klimkit"))
        self.assertTrue(parsed.switchboard_enabled)
        self.assertEqual(parsed.switchboard_config_path.name, "switchboard2.toml")

    def test_server_plan_writes_sensitive_configs_private(self) -> None:
        config = replace(default_config("server"), repo_root=ROOT)

        actions = build_plan(config, skip_services=True)

        switchboard = next(action for action in actions if action.id == "switchboard-config")
        cc_connect = next(action for action in actions if action.target.name == "config.toml" and action.component == "cc-connect")
        self.assertEqual(switchboard.mode, 0o600)
        self.assertIn("auth_token", switchboard.content or "")
        self.assertEqual(cc_connect.mode, 0o600)

    def test_code_server_install_is_manual_step_not_remote_command(self) -> None:
        config = replace(default_config("client"), install_code_server_if_missing=True)

        with mock.patch("klimkit.install.shutil.which", return_value=None):
            actions = build_plan(config, skip_services=True)

        install_action = next(action for action in actions if action.id == "install-code-server")
        self.assertEqual(install_action.kind, "manual_step")
        self.assertFalse(install_action.command)

    def test_apply_writes_manifest_backup_and_uninstall_scope(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            managed = root / "managed.txt"
            obsolete = root / "obsolete.txt"
            unmanaged = root / "unmanaged.txt"
            manifest_path = root / "state" / "install" / "manifest.json"
            backup_root = root / "state" / "backups"
            managed.write_text("old\n", encoding="utf-8")
            unmanaged.write_text("keep\n", encoding="utf-8")

            manifest = apply_plan(
                [
                    Action(
                        id="managed",
                        kind="write_file",
                        target=managed,
                        description="managed test file",
                        content="new\n",
                    ),
                    Action(
                        id="obsolete",
                        kind="write_file",
                        target=obsolete,
                        description="obsolete test file",
                        content="obsolete\n",
                    ),
                ],
                manifest_path=manifest_path,
                backup_root=backup_root,
                managed_roots=(root,),
            )

            self.assertEqual(managed.read_text(encoding="utf-8"), "new\n")
            self.assertTrue(obsolete.exists())
            self.assertTrue(manifest_path.exists())
            self.assertTrue(manifest["actions"][0]["backup"])
            self.assertTrue(Path(manifest["actions"][0]["backup"]).exists())
            self.assertEqual(unmanaged.read_text(encoding="utf-8"), "keep\n")

            manifest = apply_plan(
                [
                    Action(
                        id="managed",
                        kind="write_file",
                        target=managed,
                        description="managed test file",
                        content="newer\n",
                    ),
                ],
                manifest_path=manifest_path,
                backup_root=backup_root,
                managed_roots=(root,),
            )

            self.assertEqual(managed.read_text(encoding="utf-8"), "newer\n")
            self.assertFalse(obsolete.exists())
            self.assertEqual(manifest["pruned"][0]["target"], str(obsolete))
            self.assertTrue(Path(manifest["pruned"][0]["backup"]).exists())

            removed = uninstall_from_manifest(manifest_path=manifest_path, managed_roots=(root,))

            self.assertEqual(removed, 1)
            self.assertFalse(managed.exists())
            self.assertTrue(unmanaged.exists())

    def test_apply_and_uninstall_skip_modified_manifest_targets(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            managed = root / "managed.txt"
            obsolete = root / "obsolete.txt"
            manifest_path = root / "state" / "install" / "manifest.json"
            backup_root = root / "state" / "backups"

            apply_plan(
                [
                    Action(
                        id="managed",
                        kind="write_file",
                        target=managed,
                        description="managed test file",
                        content="new\n",
                    ),
                    Action(
                        id="obsolete",
                        kind="write_file",
                        target=obsolete,
                        description="obsolete test file",
                        content="obsolete\n",
                    ),
                ],
                manifest_path=manifest_path,
                backup_root=backup_root,
                managed_roots=(root,),
            )
            obsolete.write_text("user edit\n", encoding="utf-8")

            manifest = apply_plan(
                [
                    Action(
                        id="managed",
                        kind="write_file",
                        target=managed,
                        description="managed test file",
                        content="newer\n",
                    ),
                ],
                manifest_path=manifest_path,
                backup_root=backup_root,
                managed_roots=(root,),
            )

            self.assertTrue(obsolete.exists())
            self.assertEqual(manifest["skipped"][0]["target"], str(obsolete))
            self.assertEqual(manifest["skipped"][0]["reason"], "modified")

            managed.write_text("user edit\n", encoding="utf-8")
            removed = uninstall_from_manifest(manifest_path=manifest_path, managed_roots=(root,))

            self.assertEqual(removed, 0)
            self.assertTrue(managed.exists())
            self.assertTrue(manifest_path.exists())

    def test_service_templates_use_custom_config_path(self) -> None:
        config_path = Path("/tmp/custom-klimkit.toml")
        config = replace(
            default_config("client"),
            repo_root=ROOT,
            codex_enabled=False,
            code_server_enabled=False,
            supervisor_enabled=True,
            configure_services=True,
        )

        with mock.patch("klimkit.install.platform.system", return_value="Linux"):
            actions = build_plan(config, config_path=config_path)

        service = next(action for action in actions if action.id == "systemd:klimkit.service")
        self.assertIsNotNone(service.content)
        self.assertIn(f"KLIMKIT_CONFIG={config_path}", service.content or "")
        self.assertIn("ExecStart=", service.content or "")
        self.assertNotIn(".config/" + "klim" + "ki", service.content or "")

    def test_installer_rejects_options_and_documents_kk_flow(self) -> None:
        result = subprocess.run(
            ["bash", str(ROOT / "install.sh"), "--profile", "server"],
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("does not accept options", result.stderr)
        self.assertIn("kk/klimkit launchers", result.stderr)

    def test_public_templates_do_not_contain_private_defaults(self) -> None:
        checked_roots = [ROOT / "packs", ROOT / "templates"]
        private_tokens = [
            "/home/" + "ubuntu",
            "tail11" + "c448",
            "od" + "ev",
            "op" + "rod",
            "klimki" + "pedia",
            "q" + "md",
        ]

        for root in checked_roots:
            for path in root.rglob("*"):
                if not path.is_file():
                    continue
                text = path.read_text(encoding="utf-8", errors="ignore")
                for token in private_tokens:
                    self.assertNotIn(token, text, f"{token} leaked in {path}")


if __name__ == "__main__":
    unittest.main()
