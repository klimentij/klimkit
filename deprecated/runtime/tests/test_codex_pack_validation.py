import json
import re
import subprocess
import unittest
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib


ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ROOT = ROOT / "plugins" / "klimkit"
ROOT_SKILLS = ROOT / "skills"

EXPECTED_ROOT_SKILLS = {
    "klimkit-workflow",
    "klimkit-setup",
    "klimkit-diagnose",
    "klimkit-tdd",
    "klimkit-to-issues",
    "klimkit-triage",
    "klimkit-report-server",
    "klimkit-walkthrough",
    "klimkit-worktree-stack",
    "klimkit-github-control-plane",
}


SEMVER_RE = re.compile(
    r"^(0|[1-9]\d*)\."
    r"(0|[1-9]\d*)\."
    r"(0|[1-9]\d*)"
    r"(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)


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

    def test_root_skills_are_vercel_skill_package_compatible(self) -> None:
        self.assertTrue(ROOT_SKILLS.exists())
        skill_dirs = sorted(path for path in ROOT_SKILLS.iterdir() if path.is_dir())
        self.assertEqual({path.name for path in skill_dirs}, EXPECTED_ROOT_SKILLS)

        allowed_entries = {"SKILL.md", "agents", "references", "scripts", "assets"}
        name_re = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
        forbidden_legacy_terms = (
            "Switchboard",
            "switchboard",
            "code-server",
            "autosync",
            "Telegram",
            "kk apply",
            "kk pull",
            "repo-managed",
        )

        for skill_dir in skill_dirs:
            with self.subTest(skill=skill_dir.name):
                self.assertRegex(skill_dir.name, name_re)
                unexpected = {entry.name for entry in skill_dir.iterdir()} - allowed_entries
                self.assertEqual(unexpected, set())

                skill_md = skill_dir / "SKILL.md"
                self.assertTrue(skill_md.exists())
                content = skill_md.read_text(encoding="utf-8")
                self.assertNotIn("[TODO:", content)
                self.assertNotIn("Structuring This Skill", content)
                for term in forbidden_legacy_terms:
                    self.assertNotIn(term, content)

                match = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
                self.assertIsNotNone(match)
                frontmatter = match.group(1)
                name_match = re.search(r"^name:\s*(.+)$", frontmatter, re.MULTILINE)
                description_match = re.search(r"^description:\s*(.+)$", frontmatter, re.MULTILINE)
                self.assertIsNotNone(name_match)
                self.assertIsNotNone(description_match)

                name = name_match.group(1).strip().strip('"')
                description = description_match.group(1).strip().strip('"')
                self.assertEqual(name, skill_dir.name)
                self.assertRegex(name, name_re)
                self.assertLessEqual(len(name), 64)
                self.assertTrue(description)
                self.assertLessEqual(len(description), 1024)
                self.assertIn("Use", description)

                for entry in skill_dir.iterdir():
                    if entry.is_dir() and entry.name in {"references", "scripts", "assets"}:
                        self.assertTrue(any(entry.iterdir()), f"{entry} should not be empty")

        setup = (ROOT_SKILLS / "klimkit-setup" / "SKILL.md").read_text(encoding="utf-8")
        workflow = (ROOT_SKILLS / "klimkit-workflow" / "SKILL.md").read_text(encoding="utf-8")
        setup_state = (
            ROOT_SKILLS / "klimkit-setup" / "references" / "state-config.md"
        ).read_text(encoding="utf-8")
        self.assertIn("Ask for the operator name", setup)
        self.assertIn(".klimkit/<operator>/config.toml", setup)
        self.assertIn(".klimkit/<operator>/tasks/", setup)
        self.assertIn(".klimkit/<operator>/tasks/<feature>/", workflow)
        self.assertIn("Do not store mutable operator state inside installed skill folders", setup)
        self.assertIn("${XDG_CONFIG_HOME:-~/.config}/klimkit/config.toml", setup_state)
        self.assertIn("installed skill package", setup_state)

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
        self.assertIn("append-only timestamped cross-task Reflection Log", agents)
        self.assertIn("Entries are reflection sessions, not one required record per task", agents)
        self.assertIn("`Observations`, `Derived Pattern`, `Insight`, and `Next Probe`", agents)
        self.assertIn("up to ten named sections total", agents)
        self.assertIn("append a new-format migrated or normalized reflection entry", agents)
        self.assertIn("preserve them", agents)
        self.assertIn("solo and operator-scoped `.klimkit/**/tasks/` folders", agents)
        self.assertIn("Large or binary task artifacts should be listed as evidence", agents)
        self.assertIn("reconsider the implementation, evidence, and final response", agents)
        self.assertIn("reflection entry or explicit reflection-not-applicable note", agents)

        self.assertIn("read the configured writable reflection file when present", checklister)
        self.assertIn("create it when missing and meaningful", checklister)
        self.assertIn("run reflection after verification and before final review", checklister)
        self.assertIn("append a full-timestamped cross-task Reflection Log session", checklister)
        self.assertIn("up to ten named sections", checklister)
        self.assertIn("new-format migrated or normalized entry", checklister)
        self.assertIn("Tiny one-command tasks may mark reflection not applicable", checklister)

        self.assertIn("require the reflection entry", final_reviewer)
        self.assertIn("after verification and before final review", final_reviewer)
        self.assertIn("timestamped cross-task Reflection Log format", final_reviewer)
        self.assertIn("no more than ten named sections", final_reviewer)
        self.assertIn("older reflection formats were preserved and normalized", final_reviewer)
        self.assertIn("material reflection findings", final_reviewer)
        self.assertIn("Return KEEP WORKING if required reflection is missing", final_reviewer)

        self.assertIn("Work from fresh context", reflector_instructions)
        self.assertIn("`.klimkit/**/tasks/` archive", reflector_instructions)
        self.assertIn("Append one full-timestamped reflection session", reflector_instructions)
        self.assertIn("Entries are reflection sessions, not one required record per task", reflector_instructions)
        self.assertIn("The default required sections are `Observations`, `Derived Pattern`, `Insight`, and `Next Probe`", reflector_instructions)
        self.assertIn("up to ten named sections total", reflector_instructions)
        self.assertIn("append a new-format migrated or normalized entry", reflector_instructions)
        self.assertIn("Do not rewrite", reflector_instructions)
        self.assertNotIn("source-read summary, non-obvious synthesis, risks or contradictions", reflector_instructions)

    def test_pack_supports_team_artifact_workflow(self) -> None:
        agents = (ROOT / "packs" / "codex" / "AGENTS.md").read_text(encoding="utf-8")
        checklister = tomllib.loads(
            (ROOT / "packs" / "codex" / "agents" / "checklister.toml").read_text(encoding="utf-8")
        )["developer_instructions"]
        final_reviewer = tomllib.loads(
            (ROOT / "packs" / "codex" / "agents" / "final-reviewer.toml").read_text(encoding="utf-8")
        )["developer_instructions"]
        reflector = tomllib.loads(
            (ROOT / "packs" / "codex" / "agents" / "reflector.toml").read_text(encoding="utf-8")
        )["developer_instructions"]
        harness_tuning = (
            ROOT / "packs" / "codex" / "skills" / "harness-tuning" / "SKILL.md"
        ).read_text(encoding="utf-8")

        for text in (agents, checklister, final_reviewer, reflector, harness_tuning):
            with self.subTest(text=text[:30]):
                self.assertIn("__KLIMKIT_ARTIFACT_WORKFLOW__", text)
                self.assertIn("__KLIMKIT_OPERATOR_FOLDER__", text)
                self.assertNotIn("__KLIMKIT_ARTIFACT_OWNER__", text)

        required_agent_guidance = (
            "Current writable artifact root",
            "one active operator",
            "Solo workflow uses the flat project `.klimkit/` artifact layout",
            "Team workflow keeps `.klimkit/` as the project evidence layer",
            "write only under the current operator root",
            "readable team context",
            "attribute cross-operator facts/preferences",
            "treat that as an unmigrated project",
            "attribute the migrated flat artifacts to the current operator by default",
            "kk migrate team-workflow --dry-run",
            "__KLIMKIT_MEMORY_PATH__",
            "__KLIMKIT_LOG_PATH__",
            "__KLIMKIT_REFLECTION_PATH__",
            "__KLIMKIT_TASKS_PATH__",
            "__KLIMKIT_REPORTS_PATH__",
        )
        for phrase in required_agent_guidance:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, agents)
        for text in (checklister, final_reviewer, reflector, harness_tuning):
            with self.subTest(text=text[:30]):
                self.assertIn("one active operator", text)
                self.assertIn("readable team context", text)
        self.assertIn("solo-style flat `.klimkit` artifacts", checklister)
        self.assertIn("stop and ask __HUMAN_NAME__", agents)
        self.assertNotIn("ask Human", agents)

    def test_pack_engineering_rules_merge_quality_guidance(self) -> None:
        agents = (ROOT / "packs" / "codex" / "AGENTS.md").read_text(encoding="utf-8")

        required_guidance = (
            "ask rather than guess",
            "Push back when a simpler approach exists.",
            "Stop when confused and name what is unclear.",
            "Define success criteria for non-trivial work, not just steps to follow.",
            "Loop until verified.",
            "Checkpoint after each significant step",
            "one-use abstractions",
            "Do not add features beyond what was asked.",
            "Touch only what the request",
            "Do not improve adjacent code, comments, or formatting",
            "Before adding code, inspect exports, immediate callers, shared utilities, and relevant tests.",
            "Use project language.",
            "No hacks.",
            "If the only path is a hack, stop",
            "fake support",
            "Prefer clarity, correctness, and maintainability over preserving a flawed design.",
            "do not keep broken APIs or behavior solely for backwards compatibility",
            "Resolve conflicts explicitly.",
            "Use deterministic tools or code for deterministic work",
            "Tests must verify intent",
            "Hook, projection, service, and tool failures are part of the work.",
            "Fail loud.",
            "Do not claim completion when work, verification, or review was skipped.",
            "prototypes must be clearly marked throwaway",
        )
        for phrase in required_guidance:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, agents)

        self.assertNotIn("CLAUDE.md", agents)
        self.assertNotIn("THIS IS VERY IMPORTANT", agents)

    def test_pack_subagents_enforce_best_practice_guidance(self) -> None:
        checklister = tomllib.loads(
            (ROOT / "packs" / "codex" / "agents" / "checklister.toml").read_text(encoding="utf-8")
        )["developer_instructions"]
        code_explorer = tomllib.loads(
            (ROOT / "packs" / "codex" / "agents" / "code-explorer.toml").read_text(encoding="utf-8")
        )["developer_instructions"]
        code_reviewer = tomllib.loads(
            (ROOT / "packs" / "codex" / "agents" / "code-reviewer.toml").read_text(encoding="utf-8")
        )["developer_instructions"]
        debugger = tomllib.loads(
            (ROOT / "packs" / "codex" / "agents" / "debugger.toml").read_text(encoding="utf-8")
        )["developer_instructions"]
        final_reviewer = tomllib.loads(
            (ROOT / "packs" / "codex" / "agents" / "final-reviewer.toml").read_text(encoding="utf-8")
        )["developer_instructions"]
        test_writer = tomllib.loads(
            (ROOT / "packs" / "codex" / "agents" / "test-writer.toml").read_text(encoding="utf-8")
        )["developer_instructions"]
        harness_tuning = (ROOT / "packs" / "codex" / "skills" / "harness-tuning" / "SKILL.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("success criteria and scope boundaries", checklister)
        self.assertIn("prototype question", checklister)
        self.assertIn("surface contradictory patterns", code_explorer)
        self.assertIn("fake support", code_reviewer)
        self.assertIn("tests that assert implementation details", code_reviewer)
        self.assertIn("credible feedback loop", debugger)
        self.assertIn("skipped checks, unavailable checks, projection/service failures", final_reviewer)
        self.assertIn("public interfaces", test_writer)
        self.assertIn("one vertical slice at a time", test_writer)
        self.assertIn("synthesize it into the existing pack instead of pasting template blocks", harness_tuning)


class CodexPluginValidationTests(unittest.TestCase):
    def _parse_skill_frontmatter(self, path: Path) -> dict[str, str]:
        lines = path.read_text(encoding="utf-8").splitlines()
        self.assertGreaterEqual(len(lines), 3)
        self.assertEqual(lines[0], "---")
        end = lines.index("---", 1)
        frontmatter: dict[str, str] = {}
        for line in lines[1:end]:
            if not line.strip():
                continue
            key, value = line.split(":", 1)
            frontmatter[key] = value.strip().strip('"')
        return frontmatter

    def _parse_openai_skill_interface(self, path: Path) -> dict[str, str]:
        lines = path.read_text(encoding="utf-8").splitlines()
        self.assertEqual(lines[0], "interface:")
        interface: dict[str, str] = {}
        for line in lines[1:]:
            if not line.strip():
                continue
            self.assertTrue(line.startswith("  "), line)
            key, value = line.strip().split(": ", 1)
            self.assertTrue(value.startswith('"') and value.endswith('"'), line)
            interface[key] = value[1:-1]
        return interface

    def test_klimkit_plugin_manifest_is_public_ready(self) -> None:
        manifest = json.loads((PLUGIN_ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))

        self.assertEqual(manifest["name"], "klimkit")
        self.assertEqual(PLUGIN_ROOT.name, manifest["name"])
        self.assertRegex(manifest["version"], SEMVER_RE)
        self.assertIn("Codex workflow", manifest["description"])
        self.assertEqual(manifest["author"]["name"], "Klimkit")
        self.assertEqual(manifest["homepage"], "https://github.com/klimentij/klimkit")
        self.assertEqual(manifest["repository"], "https://github.com/klimentij/klimkit")
        self.assertEqual(manifest["license"], "MIT")
        self.assertEqual(manifest["skills"], "./skills/")
        self.assertNotIn("hooks", manifest)
        self.assertNotIn("apps", manifest)
        self.assertNotIn("mcpServers", manifest)

        interface = manifest["interface"]
        self.assertEqual(interface["displayName"], "Klimkit")
        self.assertIn("Codex workflow", interface["shortDescription"])
        self.assertIn("project evidence", interface["longDescription"])
        self.assertEqual(interface["developerName"], "Klimkit")
        self.assertEqual(interface["category"], "Productivity")
        self.assertIn("Skills", interface["capabilities"])
        self.assertIn("Workflow", interface["capabilities"])
        self.assertGreaterEqual(len(interface["defaultPrompt"]), 1)

    def test_klimkit_plugin_marketplace_entry_is_repo_local(self) -> None:
        marketplace = json.loads((ROOT / ".agents" / "plugins" / "marketplace.json").read_text(encoding="utf-8"))

        self.assertEqual(marketplace["name"], "klimkit")
        self.assertEqual(marketplace["interface"]["displayName"], "Klimkit")
        entries = {entry["name"]: entry for entry in marketplace["plugins"]}
        self.assertIn("klimkit", entries)
        entry = entries["klimkit"]
        self.assertEqual(entry["source"], {"source": "local", "path": "./plugins/klimkit"})
        self.assertEqual(entry["policy"]["installation"], "AVAILABLE")
        self.assertEqual(entry["policy"]["authentication"], "ON_INSTALL")
        self.assertNotIn("products", entry["policy"])
        self.assertEqual(entry["category"], "Productivity")

    def test_klimkit_plugin_contains_public_safe_harness_content(self) -> None:
        required = (
            "skills/klimkit-workflow/SKILL.md",
            "skills/klimkit-workflow/agents/openai.yaml",
            "skills/klimkit-workflow/references/artifact-workflow.md",
            "skills/klimkit-workflow/references/repo-managed-mode.md",
            "skills/agent-browser/SKILL.md",
            "skills/agent-browser/agents/openai.yaml",
            "skills/frontend-design/SKILL.md",
            "skills/frontend-design/agents/openai.yaml",
            "skills/grill-me/SKILL.md",
            "skills/grill-me/agents/openai.yaml",
            "skills/harness-tuning/SKILL.md",
            "skills/harness-tuning/agents/openai.yaml",
        )
        for relative in required:
            with self.subTest(relative=relative):
                self.assertTrue((PLUGIN_ROOT / relative).is_file(), relative)

        self.assertFalse((PLUGIN_ROOT / "reference").exists())

        forbidden = (
            "__HUMAN_NAME__",
            "__KLIMKIT_",
            "[TODO:",
            "*** Add File:",
            "Local developer",
            "PRIVATE_REPO_NAME",
            "PRIVATE_BRANCH_NAME",
            "private-tailnet",
        )
        for path in sorted(PLUGIN_ROOT.rglob("*")):
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for token in forbidden:
                with self.subTest(path=path, token=token):
                    self.assertNotIn(token, text)

    def test_klimkit_plugin_skills_follow_skill_creator_metadata(self) -> None:
        titles = {
            "agent-browser": "# Agent Browser",
            "frontend-design": "# Frontend Design",
            "grill-me": "# Grill Me",
            "harness-tuning": "# Harness Tuning",
            "klimkit-workflow": "# Klimkit Workflow",
        }

        for skill_dir in sorted((PLUGIN_ROOT / "skills").iterdir()):
            if not skill_dir.is_dir():
                continue
            with self.subTest(skill=skill_dir.name):
                skill_md = skill_dir / "SKILL.md"
                frontmatter = self._parse_skill_frontmatter(skill_md)
                self.assertEqual(set(frontmatter), {"name", "description"})
                self.assertEqual(frontmatter["name"], skill_dir.name)
                self.assertLessEqual(len(frontmatter["description"]), 1024)
                self.assertIn("Use ", frontmatter["description"])

                body = skill_md.read_text(encoding="utf-8").split("---", 2)[2]
                self.assertIn(titles[skill_dir.name], body)

    def test_klimkit_plugin_skills_have_openai_metadata(self) -> None:
        for skill_dir in sorted((PLUGIN_ROOT / "skills").iterdir()):
            if not skill_dir.is_dir():
                continue
            with self.subTest(skill=skill_dir.name):
                interface = self._parse_openai_skill_interface(skill_dir / "agents" / "openai.yaml")
                self.assertEqual(set(interface), {"display_name", "short_description", "default_prompt"})
                self.assertNotEqual(interface["display_name"], skill_dir.name)
                self.assertGreaterEqual(len(interface["short_description"]), 25)
                self.assertLessEqual(len(interface["short_description"]), 64)
                self.assertIn(f"${skill_dir.name}", interface["default_prompt"])

    def test_readme_documents_skills_first_install_and_legacy_deprecation(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("Klimkit is now a skills library.", readme)
        self.assertIn("npx skills add klimentij/klimkit --skill '*' -g -a codex -y", readme)
        self.assertIn("npx skills add klimentij/klimkit --list", readme)
        self.assertIn("npx skills update -g -y", readme)
        self.assertIn("The setup skill asks for the operator name first", readme)
        self.assertIn(".klimkit/<operator>/config.toml", readme)
        self.assertIn("${XDG_CONFIG_HOME:-~/.config}/klimkit/config.toml", readme)
        self.assertIn("The old Klimkit runtime system is deprecated.", readme)
        self.assertIn("The Python package, `kk` CLI, Switchboard", readme)
        self.assertIn("Do not build new workflows on the legacy runtime.", readme)
        self.assertIn("codex plugin marketplace add klimentij/klimkit --ref main", readme)
        self.assertIn("codex plugin add klimkit@klimkit", readme)
        self.assertIn("codex plugin marketplace upgrade klimkit", readme)
        self.assertNotIn("codex plugin install", readme)
        self.assertNotIn("The default path is the Codex app plus the public Klimkit plugin.", readme)
        self.assertIn("Autosync is disabled in new configs", readme)
        self.assertIn("auto_sync = false", readme)
        self.assertIn("Telegram is disabled by default", readme)
        self.assertIn("[notifications.telegram]\nenabled = false", readme)

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
