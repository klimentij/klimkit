from __future__ import annotations

import datetime as dt
import json
import os
import platform
import shlex
import shutil
import subprocess
import textwrap
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib

from .harnesses.codex import codex_harness
from .paths import (
    KLIMKIT_BACKUPS_DIR,
    KLIMKIT_CONFIG_FILE,
    KLIMKIT_MANIFEST_FILE,
    KLIMKIT_LOGS_DIR,
    KLIMKIT_STATE_DIR,
    OPS_REPO_ROOT,
)


CONFIG_MODE = 0o600
FILE_MODE = 0o644
EXEC_MODE = 0o755


@dataclass(frozen=True)
class InstallConfig:
    profile: str
    repo_root: Path
    client_enabled: bool
    server_enabled: bool
    codex_enabled: bool
    code_server_enabled: bool
    supervisor_enabled: bool
    live_sync_enabled: bool
    switchboard_agent_enabled: bool
    switchboard_enabled: bool
    configure_services: bool
    install_code_server_if_missing: bool
    tailscale_serve_enabled: bool
    state_dir: Path
    backups_dir: Path
    logs_dir: Path
    switchboard_backend_url: str
    switchboard_host: str
    switchboard_port: int
    switchboard_base_path: str
    switchboard_secure_auth_cookie: bool
    switchboard_auth_token: str
    switchboard_agent_helper_host: str
    switchboard_agent_helper_port: int
    switchboard_agent_interval_seconds: int
    switchboard_agent_heartbeat_seconds: int
    switchboard_collector_interval_seconds: float
    switchboard_heartbeat_seconds: int
    switchboard_max_session_age_days: int
    switchboard_stale_after_seconds: int
    telegram_enabled: bool
    telegram_bot_token: str
    telegram_chat_id: str
    trusted_codex_launch_bypass_sandbox: bool


@dataclass(frozen=True)
class Action:
    id: str
    kind: str
    target: Path
    description: str
    source: Path | None = None
    content: str | None = None
    mode: int = FILE_MODE
    command: tuple[str, ...] = ()
    component: str = "core"


def expand_path(value: str) -> Path:
    return Path(value).expanduser()


def _normalized_switchboard_config_path(path: Path) -> Path:
    legacy_name = "switchboard" + "2.toml"
    if path.name == legacy_name:
        return path.with_name("switchboard.toml")
    return path


def _normalized_switchboard_base_path(value: str) -> str:
    base_path = value.strip() or "/switchboard"
    if not base_path.startswith("/"):
        base_path = "/" + base_path
    legacy_path = "/switchboard" + "2"
    if base_path.rstrip("/") == legacy_path:
        return "/switchboard"
    return base_path.rstrip("/") or "/switchboard"


def _normalized_switchboard_backend_url(value: str) -> str:
    backend_url = value.strip().rstrip("/")
    legacy_suffix = "/switchboard" + "2"
    if backend_url.endswith(legacy_suffix):
        return backend_url[: -len(legacy_suffix)] + "/switchboard"
    return backend_url


def _role_flags(profile: str) -> tuple[bool, bool]:
    role = profile.strip().lower().replace("_", "-") or "first-vm"
    if role in {"client", "client-only", "second-vm", "second"}:
        return True, False
    if role in {"server-only", "central-only"}:
        return False, True
    return True, True


def _profile_from_roles(*, client_enabled: bool, server_enabled: bool) -> str:
    if server_enabled:
        return "server"
    if client_enabled:
        return "client"
    return "custom"


def default_config(profile: str = "first-vm") -> InstallConfig:
    client_enabled, server_enabled = _role_flags(profile)
    return InstallConfig(
        profile=_profile_from_roles(client_enabled=client_enabled, server_enabled=server_enabled),
        repo_root=OPS_REPO_ROOT,
        client_enabled=client_enabled,
        server_enabled=server_enabled,
        codex_enabled=client_enabled,
        code_server_enabled=client_enabled,
        supervisor_enabled=client_enabled or server_enabled,
        live_sync_enabled=False,
        switchboard_agent_enabled=client_enabled and not server_enabled,
        switchboard_enabled=server_enabled,
        configure_services=True,
        install_code_server_if_missing=client_enabled,
        tailscale_serve_enabled=True,
        state_dir=KLIMKIT_STATE_DIR,
        backups_dir=KLIMKIT_BACKUPS_DIR,
        logs_dir=KLIMKIT_LOGS_DIR,
        switchboard_backend_url="",
        switchboard_host="127.0.0.1",
        switchboard_port=4721,
        switchboard_base_path="/switchboard",
        switchboard_secure_auth_cookie=False,
        switchboard_auth_token="",
        switchboard_agent_helper_host="127.0.0.1",
        switchboard_agent_helper_port=4632,
        switchboard_agent_interval_seconds=5,
        switchboard_agent_heartbeat_seconds=60,
        switchboard_collector_interval_seconds=0.5,
        switchboard_heartbeat_seconds=15,
        switchboard_max_session_age_days=14,
        switchboard_stale_after_seconds=180,
        telegram_enabled=False,
        telegram_bot_token="",
        telegram_chat_id="",
        trusted_codex_launch_bypass_sandbox=True,
    )


