import subprocess
import unittest
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib


ROOT = Path(__file__).resolve().parents[1]


class CodexPackValidationTests(unittest.TestCase):
    def test_codex_config_parses_and_uses_inline_hooks(self) -> None:
        config = tomllib.loads((ROOT / "packs" / "codex" / "config.toml").read_text(encoding="utf-8"))

        self.assertTrue(config["features"]["codex_hooks"])
        self.assertIn("Stop", config["hooks"])
        self.assertFalse((ROOT / "packs" / "codex" / "hooks.json").exists())

    def test_skills_have_required_frontmatter(self) -> None:
        for path in sorted((ROOT / "packs" / "codex" / "skills").rglob("SKILL.md")):
            with self.subTest(path=path):
                lines = path.read_text(encoding="utf-8").splitlines()
                self.assertGreaterEqual(len(lines), 3)
                self.assertEqual(lines[0], "---")
                end = lines.index("---", 1)
                frontmatter = "\n".join(lines[1:end])
                self.assertIn("name:", frontmatter)
                self.assertIn("description:", frontmatter)

    def test_subagents_parse_and_have_required_fields(self) -> None:
        for path in sorted((ROOT / "packs" / "codex" / "agents").glob("*.toml")):
            with self.subTest(path=path):
                data = tomllib.loads(path.read_text(encoding="utf-8"))
                self.assertTrue(data.get("name"))
                self.assertTrue(data.get("description"))
                self.assertTrue(data.get("developer_instructions"))

    def test_pack_workflow_requires_checklister_and_final_reviewers(self) -> None:
        agents = (ROOT / "packs" / "codex" / "AGENTS.md").read_text(encoding="utf-8")
        checklister = tomllib.loads(
            (ROOT / "packs" / "codex" / "agents" / "checklister.toml").read_text(encoding="utf-8")
        )
        final_reviewer = tomllib.loads(
            (ROOT / "packs" / "codex" / "agents" / "final-reviewer.toml").read_text(encoding="utf-8")
        )

        self.assertEqual(checklister["name"], "checklister")
        self.assertIn("Acceptance Checklist", checklister["developer_instructions"])
        self.assertIn("before implementation starts", checklister["developer_instructions"])
        self.assertIn("For every implementation task, invoke `checklister` before coding.", agents)
        self.assertIn("Run 3 `final_reviewer` subagents in parallel.", agents)
        self.assertIn("the checklister acceptance checklist", final_reviewer["developer_instructions"])
        self.assertIn("Verify the draft against both the human request and every checklist item.", final_reviewer["developer_instructions"])

    def test_hook_scripts_are_syntax_valid(self) -> None:
        for path in sorted((ROOT / "packs" / "codex" / "hooks").glob("*.sh")):
            with self.subTest(path=path):
                result = subprocess.run(["bash", "-n", str(path)], text=True, capture_output=True, check=False)
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_stop_notify_hook_suppresses_subagent_notifications(self) -> None:
        hook = (ROOT / "packs" / "codex" / "hooks" / "stop-notify.sh").read_text(encoding="utf-8")

        self.assertIn("def is_subagent_session(session_id: str) -> bool:", hook)
        self.assertIn('source.get("subagent")', hook)
        self.assertIn("elif is_subagent_session(session_id):", hook)


if __name__ == "__main__":
    unittest.main()
