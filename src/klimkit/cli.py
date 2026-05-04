from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import socket
import subprocess
import sys
from pathlib import Path

from .install import (
    apply_plan,
    build_plan,
    ensure_config,
    format_plan,
    load_config,
    render_config,
    uninstall_from_manifest,
    validate_config,
    with_role,
)
from .notifications import send_telegram_notification
from .paths import KLIMKIT_CONFIG_FILE, KLIMKIT_MANIFEST_FILE, OPS_REPO_ROOT


EXAMPLES = """examples:
  kk setup
  kk setup --client-only
  kk preview
  kk apply
  kk doctor
  kk serve
  kk update
  kk pull
"""


PALETTE = {
    "accent": "38;2;126;240;175",
    "accent_strong": "38;2;237;255;245",
    "muted": "38;2;111;141;126",
    "muted_strong": "38;2;166;200;182",
    "warn": "38;2;244;188;103",
    "error": "38;2;255;90;107",
    "ok": "38;2;141;220;104",
}


class HelpFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
    pass


def _color_enabled(stream: object | None = None) -> bool:
    stream = stream or sys.stdout
    is_tty = getattr(stream, "isatty", lambda: False)
    return bool(is_tty()) and "KLIMKIT_NO_COLOR" not in os.environ


def _paint(text: str, style: str = "accent", *, stream: object | None = None) -> str:
    if not _color_enabled(stream):
        return text
    code = PALETTE.get(style, style)
    return f"\033[{code}m{text}\033[0m"


def _cell(text: str, width: int, style: str) -> str:
    return _paint(f"{text:<{width}}", style)


def _header(title: str, subtitle: str = "") -> str:
    parts = [_paint("Klimkit", "accent"), _paint("/", "muted"), _paint(title, "accent_strong")]
    lines = [" ".join(parts)]
    if subtitle:
        lines.append(_paint(subtitle, "muted_strong"))
    return "\n".join(lines)


def _section(title: str) -> str:
    return _paint(title, "muted_strong")


def _kv(label: str, value: object) -> str:
    return f"  {_cell(label.lower(), 10, 'muted')} {value}"


def _command_row(command: str, description: str) -> str:
    return f"  {_cell(command, 24, 'accent')} {description}"


def _status(label: str, message: str, style: str = "ok") -> str:
    return f"  {_cell(label, 10, style)} {message}"


def _error(message: str) -> str:
    return f"{_paint('error', 'error', stream=sys.stderr)} {message}"


def _print_apply_blockers(errors: list[str]) -> None:
    print(_error("Apply is blocked until the local config is complete."), file=sys.stderr)
    for error in errors:
        print(f"  {_paint('required', 'warn', stream=sys.stderr)} {error}", file=sys.stderr)


def _print_before_apply(errors: list[str]) -> None:
    if not errors:
        return
    print()
    print(_section("Before Apply"))
    for error in errors:
        print(_status("required", error, "warn"))


def _print_changed_files(manifest: dict[str, object]) -> None:
    changed = manifest.get("changed")
    if not isinstance(changed, list):
        changed = []
    print(_kv("changed", len(changed)))
    if not changed:
        return
    print()
    print(_section("Changed Files"))
    for item in changed:
        if not isinstance(item, dict):
            continue
        status = str(item.get("status", "changed"))
        target = str(item.get("target", ""))
        print(_status(status, target, "ok" if status in {"created", "updated"} else "warn"))


def _run_actions(manifest: dict[str, object]) -> list[dict[str, object]]:
    actions = manifest.get("actions")
    return (
        [
            item
            for item in actions
            if isinstance(item, dict) and item.get("kind") == "run_command" and item.get("status") == "ran"
        ]
        if isinstance(actions, list)
        else []
    )


def _run_status(description: str) -> tuple[str, str]:
    lowered = description.lower()
    if "restart" in lowered:
        return "restarted", "ok"
    if "reload" in lowered:
        return "reloaded", "ok"
    if "enable" in lowered:
        return "enabled", "ok"
    if "tailscale serve" in lowered:
        return "served", "ok"
    return "ran", "ok"


def _display_host(host: str) -> str:
    host = host.strip() or "127.0.0.1"
    if host in {"0.0.0.0", "::"}:
        return "127.0.0.1"
    if ":" in host and not host.startswith("["):
        return f"[{host}]"
    return host