def with_role(config: InstallConfig, profile: str) -> InstallConfig:
    role = default_config(profile)
    return replace(
        config,
        profile=role.profile,
        client_enabled=role.client_enabled,
        server_enabled=role.server_enabled,
        codex_enabled=role.codex_enabled,
        code_server_enabled=role.code_server_enabled,
        supervisor_enabled=role.supervisor_enabled,
        live_sync_enabled=role.live_sync_enabled,
        switchboard_agent_enabled=role.switchboard_agent_enabled,
        switchboard_enabled=role.switchboard_enabled,
        install_code_server_if_missing=role.install_code_server_if_missing,
    )


def render_config(config: InstallConfig) -> str:
    return "\n".join(
        [
            "# Klimkit local machine config.",
            "# Edit this file, then run `kk preview` or `kk apply`.",
            "# This is the only human-edited Klimkit config; other files are generated projections.",
            "",
            "[paths]",
            "# Repo checkout Klimkit should apply from.",
            f'repo_root = "{config.repo_root}"',
            "# Runtime state for manifests, DBs, and local process state.",
            f"state_dir = {json.dumps(str(config.state_dir))}",
            "# Backups created before Klimkit updates managed files.",
            f"backups_dir = {json.dumps(str(config.backups_dir))}",
            "# Logs written by the Klimkit supervisor and helpers.",
            f"logs_dir = {json.dumps(str(config.logs_dir))}",
            "",
            "[components]",
            "# Client installs local agent harness assets and code-server support.",
            f"client = {str(config.client_enabled).lower()}",
            "# Server runs the central Switchboard on this machine.",
            f"server = {str(config.server_enabled).lower()}",
            "# Supervisor runs `kk daemon`; services.enable controls login/boot startup.",
            f"supervisor = {str(config.supervisor_enabled).lower()}",
            "",
            "[workers]",
            "# live_sync: periodically fetch Git and copy Codex assets. Default false; use `kk pull` instead.",
            f"live_sync = {str(config.live_sync_enabled).lower()}",
            "# switchboard_agent: report this VM to a central Switchboard. Requires switchboard.backend_url.",
            f"switchboard_agent = {str(config.switchboard_agent_enabled).lower()}",
            "",
            "[services]",
            "# enable: install/start the systemd or launchd service for the Klimkit supervisor.",
            f"enable = {str(config.configure_services).lower()}",
            "",
            "[code_server]",
            "# Enable projection of code-server config and user settings.",
            f"enabled = {str(config.code_server_enabled).lower()}",
            "# If code-server is missing, `kk apply` may run the upstream network installer.",
            f"install_if_missing = {str(config.install_code_server_if_missing).lower()}",
            "",
            "[tailscale]",
            "# Configure Tailscale Serve for browser access from the private tailnet.",
            f"configure_serve = {str(config.tailscale_serve_enabled).lower()}",
            "",
            "[harnesses.codex]",
            "# Enable Codex pack projection into the default ~/.codex home.",
            f"enabled = {str(config.codex_enabled).lower()}",
            "",
            "[switchboard.server]",
            "# Enable the central Switchboard web UI and API on this machine.",
            f"enabled = {str(config.switchboard_enabled).lower()}",
            "# Loopback is safe without a token; non-loopback hosts require auth_token.",
            f"host = {json.dumps(config.switchboard_host)}",
            f"port = {config.switchboard_port}",
            f"base_path = {json.dumps(config.switchboard_base_path)}",
            "# Set true when Switchboard is exposed through HTTPS and browser cookies should require it.",
            f"secure_auth_cookie = {str(config.switchboard_secure_auth_cookie).lower()}",
            "# Bearer token for remote Switchboard API/UI access.",
            f"auth_token = {json.dumps(config.switchboard_auth_token)}",
            "# Collector interval controls how often local Codex state is read.",
            f"collector_interval_seconds = {config.switchboard_collector_interval_seconds}",
            f"heartbeat_seconds = {config.switchboard_heartbeat_seconds}",
            f"max_session_age_days = {config.switchboard_max_session_age_days}",
            f"stale_after_seconds = {config.switchboard_stale_after_seconds}",
            "",
            "[switchboard.agent]",
            "# Enable this VM to report local Codex sessions to the central Switchboard.",
            f"enabled = {str(config.switchboard_agent_enabled).lower()}",
            "# Central Switchboard URL, for example https://server.example.ts.net/switchboard.",
            f"backend_url = {json.dumps(config.switchboard_backend_url)}",
            "# Shared bearer token for agent-to-server reporting.",
            f"auth_token = {json.dumps(config.switchboard_auth_token)}",
            f"interval_seconds = {config.switchboard_agent_interval_seconds}",
            f"heartbeat_seconds = {config.switchboard_agent_heartbeat_seconds}",
            f"max_session_age_days = {config.switchboard_max_session_age_days}",
            "# Helper is loopback by default; expose another host only for a trusted proxy.",
            f"helper_host = {json.dumps(config.switchboard_agent_helper_host)}",
            f"helper_port = {config.switchboard_agent_helper_port}",
            "",
            "[notifications.telegram]",
            "# Telegram notifications are optional and read by the Codex Stop hook.",
            f"enabled = {str(config.telegram_enabled).lower()}",
            f"bot_token = {json.dumps(config.telegram_bot_token)}",
            f"chat_id = {json.dumps(config.telegram_chat_id)}",
            "",
            "[trusted_local_agent_launch]",
            "# Switchboard-launched Codex terminals are trusted-local automation by default.",
            f"bypass_codex_approvals_and_sandbox = {str(config.trusted_codex_launch_bypass_sandbox).lower()}",
            "",
        ]
    )


