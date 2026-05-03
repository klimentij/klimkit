from __future__ import annotations

import os
from pathlib import Path


HOME_DIR = Path.home()
OPS_REPO_ROOT = Path(
    os.environ.get("KLIMKIT_REPO_ROOT", str(Path(__file__).resolve().parents[2]))
).expanduser()
KLIMKIT_STATE_DIR = Path(
    os.environ.get("KLIMKIT_STATE_DIR", str(HOME_DIR / ".local" / "state" / "klimkit"))
).expanduser()
KLIMKIT_CONFIG_DIR = Path(
    os.environ.get("KLIMKIT_CONFIG_DIR", str(HOME_DIR / ".config" / "klimkit"))
).expanduser()
KLIMKIT_CONFIG_FILE = Path(
    os.environ.get("KLIMKIT_CONFIG", str(KLIMKIT_CONFIG_DIR / "klimkit.toml"))
).expanduser()
KLIMKIT_SWITCHBOARD_CONFIG_FILE = Path(
    os.environ.get("KLIMKIT_SWITCHBOARD_CONFIG", str(KLIMKIT_CONFIG_DIR / "switchboard2.toml"))
).expanduser()
KLIMKIT_MANIFEST_FILE = KLIMKIT_STATE_DIR / "install" / "manifest.json"


def state_path(*parts: str) -> Path:
    return KLIMKIT_STATE_DIR.joinpath(*parts)