def _switchboard_base_path(config: object) -> str:
    base_path = str(getattr(config, "switchboard_base_path", "/switchboard")).strip() or "/switchboard"
    if not base_path.startswith("/"):
        base_path = "/" + base_path
    return base_path.rstrip("/") + "/"


def _switchboard_url(config: object) -> str | None:
    if not bool(getattr(config, "switchboard_enabled", False)):
        return None
    host = _display_host(str(getattr(config, "switchboard_host", "127.0.0.1")))
    port = int(getattr(config, "switchboard_port", 4721))
    return f"http://{host}:{port}{_switchboard_base_path(config)}"


def _tailscale_dns_name() -> str:
    try:
        result = subprocess.run(
            ["tailscale", "status", "--json"],
            text=True,
            capture_output=True,
            check=False,
            timeout=2,
        )
    except (OSError, subprocess.TimeoutExpired):
        return ""
    if result.returncode != 0:
        return ""
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        return ""
    if not isinstance(payload, dict):
        return ""
    self_info = payload.get("Self")
    if not isinstance(self_info, dict):
        return ""
    return str(self_info.get("DNSName") or "").strip().rstrip(".")


def _switchboard_access_lines(config: object) -> list[tuple[str, str, str]]:
    url = _switchboard_url(config)
    if not url:
        return []
    lines = [("url", f"Switchboard: {url}", "ok")]
    dns_name = _tailscale_dns_name()
    if dns_name:
        port = int(getattr(config, "switchboard_port", 4721))
        lines.append(("tailnet", f"Switchboard proxy: https://{dns_name}/proxy/{port}/", "ok"))
        lines.append(("tailnet", f"Switchboard serve: https://{dns_name}{_switchboard_base_path(config)}", "ok"))
    return lines


def _changed_summary(manifest: dict[str, object]) -> str:
    changed = manifest.get("changed")
    if not isinstance(changed, list) or not changed:
        return "0 files changed"
    statuses: dict[str, int] = {}
    for item in changed:
        if not isinstance(item, dict):
            continue
        status = str(item.get("status") or "changed")
        statuses[status] = statuses.get(status, 0) + 1
    parts = [f"{count} {status}" for status, count in sorted(statuses.items())]
    return f"{len(changed)} files changed" + (f" ({', '.join(parts)})" if parts else "")


def _service_summary(config: object, manifest: dict[str, object], *, services_skipped: bool) -> str:
    run_actions = _run_actions(manifest)
    if run_actions:
        descriptions = [str(item.get("description") or "service command") for item in run_actions]
        return "services: " + "; ".join(descriptions)
    if services_skipped:
        return "services skipped"
    if bool(getattr(config, "supervisor_enabled", False)) and bool(getattr(config, "configure_services", False)):
        return "services unchanged"
    return "services not managed"


def _notification_switchboard_url(config: object) -> str:
    access_lines = _switchboard_access_lines(config)
    for _label, message, _style in access_lines:
        if message.startswith("Switchboard proxy: "):
            return message.replace("Switchboard proxy: ", "Switchboard: ", 1)
    for _label, message, _style in access_lines:
        if message.startswith("Switchboard: "):
            return message
    return ""


def _apply_notification_text(
    config: object,
    manifest: dict[str, object],
    *,
    command_name: str,
    services_skipped: bool,
) -> str:
    actions = manifest.get("actions")
    action_count = len(actions) if isinstance(actions, list) else 0
    command_label = command_name.replace("-", " ")
    parts = [
        f"✅ Klimkit {command_label}",
        f"🖥 Machine: {socket.gethostname()}",
        f"📦 Actions: {action_count}",
        f"📝 Changes: {_changed_summary(manifest)}",
        f"🔁 Live: {_service_summary(config, manifest, services_skipped=services_skipped)}",
    ]
    switchboard_url = _notification_switchboard_url(config)
    if switchboard_url:
        parts.append(f"🔗 {switchboard_url}")
    return "\n".join(parts)


def _send_apply_notification(
    config: object,
    manifest: dict[str, object],
    *,
    command_name: str,
    services_skipped: bool,
) -> tuple[str, str] | None:
    if not bool(getattr(config, "telegram_enabled", False)):
        return None
    if not str(getattr(config, "telegram_bot_token", "")).strip() or not str(
        getattr(config, "telegram_chat_id", "")
    ).strip():
        return ("not sent; Telegram bot_token/chat_id missing", "warn")
    text = _apply_notification_text(
        config,
        manifest,
        command_name=command_name,
        services_skipped=services_skipped,
    )
    try:
        if send_telegram_notification(config, text):
            return ("sent apply summary to Telegram", "ok")
    except Exception:
        return ("send failed; check Telegram token/chat/network", "warn")
    return ("not sent; Telegram disabled or incomplete", "warn")


