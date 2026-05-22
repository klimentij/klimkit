import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class DocsStaticTests(unittest.TestCase):
    def test_readme_has_product_first_sections(self) -> None:
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        first_paragraph = next(
            paragraph
            for paragraph in text.split("\n\n")
            if paragraph
            and not paragraph.startswith("#")
            and not paragraph.startswith("!")
            and not paragraph.startswith("[!")
        )

        self.assertIn("agent-ready machine", first_paragraph)
        self.assertNotIn("Python operator kit", first_paragraph)
        for heading in ("## Tech Stack", "## Single Config", "## Generated Projections", "## Security Model"):
            self.assertIn(heading, text)
        self.assertIn('human_name = "Human"', text)
        self.assertIn('workflow = "solo"', text)
        self.assertNotIn('artifact_owner = "Human"', text)
        self.assertIn("__HUMAN_NAME__", text)
        self.assertIn("__KLIMKIT_ARTIFACT_ROOT__", text)
        self.assertIn(".klimkit/local/klimkit.toml", text)
        self.assertIn(".klimkit/state/", text)
        self.assertIn("## Solo And Team Artifacts", text)
        self.assertIn("one active human/operator", text)
        self.assertIn("Solo remains the default", text)
        self.assertIn("preserve attribution", text)
        self.assertIn("reserved top-level names", text)
        self.assertIn("kk migrate team-workflow --dry-run", text)
        self.assertIn("kk migrate team-workflow --repo /path/to/project --human-name Alice --dry-run", text)
        self.assertIn("The core operating promise is parallel agent work", text)
        self.assertIn("## Codex Harness Workflow", text)
        self.assertIn("## Reports", text)
        self.assertIn("## Parallel Agent Worktrees", text)
        self.assertIn("examples/create-worktree.sh", text)
        self.assertIn("5-7 agents", text)
        self.assertIn(".klimkit/reports/", text)
        self.assertIn("full-width section", text)
        self.assertIn("Prefer MP4 videos", text)
        self.assertIn('repo_roots = ["~/klimkit", "~/wt", "~/projects"]', text)
        self.assertIn("valid team-scoped `.klimkit/<operator>/reports/**/*.html`", text)
        self.assertIn("symlinked report directories that escape", text)
        self.assertIn("Tailscale-served report URL", text)
        self.assertIn("https://<machine>.<tailnet>.ts.net/reports/", text)
        for screenshot in (
            "assets/brand/klimkit-readme-hero.jpg",
            "assets/screenshots/seven-hour-codex-run.png",
            "assets/screenshots/switchboard-pwa-workspace.jpg",
            "assets/screenshots/switchboard-catalog.jpg",
            "assets/screenshots/telegram-notifications.jpg",
        ):
            self.assertIn(screenshot, text)
            self.assertTrue((ROOT / screenshot).exists(), screenshot)

    def test_worktree_example_is_generic_and_syntax_valid(self) -> None:
        script_path = ROOT / "examples" / "create-worktree.sh"
        script = script_path.read_text(encoding="utf-8")

        result = subprocess.run(["bash", "-n", str(script_path)], text=True, capture_output=True, check=False)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("BASE_BRANCH", script)
        self.assertIn("SYNC_BRANCH", script)
        self.assertIn("switchboard_folder=", script)
        for private_token in ("PANTERA", "pantera", "tail11", "klimkit-dev-workstation"):
            self.assertNotIn(private_token, script)

    def test_security_and_contributing_docs_exist(self) -> None:
        security = (ROOT / "SECURITY.md").read_text(encoding="utf-8")
        contributing = (ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")

        for term in ("Switchboard", "Tailscale", "code-server", "workspace trust", "automatic tasks", "sandbox"):
            self.assertIn(term, security)
        self.assertIn("proof reports are served only from configured repo roots", security)
        self.assertIn("symlinked `.klimkit` roots, operator directories, or report directories", security)
        self.assertIn("uv run python -m unittest discover -s tests -q", contributing)
        self.assertIn("KLIMKIT_RUN_CODEX_SMOKE=1", contributing)

    def test_switchboard_static_uses_manual_tabs_and_simplified_statuses(self) -> None:
        index = (ROOT / "src" / "klimkit" / "apps" / "switchboard" / "static" / "index.html").read_text(encoding="utf-8")
        app = (ROOT / "src" / "klimkit" / "apps" / "switchboard" / "static" / "app.js").read_text(encoding="utf-8")
        hook = (ROOT / "packs" / "codex" / "hooks" / "stop-notify.sh").read_text(encoding="utf-8")
        gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")

        self.assertIn("Manual tabs", index)
        self.assertIn("Tab Browser", index)
        self.assertIn('role="tab"', index)
        self.assertIn("<th>Archived</th>", index)
        self.assertNotIn("workspace-drawer-logo", index)
        for status in ('value="new"', 'value="working"', 'value="ask"', 'value="done"', 'value="seen"'):
            self.assertIn(status, index)
        for abbreviated_status in ('return "wrk"', 'return "fin"', 'return "see"'):
            self.assertNotIn(abbreviated_status, app)
        for old_status in ("Planning", "Awaiting approval", "Needs input", "Stale", "Errored", "Starting", "Idle"):
            self.assertNotIn(old_status, index)
        self.assertIn("materializeManualWorkspaces", app)
        self.assertIn("activateLocationTarget", app)
        self.assertIn("TAB_BROWSER_ID", app)
        self.assertIn("WORKSPACE_MANUAL_ORDER_KEY", app)
        self.assertIn("sanitizeCatalogFilters", app)
        self.assertIn("moveWorkspaceNear", app)
        self.assertIn("handleWorkspaceDrop", app)
        self.assertIn("navigationIds", app)
        self.assertIn('openDrawer("catalog");', app)
        self.assertIn(".klimkit/reports/", gitignore)
        for extension in ("png", "jpg", "jpeg", "gif", "webp", "mp4", "webm", "mov"):
            self.assertIn(f".klimkit/reports/**/*.{extension}", gitignore)
            self.assertIn(f".klimkit/*/reports/**/*.{extension}", gitignore)
        self.assertIn("/proxy/4721/#{target}", hook)
        self.assertIn("code_server_url = f\"https://{dns_name}/?folder={urllib.parse.quote(folder, safe=chr(47))}\"", hook)
        self.assertIn("Open code-server directly", hook)
        self.assertIn('"code_server_url": code_server_url or ""', hook)
        self.assertNotIn("Quick open on this Mac", hook)
        self.assertNotIn("43123", hook)
        self.assertFalse((ROOT / "src" / "klimkit" / "apps" / "macos" / "codex-focus").exists())


if __name__ == "__main__":
    unittest.main()
