import importlib
import os
import unittest
from pathlib import Path
from unittest import mock

import klimkit.paths as paths


class KlimkitPathsTests(unittest.TestCase):
    def test_defaults_are_repo_local(self) -> None:
        self.assertEqual(paths.KLIMKIT_CONFIG_FILE, paths.OPS_REPO_ROOT / ".klimkit" / "local" / "klimkit.toml")
        self.assertEqual(paths.KLIMKIT_STATE_DIR, paths.OPS_REPO_ROOT / ".klimkit" / "state")
        self.assertEqual(paths.KLIMKIT_BACKUPS_DIR, paths.OPS_REPO_ROOT / ".klimkit" / "backups")
        self.assertEqual(paths.KLIMKIT_LOGS_DIR, paths.OPS_REPO_ROOT / ".klimkit" / "logs")
        self.assertEqual(paths.KLIMKIT_MANIFEST_FILE, paths.KLIMKIT_STATE_DIR / "install" / "manifest.json")

    def test_env_overrides_still_win(self) -> None:
        with mock.patch.dict(
            os.environ,
            {
                "KLIMKIT_REPO_ROOT": "/tmp/repo",
                "KLIMKIT_CONFIG": "/tmp/config.toml",
                "KLIMKIT_STATE_DIR": "/tmp/state",
            },
            clear=False,
        ):
            reloaded = importlib.reload(paths)
            try:
                self.assertEqual(reloaded.OPS_REPO_ROOT, Path("/tmp/repo"))
                self.assertEqual(reloaded.KLIMKIT_CONFIG_FILE, Path("/tmp/config.toml"))
                self.assertEqual(reloaded.KLIMKIT_STATE_DIR, Path("/tmp/state"))
            finally:
                importlib.reload(paths)


if __name__ == "__main__":
    unittest.main()