def _print_live_report(
    config: object,
    manifest: dict[str, object],
    *,
    services_skipped: bool,
    telegram_status: tuple[str, str] | None = None,
) -> None:
    run_actions = _run_actions(manifest)

    print()
    print(_section("Live"))
    if run_actions:
        for item in run_actions:
            description = str(item.get("description", "command"))
            status, style = _run_status(description)
            print(_status(status, description, style))
    elif services_skipped:
        print(_status("skipped", "service reload/restart skipped by --skip-services", "warn"))
    elif bool(getattr(config, "supervisor_enabled", False)) and bool(getattr(config, "configure_services", False)):
        print(_status("unchanged", "no service command ran", "warn"))

    for label, message, style in _switchboard_access_lines(config):
        print(_status(label, message, style))

    if telegram_status is not None:
        message, style = telegram_status
        print(_status("telegram", message, style))

    if bool(getattr(config, "codex_enabled", False)):
        print(_status("live", f"Codex projection: {Path.home() / '.codex'}", "ok"))

    if bool(getattr(config, "code_server_enabled", False)):
        settings_path = Path.home() / ".local" / "share" / "code-server" / "User" / "settings.json"
        print(_status("live", f"code-server settings: {settings_path}", "ok"))

    if bool(getattr(config, "switchboard_agent_enabled", False)):
        backend_url = str(getattr(config, "switchboard_backend_url", "")).strip()
        helper_host = _display_host(str(getattr(config, "switchboard_agent_helper_host", "127.0.0.1")))
        helper_port = int(getattr(config, "switchboard_agent_helper_port", 4632))
        if backend_url:
            print(_status("reports", f"Switchboard agent backend: {backend_url}", "ok"))
        print(_status("url", f"Switchboard helper: http://{helper_host}:{helper_port}/", "ok"))

    if run_actions or (bool(getattr(config, "supervisor_enabled", False)) and not services_skipped):
        check_command = (
            "launchctl print gui/$(id -u)/com.klim.klimkit"
            if platform.system() == "Darwin"
            else "systemctl --user status klimkit.service --no-pager"
        )
        print(_status("check", check_command, "muted"))


def _manifest_path(config: object) -> Path:
    state_dir = getattr(config, "state_dir")
    if not isinstance(state_dir, Path):
        state_dir = Path(str(state_dir)).expanduser()
    return state_dir / "install" / "manifest.json"


def _format_welcome() -> str:
    lines = [
        _header("machine kit", "Keep an agent-ready machine reproducible from one repo."),
        "",
        _section("Paths"),
        _kv("config", KLIMKIT_CONFIG_FILE),
        _kv("manifest", KLIMKIT_MANIFEST_FILE),
        "",
        _section("Start Here"),
        _command_row("kk setup", "create config and show the plan"),
        _command_row("kk setup --client-only", "create a second-VM/client-only config"),
        _command_row("kk preview", "show what would change"),
        _command_row("kk apply", "write managed files, restart services, and report URLs"),
        _command_row("kk doctor", "diagnose local setup"),
        _command_row("kk serve", "run Switchboard"),
        _command_row("kk update", "pull the checkout only"),
        _command_row("kk pull", "pull current branch and apply this VM"),
    ]
    if KLIMKIT_CONFIG_FILE.exists():
        try:
            config = load_config(KLIMKIT_CONFIG_FILE)
        except Exception:
            config = None
        if config is not None:
            access_lines = _switchboard_access_lines(config)
            if access_lines:
                lines.extend(["", _section("URLs")])
                for label, message, style in access_lines:
                    lines.append(_status(label, message, style))
    return "\n".join(lines) + "\n"


def _prog_name() -> str:
    return "kk"


