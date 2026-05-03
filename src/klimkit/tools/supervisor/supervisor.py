#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib

from klimkit.paths import (
    KLIMKIT_CONFIG_FILE,
    KLIMKIT_STATE_DIR,
    KLIMKIT_SWITCHBOARD_AGENT_CONFIG_FILE,
    KLIMKIT_SWITCHBOARD_CONFIG_FILE,
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
LIVE_SYNC_EXCLUDES = {"packs/codex/skills": (".system/",)}
_SWITCHBOARD_HELPER_SERVER: Any | None = None


@dataclass(frozen=True)
class LiveMapping:
    repo_path: str
    target_path: Path
    kind: str


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
    switchboard_config_path: Path = KLIMKIT_SWITCHBOARD_CONFIG_FILE
    switchboard_agent_config_path: Path = KLIMKIT_SWITCHBOARD_AGENT_CONFIG_FILE


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
        help="Manually fetch origin and sync only live-managed prompts/config into $HOME once.",
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
    defaults = {
        "machine": {
            "profile": "first-vm",
            "repo_root": str(OPS_REPO_ROOT),
        },
        "live_sync": {
            "enabled": False,
            "interval_seconds": 60,
            "fetch_ref": "origin/main",
        },
        "workers": {
            "live_sync": False,
            "switchboard_agent": False,
        },
        "components": {
            "client": True,
            "server": True,
            "switchboard": False,
        },
        "switchboard": {
            "config_path": str(path.expanduser().parent / "switchboard.toml"),
            "agent_config_path": str(path.expanduser().parent / "switchboard-agent.toml"),
        },
    }

    raw = {}
    if path.exists():
        raw = tomllib.loads(path.read_text(encoding="utf-8"))

    def nested(section: str, key: str) -> Any:
        return raw.get(section, {}).get(key, defaults[section][key])

    component_config = {**raw.get("central", {}), **raw.get("components", {})}
    legacy_profile = str(nested("machine", "profile")).strip().lower().replace("_", "-") or "first-vm"
    if legacy_profile in {"client", "client-only", "second-vm", "second"}:
        default_client_enabled = True
        default_server_enabled = False
    elif legacy_profile in {"server-only", "central-only"}:
        default_client_enabled = False
        default_server_enabled = True
    elif legacy_profile in {"server", "first-vm"}:
        default_client_enabled = True
        default_server_enabled = True
    else:
        raise ValueError(f"Unsupported machine.profile: {legacy_profile}")

    client_enabled = bool(component_config.get("client", default_client_enabled))
    server_enabled = bool(component_config.get("server", default_server_enabled))
    profile = "server" if server_enabled else "client" if client_enabled else "custom"

    repo_root = Path(str(nested("machine", "repo_root"))).expanduser()
    component_defaults = {
        "switchboard": server_enabled,
    }

    return SupervisorConfig(
        profile=profile,
        repo_root=repo_root,
        machine_config_path=path.expanduser(),
        live_sync_enabled=bool(raw.get("workers", {}).get("live_sync", nested("live_sync", "enabled"))),
        live_sync_interval_seconds=max(15, int(nested("live_sync", "interval_seconds"))),
        fetch_ref=str(nested("live_sync", "fetch_ref")).strip() or "origin/main",
        switchboard_agent_enabled=bool(nested("workers", "switchboard_agent")),
        manage_switchboard=bool(component_config.get("switchboard", component_defaults["switchboard"])),
        switchboard_config_path=Path(str(nested("switchboard", "config_path"))).expanduser(),
        switchboard_agent_config_path=Path(str(nested("switchboard", "agent_config_path"))).expanduser(),
    )


def write_machine_config(path: Path, *, profile: str, repo_root: Path) -> None:
    path = path.expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                "[machine]",
                f'repo_root = "{repo_root.expanduser()}"',
                "",
                "[live_sync]",
                "enabled = false",
                "interval_seconds = 60",
                'fetch_ref = "origin/main"',
                "",
                "[workers]",
                "live_sync = false",
                "switchboard_agent = false",
                "",
                "[components]",
                f"client = {'false' if profile == 'server-only' else 'true'}",
                f"server = {'false' if profile in {'client', 'client-only'} else 'true'}",
                "",
                "[switchboard]",
                f'config_path = "{path.parent / "switchboard.toml"}"',
                f'agent_config_path = "{path.parent / "switchboard-agent.toml"}"',
                'backend_url = ""',
                "",
            ]
        ),
        encoding="utf-8",
    )


def live_mappings() -> list[LiveMapping]:
    home = Path.home()
    return [
        LiveMapping("packs/codex/AGENTS.md", home / "AGENTS.md", "file"),
        LiveMapping("packs/codex/config.toml", home / ".codex" / "config.toml", "file"),
        LiveMapping("packs/codex/hooks.json", home / ".codex" / "hooks.json", "file"),
        LiveMapping("packs/codex/hooks", home / ".codex" / "hooks", "dir"),
        LiveMapping("packs/codex/agents", home / ".codex" / "agents", "dir"),
        LiveMapping("packs/codex/skills", home / ".codex" / "skills", "dir"),
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
    subprocess.run(
        ["git", "fetch", "--quiet", remote, branch],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    return git_output(repo_root, "rev-parse", fetch_ref)


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
    files = [line.strip() for line in output.splitlines() if line.strip()]
    excludes = LIVE_SYNC_EXCLUDES.get(repo_path, ())
    if not excludes:
        return files
    return [
        path
        for path in files
        if not any(path[len(repo_path) + 1 :].startswith(prefix) for prefix in excludes)
    ]


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
    agent_config = load_switchboard_config(config.switchboard_agent_config_path)
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
    log_dir = KLIMKIT_STATE_DIR / "supervisor" / "logs"
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
                [str(config.repo_root / "klimkit"), "serve", "--config", str(config.switchboard_config_path)],
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
            changes = run_supervisor_step("live sync", lambda: sync_live_managed_paths(config, state))
            if changes is not None:
                if changes:
                    print("klimkit: live sync updated " + ", ".join(changes), flush=True)
                next_live_sync_at = now + config.live_sync_interval_seconds

        if config.switchboard_agent_enabled and now >= next_switchboard_report_at:
            switchboard_summary = run_supervisor_step(
                "switchboard-agent", lambda: run_switchboard_agent_once(config)
            )
            if switchboard_summary is not None:
                print(switchboard_summary, flush=True)
                switchboard_config = load_switchboard_config(config.switchboard_agent_config_path)
                next_switchboard_report_at = now + switchboard_config.interval_seconds

        time.sleep(5)

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
        changes = sync_live_managed_paths(config, load_supervisor_state())
        if changes:
            print("klimkit: live sync updated " + ", ".join(changes), flush=True)
        else:
            print("klimkit: live sync unchanged", flush=True)
        return 0

    if args.command == "daemon":
        return daemon_loop(config)

    raise ValueError(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
