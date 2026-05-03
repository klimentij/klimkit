from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

from .install import apply_plan, build_plan, ensure_config, format_plan, load_config, render_config, uninstall_from_manifest, with_role
from .paths import KLIMKIT_CONFIG_FILE, KLIMKIT_MANIFEST_FILE, OPS_REPO_ROOT


EXAMPLES = """examples:
  kk setup
  kk setup --client-only
  kk preview
  kk apply --yes
  kk doctor
  kk serve
  kk update
  kk quick
"""


WELCOME = """Klimkit
Agentic engineering across machines, under control.

Config: {config}
Manifest: {manifest}

Start here:
  kk setup           # create config and show the plan
  kk setup --client-only
                     # create a second-VM/client-only config
  kk preview         # show what would change
  kk apply --yes     # write managed files and services
  kk doctor          # diagnose local setup
  kk serve           # run Switchboard
  kk update          # pull the latest checkout
  kk quick           # pull current branch and apply this VM
"""


class HelpFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
    pass


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
        description="Agentic engineering across machines, under control.",
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
    setup.add_argument("--yes", action="store_true", help="Apply the generated plan after setup.")
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
        description="Apply the current TOML plan, writing backups and the install manifest.",
        examples="  kk apply --yes\n  kk apply --yes --skip-services",
    )
    apply.add_argument("--yes", action="store_true", help="Required confirmation for noninteractive apply.")
    apply.add_argument("--skip-services", action="store_true", help="Do not start or enable services.")

    _add_command(
        subparsers,
        "doctor",
        help="Check config, repo, and runtime prerequisites.",
        description="Check the configured repo, TOML config, manifest path, uv, and git.",
        examples="  kk doctor\n  kk --config ~/.config/klimkit/klimkit.toml doctor",
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
        help="Fetch and sync live-managed Codex assets once.",
        description="Run one explicit live-sync pass for managed Codex assets and templates.",
        examples="  kk sync-live\n  kk --config /path/to/klimkit.toml sync-live",
    )
    _add_command(
        subparsers,
        "update",
        help="Update the Klimkit checkout.",
        description="Fetch and fast-forward the current Klimkit checkout, refusing dirty local changes.",
        examples="  kk update",
    )

    quick = _add_command(
        subparsers,
        "quick",
        help="Pull the current branch and apply the local config.",
        description=(
            "Fast-forward the current Klimkit checkout from its Git upstream, then apply the "
            "existing local TOML config. Intended for updating another VM after you push changes."
        ),
        examples="  kk quick\n  kk quick --skip-services",
    )
    quick.add_argument("--skip-services", action="store_true", help="Do not start or enable services.")

    serve = _add_command(
        subparsers,
        "serve",
        help="Run the Switchboard web UI/API.",
        description="Run Switchboard or print projected session state for agent-testable checks.",
        examples="  kk serve\n  kk serve --print-projections\n  kk serve --config src/klimkit/apps/switchboard/switchboard.toml",
    )
    serve.add_argument("--config", dest="switchboard_config", type=Path, default=None, help="Switchboard TOML config path.")
    serve.add_argument("--print-projections", action="store_true", help="Print local projections and exit.")

    uninstall = _add_command(
        subparsers,
        "uninstall",
        help="Remove files owned by the Klimkit install manifest.",
        description="Remove only files recorded in the Klimkit install manifest.",
        examples="  kk uninstall --yes",
    )
    uninstall.add_argument("--yes", action="store_true", help="Required confirmation for uninstall.")
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
            "Commit or stash them first, or run `kk apply --yes` to apply the local checkout without pulling."
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
    actions = build_plan(config, skip_services=_skip_services(args), config_path=args.config)
    suffix = " (created)" if created else " (updated)" if updated else ""
    print(f"Config: {args.config.expanduser()}" + suffix)
    print(format_plan(actions, config_path=args.config), end="")
    if args.yes:
        manifest = apply_plan(actions)
        print(f"Applied actions: {len(manifest['actions'])}")
        print(f"Manifest: {KLIMKIT_MANIFEST_FILE}")
    else:
        print("No changes applied. Run `kk apply --yes` to apply this plan.")
    return 0


def cmd_preview(args: argparse.Namespace) -> int:
    if not args.config.expanduser().exists():
        print("Config is missing; run `kk setup` first.", file=sys.stderr)
        return 1
    config = load_config(args.config)
    actions = build_plan(config, skip_services=_skip_services(args), config_path=args.config)
    print(format_plan(actions, config_path=args.config), end="")
    return 0


def cmd_apply(args: argparse.Namespace) -> int:
    if not args.yes:
        print("Refusing to apply without --yes.", file=sys.stderr)
        return 2
    config, _ = ensure_config(args.config, profile="first-vm")
    actions = build_plan(config, skip_services=_skip_services(args), config_path=args.config)
    manifest = apply_plan(actions)
    print(f"Applied actions: {len(manifest['actions'])}")
    print(f"Manifest: {KLIMKIT_MANIFEST_FILE}")
    return 0


def cmd_doctor(args: argparse.Namespace) -> int:
    status = 0
    print(f"Repo: {OPS_REPO_ROOT}")
    print(f"Config: {args.config.expanduser()}")
    print(f"Manifest: {KLIMKIT_MANIFEST_FILE}")
    if not args.config.expanduser().exists():
        print("Config: missing; run `kk setup`")
        status = 1
    else:
        load_config(args.config)
        print("Config: ok")
    print(f"uv: {shutil.which('uv') or 'missing'}")
    print(f"git: {shutil.which('git') or 'missing'}")
    if shutil.which("uv") is None:
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
        print(f"Update failed: {exc}", file=sys.stderr)
        return 1
    print(f"Updated Klimkit checkout: {summary}.")
    return 0


def cmd_quick(args: argparse.Namespace) -> int:
    if not args.config.expanduser().exists():
        print("Config is missing; run `kk setup` first.", file=sys.stderr)
        return 1
    try:
        summary = update_checkout()
    except RuntimeError as exc:
        print(f"Quick update failed: {exc}", file=sys.stderr)
        return 1
    config = load_config(args.config)
    actions = build_plan(config, skip_services=_skip_services(args), config_path=args.config)
    manifest = apply_plan(actions)
    print(f"Updated Klimkit checkout: {summary}.")
    print(f"Applied actions: {len(manifest['actions'])}")
    print(f"Manifest: {KLIMKIT_MANIFEST_FILE}")
    return 0


def cmd_serve(args: argparse.Namespace) -> int:
    from .apps.switchboard import daemon

    daemon_args: list[str] = []
    if args.switchboard_config is not None:
        daemon_args.extend(["--config", str(args.switchboard_config)])
    if args.print_projections:
        daemon_args.append("--print-projections")
    return daemon.main(daemon_args)


def cmd_uninstall(args: argparse.Namespace) -> int:
    if not args.yes:
        print("Refusing to uninstall without --yes.", file=sys.stderr)
        return 2
    removed = uninstall_from_manifest()
    print(f"Removed files: {removed}")
    return 0


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    if not argv:
        print(WELCOME.format(config=KLIMKIT_CONFIG_FILE, manifest=KLIMKIT_MANIFEST_FILE))
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
        "quick": cmd_quick,
        "serve": cmd_serve,
        "uninstall": cmd_uninstall,
    }
    return commands[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
