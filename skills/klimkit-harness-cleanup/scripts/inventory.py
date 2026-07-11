#!/usr/bin/env python3
"""Emit a metadata-only inventory of Codex, Claude Code, and shared harness files."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import socket
import stat
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

try:
    import grp
    import pwd
except ImportError:  # Windows
    grp = None
    pwd = None


EXACT_NAMES = {
    "agents.md",
    "agents.override.md",
    "claude.md",
    "claude.local.md",
    "skill.md",
    ".mcp.json",
    "mcp.json",
    "mcp.yaml",
    "mcp.yml",
    "config.toml",
    "settings.json",
    "settings.local.json",
    "hooks.json",
    "plugin.json",
    ".skill-lock.json",
}

SENSITIVE_NAMES = {
    ".claude.json",
    ".credentials.json",
    "auth.json",
    "credentials.json",
    "cookies",
    "login data",
    "secure preferences",
    "token.json",
}

TEXT_SUFFIXES = {
    ".md",
    ".toml",
    ".json",
    ".jsonc",
    ".yaml",
    ".yml",
    ".rules",
    ".sh",
    ".bash",
    ".zsh",
    ".py",
    ".js",
    ".mjs",
    ".cjs",
    ".ts",
    ".txt",
    ".ini",
    ".conf",
}

CONFIG_DIRS = {
    "agents",
    "skills",
    "commands",
    "prompts",
    "rules",
    "hooks",
    "policies",
    "contexts",
    "mcp-configs",
}

WALK_PRUNE = {
    ".git",
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
    "dist",
    "build",
    ".next",
    "target",
    ".tox",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
}

REPO_PRUNE = WALK_PRUNE

HARNESS_RUNTIME_PRUNE = {
    "sessions",
    "archived_sessions",
    "attachments",
    "shell_snapshots",
    "shell-snapshots",
    "session-env",
    "projects",
    "tasks",
    "history",
    "logs",
}

STATE_PARTS = {
    "memories",
    "memory",
    "history",
    "sessions",
    "projects",
    "tasks",
    "worktrees",
    "agent-memory",
    "backups",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def normalized_roots(values: Iterable[str], errors: list[dict[str, str]], purpose: str) -> list[Path]:
    roots: set[Path] = set()
    for value in values:
        path = Path(value).expanduser().resolve()
        if path.exists():
            roots.add(path)
        else:
            errors.append({"path": str(path), "error": f"{purpose} root does not exist"})
    return sorted(roots, key=str)


def under(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def walk_files(root: Path, errors: list[dict[str, str]]) -> Iterable[Path]:
    def onerror(error: OSError) -> None:
        errors.append({"path": error.filename or str(root), "error": str(error)})

    for current, dirs, files in os.walk(root, topdown=True, followlinks=False, onerror=onerror):
        current_path = Path(current)
        inside_harness_state = any(part in {".codex", ".claude"} for part in current_path.parts)
        dirs[:] = [
            name
            for name in dirs
            if name not in WALK_PRUNE and not (inside_harness_state and name in HARNESS_RUNTIME_PRUNE)
        ]
        for name in files:
            yield current_path / name


def relevant(path: Path, home: Path) -> bool:
    name = path.name.lower()
    parts = [part.lower() for part in path.parts]
    if name in EXACT_NAMES:
        return True
    if name in SENSITIVE_NAMES:
        return any(part in {".codex", ".claude"} for part in parts) or path.parent == home
    if name.startswith("mcp") and path.suffix.lower() in {".json", ".jsonc", ".yaml", ".yml"}:
        return True
    if ".codex-plugin" in parts or ".claude-plugin" in parts:
        return path.suffix.lower() in TEXT_SUFFIXES
    for marker in (".codex", ".claude", ".agents"):
        if marker not in parts:
            continue
        index = parts.index(marker)
        relative = parts[index + 1 :]
        if not relative:
            return False
        if len(relative) == 1:
            return name in EXACT_NAMES or path.suffix.lower() in {".md", ".toml", ".json", ".jsonc", ".yaml", ".yml", ".rules"}
        if relative[0] in CONFIG_DIRS:
            return name == "skill.md" if relative[0] == "skills" else path.suffix.lower() in TEXT_SUFFIXES
    return path.parent == home and name in {"agents.md", "agents.override.md", "claude.md", "claude.local.md", ".claude.json", ".mcp.json"}


def discover_repositories(roots: list[Path], errors: list[dict[str, str]]) -> list[Path]:
    repositories: set[Path] = set()

    def onerror(error: OSError) -> None:
        errors.append({"path": error.filename or "", "error": str(error)})

    for root in roots:
        for current, dirs, files in os.walk(root, topdown=True, followlinks=False, onerror=onerror):
            current_path = Path(current)
            if ".git" in dirs or ".git" in files:
                repositories.add(current_path)
            inside_harness_state = any(part in {".codex", ".claude"} for part in current_path.parts)
            dirs[:] = [
                name
                for name in dirs
                if name not in REPO_PRUNE and not (inside_harness_state and name in HARNESS_RUNTIME_PRUNE)
            ]
    return sorted(repositories, key=str)


def git_text(repository: Path, arguments: list[str], timeout: int = 30) -> tuple[int, str]:
    try:
        result = subprocess.run(
            ["git", "-C", str(repository), *arguments],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            env={**os.environ, "GIT_OPTIONAL_LOCKS": "0"},
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return 1, ""
    return result.returncode, result.stdout.strip()


def repository_metadata(repository: Path) -> dict[str, Any]:
    _, branch = git_text(repository, ["branch", "--show-current"])
    _, head = git_text(repository, ["rev-parse", "HEAD"])
    _, origin = git_text(repository, ["config", "--get", "remote.origin.url"])
    _, common = git_text(repository, ["rev-parse", "--git-common-dir"])
    _, upstream = git_text(repository, ["rev-parse", "--abbrev-ref", "@{upstream}"])
    _, status_output = git_text(repository, ["status", "--porcelain=v1", "-z", "-uno"])
    _, untracked_output = git_text(repository, ["ls-files", "--others", "--exclude-standard", "-z"])
    tracked_changes = len([item for item in status_output.split("\0") if item]) if status_output else 0
    untracked_entries = len([item for item in untracked_output.split("\0") if item]) if untracked_output else 0
    ahead = behind = None
    if upstream:
        code, counts = git_text(repository, ["rev-list", "--left-right", "--count", f"{upstream}...HEAD"])
        if code == 0 and len(counts.split()) == 2:
            behind, ahead = (int(value) for value in counts.split())
    lower = str(repository).lower()
    kind = "project"
    common_path = Path(common) if common else None
    if common_path and not common_path.is_absolute():
        common_path = (repository / common_path).resolve()
    if common_path and common_path != (repository / ".git").resolve():
        kind = "worktree"
    if any(token in lower for token in ("/experiments/", "/run-snapshot", "/eval-runs/")):
        kind = "experiment"
    elif any(token in lower for token in ("/.cache/", "/.tmp/", "/plugins/cache/", "/vendor_imports/")):
        kind = "managed-cache"
    return {
        "path": str(repository),
        "name": repository.name,
        "kind": kind,
        "branch": branch or "DETACHED",
        "head": head or None,
        "origin": origin or None,
        "upstream": upstream or None,
        "ahead": ahead,
        "behind": behind,
        "clean": tracked_changes == 0 and untracked_entries == 0,
        "tracked_changes": tracked_changes,
        "untracked_entries": untracked_entries,
        "git_common_dir": common or None,
    }


def nearest_repository(path: Path, repositories: list[Path]) -> Path | None:
    matches = [repository for repository in repositories if under(path, repository)]
    return max(matches, key=lambda item: len(str(item))) if matches else None


def tracked_files(repository: Path) -> set[str]:
    try:
        result = subprocess.run(
            ["git", "-C", str(repository), "ls-files", "-z"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            env={**os.environ, "GIT_OPTIONAL_LOCKS": "0"},
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return set()
    return {item.decode(errors="replace") for item in result.stdout.split(b"\0") if item}


def sensitive(path: Path) -> bool:
    name = path.name.lower()
    return name in SENSITIVE_NAMES or any(token in name for token in ("credential", "secret", "token", "cookie"))


def sha256(path: Path) -> str | None:
    try:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()
    except (OSError, PermissionError):
        return None


def first_heading(path: Path) -> str | None:
    if path.suffix.lower() not in TEXT_SUFFIXES:
        return None
    try:
        text = path.read_text(errors="replace")[:32768]
    except (OSError, PermissionError):
        return None
    for line in text.splitlines():
        if line.strip().startswith("# "):
            return line.strip()[2:][:180]
    return None


def owner_and_mode(path: Path, metadata: os.stat_result) -> tuple[str, str, str]:
    try:
        if pwd is None:
            raise KeyError
        owner = pwd.getpwuid(metadata.st_uid).pw_name
    except KeyError:
        owner = str(metadata.st_uid)
    try:
        if grp is None:
            raise KeyError
        group = grp.getgrgid(metadata.st_gid).gr_name
    except KeyError:
        group = str(metadata.st_gid)
    return owner, group, oct(stat.S_IMODE(metadata.st_mode))


def artifact_type(path: Path) -> str:
    name = path.name.lower()
    parts = [part.lower() for part in path.parts]
    if name.startswith("agents") and name.endswith(".md"):
        return "codex-instructions"
    if name.startswith("claude") and name.endswith(".md"):
        return "claude-instructions"
    if name == "skill.md":
        return "skill"
    if sensitive(path):
        return "credential-or-mixed-state"
    if name.startswith("mcp") or name == ".mcp.json":
        return "mcp-config"
    if "agents" in parts:
        return "subagent"
    if "hooks" in parts or "hook" in name:
        return "hook"
    if "rules" in parts or path.suffix.lower() == ".rules":
        return "rule-or-policy"
    if "commands" in parts or "prompts" in parts:
        return "command-or-prompt"
    if name == "plugin.json" or ".codex-plugin" in parts or ".claude-plugin" in parts:
        return "plugin-config"
    if "settings" in name or name.startswith("config"):
        return "settings"
    return "harness-config"


def harness(path: Path) -> str:
    parts = [part.lower() for part in path.parts]
    name = path.name.lower()
    codex = ".codex" in parts or name.startswith("agents")
    claude = ".claude" in parts or name.startswith("claude") or name == ".claude.json"
    shared = ".agents" in parts or name == "skill.md" or name.startswith("mcp") or name == ".mcp.json"
    labels = []
    if codex:
        labels.append("Codex")
    if claude:
        labels.append("Claude Code")
    if shared:
        labels.append("shared-compatible")
    return " + ".join(labels) if labels else "unknown harness"


def layer_and_classification(path: Path, home: Path, repository: Path | None) -> tuple[str, str, str]:
    lower = str(path).lower()
    parts = {part.lower() for part in path.parts}
    if sensitive(path):
        return "sensitive state", "credential", "content deliberately not inspected"
    if (
        "/.codex/skills/.system/" in lower
        or lower.startswith("/etc/codex/")
        or lower.startswith("/etc/claude-code/")
        or "/library/application support/claudecode/" in lower
        or "/program files/claudecode/" in lower
    ):
        return "system or managed", "authoritative", "system/managed path"
    if any(token in lower for token in ("/cache/", "/.cache/", "/.tmp/", "/vendor_imports/")):
        return "managed cache", "cache", "cache/catalog path"
    if any(token in lower for token in ("/experiments/", "/run-snapshot", "/eval-runs/")):
        return "experiment", "evidence", "experiment/run path"
    if parts & STATE_PARTS:
        return "state or backup", "state", "state/backup path"
    if repository:
        return "project", "authoritative", "repository source path"
    if under(path, home / ".codex") or under(path, home / ".claude") or under(path, home / ".agents") or path.parent == home:
        return "user", "unknown", "candidate user-global surface; prove activation separately"
    return "system or external", "unknown", "activation not evaluated"


def collect_artifacts(roots: list[Path], home: Path, repositories: list[Path], errors: list[dict[str, str]]) -> list[dict[str, Any]]:
    paths: set[Path] = set()
    for root in roots:
        for path in walk_files(root, errors):
            if relevant(path, home):
                paths.add(path)
    tracking = {repository: tracked_files(repository) for repository in repositories}
    records = []
    for path in sorted(paths, key=str):
        repository = nearest_repository(path, repositories)
        is_sensitive = sensitive(path)
        try:
            metadata = path.lstat()
        except (OSError, PermissionError) as exc:
            errors.append({"path": str(path), "error": str(exc)})
            metadata = None
        owner = group = mode = None
        if metadata:
            owner, group, mode = owner_and_mode(path, metadata)
        regular = bool(metadata and stat.S_ISREG(metadata.st_mode))
        relative = str(path.relative_to(repository)) if repository else None
        layer, classification, activation = layer_and_classification(path, home, repository)
        records.append(
            {
                "path": str(path),
                "harness": harness(path),
                "artifact_type": artifact_type(path),
                "layer": layer,
                "classification": classification,
                "activation_evidence": activation,
                "repository": str(repository) if repository else None,
                "repository_relative": relative,
                "tracked": relative in tracking[repository] if repository else None,
                "is_symlink": path.is_symlink(),
                "symlink_target": os.readlink(path) if path.is_symlink() else None,
                "sensitive": is_sensitive,
                "owner": owner,
                "group": group,
                "mode": mode,
                "size_bytes": metadata.st_size if metadata else None,
                "mtime": datetime.fromtimestamp(metadata.st_mtime, timezone.utc).isoformat().replace("+00:00", "Z") if metadata else None,
                "sha256": None if is_sensitive or not regular else sha256(path),
                "title": None if is_sensitive or not regular else first_heading(path),
            }
        )
    return records


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--label", default=socket.gethostname(), help="Stable machine label for reports")
    parser.add_argument("--home", default=str(Path.home()), help="Home directory for user-scope classification")
    parser.add_argument("--root", action="append", default=[], help="Filesystem root to scan; repeatable (default: home)")
    parser.add_argument("--repo-root", action="append", default=[], help="Root under which to discover Git repositories; repeatable (default: scan roots)")
    args = parser.parse_args()

    errors: list[dict[str, str]] = []
    home = Path(args.home).expanduser().resolve()
    roots = normalized_roots(args.root or [str(home)], errors, "scan")
    repo_roots = normalized_roots(args.repo_root, errors, "repository search") if args.repo_root else roots
    repositories = discover_repositories(repo_roots, errors)
    repository_records = [repository_metadata(repository) for repository in repositories]
    artifacts = collect_artifacts(roots, home, repositories, errors)
    counts: dict[str, int] = defaultdict(int)
    for artifact in artifacts:
        if artifact["repository"]:
            counts[artifact["repository"]] += 1
    for repository in repository_records:
        repository["artifact_count"] = counts[repository["path"]]

    scanned_at = utc_now()
    report_hash = hashlib.sha256("\n".join(record["path"] for record in artifacts).encode()).hexdigest()[:8]
    output = {
        "schema": 1,
        "scan_id": f"{scanned_at}-{report_hash}",
        "scanned_at": scanned_at,
        "machine": {"label": args.label, "hostname": socket.gethostname(), "platform": platform.platform(), "home": str(home)},
        "roots": [str(root) for root in roots],
        "repo_roots": [str(root) for root in repo_roots],
        "excluded_directory_names": sorted(WALK_PRUNE | HARNESS_RUNTIME_PRUNE),
        "coverage": "complete" if not errors else "partial",
        "errors": errors,
        "repository_count": len(repository_records),
        "artifact_count": len(artifacts),
        "repositories": repository_records,
        "artifacts": artifacts,
    }
    json.dump(output, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