def render_switchboard_config(config: InstallConfig) -> str:
    return "\n".join(
        [
            "# Klimkit Switchboard config.",
            "# This file is local because it may contain backend.auth_token.",
            "",
            "[paths]",
            f"state_dir = {json.dumps(str(config.state_dir / 'switchboard'))}",
            f"sessions_root = {json.dumps(str(Path.home() / '.codex' / 'sessions'))}",
            f"session_index = {json.dumps(str(Path.home() / '.codex' / 'session_index.jsonl'))}",
            f"hooks_events = {json.dumps(str(Path.home() / '.codex' / 'switchboard' / 'events.jsonl'))}",
            "",
            "[server]",
            "enabled = true",
            f"host = {json.dumps(config.switchboard_host)}",
            f"port = {config.switchboard_port}",
            f"base_path = {json.dumps(config.switchboard_base_path)}",
            "",
            "[backend]",
            "base_url = \"\"",
            "timeout_seconds = 10",
            f"auth_token = {json.dumps(config.switchboard_auth_token)}",
            "",
            "[collector]",
            "enabled = true",
            "interval_seconds = 0.5",
            "heartbeat_seconds = 15",
            "max_session_age_days = 14",
            "stale_after_seconds = 180",
            "",
            "[machine]",
            "id = \"\"",
            "dns_name = \"\"",
            "",
        ]
    )


def render_switchboard_agent_config(config: InstallConfig) -> str:
    return "\n".join(
        [
            "# Klimkit Switchboard agent config.",
            "# This file is local because it may contain backend.auth_token.",
            "",
            "[paths]",
            f"sessions_root = {json.dumps(str(Path.home() / '.codex' / 'sessions'))}",
            f"session_index = {json.dumps(str(Path.home() / '.codex' / 'session_index.jsonl'))}",
            f"state_dir = {json.dumps(str(config.state_dir / 'switchboard-agent'))}",
            "",
            "[backend]",
            f"base_url = {json.dumps(config.switchboard_backend_url)}",
            f"auth_token = {json.dumps(config.switchboard_auth_token)}",
            "timeout_seconds = 15",
            "",
            "[agent]",
            "interval_seconds = 5",
            "heartbeat_seconds = 60",
            "max_session_age_days = 14",
            "",
            "[helper]",
            "enabled = true",
            "port = 4632",
            "",
        ]
    )


def _bool(raw: Any, default: bool) -> bool:
    if raw is None:
        return default
    if isinstance(raw, bool):
        return raw
    return str(raw).strip().lower() in {"1", "true", "yes", "on"}


