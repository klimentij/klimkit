import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"

EXPECTED_SKILLS = {
    "klimkit-implement",
    "klimkit-setup",
    "klimkit-checklister",
    "klimkit-code-explorer",
    "klimkit-security-auditor",
    "klimkit-reflector",
    "klimkit-final-reviewer",
    "klimkit-grill-me",
    "klimkit-diagnose",
    "klimkit-tdd",
    "klimkit-report-server",
    "klimkit-walkthrough",
    "klimkit-worktree-stack",
    "klimkit-agent-browser",
    "klimkit-web-design-guidelines",
    "klimkit-ui-ux-pro-max",
    "klimkit-improve-codebase-architecture",
    "klimkit-impeccable",
    "klimkit-antigravity-security-auditor",
}

REMOVED_SCOPE_TERMS = (
    "klimkit-to-issues",
    "klimkit-triage",
    "klimkit-github-control-plane",
    "KK Status",
    "GitHub control",
    "GitHub Project",
    "issue workpad",
)

LEGACY_ROOTS = (
    "install.sh",
    "kk",
    "klimkit",
    "pyproject.toml",
    "uv.lock",
    "src",
    "packs",
    "templates",
    "examples",
    "plugins",
)


class RootSkillTests(unittest.TestCase):
    def test_root_contains_only_skills_first_package(self) -> None:
        self.assertEqual({path.name for path in SKILLS.iterdir() if path.is_dir()}, EXPECTED_SKILLS)
        for legacy in LEGACY_ROOTS:
            with self.subTest(legacy=legacy):
                self.assertFalse((ROOT / legacy).exists())

    def test_skills_are_vercel_package_compatible(self) -> None:
        allowed_entries = {"SKILL.md", "agents", "references", "scripts", "assets"}
        name_re = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

        for skill_dir in sorted(SKILLS.iterdir()):
            if not skill_dir.is_dir():
                continue
            with self.subTest(skill=skill_dir.name):
                self.assertRegex(skill_dir.name, name_re)
                self.assertEqual({entry.name for entry in skill_dir.iterdir()} - allowed_entries, set())

                skill_md = skill_dir / "SKILL.md"
                content = skill_md.read_text(encoding="utf-8")
                self.assertNotIn("[TODO:", content)
                match = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
                self.assertIsNotNone(match)
                frontmatter = match.group(1)
                self.assertIn(f"name: {skill_dir.name}", frontmatter)
                self.assertRegex(frontmatter, r"(?m)^description:\s*.+Use .+")

    def test_setup_owns_operator_and_personality_config(self) -> None:
        setup = (SKILLS / "klimkit-setup" / "SKILL.md").read_text(encoding="utf-8")
        state = (SKILLS / "klimkit-setup" / "references" / "state-config.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("Resolve the operator name", setup)
        self.assertIn("home Klimkit repo", setup)
        self.assertIn("agent personality", setup)
        self.assertIn("Steady Operator", setup)
        self.assertIn("${XDG_CONFIG_HOME:-~/.config}/klimkit/config.toml", setup)
        self.assertIn(".klimkit/<operator>/config.toml", state)
        self.assertIn("personality_name", state)

    def test_grill_me_records_questions_and_decisions(self) -> None:
        grill = (SKILLS / "klimkit-grill-me" / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("Ask exactly one question at a time", grill)
        self.assertIn("private top-question list", grill)
        self.assertIn("Question Triage", grill)
        self.assertIn("up to 10 considered questions", grill)
        self.assertIn("Candidate question TLDR", grill)
        self.assertIn("why it is top priority", grill)
        self.assertIn("Rebuild and rerank", grill)
        self.assertIn("Search the web", grill)
        self.assertIn("contradictions", grill)
        self.assertIn("number-prefixed agent-authored Markdown note", grill)
        self.assertIn(".klimkit/<operator>/tasks/", grill)
        self.assertIn("Approved decision:", grill)

    def test_implement_routes_old_subagent_roles_to_skills(self) -> None:
        implement = (SKILLS / "klimkit-implement" / "SKILL.md").read_text(encoding="utf-8")

        for skill_name in (
            "klimkit-checklister",
            "klimkit-code-explorer",
            "klimkit-security-auditor",
            "klimkit-reflector",
            "klimkit-final-reviewer",
        ):
            with self.subTest(skill_name=skill_name):
                self.assertIn(skill_name, implement)
        self.assertIn("Do not use subagents for exploration, checklists, debugging, security, or reflection", implement)
        self.assertIn("final-review gate", implement)
        self.assertIn("Treat TDD as the default required implementation style", implement)
        self.assertIn("Prefer 1-2 independent final-review subagents", implement)

    def test_setup_checks_agents_md_contradictions(self) -> None:
        setup = (SKILLS / "klimkit-setup" / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("home/global `AGENTS.md`", setup)
        self.assertIn("contradictions", setup)
        self.assertIn("propose focused `AGENTS.md` edits", setup)

    def test_extracted_role_skills_cover_legacy_roles(self) -> None:
        expected_phrases = {
            "klimkit-checklister": "Acceptance Checklist",
            "klimkit-code-explorer": "Trace the execution path",
            "klimkit-security-auditor": "plausible abuse path",
            "klimkit-reflector": "### YYYY-MM-DDTHH:MM:SSZ",
            "klimkit-final-reviewer": "READY FOR USER",
        }

        for skill_name, phrase in expected_phrases.items():
            with self.subTest(skill_name=skill_name):
                content = (SKILLS / skill_name / "SKILL.md").read_text(encoding="utf-8")
                self.assertIn(phrase, content)

    def test_imported_candidate_skills_have_central_notices(self) -> None:
        notice = ROOT.joinpath("THIRD_PARTY_NOTICES.md").read_text(encoding="utf-8")
        imported = {
            "klimkit-agent-browser",
            "klimkit-web-design-guidelines",
            "klimkit-ui-ux-pro-max",
            "klimkit-improve-codebase-architecture",
            "klimkit-impeccable",
            "klimkit-antigravity-security-auditor",
        }

        for skill_name in imported:
            with self.subTest(skill_name=skill_name):
                self.assertIn(skill_name, notice)
                self.assertFalse((SKILLS / skill_name / "references" / "upstream.md").exists())

    def test_readme_and_skills_exclude_deferred_issue_scope(self) -> None:
        public_text = [ROOT.joinpath("README.md").read_text(encoding="utf-8")]
        public_text.extend(path.read_text(encoding="utf-8") for path in SKILLS.rglob("*.md"))
        combined = "\n".join(public_text)

        for term in REMOVED_SCOPE_TERMS:
            with self.subTest(term=term):
                self.assertNotIn(term, combined)
        self.assertIn("intentionally out of scope", combined)

    def test_readme_points_legacy_users_to_deprecated_paths(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        for path in (
            "deprecated/runtime/install.sh",
            "deprecated/runtime/kk",
            "deprecated/runtime/klimkit",
            "deprecated/runtime/src/klimkit/apps/switchboard/",
            "deprecated/runtime/packs/codex/",
            "deprecated/codex-plugin/plugins/klimkit/",
        ):
            with self.subTest(path=path):
                self.assertIn(path, readme)


if __name__ == "__main__":
    unittest.main()
