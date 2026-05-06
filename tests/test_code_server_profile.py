from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from klimkit.tools import code_server_profile


class CodeServerProfileTests(unittest.TestCase):
    def test_install_extensions_skips_already_installed_extensions(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            extensions_file = root / "extensions.txt"
            extensions_file.write_text("publisher.example\n", encoding="utf-8")
            installed_package = (
                root
                / ".local"
                / "share"
                / "code-server"
                / "extensions"
                / "publisher.example-1.0.0"
                / "package.json"
            )
            installed_package.parent.mkdir(parents=True)
            installed_package.write_text(
                json.dumps({"publisher": "publisher", "name": "example"}),
                encoding="utf-8",
            )

            with (
                mock.patch("klimkit.tools.code_server_profile.shutil.which", return_value="/usr/bin/code-server"),
                mock.patch(
                    "klimkit.tools.code_server_profile.Path.home",
                    return_value=root,
                ),
                mock.patch("klimkit.tools.code_server_profile.subprocess.run") as run_mock,
            ):
                result = code_server_profile.install_extensions(extensions_file)

            self.assertEqual(result, 0)
            run_mock.assert_not_called()

    def test_install_extensions_runs_missing_extensions_with_timeout(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            extensions_file = Path(tmpdir) / "extensions.txt"
            extensions_file.write_text("publisher.example\n", encoding="utf-8")

            with (
                mock.patch("klimkit.tools.code_server_profile.shutil.which", return_value="/usr/bin/code-server"),
                mock.patch("klimkit.tools.code_server_profile.subprocess.run") as run_mock,
            ):
                result = code_server_profile.install_extensions(extensions_file, timeout_seconds=12)

            self.assertEqual(result, 0)
            run_mock.assert_called_once_with(
                ["/usr/bin/code-server", "--install-extension", "publisher.example"],
                check=True,
                timeout=12,
            )


if __name__ == "__main__":
    unittest.main()