def parse_config(raw: str) -> InstallConfig:
    data = tomllib.loads(raw) if raw.strip() else {}
    paths = data.get("paths", {})
    machine = data.get("machine", {})
    components = data.get("components", {})
    workers = data.get("workers", {})
    services = data.get("services", {})
    code_server = data.get("code_server", {})
    tailscale = data.get("tailscale", {})
    harnesses = data.get("harnesses", {})
    codex = harnesses.get("codex", {}) if isinstance(harnesses.get("codex", {}), dict) else {}
    switchboard = data.get("switchboard", {})
    switchboard_server = switchboard.get("server", {}) if isinstance(switchboard.get("server", {}), dict) else {}
    switchboard_agent = switchboard.get("agent", {}) if isinstance(switchboard.get("agent", {}), dict) else {}
    notifications = data.get("notifications", {})
    telegram = notifications.get("telegram", {}) if isinstance(notifications.get("telegram", {}), dict) else {}
    trusted_launch = data.get("trusted_local_agent_launch", {})
    role = str(machine.get("profile", "first-vm")).strip() or "first-vm"
    default_client_enabled, default_server_enabled = _role_flags(role)
    client_enabled = _bool(components.get("client"), default_client_enabled)
    server_enabled = _bool(components.get("server"), default_server_enabled)
    state_dir = expand_path(str(paths.get("state_dir", KLIMKIT_STATE_DIR)))
    server_enabled_default = _bool(components.get("switchboard"), server_enabled)
    agent_enabled_default = _bool(workers.get("switchboard_agent"), client_enabled and not server_enabled)
    auth_token = str(
        switchboard_agent.get(
            "auth_token",
            switchboard_server.get("auth_token", switchboard.get("auth_token", "")),
        )
    ).strip()
    return InstallConfig(
        profile=_profile_from_roles(client_enabled=client_enabled, server_enabled=server_enabled),
        repo_root=expand_path(str(paths.get("repo_root", machine.get("repo_root", OPS_REPO_ROOT)))),
        client_enabled=client_enabled,
        server_enabled=server_enabled,
        codex_enabled=_bool(codex.get("enabled", components.get("codex")), client_enabled),
        code_server_enabled=_bool(code_server.get("enabled", components.get("code_server")), client_enabled),
        supervisor_enabled=_bool(components.get("supervisor"), client_enabled or server_enabled),
        live_sync_enabled=_bool(workers.get("live_sync"), False),
        switchboard_agent_enabled=_bool(switchboard_agent.get("enabled"), agent_enabled_default),
        switchboard_enabled=_bool(switchboard_server.get("enabled"), server_enabled_default),
        configure_services=_bool(services.get("enable", services.get("configure")), True),
        install_code_server_if_missing=_bool(
            code_server.get("install_if_missing"), client_enabled
        ),
        tailscale_serve_enabled=_bool(
            tailscale.get("configure_serve"), True
        ),
        state_dir=state_dir,
        backups_dir=expand_path(str(paths.get("backups_dir", KLIMKIT_BACKUPS_DIR))),
        logs_dir=expand_path(str(paths.get("logs_dir", KLIMKIT_LOGS_DIR))),
        switchboard_backend_url=_normalized_switchboard_backend_url(
            str(switchboard_agent.get("backend_url", switchboard.get("backend_url", "")))
        ),
        switchboard_host=str(switchboard_server.get("host", switchboard.get("host", "127.0.0.1"))).strip()
        or "127.0.0.1",
        switchboard_port=max(1, int(switchboard_server.get("port", switchboard.get("port", 4721)))),
        switchboard_base_path=_normalized_switchboard_base_path(
            str(switchboard_server.get("base_path", switchboard.get("base_path", "/switchboard")))
        ),
        switchboard_secure_auth_cookie=_bool(switchboard_server.get("secure_auth_cookie"), False),
        switchboard_auth_token=auth_token,
        switchboard_agent_helper_host=str(switchboard_agent.get("helper_host", "127.0.0.1")).strip()
        or "127.0.0.1",
        switchboard_agent_helper_port=max(1, int(switchboard_agent.get("helper_port", 4632))),
        switchboard_agent_interval_seconds=max(1, int(switchboard_agent.get("interval_seconds", 5))),
        switchboard_agent_heartbeat_seconds=max(5, int(switchboard_agent.get("heartbeat_seconds", 60))),
        switchboard_collector_interval_seconds=max(
            0.1, float(switchboard_server.get("collector_interval_seconds", 0.5))
        ),
        switchboard_heartbeat_seconds=max(5, int(switchboard_server.get("heartbeat_seconds", 15))),
        switchboard_max_session_age_days=max(
            1,
            int(
                switchboard_server.get(
                    "max_session_age_days",
                    switchboard_agent.get("max_session_age_days", 14),
                )
            ),
        ),
        switchboard_stale_after_seconds=max(30, int(switchboard_server.get("stale_after_seconds", 180))),
        telegram_enabled=_bool(telegram.get("enabled"), False),
        telegram_bot_token=str(telegram.get("bot_token", "")).strip(),
        telegram_chat_id=str(telegram.get("chat_id", "")).strip(),
        trusted_codex_launch_bypass_sandbox=_bool(
            trusted_launch.get("bypass_codex_approvals_and_sandbox"), True
        ),
    )