def _add_command(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
    name: str,
    *,
    help: str,
    description: str,
    examples: str,
) -> argparse.ArgumentParser:
    return subparsers.add_parser(
        name,
        help=help,
        description=description,
        epilog=f"examples:\n{examples}",
        formatter_class=HelpFormatter,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=_prog_name(),
        description="Keep an agent-ready machine reproducible from one repo.",
        epilog=EXAMPLES,
        formatter_class=HelpFormatter,
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path(os.environ.get("KLIMKIT_CONFIG", KLIMKIT_CONFIG_FILE)),
        help="Klimkit TOML config path.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    setup = _add_command(
        subparsers,
        "setup",
        help="Create config if needed and print the install preview.",
        description="Create the Klimkit TOML config if missing, then show the exact install plan.",
        examples="  kk setup\n  kk setup --client-only\n  kk setup --server-only\n  kk setup --skip-services",
    )
    role_group = setup.add_mutually_exclusive_group()
    role_group.add_argument("--client-only", action="store_true", help="Configure a non-central VM.")
    role_group.add_argument("--server-only", action="store_true", help="Configure a central VM without local client assets.")
    role_group.add_argument(
        "--profile",
        choices=("client", "server", "first-vm", "client-only", "server-only"),
        default=None,
        help="Initial role for new configs. Kept for compatibility; prefer --client-only for second VMs.",
    )
    setup.add_argument("--skip-services", action="store_true", help="Do not start or enable services.")

    _add_command(
        subparsers,
        "preview",
        help="Print the install plan without changing files.",
        description="Render file writes, directory syncs, service changes, and external installs without mutating disk.",
        examples="  kk preview",
    )

    apply = _add_command(
        subparsers,
        "apply",
        help="Apply the install plan.",
        description="Apply the current TOML plan, restart managed services, and report what is live.",
        examples="  kk apply\n  kk apply --skip-services",
    )
    apply.add_argument("--skip-services", action="store_true", help="Do not start or enable services.")
    apply.add_argument(
        "--defer-service-restart",
        action="store_true",
        help=argparse.SUPPRESS,
    )

    _add_command(
        subparsers,
        "doctor",
        help="Check config, repo, and runtime prerequisites.",
        description="Check the configured repo, TOML config, manifest path, uv, and git.",
        examples="  kk doctor\n  kk --config .klimkit/local/klimkit.toml doctor",
    )
    _add_command(
        subparsers,
        "daemon",
        help="Run the long-lived Klimkit supervisor.",
        description="Run the supervisor in the foreground for launchd, systemd, or direct debugging.",
        examples="  kk daemon\n  KLIMKIT_CONFIG=/path/to/klimkit.toml kk daemon",
    )
    _add_command(
        subparsers,
        "sync-live",
        help="Run one autosync pass now.",
        description="Fetch main, fast-forward this checkout when possible, apply projections, and restart services.",
        examples="  kk sync-live\n  kk --config /path/to/klimkit.toml sync-live",
    )
    _add_command(
        subparsers,
        "update",
        help="Update the Klimkit checkout.",
        description="Fetch and fast-forward the current Klimkit checkout, refusing dirty local changes.",
        examples="  kk update",
    )

    pull = _add_command(
        subparsers,
        "pull",
        help="Pull the current branch and apply the local config.",
        description=(
            "Fast-forward the current Klimkit checkout from its Git upstream, then apply the "
            "existing local TOML config. Intended for updating another VM after you push changes."
        ),
        examples="  kk pull\n  kk pull --skip-services",
    )
    pull.add_argument("--skip-services", action="store_true", help="Do not start or enable services.")

    serve = _add_command(
        subparsers,
        "serve",
        help="Run the Switchboard web UI/API.",
        description="Run Switchboard or print projected session state for agent-testable checks.",
        examples="  kk serve\n  kk serve --print-projections\n  kk serve --config .klimkit/local/klimkit.toml",
    )
    serve.add_argument("--config", dest="switchboard_config", type=Path, default=None, help="Klimkit TOML config path for Switchboard.")
    serve.add_argument("--print-projections", action="store_true", help="Print local projections and exit.")

    uninstall = _add_command(
        subparsers,
        "uninstall",
        help="Remove files owned by the Klimkit install manifest.",
        description="Remove only files recorded in the Klimkit install manifest.",
        examples="  kk uninstall",
    )
    return parser


def _skip_services(args: argparse.Namespace) -> bool:
    return bool(getattr(args, "skip_services", False))


def _setup_role(args: argparse.Namespace) -> str:
    if getattr(args, "client_only", False):
        return "client-only"
    if getattr(args, "server_only", False):
        return "server-only"
    return getattr(args, "profile", None) or "first-vm"


def subprocess_run(command: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "command failed").strip()
        raise RuntimeError(detail)
    return result


