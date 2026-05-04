from __future__ import annotations

import os
from pathlib import Path


HOME_DIR = Path.home()
OPS_REPO_ROOT = Path(
    os.environ.get("KLIMKIT_REPO_ROOT", str(Path(__file__).resolve().parents[2]))
).expanduser()
KLIMKIT_ROOT_DIR = Path(
    os.environ.get("KLIMKIT_ROOT_DIR", str(OPS_REPO_ROOT / ".klimkit"))
).expanduser()
KLIMKIT_LOCAL_DIR = Path(
    os.environ.get("KLIMKIT_CONFIG_DIR", str(KLIMKIT_ROOT_DIR / "local"))
).expanduser()
KLIMKIT_STATE_DIR = Path(
    os.environ.get("KLIMKIT_STATE_DIR", str(KLIMKIT_ROOT_DIR / "state"))
).expanduser()
KLIMKIT_CONFIG_FILE = Path(
    os.environ.get("KLIMKIT_CONFIG", str(KLIMKIT_LOCAL_DIR / "klimkit.toml"))
).expanduser()
KLIMKIT_BACKUPS_DIR = Path(
    os.environ.get("KLIMKIT_BACKUPS_DIR", str(KLIMKIT_ROOT_DIR / "backups"))
).expanduser()
KLIMKIT_LOGS_DIR = Path(
    os.environ.get("KLIMKIT_LOGS_DIR", str(KLIMKIT_ROOT_DIR / "logs"))
).expanduser()

# Compatibility aliases for callers that still accept explicit standalone
# Switchboard config paths. They are not default generated config sources.
KLIMKIT_CONFIG_DIR = KLIMKIT_LOCAL_DIR
KLIMKIT_SWITCHBOARD_CONFIG_FILE = Path(
    os.environ.get("KLIMKIT_SWITCHBOARD_CONFIG", str(KLIMKIT_CONFIG_FILE))
).expanduser()
KLIMKIT_SWITCHBOARD_AGENT_CONFIG_FILE = Path(
    os.environ.get("KLIMKIT_SWITCHBOARD_AGENT_CONFIG", str(KLIMKIT_CONFIG_FILE))
).expanduser()
KLIMKIT_MANIFEST_FILE = KLIMKIT_STATE_DIR / "install" / "manifest.json"


def state_path(*parts: str) -> Path:
    return KLIMKIT_STATE_DIR.joinpath(*parts)
