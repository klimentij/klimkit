from __future__ import annotations

from pathlib import Path

from klimkit.paths import OPS_REPO_ROOT

from .base import Harness, HarnessProjection


def codex_harness(home: Path | None = None, repo_root: Path | None = None) -> Harness:
    home = home or Path.home()
    repo_root = repo_root or OPS_REPO_ROOT
    pack = repo_root / "packs" / "codex"
    codex_home = home / ".codex"
    return Harness(
        name="codex",
        managed_roots=(codex_home,),
        projections=(
            HarnessProjection(
                "codex-agents-md",
                pack / "AGENTS.md",
                codex_home / "AGENTS.md",
                "file",
                "Codex global AGENTS guidance",
                "codex",
            ),
            HarnessProjection(
                "codex-config",
                pack / "config.toml",
                codex_home / "config.toml",
                "file",
                "Codex config projection",
                "codex",
            ),
            HarnessProjection(
                "codex-hooks",
                pack / "hooks",
                codex_home / "hooks",
                "dir",
                "Codex hooks",
                "codex",
            ),
            HarnessProjection(
                "codex-agents",
                pack / "agents",
                codex_home / "agents",
                "dir",
                "Codex subagents",
                "codex",
            ),
            HarnessProjection(
                "codex-skills",
                pack / "skills",
                codex_home / "skills",
                "dir",
                "Codex skills",
                "codex",
                exclude_prefixes=(".system/",),
            ),
        ),
    )


CODEX_HARNESS = codex_harness()
