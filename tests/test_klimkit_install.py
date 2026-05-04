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
    render_switchboard_agent_config,
    uninstall_from_manifest,
)


ROOT = Path(__file__).resolve().parents[1]


class KlimkitInstallTests(unittest.TestCase):
    def test_default_config_is_first_vm_with_client_and_server(self) -> None:
        config = replace(default_config(), repo_root=Path("/tmp/klimkit"))

        parsed = parse_config(render_config(config))

        self.assertEqual(parsed.profile, "server")
        self.assertTrue(parsed.client_enabled)
        self.assertTrue(parsed.server_enabled)
        self.assertEqual(parsed.repo_root, Path("/tmp/klimkit"))
        self.assertTrue(parsed.switchboard_enabled)
        self.assertFalse(parsed.live_sync_enabled)
        self.assertTrue(parsed.install_code_server_if_missing)
        self.assertEqual(parsed.switchboard_config_path.name, "switchboard.toml")
        self.assertIn("First VM default", render_config(config))
        self.assertIn("enable = true", render_config(config))

    def test_client_only_role_disables_server_components(self) -> None:
        config = parse_config(
            "\n".join(
                [
                    "[components]",
                    "client = true",
                    "server = false",
                    "",
                ]
            )
        )

        self.assertEqual(config.profile, "client")
        self.assertTrue(config.codex_enabled)
        self.assertFalse(config.live_sync_enabled)
        self.assertFalse(config.switchboard_enabled)
        self.assertTrue(config.switchboard_agent_enabled)

    def test_legacy_services_configure_key_still_loads(self) -> None:
        config = parse_config(
            "\n".join(
                [
                    "[services]",
                    "configure = false",
                    "",
                ]
            )
        )

        self.assertFalse(config.configure_services)

    def test_legacy_switchboard_defaults_migrate_to_switchboard_name(self) -> None:
        config = parse_config(
            "\n".join(
                [
                    "[switchboard]",
                    f'config_path = "~/.config/klimkit/{"switchboard" + "2.toml"}"',
                    f'backend_url = "https://server.example.ts.net/{"switchboard" + "2"}"',
                    f'base_path = "/{"switchboard" + "2"}"',
                    "",
                ]
            )
        )

        self.assertEqual(config.switchboard_config_path.name, "switchboard.toml")
        self.assertEqual(config.switchboard_backend_url, "https://server.example.ts.net/switchboard")
        self.assertEqual(config.switchboard_base_path, "/switchboard")

    def test_legacy_server_profile_still_enables_server_role(self) -> None:
        config = parse_config(
            "\n".join(
                [
                    "[machine]",
                    'profile = "server"',
                    "",
                ]
            )
        )

        self.assertEqual(config.profile, "server")
        self.assertTrue(config.client_enabled)
        self.assertTrue(config.server_enabled)
        self.assertTrue(config.switchboard_enabled)

    def test_server_plan_writes_sensitive_configs_private(self) -> None:
        config = replace(default_config(), repo_root=ROOT)

        actions = build_plan(config, skip_services=True)

        switchboard = next(action for action in actions if action.id == "switchboard-config")
        self.assertEqual(switchboard.mode, 0o600)
        self.assertIn("auth_token", switchboard.content or "")

    def test_switchboard_agent_config_uses_private_backend_settings(self) -> None:
        config = replace(
            default_config("client"),
            switchboard_agent_enabled=True,
            switchboard_backend_url="https://server.example.ts.net/switchboard",
            switchboard_auth_token="secret",
        )

        content = render_switchboard_agent_config(config)

        self.assertIn('base_url = "https://server.example.ts.net/switchboard"', content)
        self.assertIn('auth_token = "secret"', content)

    def test_code_server_install_is_run_command_when_missing(self) -> None:
        config = default_config("client")

        with mock.patch("klimkit.install.shutil.which", return_value=None):
            actions = build_plan(config, skip_services=True)

        install_action = next(action for action in actions if action.id == "install-code-server")
        self.assertEqual(install_action.kind, "run_command")
        self.assertIn("code-server.dev/install.sh", " ".join(install_action.command))

    def test_code_server_install_can_be_disabled_for_self_managed_clients(self) -> None:
        config = replace(default_config("client"), install_code_server_if_missing=False)

        with mock.patch("klimkit.install.shutil.which", return_value=None):
            actions = build_plan(config, skip_services=True)

        self.assertFalse(any(action.id == "install-code-server" for action in actions))

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
            self.assertEqual(manifest["changed"][0]["status"], "updated")
            self.assertEqual(manifest["changed"][1]["status"], "created")
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
            self.assertEqual(manifest["changed"][-1]["status"], "removed")
            self.assertTrue(Path(manifest["pruned"][0]["backup"]).exists())

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

            self.assertEqual(manifest["changed"], [])

            removed = uninstall_from_manifest(manifest_path=manifest_path, managed_roots=(root,))

            self.assertEqual(removed, 1)
            self.assertFalse(managed.exists())
            self.assertTrue(unmanaged.exists())

    def test_ensure_file_preserves_existing_secret_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            target = root / "secret.toml"
            manifest_path = root / "state" / "install" / "manifest.json"
            backup_root = root / "state" / "backups"
            target.write_text("token = \"real\"\n", encoding="utf-8")

            manifest = apply_plan(
                [
                    Action(
                        id="secret",
                        kind="ensure_file",
                        target=target,
                        description="secret config",
                        content="token = \"\"\n",
                        mode=0o600,
                    ),
                ],
                manifest_path=manifest_path,
                backup_root=backup_root,
                managed_roots=(root,),
            )

            self.assertEqual(target.read_text(encoding="utf-8"), "token = \"real\"\n")
            self.assertEqual(target.stat().st_mode & 0o777, 0o600)
            self.assertEqual(manifest["skipped"][0]["reason"], "exists")

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
        self.assertIn("kk launcher", result.stderr)

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

    def test_codex_skill_descriptions_stay_within_cli_limit(self) -> None:
        for path in (ROOT / "packs" / "codex" / "skills").rglob("SKILL.md"):
            lines = path.read_text(encoding="utf-8").splitlines()
            if not lines or lines[0] != "---":
                self.fail(f"{path} is missing YAML frontmatter")
            try:
                end = lines.index("---", 1)
            except ValueError:
                self.fail(f"{path} has unterminated YAML frontmatter")
            description = ""
            for line in lines[1:end]:
                if line.startswith("description:"):
                    description = line.split(":", 1)[1].strip().strip('"').strip("'")
                    break
            self.assertTrue(description, f"{path} is missing a description")
            self.assertLessEqual(len(description), 500, f"{path} description exceeds Codex CLI limit")


if __name__ == "__main__":
    unittest.main()
