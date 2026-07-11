import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "skills" / "klimkit-harness-cleanup" / "scripts" / "inventory.py"


class HarnessCleanupInventoryTests(unittest.TestCase):
    def run_inventory(self, home: Path) -> dict:
        result = subprocess.run(
            [
                sys.executable,
                str(INVENTORY),
                "--label",
                "fixture",
                "--home",
                str(home),
                "--root",
                str(home),
                "--repo-root",
                str(home),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        self.assertNotIn("super-secret", result.stdout)
        return json.loads(result.stdout)

    def test_inventory_is_read_only_and_redacts_sensitive_content(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory).resolve()
            system_skill = home / ".codex/skills/.system/openai-docs/SKILL.md"
            custom_skill = home / ".codex/skills/custom/SKILL.md"
            auth = home / ".codex/auth.json"
            settings = home / ".claude/settings.json"
            pruned = home / ".claude/projects/session/CLAUDE.md"
            for path, content in (
                (system_skill, "---\nname: openai-docs\ndescription: docs\n---\n"),
                (custom_skill, "---\nname: custom\ndescription: custom\n---\n"),
                (auth, '{"token":"super-secret"}\n'),
                (settings, '{"enabledPlugins":{}}\n'),
                (pruned, "# Session copy\n"),
            ):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content)

            project = home / "projects/example"
            project.mkdir(parents=True)
            subprocess.run(["git", "init", "-q", str(project)], check=True)
            subprocess.run(["git", "-C", str(project), "config", "user.email", "test@example.com"], check=True)
            subprocess.run(["git", "-C", str(project), "config", "user.name", "Test"], check=True)
            agents = project / "AGENTS.md"
            agents.write_text("# Project guidance\n")
            subprocess.run(["git", "-C", str(project), "add", "AGENTS.md"], check=True)
            subprocess.run(["git", "-C", str(project), "commit", "-qm", "fixture"], check=True)

            before = {path: path.read_bytes() for path in (system_skill, custom_skill, auth, settings, agents)}
            report = self.run_inventory(home)
            after = {path: path.read_bytes() for path in before}

            self.assertEqual(before, after)
            self.assertEqual(report["coverage"], "complete")
            self.assertEqual(report["repository_count"], 1)
            self.assertIn(str(project), {row["path"] for row in report["repositories"]})

            artifacts = {row["path"]: row for row in report["artifacts"]}
            self.assertTrue(artifacts[str(auth)]["sensitive"])
            self.assertIsNone(artifacts[str(auth)]["sha256"])
            self.assertIsNone(artifacts[str(auth)]["title"])
            self.assertEqual(artifacts[str(system_skill)]["classification"], "authoritative")
            self.assertEqual(artifacts[str(custom_skill)]["layer"], "user")
            self.assertTrue(artifacts[str(agents)]["tracked"])
            self.assertNotIn(str(pruned), artifacts)


if __name__ == "__main__":
    unittest.main()
