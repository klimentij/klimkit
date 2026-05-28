#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import signal
import socket
import subprocess
import sys
import time
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

from klimkit.harnesses.codex import codex_harness
from klimkit.install import default_config, parse_config, render_config, with_role
from klimkit.notifications import build_direct_code_server_url, send_telegram_notification
from klimkit.paths import (
    KLIMKIT_CONFIG_FILE,
    KLIMKIT_LOGS_DIR,
    KLIMKIT_STATE_DIR,
    OPS_REPO_ROOT,
)
from klimkit.tools.switchboard_agent.switchboard_agent import (
    init_db as init_switchboard_db,
    load_config as load_switchboard_config,
    run_once as run_switchboard_report,
    start_helper_server as start_switchboard_helper_server,
)


DEFAULT_MACHINE_CONFIG = KLIMKIT_CONFIG_FILE
SUPERVISOR_STATE_FILE = KLIMKIT_STATE_DIR / "supervisor" / "state.json"
_SWITCHBOARD_HELPER_SERVER: Any | None = None


@dataclass(frozen=True)
class LiveMapping:
    repo_path: str
    target_path: Path
    kind: str
    exclude_prefixes: tuple[str, ...] = ()


@dataclass
class ManagedProcess:
    name: str
    process: subprocess.Popen[str]
    log_handle: Any


@dataclass(frozen=True)
class SupervisorConfig:
    profile: str
    repo_root: Path
    machine_config_path: Path
    live_sync_enabled: bool
    live_sync_interval_seconds: int
    fetch_ref: str
    switchboard_agent_enabled: bool
    manage_switchboard: bool
    telegram_enabled: bool = False
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    code_server_enabled: bool = False
    switchboard_backend_url: str = ""
    switchboard_port: int = 4721


@dataclass(frozen=True)
class CheckoutUpdate:
    previous_revision: str
    new_revision: str
    changed_files: tuple[str, ...]


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Klimkit operator supervisor.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    daemon_parser = subparsers.add_parser("daemon", help="Run the long-lived Klimkit supervisor.")
    daemon_parser.add_argument(
        "--config",
        type=Path,
        default=Path(os.environ.get("KLIMKIT_CONFIG", DEFAULT_MACHINE_CONFIG)),
        help="Path to the Klimkit TOML config.",
    )

    sync_live_parser = subparsers.add_parser(
        "sync-live-once",
        help="Manually fetch main, fast-forward this checkout, apply projections, and restart once.",
    )
    sync_live_parser.add_argument(
        "--config",
        type=Path,
        default=Path(os.environ.get("KLIMKIT_CONFIG", DEFAULT_MACHINE_CONFIG)),
        help="Path to the Klimkit TOML config.",
    )

    write_config_parser = subparsers.add_parser(
        "write-config",
        help="Write a machine config file with the chosen profile.",
    )
    write_config_parser.add_argument(
        "--config",
        type=Path,
        default=Path(os.environ.get("KLIMKIT_CONFIG", DEFAULT_MACHINE_CONFIG)),
        help="Destination TOML config path.",
    )
    write_config_parser.add_argument(
        "--profile",
        choices=("client", "server", "first-vm", "client-only", "server-only"),
        default="first-vm",
        help="Machine role. Use client-only for second VMs.",
    )
    write_config_parser.add_argument(
        "--repo-root",
        type=Path,
        default=OPS_REPO_ROOT,
        help="Checked-out Klimkit repository path.",
    )
    return parser.parse_args(argv)


def load_machine_config(path: Path) -> SupervisorConfig:
    config = parse_config(path.read_text(encoding="utf-8") if path.exists() else "")

    return SupervisorConfig(
        profile=config.profile,
        repo_root=config.repo_root,
        machine_config_path=path.expanduser(),
        live_sync_enabled=config.live_sync_enabled,
        live_sync_interval_seconds=config.live_sync_interval_seconds,
        fetch_ref=config.live_sync_ref,
        switchboard_agent_enabled=config.switchboard_agent_enabled,
        manage_switchboard=config.switchboard_enabled,
        telegram_enabled=config.telegram_enabled,
        telegram_bot_token=config.telegram_bot_token,
        telegram_chat_id=config.telegram_chat_id,
        code_server_enabled=config.code_server_enabled,
        switchboard_backend_url=config.switchboard_backend_url,
        switchboard_port=config.switchboard_port,
    )