def ensure_config(path: Path = KLIMKIT_CONFIG_FILE, *, profile: str = "first-vm") -> tuple[InstallConfig, bool]:
    path = path.expanduser()
    if path.exists():
        path.chmod(CONFIG_MODE)
        return parse_config(path.read_text(encoding="utf-8")), False
    config = default_config(profile)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_config(config), encoding="utf-8")
    path.chmod(CONFIG_MODE)
    return config, True


def load_config(path: Path = KLIMKIT_CONFIG_FILE) -> InstallConfig:
    return parse_config(path.expanduser().read_text(encoding="utf-8"))


def validate_config(config: InstallConfig) -> list[str]:
    errors: list[str] = []
    if config.switchboard_agent_enabled and not config.switchboard_backend_url:
        errors.append(
            "[switchboard.agent] enabled = true requires backend_url, "
            "for example https://<first-vm>.<tailnet>.ts.net/switchboard"
        )
    return errors


def _template_text(path: Path, config: InstallConfig, *, config_path: Path = KLIMKIT_CONFIG_FILE) -> str:
    text = path.read_text(encoding="utf-8")
    replacements = {
        "__REPO_ROOT__": str(config.repo_root),
        "__CONFIG_FILE__": str(config_path.expanduser()),
        "__PYTHON_BIN__": shutil.which("python3") or "python3",
        "__UV_BIN__": shutil.which("uv") or "uv",
        "__STATE_DIR__": str(KLIMKIT_STATE_DIR),
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def _file_action(
    action_id: str,
    source: Path,
    target: Path,
    description: str,
    *,
    component: str,
    mode: int = FILE_MODE,
    config: InstallConfig | None = None,
    config_path: Path = KLIMKIT_CONFIG_FILE,
) -> Action:
    content = (
        _template_text(source, config, config_path=config_path)
        if config is not None and source.suffix in {".service", ".plist"}
        else None
    )
    return Action(
        id=action_id,
        kind="write_file",
        source=source,
        target=target,
        description=description,
        component=component,
        mode=mode,
        content=content,
    )


def _dir_actions(
    action_id: str,
    source_root: Path,
    target_root: Path,
    description: str,
    *,
    component: str,
    exclude_prefixes: tuple[str, ...] = (),
) -> list[Action]:
    actions: list[Action] = []
    if not source_root.exists():
        return actions
    for source in sorted(path for path in source_root.rglob("*") if path.is_file()):
        relative = source.relative_to(source_root)
        if any(str(relative).startswith(prefix) for prefix in exclude_prefixes):
            continue
        mode = EXEC_MODE if os.access(source, os.X_OK) else FILE_MODE
        actions.append(
            _file_action(
                f"{action_id}:{relative}",
                source,
                target_root / relative,
                f"{description}: {relative}",
                component=component,
                mode=mode,
            )
        )
    return actions


def build_plan(
    config: InstallConfig,
    *,
    skip_services: bool = False,
    config_path: Path = KLIMKIT_CONFIG_FILE,
) -> list[Action]:
    repo = config.repo_root
    home = Path.home()
    actions: list[Action] = [
        Action(
            id="klimkit-config",
            kind="write_file",
            target=config_path.expanduser(),
            description="Klimkit single source config",
            content=render_config(config),
            mode=CONFIG_MODE,
            component="core",
        )
    ]

    if config.codex_enabled:
        for projection in codex_harness(home=home, repo_root=repo).projections:
            if projection.kind == "file":
                actions.append(
                    _file_action(
                        projection.id,
                        projection.source,
                        projection.target,
                        projection.description,
                        component=projection.component,
                    )
                )
            elif projection.kind == "dir":
                actions.extend(
                    _dir_actions(
                        projection.id,
                        projection.source,
                        projection.target,
                        projection.description,
                        component=projection.component,
                        exclude_prefixes=projection.exclude_prefixes,
                    )
                )

    if config.code_server_enabled:
        actions.append(
            _file_action(
                "code-server-config",
                repo / "templates" / "code-server" / "config.yaml",
                home / ".config" / "code-server" / "config.yaml",
                "code-server config",
                component="code-server",
                mode=CONFIG_MODE,
            )
        )
        actions.extend(
            _dir_actions(
                "code-server-user",
                repo / "templates" / "code-server" / "User",
                home / ".local" / "share" / "code-server" / "User",
                "code-server user settings",
                component="code-server",
            )
        )
        if config.install_code_server_if_missing and shutil.which("code-server") is None:
            actions.append(
                Action(
                    id="install-code-server",
                    kind="run_command",
                    target=Path("code-server"),
                    description="external network installer: code-server upstream script",
                    command=(
                        "sh",
                        "-c",
                        "command -v curl >/dev/null 2>&1 || { echo 'curl is required to install code-server' >&2; exit 1; }; "
                        "curl -fsSL https://code-server.dev/install.sh | sh",
                    ),
                    component="external-installer",
                )
            )

    if config.supervisor_enabled and config.configure_services and not skip_services:
        if platform.system() == "Darwin":
            actions.append(
                _file_action(
                    "launchd-klimkit",
                    source=repo / "templates" / "launchd" / "com.klim.klimkit.plist",
                    target=home / "Library" / "LaunchAgents" / "com.klim.klimkit.plist",
                    description="Klimkit launchd agent",
                    mode=FILE_MODE,
                    component="service",
                    config=config,
                    config_path=config_path,
                )
            )
            actions.append(
                Action(
                    id="launchd-start-klimkit",
                    kind="run_command",
                    target=Path("launchctl"),
                    description="restart Klimkit launchd agent",
                    command=(
                        "sh",
                        "-c",
                        f"launchctl bootout gui/$(id -u) {home}/Library/LaunchAgents/com.klim.klimkit.plist >/dev/null 2>&1 || true; "
                        f"launchctl bootstrap gui/$(id -u) {home}/Library/LaunchAgents/com.klim.klimkit.plist; "
                        f"launchctl kickstart -k gui/$(id -u)/com.klim.klimkit",
                    ),
                    component="service",
                )
            )
        else:
            for source in sorted((repo / "templates" / "systemd" / "user").glob("*.service")):
                actions.append(
                    _file_action(
                        f"systemd:{source.name}",
                        source,
                        home / ".config" / "systemd" / "user" / source.name,
                        f"systemd user unit {source.name}",
                        component="service",
                        config=config,
                        config_path=config_path,
                    )
                )
            actions.append(
                Action(
                    id="systemd-start-klimkit",
                    kind="run_command",
                    target=Path("systemctl"),
                    description="enable and restart Klimkit user service",
                    command=("systemctl", "--user", "enable", "--now", "klimkit.service"),
                    component="service",
                )
            )

    return actions


def render_launchd_plist(config: InstallConfig, *, config_path: Path = KLIMKIT_CONFIG_FILE) -> str:
    template = config.repo_root / "templates" / "launchd" / "com.klim.klimkit.plist"
    return _template_text(template, config, config_path=config_path)


def _ansi(text: str, code: str, *, color: bool) -> str:
    if not color:
        return text
    return f"\033[{code}m{text}\033[0m"


def _ansi_cell(text: str, width: int, code: str, *, color: bool) -> str:
    return _ansi(f"{text:<{width}}", code, color=color)


def _plan_width() -> int:
    columns = shutil.get_terminal_size((104, 20)).columns
    return max(78, min(columns, 108))


def _rule(width: int, *, color: bool) -> str:
    return "  " + _ansi("-" * min(width - 2, 88), "38;2;47;65;56", color=color)


def _component_name(component: str) -> str:
    names = {
        "core": "Core",
        "codex": "Codex",
        "code-server": "Code Server",
        "external-installer": "External Installers",
        "service": "Services",
        "switchboard": "Switchboard",
        "switchboard-agent": "Switchboard Agent",
    }
    return names.get(component, component.replace("-", " ").title())


def _kind_label(action: Action) -> tuple[str, str]:
    labels = {
        "run_command": ("run", "38;2;244;188;103"),
        "manual_step": ("manual", "38;2;240;123;95"),
        "ensure_file": ("ensure", "38;2;119;199;255"),
        "write_file": ("write", "38;2;126;240;175"),
    }
    return labels.get(action.kind, (action.kind, "38;2;166;200;182"))


def _action_detail(action: Action) -> tuple[str, str]:
    if action.kind == "run_command":
        return "$", shlex.join(action.command)
    return "->", str(action.target)


def _detail_lines(prefix: str, value: str, *, width: int, color: bool) -> list[str]:
    indent = " " * 10
    marker_width = 2
    available = max(36, width - len(indent) - marker_width - 1)
    wrapped = textwrap.wrap(
        value,
        width=available,
        break_long_words=False,
        break_on_hyphens=False,
    ) or [""]
    lines = []
    for index, line in enumerate(wrapped):
        marker = prefix if index == 0 else " " * marker_width
        lines.append(f"{indent}{_ansi(marker, '38;2;111;141;126', color=color)} {line}")
    return lines


def _component_groups(actions: list[Action]) -> list[tuple[str, list[Action]]]:
    groups: list[tuple[str, list[Action]]] = []
    by_component: dict[str, list[Action]] = {}
    for action in actions:
        if action.component not in by_component:
            by_component[action.component] = []
            groups.append((action.component, by_component[action.component]))
        by_component[action.component].append(action)
    return groups


def format_plan(
    actions: list[Action],
    *,
    config_path: Path = KLIMKIT_CONFIG_FILE,
    manifest_path: Path = KLIMKIT_MANIFEST_FILE,
    color: bool = False,
) -> str:
    width = _plan_width()
    groups = _component_groups(actions)
    lines = [
        _ansi("Klimkit Setup Preview", "1;38;2;126;240;175", color=color),
        "",
        f"  {'config':<9} {config_path.expanduser()}",
        f"  {'manifest':<9} {manifest_path.expanduser()}",
        f"  {'actions':<9} {len(actions)}",
        "",
        _rule(width, color=color),
        _ansi("Plan", "1;38;2;166;200;182", color=color),
    ]
    if not actions:
        lines.append("  No actions. This machine is already aligned with the current config.")
    for component, component_actions in groups:
        count = len(component_actions)
        suffix = "action" if count == 1 else "actions"
        lines.extend(
            [
                "",
                _rule(width, color=color),
                f"  {_ansi(_component_name(component), '1;38;2;237;255;245', color=color)} "
                f"{_ansi(f'{count} {suffix}', '38;2;111;141;126', color=color)}",
                _rule(width, color=color),
            ]
        )
        for index, action in enumerate(component_actions):
            label, label_color = _kind_label(action)
            detail_prefix, detail_value = _action_detail(action)
            lines.append(f"  {_ansi_cell(label, 7, label_color, color=color)} {action.description}")
            lines.extend(_detail_lines(detail_prefix, detail_value, width=width, color=color))
            if index != len(component_actions) - 1:
                lines.append("")
    return "\n".join(lines) + "\n"


def _hash_file(path: Path) -> str:
    import hashlib

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_manifest(path: Path = KLIMKIT_MANIFEST_FILE) -> dict[str, Any]:
    if not path.exists():
        return {"version": 1, "actions": []}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"version": 1, "actions": []}


