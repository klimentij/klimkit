import json
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
    "klimkit-create-worktree",
    "klimkit-codex-control",
    "klimkit-harness-cleanup",
    "klimkit-agent-browser",
    "klimkit-web-design-guidelines",
    "klimkit-ui-ux-pro-max",
    "klimkit-improve-codebase-architecture",
    "klimkit-impeccable",
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
    IMPORTED_SKILLS = {
        "klimkit-agent-browser",
        "klimkit-web-design-guidelines",
        "klimkit-ui-ux-pro-max",
        "klimkit-improve-codebase-architecture",
        "klimkit-impeccable",
    }

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
                if skill_dir.name not in self.IMPORTED_SKILLS:
                    self.assertEqual({entry.name for entry in skill_dir.iterdir()} - allowed_entries, set())

                skill_md = skill_dir / "SKILL.md"
                content = skill_md.read_text(encoding="utf-8")
                self.assertNotIn("[TODO:", content)
                match = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
                self.assertIsNotNone(match)
                frontmatter = match.group(1)
                self.assertIn(f"name: {skill_dir.name}", frontmatter)
                if skill_dir.name not in self.IMPORTED_SKILLS:
                    self.assertRegex(frontmatter, r"(?m)^description:\s*.+Use .+")

    def test_setup_owns_operator_and_personality_config(self) -> None:
        setup = (SKILLS / "klimkit-setup" / "SKILL.md").read_text(encoding="utf-8")
        state = (SKILLS / "klimkit-setup" / "references" / "state-config.md").read_text(
            encoding="utf-8"
        )
        workflow = (
            SKILLS / "klimkit-setup" / "references" / "artifact-workflow.md"
        ).read_text(encoding="utf-8")

        self.assertIn("Resolve the operator name", setup)
        self.assertIn("agent personality", setup)
        self.assertIn("Steady Operator", setup)
        self.assertIn("${XDG_CONFIG_HOME:-~/.config}/klimkit/config.toml", setup)
        self.assertIn("docs/work/README.md", setup)
        self.assertIn("docs/agents/memory.md", setup)
        self.assertIn("${XDG_CONFIG_HOME:-~/.config}/klimkit/config.toml", state)
        self.assertIn("personality_name", state)
        self.assertIn("docs/work/<NNN-DDMMYY-slug>/", workflow)
        self.assertIn("LOG.md", workflow)
        self.assertNotIn(".klimkit/<operator>", workflow)

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
        self.assertIn("docs/work/", grill)
        self.assertIn("Approved decision:", grill)

    def test_create_worktree_includes_deterministic_script_contract(self) -> None:
        skill_dir = SKILLS / "klimkit-create-worktree"
        skill = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
        reference = (skill_dir / "references" / "create-worktree.md").read_text(
            encoding="utf-8"
        )

        for script_name in ("create_worktree.sh", "worktree_lib.sh"):
            with self.subTest(script_name=script_name):
                script = skill_dir / "scripts" / script_name
                self.assertTrue(script.exists())
                self.assertTrue(script.stat().st_mode & 0o111)

        for phrase in (
            "If The Request Is Ambiguous",
            "--sync-from main",
            "--push-base",
            "--dry-run",
            "${KLIMKIT_WORKTREE_ROOT:-$HOME/wt}",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, skill + "\n" + reference)

    def test_harness_cleanup_has_a_two_phase_approval_gate(self) -> None:
        skill_dir = SKILLS / "klimkit-harness-cleanup"
        skill = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
        report_contract = (skill_dir / "references" / "report-contract.md").read_text(encoding="utf-8")
        inventory = skill_dir / "scripts" / "inventory.py"

        self.assertTrue(inventory.exists())
        for phrase in (
            "Phase 1 — Discover, Research, Report",
            "Report and stop",
            "Phase 2 — Execute Approved Actions",
            "explicitly approves action or batch IDs",
            "Preserve credentials, authentication, sessions, history, memories",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, skill)
        self.assertIn("Stable action IDs", report_contract)
        self.assertIn("Never reuse an ID", report_contract)

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

    def test_extracted_role_skills_cover_legacy_roles(self) -> None:
        expected_phrases = {
            "klimkit-checklister": "Acceptance Checklist",
            "klimkit-code-explorer": "Trace the execution path",
            "klimkit-security-auditor": "SSRF and network access",
            "klimkit-reflector": "### YYYY-MM-DDTHH:MM:SSZ",
            "klimkit-final-reviewer": "READY FOR USER",
        }

        for skill_name, phrase in expected_phrases.items():
            with self.subTest(skill_name=skill_name):
                content = (SKILLS / skill_name / "SKILL.md").read_text(encoding="utf-8")
                self.assertIn(phrase, content)

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

    def test_skills_sh_metadata_groups_root_skills(self) -> None:
        metadata = json.loads((ROOT / "skills.sh.json").read_text(encoding="utf-8"))
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertEqual(metadata["$schema"], "https://skills.sh/schemas/skills.sh.schema.json")
        self.assertEqual(metadata["notGrouped"], "bottom")
        self.assertIn("https://skills.sh/b/klimentij/klimkit", readme)
        self.assertIn("https://skills.sh/klimentij/klimkit", readme)

        grouped = []
        for grouping in metadata["groupings"]:
            self.assertTrue(grouping["title"])
            self.assertTrue(grouping["description"])
            self.assertTrue(grouping["skills"])
            grouped.extend(grouping["skills"])

        self.assertEqual(set(grouped), EXPECTED_SKILLS)
        self.assertEqual(len(grouped), len(set(grouped)))


if __name__ == "__main__":
    unittest.main()