def write_machine_config(path: Path, *, profile: str, repo_root: Path) -> None:
    config = with_role(default_config(profile), profile)
    config = replace(config, repo_root=repo_root.expanduser())
    path = path.expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_config(config), encoding="utf-8")
    path.chmod(0o600)


def live_mappings() -> list[LiveMapping]:
    return [
        LiveMapping(
            str(projection.source.relative_to(OPS_REPO_ROOT)),
            projection.target,
            projection.kind,
            projection.exclude_prefixes,
        )
        for projection in codex_harness().projections
    ]


def git_output(repo_root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "git command failed").strip()
        raise RuntimeError(detail)
    return result.stdout.strip()


def fetch_remote(repo_root: Path, fetch_ref: str) -> str:
    remote, branch = fetch_ref.split("/", 1)
    remote_tracking_ref = f"refs/remotes/{remote}/{branch}"
    result = subprocess.run(
        ["git", "fetch", "--quiet", remote, f"{branch}:{remote_tracking_ref}"],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "git fetch failed").strip()
        raise RuntimeError(detail)
    return git_output(repo_root, "rev-parse", remote_tracking_ref)


def is_ancestor(repo_root: Path, ancestor: str, descendant: str) -> bool:
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", ancestor, descendant],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode == 0:
        return True
    if result.returncode == 1:
        return False
    detail = (result.stderr or result.stdout or "git merge-base failed").strip()
    raise RuntimeError(detail)


def changed_files_between(repo_root: Path, previous_revision: str, new_revision: str) -> tuple[str, ...]:
    output = git_output(repo_root, "diff", "--name-only", previous_revision, new_revision)
    return tuple(line.strip() for line in output.splitlines() if line.strip())


def fast_forward_checkout(config: SupervisorConfig, state: dict[str, Any] | None = None) -> CheckoutUpdate | None:
    new_revision = fetch_remote(config.repo_root, config.fetch_ref)
    previous_revision = git_output(config.repo_root, "rev-parse", "HEAD")
    auto_state = state.setdefault("auto_sync", {}) if state is not None else {}
    applied_revision = str(auto_state.get("current_revision") or "").strip()
    if new_revision == previous_revision:
        if applied_revision == new_revision:
            return None
        if applied_revision:
            changed_files = changed_files_between(config.repo_root, applied_revision, new_revision)
            notification_previous = applied_revision
        else:
            changed_files = changed_files_for_revision(config.repo_root, new_revision)
            notification_previous = parent_revision(config.repo_root, new_revision) or new_revision
        return CheckoutUpdate(
            previous_revision=notification_previous,
            new_revision=new_revision,
            changed_files=changed_files,
        )
    dirty = git_output(config.repo_root, "status", "--porcelain")
    if dirty.strip():
        raise RuntimeError("autosync refused: Klimkit checkout has uncommitted changes")
    if is_ancestor(config.repo_root, previous_revision, new_revision):
        changed_files = changed_files_between(config.repo_root, previous_revision, new_revision)
        git_output(config.repo_root, "merge", "--ff-only", new_revision)
        return CheckoutUpdate(
            previous_revision=previous_revision,
            new_revision=new_revision,
            changed_files=changed_files,
        )
    if is_ancestor(config.repo_root, new_revision, previous_revision):
        if applied_revision == previous_revision:
            return None
        if applied_revision and is_ancestor(config.repo_root, applied_revision, previous_revision):
            changed_files = changed_files_between(config.repo_root, applied_revision, previous_revision)
            notification_previous = applied_revision
        else:
            changed_files = changed_files_for_revision(config.repo_root, previous_revision)
            notification_previous = parent_revision(config.repo_root, previous_revision) or previous_revision
        return CheckoutUpdate(
            previous_revision=notification_previous,
            new_revision=previous_revision,
            changed_files=changed_files,
        )
    else:
        raise RuntimeError(
            f"autosync refused: {config.fetch_ref} is not a fast-forward from current HEAD"
        )


def parent_revision(repo_root: Path, revision: str) -> str:
    try:
        return git_output(repo_root, "rev-parse", f"{revision}^")
    except RuntimeError:
        return ""


