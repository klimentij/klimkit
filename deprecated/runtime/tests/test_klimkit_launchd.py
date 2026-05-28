from __future__ import annotations

import unittest
from pathlib import Path

from klimkit.install import default_config, render_launchd_plist


class KlimkitLaunchdTests(unittest.TestCase):
    def test_launchd_plist_uses_klimkit_names_and_config(self) -> None:
        config = default_config("client")
        config_path = Path("/tmp/custom-klimkit.toml")

        content = render_launchd_plist(config, config_path=config_path)

        self.assertIn("<string>com.klim.klimkit</string>", content)
        self.assertIn("<string>klimkit</string>", content)
        self.assertIn("<string>daemon</string>", content)
        self.assertIn(f"<string>{config_path}</string>", content)


if __name__ == "__main__":
    unittest.main()
