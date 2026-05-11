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

    def test_pack_workflow_requires_ui_reports_with_video(self) -> None:
        agents = (ROOT / "packs" / "codex" / "AGENTS.md").read_text(encoding="utf-8")
        checklister = tomllib.loads(
            (ROOT / "packs" / "codex" / "agents" / "checklister.toml").read_text(encoding="utf-8")
        )["developer_instructions"]
        final_reviewer = tomllib.loads(
            (ROOT / "packs" / "codex" / "agents" / "final-reviewer.toml").read_text(encoding="utf-8")
        )["developer_instructions"]

        for text in (checklister, final_reviewer, agents):
            self.assertIn(".klimkit/reports/", text)
        self.assertIn("native `agent-browser` video recording", checklister)
        self.assertIn("required screenshots", checklister)
        self.assertIn("full-width sections", checklister)
        self.assertIn("MP4", checklister)
        self.assertIn("final HTML proof report", checklister)
        self.assertIn("inspect every screenshot", final_reviewer)
        self.assertIn("sampling representative frames", final_reviewer)
        self.assertIn("scrubbing", final_reviewer)
        self.assertIn("full-width sections", final_reviewer)
        self.assertIn("MP4", final_reviewer)
        self.assertIn("video evidence", final_reviewer)
        self.assertIn("Tailscale-served report URL", final_reviewer)
        self.assertIn("localhost report URLs are not sufficient", final_reviewer)
        self.assertIn("Tailscale-served report URL", agents)
        self.assertIn("full-width section", agents)
        self.assertIn("Prefer MP4", agents)

    def test_pack_workflow_requires_reflection_before_final_review(self) -> None:
        agents = (ROOT / "packs" / "codex" / "AGENTS.md").read_text(encoding="utf-8")
        checklister = tomllib.loads(
            (ROOT / "packs" / "codex" / "agents" / "checklister.toml").read_text(encoding="utf-8")
        )["developer_instructions"]
        final_reviewer = tomllib.loads(
            (ROOT / "packs" / "codex" / "agents" / "final-reviewer.toml").read_text(encoding="utf-8")
        )["developer_instructions"]
        reflector = tomllib.loads(
            (ROOT / "packs" / "codex" / "agents" / "reflector.toml").read_text(encoding="utf-8")
        )
        reflector_instructions = reflector["developer_instructions"]

        self.assertEqual(reflector["name"], "reflector")
        self.assertIn("fresh-context", reflector["description"].lower())
        self.assertIn("Reflection Gate", agents)
        self.assertLess(agents.index("**Reflection Gate**"), agents.index("**Final Review Gate**"))
        self.assertIn("run a fresh-context `reflector` pass after verification and before final reviewers", agents)
        self.assertIn(".klimkit/reflection.md", agents)
        self.assertIn("append-only repo-level synthesis ledger", agents)
        self.assertIn("current task first", agents)
        self.assertIn("wider `.klimkit/tasks/` archive", agents)
        self.assertIn("Large or binary task artifacts should be listed as evidence", agents)
        self.assertIn("reconsider the implementation, evidence, and final response", agents)
        self.assertIn("reflection entry or explicit reflection-not-applicable note", agents)

        self.assertIn("read `.klimkit/reflection.md` when present", checklister)
        self.assertIn("create it when missing and meaningful", checklister)
        self.assertIn("run reflection after verification and before final review", checklister)
        self.assertIn("append a dated repo-level reflection entry", checklister)
        self.assertIn("Tiny one-command tasks may mark reflection not applicable", checklister)

        self.assertIn("require the reflection entry", final_reviewer)
        self.assertIn("after verification and before final review", final_reviewer)
        self.assertIn("material reflection findings", final_reviewer)
        self.assertIn("Return KEEP WORKING if required reflection is missing", final_reviewer)

        self.assertIn("Work from fresh context", reflector_instructions)
        self.assertIn("`.klimkit/tasks/` archive", reflector_instructions)
        self.assertIn("Append one dated entry", reflector_instructions)
        self.assertIn("Do not rewrite", reflector_instructions)
        self.assertIn("source-read summary", reflector_instructions)
        self.assertIn("risks or contradictions", reflector_instructions)

    def test_pack_engineering_rules_merge_quality_guidance(self) -> None:
        agents = (ROOT / "packs" / "codex" / "AGENTS.md").read_text(encoding="utf-8")

        required_guidance = (
            "ask rather than guess",
            "checkpoint after each significant step",
            "one-use abstractions",
            "Touch only what the request",
            "Before adding code, inspect exports, immediate callers, shared utilities, and relevant tests.",
            "No hacks.",
            "If the only path is a hack, stop",
            "Prefer clarity, correctness, and maintainability over preserving a flawed design.",
            "do not keep broken APIs or behavior solely for backwards compatibility",
            "Resolve conflicts explicitly.",
            "Use deterministic tools or code for deterministic work",
            "Tests must verify intent",
            "Fail loud.",
            "Do not claim completion when work, verification, or review was skipped.",
        )
        for phrase in required_guidance:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, agents)

        self.assertNotIn("CLAUDE.md", agents)
        self.assertNotIn("THIS IS VERY IMPORTANT", agents)

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