def _write_manifest(path: Path, manifest: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _default_delete_roots(home: Path | None = None) -> tuple[Path, ...]:
    home = home or Path.home()
    return (
        home / "AGENTS.md",
        home / ".codex",
        home / ".config" / "code-server",
        home / ".local" / "share" / "code-server" / "User",
        home / ".config" / "systemd" / "user" / "klimkit.service",
        home / "Library" / "LaunchAgents" / "com.klim.klimkit.plist",
    )


def _is_same_or_child(path: Path, root: Path) -> bool:
    path = path.expanduser().absolute()
    root = root.expanduser().absolute()
    return path == root or root in path.parents


def _is_managed_delete_target(path: Path, roots: tuple[Path, ...]) -> bool:
    return any(_is_same_or_child(path, root) for root in roots)


def _manifest_hash_matches(item: dict[str, Any], target: Path) -> bool:
    expected_hash = str(item.get("hash") or "")
    if not expected_hash or not target.exists() or not target.is_file():
        return False
    return _hash_file(target) == expected_hash


def apply_plan(
    actions: list[Action],
    *,
    manifest_path: Path = KLIMKIT_MANIFEST_FILE,
    backup_root: Path | None = None,
    managed_roots: tuple[Path, ...] | None = None,
) -> dict[str, Any]:
    backup_root = (backup_root or KLIMKIT_BACKUPS_DIR) / dt.datetime.now(dt.UTC).strftime(
        "%Y%m%dT%H%M%SZ"
    )
    previous_manifest = _load_manifest(manifest_path)
    planned_targets = {str(action.target.expanduser()) for action in actions if action.kind != "run_command"}
    manifest: dict[str, Any] = {
        "version": 1,
        "applied_at": dt.datetime.now(dt.UTC).isoformat(),
        "actions": [],
        "changed": [],
        "pruned": [],
        "skipped": [],
    }
    delete_roots = managed_roots or _default_delete_roots()
    for action in actions:
        if action.kind == "manual_step":
            manifest["actions"].append(
                {"id": action.id, "kind": action.kind, "target": str(action.target), "description": action.description}
            )
            _write_manifest(manifest_path, manifest)
            continue
        if action.kind == "run_command":
            _write_manifest(manifest_path, manifest)
            subprocess.run(list(action.command), check=True)
            manifest["actions"].append(
                {"id": action.id, "kind": action.kind, "target": str(action.target), "command": list(action.command)}
            )
            _write_manifest(manifest_path, manifest)
            continue
        action.target.parent.mkdir(parents=True, exist_ok=True)
        if action.kind == "ensure_file" and action.target.exists():
            action.target.chmod(action.mode)
            manifest["skipped"].append({"target": str(action.target), "reason": "exists"})
            _write_manifest(manifest_path, manifest)
            continue
        backup = ""
        new_bytes = action.content.encode("utf-8") if action.content is not None else action.source.read_bytes()
        change_status = "created"
        if action.target.exists():
            if action.target.read_bytes() == new_bytes:
                action.target.chmod(action.mode)
                manifest["actions"].append(
                    {
                        "id": action.id,
                        "kind": action.kind,
                        "target": str(action.target),
                        "source": str(action.source or ""),
                        "backup": "",
                        "hash": _hash_file(action.target),
                    }
                )
                _write_manifest(manifest_path, manifest)
                continue
            change_status = "updated"
            backup_path = backup_root / action.target.relative_to(action.target.anchor)
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(action.target, backup_path)
            backup = str(backup_path)
        if action.content is not None:
            action.target.write_text(action.content, encoding="utf-8")
        elif action.source is not None:
            shutil.copy2(action.source, action.target)
        action.target.chmod(action.mode)
        manifest["actions"].append(
            {
                "id": action.id,
                "kind": action.kind,
                "target": str(action.target),
                "source": str(action.source or ""),
                "backup": backup,
                "hash": _hash_file(action.target),
            }
        )
        manifest["changed"].append(
            {
                "target": str(action.target),
                "status": change_status,
                "backup": backup,
            }
        )
        _write_manifest(manifest_path, manifest)
    for item in reversed(previous_manifest.get("actions", [])):
        if item.get("kind") in {"run_command", "manual_step"}:
            continue
        target = Path(str(item.get("target", ""))).expanduser()
        if str(target) in planned_targets or not target.exists() or not target.is_file():
            continue
        if not _is_managed_delete_target(target, delete_roots):
            manifest["skipped"].append({"target": str(target), "reason": "outside-managed-roots"})
            continue
        if not _manifest_hash_matches(item, target):
            manifest["skipped"].append({"target": str(target), "reason": "modified"})
            continue
        backup_path = backup_root / target.relative_to(target.anchor)
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(target, backup_path)
        target.unlink()
        manifest["pruned"].append({"target": str(target), "backup": str(backup_path)})
        manifest["changed"].append({"target": str(target), "status": "removed", "backup": str(backup_path)})
    _write_manifest(manifest_path, manifest)
    return manifest


def uninstall_from_manifest(
    *,
    manifest_path: Path = KLIMKIT_MANIFEST_FILE,
    managed_roots: tuple[Path, ...] | None = None,
) -> int:
    manifest = _load_manifest(manifest_path)
    removed = 0
    delete_roots = managed_roots or _default_delete_roots()
    skipped_targets: set[str] = set()
    for item in reversed(manifest.get("actions", [])):
        if item.get("kind") in {"run_command", "manual_step"}:
            continue
        target = Path(str(item.get("target", ""))).expanduser()
        if target.exists() and target.is_file():
            if not _is_managed_delete_target(target, delete_roots) or not _manifest_hash_matches(item, target):
                skipped_targets.add(str(target))
                continue
            target.unlink()
            removed += 1
    if skipped_targets:
        manifest["actions"] = [
            item
            for item in manifest.get("actions", [])
            if item.get("kind") == "run_command" or str(item.get("target", "")) in skipped_targets
        ]
        manifest["skipped"] = sorted(skipped_targets)
        _write_manifest(manifest_path, manifest)
    elif manifest_path.exists():
        manifest_path.unlink()
    return removed