def update_checkout() -> str:
    if not (OPS_REPO_ROOT / ".git").exists():
        raise RuntimeError(f"Repo is not a Git checkout: {OPS_REPO_ROOT}")
    dirty = subprocess_run(["git", "status", "--porcelain"], cwd=OPS_REPO_ROOT)
    if dirty.stdout.strip():
        raise RuntimeError(
            "Refusing to pull with local changes in the Klimkit checkout. "
            "Commit or stash them first, or run `kk apply` to apply the local checkout without pulling."
        )
    branch = subprocess_run(["git", "branch", "--show-current"], cwd=OPS_REPO_ROOT).stdout.strip()
    if not branch:
        raise RuntimeError("Refusing to update detached HEAD checkout.")
    try:
        upstream = subprocess_run(
            ["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"],
            cwd=OPS_REPO_ROOT,
        ).stdout.strip()
    except RuntimeError:
        upstream = f"origin/{branch}"
    if "/" not in upstream:
        raise RuntimeError(f"Unsupported Git upstream: {upstream}")
    remote, remote_branch = upstream.split("/", 1)
    subprocess_run(["git", "fetch", remote, remote_branch], cwd=OPS_REPO_ROOT)
    subprocess_run(["git", "pull", "--ff-only", remote, remote_branch], cwd=OPS_REPO_ROOT)
    return f"{branch} from {upstream}"


def cmd_setup(args: argparse.Namespace) -> int:
    role = _setup_role(args)
    config, created = ensure_config(args.config, profile=role)
    updated = False
    if not created and (getattr(args, "client_only", False) or getattr(args, "server_only", False) or args.profile):
        config = with_role(config, role)
        config_path = args.config.expanduser()
        config_path.write_text(render_config(config), encoding="utf-8")
        config_path.chmod(0o600)
        updated = True
    actions = build_plan(
        config,
        skip_services=_skip_services(args),
        config_path=args.config,
    )
    validation_errors = validate_config(config)
    suffix = " (created)" if created else " (updated)" if updated else ""
    print(_header("setup", "Config prepared; no files were applied."))
    print(_kv("config", f"{args.config.expanduser()}{suffix}"))
    print()
    print(
        format_plan(
            actions,
            config_path=args.config,
            manifest_path=_manifest_path(config),
            color=_color_enabled(),
        ),
        end="",
    )
    _print_before_apply(validation_errors)
    print()
    print(_section("Next"))
    if validation_errors:
        print(_command_row(f"edit {args.config.expanduser()}", "set the required local values"))
        print(_command_row("kk apply", "apply after the config is complete"))
    else:
        print(_command_row("kk apply", "apply this plan"))
    return 0


def cmd_preview(args: argparse.Namespace) -> int:
    if not args.config.expanduser().exists():
        print(_error("Config is missing; run `kk setup` first."), file=sys.stderr)
        return 1
    config = load_config(args.config)
    actions = build_plan(
        config,
        skip_services=_skip_services(args),
        restart_services=not bool(getattr(args, "defer_service_restart", False)),
        config_path=args.config,
    )
    print(
        format_plan(
            actions,
            config_path=args.config,
            manifest_path=_manifest_path(config),
            color=_color_enabled(),
        ),
        end="",
    )
    _print_before_apply(validate_config(config))
    return 0


def cmd_apply(args: argparse.Namespace) -> int:
    config, _ = ensure_config(args.config, profile="first-vm")
    validation_errors = validate_config(config)
    if validation_errors:
        _print_apply_blockers(validation_errors)
        return 1
    actions = build_plan(
        config,
        skip_services=_skip_services(args),
        restart_services=not bool(getattr(args, "defer_service_restart", False)),
        config_path=args.config,
    )
    manifest_path = _manifest_path(config)
    manifest = apply_plan(actions, manifest_path=manifest_path, backup_root=config.backups_dir)
    print(_header("apply", "Local plan applied."))
    print(_kv("actions", len(manifest["actions"])))
    _print_changed_files(manifest)
    print(_kv("manifest", manifest_path))
    telegram_status = (
        None
        if bool(getattr(args, "defer_service_restart", False))
        else _send_apply_notification(
            config,
            manifest,
            command_name="apply",
            services_skipped=_skip_services(args),
        )
    )
    _print_live_report(config, manifest, services_skipped=_skip_services(args), telegram_status=telegram_status)
    return 0


