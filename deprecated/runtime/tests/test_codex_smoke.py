import os
import pty
import shutil
import select
import subprocess
import tempfile
import time
import unittest
from pathlib import Path

from klimkit.harnesses.codex import codex_harness


def project_current_codex_pack(codex_home: Path) -> None:
    harness = codex_harness(home=Path("/tmp/klimkit-codex-smoke-home"))
    harness_root = harness.managed_roots[0]
    for projection in harness.projections:
        projection_target = codex_home / projection.target.relative_to(harness_root)
        if projection.kind == "file":
            projection_target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(projection.source, projection_target)
            continue
        if projection.kind != "dir":
            continue
        for source in sorted(path for path in projection.source.rglob("*") if path.is_file()):
            relative = source.relative_to(projection.source)
            if any(str(relative).startswith(prefix) for prefix in projection.exclude_prefixes):
                continue
            target = projection_target / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
    expected = (codex_home / "config.toml", codex_home / "AGENTS.md", codex_home / "hooks" / "stop-notify.sh")
    missing = [str(path) for path in expected if not path.exists()]
    if missing:
        raise AssertionError(f"missing projected Codex pack files: {', '.join(missing)}")


def copy_existing_codex_runtime_files(codex_home: Path) -> None:
    real_home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser()
    for name in ("auth.json", "installation_id"):
        source = real_home / name
        if source.exists():
            shutil.copy2(source, codex_home / name)
    plugins = real_home / "plugins"
    if plugins.exists():
        shutil.copytree(plugins, codex_home / "plugins", dirs_exist_ok=True)


@unittest.skipUnless(os.environ.get("KLIMKIT_RUN_CODEX_SMOKE") == "1", "set KLIMKIT_RUN_CODEX_SMOKE=1 to run")
class CodexSmokeTests(unittest.TestCase):
    def test_codex_tui_startup_has_no_pack_warnings(self) -> None:
        codex = shutil.which("codex")
        self.assertIsNotNone(codex, "codex CLI is not installed")
        assert codex is not None
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir)
            codex_home = repo / "codex-home"
            fake_home = repo / "home"
            codex_home.mkdir()
            fake_home.mkdir()
            (fake_home / ".codex").symlink_to(codex_home, target_is_directory=True)
            copy_existing_codex_runtime_files(codex_home)
            project_current_codex_pack(codex_home)
            (repo / "AGENTS.md").write_text("Reply concisely.\n", encoding="utf-8")
            master_fd, slave_fd = pty.openpty()
            env = {
                **os.environ,
                "CODEX_HOME": str(codex_home),
                "HOME": str(fake_home),
                "TERM": os.environ.get("TERM", "xterm-256color"),
            }
            process = subprocess.Popen(
                [codex, "--no-alt-screen"],
                cwd=repo,
                stdin=slave_fd,
                stdout=slave_fd,
                stderr=slave_fd,
                env=env,
                close_fds=True,
            )
            os.close(slave_fd)
            output = bytearray()
            deadline = time.monotonic() + 6
            try:
                while time.monotonic() < deadline:
                    ready, _, _ = select.select([master_fd], [], [], 0.1)
                    if ready:
                        try:
                            chunk = os.read(master_fd, 65536)
                        except OSError:
                            break
                        if not chunk:
                            break
                        output.extend(chunk)
                    if process.poll() is not None:
                        break
            finally:
                if process.poll() is None:
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait(timeout=5)
                while True:
                    ready, _, _ = select.select([master_fd], [], [], 0)
                    if not ready:
                        break
                    try:
                        chunk = os.read(master_fd, 65536)
                    except OSError:
                        break
                    if not chunk:
                        break
                    output.extend(chunk)
                os.close(master_fd)

        combined = output.decode("utf-8", errors="replace").lower()
        self.assertNotIn("stdin is not a terminal", combined)
        for pattern in (
            "hooks.json",
            "failed to load hook",
            "failed to load skill",
            "failed to load subagent",
            "invalid config",
            "invalid skill",
            "invalid subagent",
            "toml error",
            "toml parse",
        ):
            self.assertNotIn(pattern, combined)


if __name__ == "__main__":
    unittest.main()
