from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest import mock

from klimkit.install import (
    Action,
    TAILSCALE_SERVE_SKIPPED_EXIT,
    apply_plan,
    build_plan,
    capture_code_server_profile,
    code_server_extension_ids,
    default_config,
    installed_code_server_extension_ids,
    parse_config,
    render_config,
    uninstall_from_manifest,
)


ROOT = Path(__file__).resolve().parents[1]


class KlimkitInstallTests(unittest.TestCase):
    def test_default_config_is_first_vm_with_client_and_server(self) -> None:
        config = replace(default_config(), repo_root=Path("/tmp/klimkit"))

        parsed = parse_config(render_config(config))

        self.assertEqual(parsed.profile, "server")
        self.assertEqual(parsed.human_name, "Human")
        self.assertTrue(parsed.client_enabled)
        self.assertTrue(parsed.server_enabled)
        self.assertEqual(parsed.repo_root, Path("/tmp/klimkit"))
        self.assertTrue(parsed.switchboard_enabled)
        self.assertTrue(parsed.switchboard_agent_enabled)
        self.assertTrue(parsed.live_sync_enabled)
        self.assertEqual(parsed.live_sync_interval_seconds, 5)
        self.assertEqual(parsed.live_sync_ref, "origin/main")
        self.assertTrue(parsed.install_code_server_if_missing)
        self.assertTrue(parsed.code_server_managed_profile)
        self.assertEqual(parsed.state_dir, ROOT / ".klimkit" / "state")
        self.assertIn("only human-edited Klimkit config", render_config(config))
        self.assertIn("auto_sync = true", render_config(config))
        self.assertIn("switchboard_agent = true", render_config(config))
        self.assertIn("auto_sync_interval_seconds = 5", render_config(config))
        self.assertIn('human_name = "Human"', render_config(config))
        self.assertIn("enable = true", render_config(config))
        self.assertIn("[switchboard.server]", render_config(config))
        self.assertIn("[notifications.telegram]", render_config(config))

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
        self.assertTrue(config.live_sync_enabled)
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

    def test_switchboard_nested_config_loads_single_toml(self) -> None:
        config = parse_config(
            "\n".join(
                [
                    "[switchboard.server]",
                    "enabled = true",
                    'base_path = "/switchboard"',
                    'auth_token = "server-secret"',
                    "",
                    "[switchboard.agent]",
                    "enabled = true",
                    'backend_url = "https://server.example.ts.net/switchboard"',
                    "",
                ]
            )
        )

        self.assertEqual(config.switchboard_backend_url, "https://server.example.ts.net/switchboard")
        self.assertEqual(config.switchboard_base_path, "/switchboard")
        self.assertEqual(config.switchboard_auth_token, "server-secret")

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

    def test_build_plan_writes_single_klimkit_toml_only(self) -> None:
        config = replace(default_config(), repo_root=ROOT)

        actions = build_plan(config, skip_services=True)

        self.assertTrue(any(action.id == "klimkit-config" for action in actions))
        self.assertFalse(any(action.id == "switchboard-config" for action in actions))
        self.assertFalse(any(action.id == "switchboard-agent-config" for action in actions))
        config_action = next(action for action in actions if action.id == "klimkit-config")
        self.assertEqual(config_action.mode, 0o600)
        self.assertIn("[switchboard.server]", config_action.content or "")
        self.assertIn("[switchboard.agent]", config_action.content or "")

    def test_codex_pack_projects_human_name_template(self) -> None:
        config = replace(default_config(), repo_root=ROOT, human_name="Ada")

        actions = build_plan(config, skip_services=True)
        agents_action = next(action for action in actions if action.id == "codex-agents-md")
        skill_action = next(action for action in actions if action.id.endswith("harness-tuning/SKILL.md"))

        self.assertIsNotNone(agents_action.content)
        self.assertIsNotNone(skill_action.content)
        assert agents_action.content is not None
        assert skill_action.content is not None
        self.assertIn("You're Ada's coding agent.", agents_action.content)
        self.assertIn("Before returning to Ada", agents_action.content)
        self.assertIn("when Ada asks", skill_action.content)
        self.assertNotIn("__HUMAN_NAME__", agents_action.content)
        self.assertNotIn("Klim's coding agent", agents_action.content)

    def test_single_config_uses_private_backend_settings(self) -> None:
        config = replace(
            default_config("client"),
            switchboard_agent_enabled=True,
            switchboard_backend_url="https://server.example.ts.net/switchboard",
            switchboard_auth_token="secret",
        )

        content = render_config(config)

        self.assertIn('backend_url = "https://server.example.ts.net/switchboard"', content)
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

    def test_code_server_user_settings_are_managed_by_default(self) -> None:
        config = replace(default_config("client"), repo_root=ROOT)

        with mock.patch("klimkit.install.shutil.which", return_value="/usr/bin/code-server"):
            actions = build_plan(config, skip_services=True)

        settings_action = next(
            action for action in actions if action.id == "code-server-user:settings.json"
        )
        keybindings_action = next(
            action for action in actions if action.id == "code-server-user:keybindings.json"
        )

        self.assertEqual(settings_action.kind, "write_file")
        self.assertEqual(keybindings_action.kind, "write_file")

    def test_code_server_user_settings_can_be_seed_only(self) -> None:
        config = replace(default_config("client"), repo_root=ROOT, code_server_managed_profile=False)

        with mock.patch("klimkit.install.shutil.which", return_value="/usr/bin/code-server"):
            actions = build_plan(config, skip_services=True)

        settings_action = next(
            action for action in actions if action.id == "code-server-user:settings.json"
        )
        keybindings_action = next(
            action for action in actions if action.id == "code-server-user:keybindings.json"
        )

        self.assertEqual(settings_action.kind, "ensure_file")
        self.assertEqual(keybindings_action.kind, "ensure_file")

    def test_seed_only_code_server_profile_preserves_existing_user_preferences(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            home = root / "home"
            config_path = home / ".klimkit" / "config.toml"
            manifest_path = home / ".klimkit" / "state" / "install" / "manifest.json"
            backup_root = home / ".klimkit" / "backups"
            settings = home / ".local" / "share" / "code-server" / "User" / "settings.json"
            settings.parent.mkdir(parents=True)
            settings.write_text(
                json.dumps(
                    {
                        "workbench.colorTheme": "Default Dark Modern",
                        "minipam.enabled": False,
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            before = settings.read_text(encoding="utf-8")
            config = replace(
                default_config("client"),
                repo_root=ROOT,
                codex_enabled=False,
                code_server_managed_profile=False,
                install_code_server_if_missing=False,
            )

            with (
                mock.patch("klimkit.install.Path.home", return_value=home),
                mock.patch("klimkit.install.shutil.which", return_value="/usr/bin/code-server"),
            ):
                actions = build_plan(config, skip_services=True, config_path=config_path)
                manifest = apply_plan(
                    actions,
                    manifest_path=manifest_path,
                    backup_root=backup_root,
                    managed_roots=(home,),
                )

            self.assertEqual(settings.read_text(encoding="utf-8"), before)
            self.assertTrue(
                (home / ".local" / "share" / "code-server" / "User" / "keybindings.json").exists()
            )
            self.assertIn({"target": str(settings), "reason": "exists"}, manifest["skipped"])

    def test_managed_code_server_profile_installs_extensions(self) -> None:
        config = replace(default_config("client"), repo_root=ROOT)

        with mock.patch("klimkit.install.shutil.which", return_value="/usr/bin/code-server"):
            actions = build_plan(config, skip_services=True)

        extension_ids = code_server_extension_ids(ROOT)
        extension_action = next(action for action in actions if action.id == "code-server-extensions")

        self.assertGreaterEqual(len(extension_ids), 1)
        self.assertEqual(extension_action.kind, "run_command")
        self.assertIn("klimkit.tools.code_server_profile", " ".join(extension_action.command))

    def test_capture_code_server_profile_copies_settings_and_extension_ids(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            user_dir = root / "live" / "User"
            extensions_root = root / "live" / "extensions"
            user_dir.mkdir(parents=True)
            extensions_root.mkdir(parents=True)
            (user_dir / "settings.json").write_text(
                json.dumps({"workbench.colorTheme": "Dark 2026", "editor.minimap.enabled": False}) + "\n",
                encoding="utf-8",
            )
            (user_dir / "keybindings.json").write_text("[]\n", encoding="utf-8")
            package_json = extensions_root / "publisher.example-1.2.3" / "package.json"
            package_json.parent.mkdir()
            package_json.write_text(
                json.dumps({"publisher": "publisher", "name": "example"}),
                encoding="utf-8",
            )

            result = capture_code_server_profile(root, user_dir=user_dir, extensions_root=extensions_root)

            captured_settings = root / "templates" / "code-server" / "User" / "settings.json"
            captured_extensions = root / "templates" / "code-server" / "extensions.txt"
            self.assertEqual(json.loads(captured_settings.read_text(encoding="utf-8"))["workbench.colorTheme"], "Dark 2026")
            self.assertEqual(captured_extensions.read_text(encoding="utf-8"), "publisher.example\n")
            self.assertEqual(result["extensions"], ["publisher.example"])
            self.assertEqual(installed_code_server_extension_ids(extensions_root), ["publisher.example"])

    def test_client_plan_configures_tailscale_serve_for_code_server(self) -> None:
        config = replace(default_config("client"), configure_services=True)

        with mock.patch("klimkit.install.shutil.which", return_value="/usr/bin/code-server"):
            actions = build_plan(config, skip_services=False)

        serve_action = next(action for action in actions if action.id == "tailscale-serve-code-server")
        self.assertEqual(serve_action.kind, "run_command")
        command = " ".join(serve_action.command)
        self.assertIn("tailscale serve --bg --yes --set-path / http://127.0.0.1:8080", command)
        self.assertIn("sudo tailscale set --operator=$USER", command)
        self.assertIn("exit 78", command)
        self.assertFalse(any(action.id == "tailscale-serve-switchboard" for action in actions))

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

    def test_apply_prunes_legacy_home_agents_md_only_when_hash_matches(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            home = Path(tmpdir)
            legacy_agents = home / "AGENTS.md"
            manifest_path = home / ".klimkit" / "state" / "install" / "manifest.json"
            backup_root = home / ".klimkit" / "backups"
            legacy_agents.write_text("old managed guidance\n", encoding="utf-8")
            legacy_hash = self._sha256(legacy_agents)
            manifest_path.parent.mkdir(parents=True)
            manifest_path.write_text(
                json.dumps(
                    {
                        "version": 1,
                        "actions": [
                            {
                                "id": "codex-agents-md",
                                "kind": "write_file",
                                "target": str(legacy_agents),
                                "hash": legacy_hash,
                            }
                        ],
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            with mock.patch("klimkit.install.Path.home", return_value=home):
                manifest = apply_plan([], manifest_path=manifest_path, backup_root=backup_root)

            self.assertFalse(legacy_agents.exists())
            self.assertEqual(manifest["pruned"][0]["target"], str(legacy_agents))

            legacy_agents.write_text("user guidance\n", encoding="utf-8")
            manifest_path.write_text(
                json.dumps(
                    {
                        "version": 1,
                        "actions": [
                            {
                                "id": "codex-agents-md",
                                "kind": "write_file",
                                "target": str(legacy_agents),
                                "hash": legacy_hash,
                            }
                        ],
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            with mock.patch("klimkit.install.Path.home", return_value=home):
                manifest = apply_plan([], manifest_path=manifest_path, backup_root=backup_root)

            self.assertTrue(legacy_agents.exists())
            self.assertEqual(manifest["skipped"][0]["reason"], "modified")

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

    def test_linux_service_plan_reloads_enables_and_restarts(self) -> None:
        config = replace(
            default_config("server"),
            repo_root=ROOT,
            codex_enabled=False,
            code_server_enabled=False,
            supervisor_enabled=True,
            configure_services=True,
        )

        with mock.patch("klimkit.install.platform.system", return_value="Linux"):
            actions = build_plan(config, config_path=Path("/tmp/klimkit.toml"))

        service_commands = [action for action in actions if action.component == "service" and action.kind == "run_command"]
        self.assertEqual([action.id for action in service_commands], [
            "systemd-daemon-reload",
            "systemd-enable-klimkit",
            "systemd-restart-klimkit",
        ])
        self.assertEqual(service_commands[0].command, ("systemctl", "--user", "daemon-reload"))
        self.assertEqual(service_commands[1].command, ("systemctl", "--user", "enable", "klimkit.service"))
        self.assertEqual(service_commands[2].command, ("systemctl", "--user", "restart", "klimkit.service"))

    def test_linux_service_plan_can_defer_restart_for_daemon_autosync(self) -> None:
        config = replace(
            default_config("server"),
            repo_root=ROOT,
            codex_enabled=False,
            code_server_enabled=False,
            supervisor_enabled=True,
            configure_services=True,
        )

        with mock.patch("klimkit.install.platform.system", return_value="Linux"):
            actions = build_plan(config, config_path=Path("/tmp/klimkit.toml"), restart_services=False)

        service_commands = [action for action in actions if action.component == "service" and action.kind == "run_command"]
        self.assertEqual([action.id for action in service_commands], [
            "systemd-daemon-reload",
            "systemd-enable-klimkit",
        ])

    def test_apply_plan_records_run_commands_as_live_actions(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            manifest_path = root / "state" / "install" / "manifest.json"
            backup_root = root / "backups"

            with mock.patch("klimkit.install.subprocess.run") as run_mock:
                manifest = apply_plan(
                    [
                        Action(
                            id="systemd-restart-klimkit",
                            kind="run_command",
                            target=Path("systemctl"),
                            description="restart Klimkit user service",
                            command=("systemctl", "--user", "restart", "klimkit.service"),
                            component="service",
                        )
                    ],
                    manifest_path=manifest_path,
                    backup_root=backup_root,
                    managed_roots=(root,),
                )

            run_mock.assert_called_once_with(["systemctl", "--user", "restart", "klimkit.service"], check=True)
            self.assertEqual(manifest["actions"][0]["status"], "ran")
            self.assertEqual(manifest["actions"][0]["description"], "restart Klimkit user service")
            self.assertEqual(manifest["actions"][0]["component"], "service")

    def test_apply_plan_records_tailscale_serve_permission_skip(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            manifest_path = root / "state" / "install" / "manifest.json"
            backup_root = root / "backups"

            with mock.patch("klimkit.install.subprocess.run") as run_mock:
                run_mock.side_effect = subprocess.CalledProcessError(
                    TAILSCALE_SERVE_SKIPPED_EXIT,
                    ["sh", "-c", "tailscale serve"],
                )
                manifest = apply_plan(
                    [
                        Action(
                            id="tailscale-serve-code-server",
                            kind="run_command",
                            target=Path("tailscale"),
                            description="configure Tailscale Serve for code-server",
                            command=("sh", "-c", "tailscale serve"),
                            component="tailscale",
                        )
                    ],
                    manifest_path=manifest_path,
                    backup_root=backup_root,
                    managed_roots=(root,),
                )

            self.assertEqual(manifest["actions"][0]["status"], "skipped")
            self.assertEqual(
                manifest["actions"][0]["reason"],
                "tailscale serve operator permission required",
            )
            self.assertIn("sudo tailscale set --operator=$USER", manifest["actions"][0]["message"])

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

    @staticmethod
    def _sha256(path: Path) -> str:
        import hashlib

        return hashlib.sha256(path.read_bytes()).hexdigest()


if __name__ == "__main__":
    unittest.main()