def changed_files_for_revision(repo_root: Path, revision: str) -> tuple[str, ...]:
    output = git_output(repo_root, "diff-tree", "--no-commit-id", "--name-only", "-r", revision)
    return tuple(line.strip() for line in output.splitlines() if line.strip())


def run_apply_for_autosync(config: SupervisorConfig) -> str:
    command = [
        str(config.repo_root / "klimkit"),
        "--config",
        str(config.machine_config_path),
        "apply",
        "--defer-service-restart",
    ]
    result = subprocess.run(
        command,
        cwd=config.repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    output = "\n".join(part.strip() for part in (result.stdout, result.stderr) if part.strip())
    if result.returncode != 0:
        raise RuntimeError(output or "autosync apply failed")
    return output


def summarize_changed_files(changed_files: tuple[str, ...]) -> str:
    groups: list[str] = []
    if any(path.startswith("packs/codex/") for path in changed_files):
        groups.append("Codex pack")
    if any(
        path.startswith("src/klimkit/apps/switchboard/")
        or path.startswith("src/klimkit/tools/switchboard_agent/")
        for path in changed_files
    ):
        groups.append("Switchboard")
    if any(
        path.startswith("src/klimkit/")
        or path.startswith("templates/")
        or path in {"klimkit", "install.sh", "pyproject.toml", "uv.lock"}
        for path in changed_files
    ):
        groups.append("Klimkit code")
    if any(path.startswith(".github/") for path in changed_files):
        groups.append("CI")
    if any(path.endswith(".md") for path in changed_files):
        groups.append("docs")
    if not groups:
        groups.append("repo files")
    return ", ".join(groups[:4])


def tailscale_dns_name() -> str:
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


def autosync_notification_link_lines(config: SupervisorConfig) -> list[str]:
    dns_name = tailscale_dns_name()
    lines: list[str] = []
    switchboard_url = ""
    if config.switchboard_backend_url:
        switchboard_url = config.switchboard_backend_url
    elif config.manage_switchboard and dns_name:
        switchboard_url = f"https://{dns_name}/proxy/{config.switchboard_port}/"
    if switchboard_url:
        lines.append(f"🔗 Switchboard: {switchboard_url}")
    code_server_url = (
        build_direct_code_server_url(dns_name, str(config.repo_root))
        if config.code_server_enabled
        else ""
    )
    if code_server_url:
        lines.append(f"↗ Code-server direct: {code_server_url}")
    return lines


def autosync_notification_text(config: SupervisorConfig, update: CheckoutUpdate) -> str:
    machine = socket.gethostname()
    summary = summarize_changed_files(update.changed_files)
    lines = [
        "🔄 Klimkit autosync",
        f"🖥 Machine: {machine}",
        f"🧩 Profile: {config.profile}",
        f"🌿 Revision: {update.previous_revision[:7]} -> {update.new_revision[:7]}",
        f"📝 Changes: {len(update.changed_files)} files ({summary})",
        "🔁 Live: projections applied; restarting Klimkit service",
    ]
    lines.extend(autosync_notification_link_lines(config))
    return "\n".join(lines)


def restart_managed_service() -> str:
    if sys.platform == "darwin":
        command = (
            "sh",
            "-c",
            "launchctl kickstart -k gui/$(id -u)/com.klim.klimkit",
        )
        label = "launchd agent"
    else:
        command = ("systemctl", "--user", "restart", "klimkit.service")
        label = "systemd user service"
    try:
        subprocess.run(list(command), check=True)
    except subprocess.CalledProcessError as exc:
        if exc.returncode == -signal.SIGTERM:
            return f"restarted {label}"
        raise
    return f"restarted {label}"


def auto_sync_once(config: SupervisorConfig, state: dict[str, Any]) -> str:
    update = fast_forward_checkout(config, state)
    auto_state = state.setdefault("auto_sync", {})
    if update is None:
        auto_state["last_checked_ref"] = config.fetch_ref
        auto_state["current_revision"] = git_output(config.repo_root, "rev-parse", "HEAD")
        save_supervisor_state(state)
        return "autosync: main unchanged"

    auto_state.update(
        {
            "previous_revision": update.previous_revision,
            "current_revision": update.new_revision,
            "changed_files": list(update.changed_files),
            "applied_at": time.time(),
        }
    )
    apply_output = run_apply_for_autosync(config)
    if apply_output:
        print(apply_output, flush=True)
    save_supervisor_state(state)
    notification = autosync_notification_text(config, update)
    try:
        if send_telegram_notification(config, notification):
            print("klimkit: sent autosync Telegram notification", flush=True)
    except Exception as exc:
        print(f"klimkit warning (telegram): {exc}", file=sys.stderr, flush=True)
    restart_summary = restart_managed_service()
    return (
        "autosync: updated "
        f"{update.previous_revision[:7]}..{update.new_revision[:7]}, "
        f"{len(update.changed_files)} changed files, {restart_summary}"
    )


def object_id(repo_root: Path, revision: str, repo_path: str) -> str:
    result = subprocess.run(
        ["git", "rev-parse", f"{revision}:{repo_path}"],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def file_bytes(repo_root: Path, revision: str, repo_path: str) -> bytes:
    result = subprocess.run(
        ["git", "show", f"{revision}:{repo_path}"],
        cwd=repo_root,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout.decode("utf-8", errors="ignore") or "git show failed").strip()
        raise RuntimeError(detail)
    return result.stdout


def list_tree_files(repo_root: Path, revision: str, repo_path: str) -> list[str]:
    output = git_output(repo_root, "ls-tree", "-r", "--name-only", revision, "--", repo_path)
    if not output:
        return []
    return [line.strip() for line in output.splitlines() if line.strip()]


def load_supervisor_state() -> dict[str, Any]:
    if not SUPERVISOR_STATE_FILE.exists():
        return {"live_sync": {}}
    try:
        return json.loads(SUPERVISOR_STATE_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"live_sync": {}}


def save_supervisor_state(state: dict[str, Any]) -> None:
    SUPERVISOR_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    SUPERVISOR_STATE_FILE.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")


def sync_file_from_remote(repo_root: Path, revision: str, mapping: LiveMapping) -> str:
    target = mapping.target_path.expanduser()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(file_bytes(repo_root, revision, mapping.repo_path))
    return str(target)


def sync_dir_from_remote(repo_root: Path, revision: str, mapping: LiveMapping) -> str:
    target_root = mapping.target_path.expanduser()
    target_root.mkdir(parents=True, exist_ok=True)
    repo_files = list_tree_files(repo_root, revision, mapping.repo_path)
    if mapping.exclude_prefixes:
        repo_files = [
            path
            for path in repo_files
            if not any(
                Path(path).relative_to(mapping.repo_path).as_posix().startswith(prefix)
                for prefix in mapping.exclude_prefixes
            )
        ]
    expected: set[Path] = set()

    for repo_file in repo_files:
        relative_path = Path(repo_file).relative_to(mapping.repo_path)
        target_path = target_root / relative_path
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_bytes(file_bytes(repo_root, revision, repo_file))
        expected.add(target_path)

    if target_root.exists():
        for existing in sorted(target_root.rglob("*"), reverse=True):
            if existing.is_dir():
                try:
                    existing.rmdir()
                except OSError:
                    pass
                continue
            if existing not in expected:
                existing.unlink()

    return str(target_root)


def sync_live_managed_paths(config: SupervisorConfig, state: dict[str, Any]) -> list[str]:
    revision = fetch_remote(config.repo_root, config.fetch_ref)
    live_state = state.setdefault("live_sync", {})
    updated: list[str] = []

    for mapping in live_mappings():
        current_object_id = object_id(config.repo_root, revision, mapping.repo_path)
        if live_state.get(mapping.repo_path) == current_object_id:
            continue

        if mapping.kind == "file":
            target = sync_file_from_remote(config.repo_root, revision, mapping)
        else:
            target = sync_dir_from_remote(config.repo_root, revision, mapping)
        live_state[mapping.repo_path] = current_object_id
        updated.append(f"{mapping.repo_path} -> {target}")

    live_state["revision"] = revision
    save_supervisor_state(state)
    return updated


def run_switchboard_agent_once(config: SupervisorConfig) -> str:
    global _SWITCHBOARD_HELPER_SERVER
    agent_config = load_switchboard_config(config.machine_config_path)
    if agent_config.helper_enabled and _SWITCHBOARD_HELPER_SERVER is None:
        _SWITCHBOARD_HELPER_SERVER = start_switchboard_helper_server(agent_config)
    conn = init_switchboard_db(agent_config.state_dir)
    try:
        changed = run_switchboard_report(conn, agent_config, print_snapshot=False)
    finally:
        conn.close()
    return "switchboard-agent: reported snapshot" if changed else "switchboard-agent: unchanged"


def start_process(
    name: str,
    *,
    command: list[str],
    cwd: Path,
    env: dict[str, str],
) -> ManagedProcess:
    log_dir = KLIMKIT_LOGS_DIR / "supervisor"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_handle = (log_dir / f"{name}.log").open("a", encoding="utf-8")
    process = subprocess.Popen(
        command,
        cwd=cwd,
        env=env,
        stdout=log_handle,
        stderr=subprocess.STDOUT,
        text=True,
    )
    print(f"klimkit: started {name}", flush=True)
    return ManagedProcess(name=name, process=process, log_handle=log_handle)


def ensure_central_processes(
    config: SupervisorConfig,
    processes: dict[str, ManagedProcess],
) -> None:
    common_env = os.environ.copy()

    specs = []
    if config.manage_switchboard:
        specs.append(
            (
                "switchboard",
                [str(config.repo_root / "klimkit"), "serve", "--config", str(config.machine_config_path)],
                config.repo_root,
            )
        )
    for name, command, cwd in specs:
        managed = processes.get(name)
        if managed is not None and managed.process.poll() is None:
            continue
        if managed is not None:
            managed.log_handle.close()
        processes[name] = start_process(name, command=command, cwd=cwd, env=common_env)


def terminate_processes(processes: dict[str, ManagedProcess]) -> None:
    global _SWITCHBOARD_HELPER_SERVER
    for managed in processes.values():
        if managed.process.poll() is None:
            managed.process.terminate()
    for managed in processes.values():
        try:
            managed.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            managed.process.kill()
            managed.process.wait(timeout=5)
        managed.log_handle.close()
    if _SWITCHBOARD_HELPER_SERVER is not None:
        _SWITCHBOARD_HELPER_SERVER.shutdown()
        _SWITCHBOARD_HELPER_SERVER.server_close()
        _SWITCHBOARD_HELPER_SERVER = None


def run_supervisor_step(label: str, action: Any) -> Any | None:
    try:
        return action()
    except Exception as exc:
        print(f"klimkit error ({label}): {exc}", file=sys.stderr, flush=True)
        return None


def daemon_loop(config: SupervisorConfig) -> int:
    state = load_supervisor_state()
    processes: dict[str, ManagedProcess] = {}
    next_live_sync_at = 0.0
    next_switchboard_report_at = 0.0
    stop = False

    def _handle_signal(signum: int, _frame: Any) -> None:
        nonlocal stop
        print(f"klimkit: received signal {signum}, shutting down", flush=True)
        stop = True

    signal.signal(signal.SIGTERM, _handle_signal)
    signal.signal(signal.SIGINT, _handle_signal)

    while not stop:
        now = time.time()
        if config.manage_switchboard:
            run_supervisor_step("central", lambda: ensure_central_processes(config, processes))

        if config.live_sync_enabled and now >= next_live_sync_at:
            summary = run_supervisor_step("autosync", lambda: auto_sync_once(config, state))
            if summary is not None:
                if summary != "autosync: main unchanged":
                    print(f"klimkit: {summary}", flush=True)
                next_live_sync_at = now + config.live_sync_interval_seconds

        if config.switchboard_agent_enabled and now >= next_switchboard_report_at:
            switchboard_summary = run_supervisor_step(
                "switchboard-agent", lambda: run_switchboard_agent_once(config)
            )
            if switchboard_summary is not None:
                print(switchboard_summary, flush=True)
                switchboard_config = load_switchboard_config(config.machine_config_path)
                next_switchboard_report_at = now + switchboard_config.interval_seconds

        time.sleep(1)

    terminate_processes(processes)
    return 0


def main(argv: list[str]) -> int:
    args = parse_args(argv)

    if args.command == "write-config":
        write_machine_config(
            args.config,
            profile=args.profile,
            repo_root=args.repo_root,
        )
        print(f"Wrote {args.config.expanduser()}", flush=True)
        return 0

    config = load_machine_config(args.config.expanduser())

    if args.command == "sync-live-once":
        print("klimkit: " + auto_sync_once(config, load_supervisor_state()), flush=True)
        return 0

    if args.command == "daemon":
        return daemon_loop(config)

    raise ValueError(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
