from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


def _installed_extension_ids(extensions_root: Path | None = None) -> set[str]:
    extensions_root = extensions_root or Path.home() / ".local" / "share" / "code-server" / "extensions"
    installed: set[str] = set()
    for package_json in extensions_root.glob("*/package.json"):
        try:
            payload = json.loads(package_json.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(payload, dict):
            continue
        publisher = str(payload.get("publisher") or "").strip()
        name = str(payload.get("name") or "").strip()
        if publisher and name:
            installed.add(f"{publisher}.{name}".lower())
    return installed


def _extension_ids(extensions_file: Path) -> list[str]:
    extensions: list[str] = []
    for raw_line in extensions_file.read_text(encoding="utf-8").splitlines():
        extension = raw_line.split("#", 1)[0].strip()
        if extension:
            extensions.append(extension)
    return sorted(dict.fromkeys(extensions))


def install_extensions(extensions_file: Path, *, timeout_seconds: int = 300) -> int:
    code_server = shutil.which("code-server")
    if not code_server:
        print("code-server not found; skipping extension install", file=sys.stderr)
        return 0

    installed = _installed_extension_ids()
    for extension in _extension_ids(extensions_file):
        if extension.lower() in installed:
            print(f"code-server extension already installed: {extension}")
            continue
        print(f"installing code-server extension: {extension}")
        try:
            subprocess.run([code_server, "--install-extension", extension], check=True, timeout=timeout_seconds)
        except subprocess.TimeoutExpired:
            print(f"code-server extension install timed out: {extension}", file=sys.stderr)
            return 1
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage Klimkit's code-server profile.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    install = subparsers.add_parser("install-extensions", help="Install extension IDs from a text file.")
    install.add_argument("extensions_file", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "install-extensions":
        return install_extensions(args.extensions_file.expanduser())
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