def cmd_doctor(args: argparse.Namespace) -> int:
    status = 0
    config = None
    config_error = ""
    if args.config.expanduser().exists():
        try:
            config = load_config(args.config)
        except Exception as exc:
            config_error = str(exc)
    manifest_path = _manifest_path(config) if config is not None else KLIMKIT_MANIFEST_FILE
    print(_header("doctor", "Local Klimkit health check."))
    print(_section("Paths"))
    print(_kv("repo", OPS_REPO_ROOT))
    print(_kv("config", args.config.expanduser()))
    print(_kv("manifest", manifest_path))
    print()
    print(_section("Checks"))
    if not args.config.expanduser().exists():
        print(_status("missing", "config; run `kk setup`", "warn"))
        status = 1
    elif config_error:
        print(_status("invalid", f"config: {config_error}", "error"))
        status = 1
    else:
        print(_status("ok", "config"))
    uv_path = shutil.which("uv")
    git_path = shutil.which("git")
    print(_status("ok" if uv_path else "missing", f"uv: {uv_path or 'missing'}", "ok" if uv_path else "warn"))
    print(_status("ok" if git_path else "missing", f"git: {git_path or 'missing'}", "ok" if git_path else "warn"))
    if config is not None:
        access_lines = _switchboard_access_lines(config)
        if access_lines:
            print()
            print(_section("URLs"))
            for label, message, style in access_lines:
                print(_status(label, message, style))
    if uv_path is None:
        status = 1
    return status


def cmd_daemon(args: argparse.Namespace) -> int:
    from .tools.supervisor import supervisor

    return supervisor.main(["daemon", "--config", str(args.config.expanduser())])


def cmd_sync_live(args: argparse.Namespace) -> int:
    from .tools.supervisor import supervisor

    return supervisor.main(["sync-live-once", "--config", str(args.config.expanduser())])


def cmd_update(args: argparse.Namespace) -> int:
    del args
    try:
        summary = update_checkout()
    except RuntimeError as exc:
        print(_error(f"Update failed: {exc}"), file=sys.stderr)
        return 1
    print(_header("update", "Checkout fast-forwarded."))
    print(_kv("checkout", summary))
    return 0


def cmd_pull(args: argparse.Namespace) -> int:
    if not args.config.expanduser().exists():
        print(_error("Config is missing; run `kk setup` first."), file=sys.stderr)
        return 1
    config = load_config(args.config)
    validation_errors = validate_config(config)
    if validation_errors:
        _print_apply_blockers(validation_errors)
        return 1
    try:
        summary = update_checkout()
    except RuntimeError as exc:
        print(_error(f"Pull failed: {exc}"), file=sys.stderr)
        return 1
    actions = build_plan(config, skip_services=_skip_services(args), config_path=args.config)
    manifest_path = _manifest_path(config)
    manifest = apply_plan(actions, manifest_path=manifest_path, backup_root=config.backups_dir)
    print(_header("pull", "Checkout updated and local plan applied."))
    print(_kv("checkout", summary))
    print(_kv("actions", len(manifest["actions"])))
    _print_changed_files(manifest)
    print(_kv("manifest", manifest_path))
    telegram_status = _send_apply_notification(
        config,
        manifest,
        command_name="pull",
        services_skipped=_skip_services(args),
    )
    _print_live_report(config, manifest, services_skipped=_skip_services(args), telegram_status=telegram_status)
    return 0


def cmd_serve(args: argparse.Namespace) -> int:
    from .apps.switchboard import daemon

    daemon_args: list[str] = []
    daemon_args.extend(["--config", str((args.switchboard_config or args.config).expanduser())])
    if args.print_projections:
        daemon_args.append("--print-projections")
    return daemon.main(daemon_args)


def cmd_uninstall(args: argparse.Namespace) -> int:
    manifest_path = KLIMKIT_MANIFEST_FILE
    if args.config.expanduser().exists():
        manifest_path = _manifest_path(load_config(args.config))
    removed = uninstall_from_manifest(manifest_path=manifest_path)
    print(_header("uninstall", "Manifest-owned files removed."))
    print(_kv("removed", removed))
    print(_kv("manifest", manifest_path))
    return 0


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    if not argv:
        print(_format_welcome())
        return 0
    args = build_parser().parse_args(argv)
    commands = {
        "setup": cmd_setup,
        "preview": cmd_preview,
        "apply": cmd_apply,
        "doctor": cmd_doctor,
        "daemon": cmd_daemon,
        "sync-live": cmd_sync_live,
        "update": cmd_update,
        "pull": cmd_pull,
        "serve": cmd_serve,
        "uninstall": cmd_uninstall,
    }
    return commands[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
