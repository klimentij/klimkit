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
        self.assertIn(".klimkit/local/klimkit.toml", text)
        self.assertIn(".klimkit/state/", text)

    def test_security_and_contributing_docs_exist(self) -> None:
        security = (ROOT / "SECURITY.md").read_text(encoding="utf-8")
        contributing = (ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")

        for term in ("Switchboard", "Tailscale", "code-server", "workspace trust", "automatic tasks", "sandbox"):
            self.assertIn(term, security)
        self.assertIn("uv run python -m unittest discover -s tests -q", contributing)
        self.assertIn("KLIMKIT_RUN_CODEX_SMOKE=1", contributing)

    def test_switchboard_static_uses_manual_tabs_and_simplified_statuses(self) -> None:
        index = (ROOT / "src" / "klimkit" / "apps" / "switchboard" / "static" / "index.html").read_text(encoding="utf-8")
        app = (ROOT / "src" / "klimkit" / "apps" / "switchboard" / "static" / "app.js").read_text(encoding="utf-8")
        hook = (ROOT / "packs" / "codex" / "hooks" / "stop-notify.sh").read_text(encoding="utf-8")

        self.assertIn("Manual tabs", index)
        self.assertNotIn("workspace-drawer-logo", index)
        for status in ('value="new"', 'value="working"', 'value="ask"', 'value="done"', 'value="seen"'):
            self.assertIn(status, index)
        for abbreviated_status in ('return "wrk"', 'return "fin"', 'return "see"'):
            self.assertNotIn(abbreviated_status, app)
        for old_status in ("Planning", "Awaiting approval", "Needs input", "Stale", "Errored", "Starting", "Idle"):
            self.assertNotIn(old_status, index)
        self.assertIn("materializeManualWorkspaces", app)
        self.assertIn("activateLocationTarget", app)
        self.assertIn("/proxy/4721/#{target}", hook)
        self.assertNotIn("Quick open on this Mac", hook)
        self.assertNotIn("43123", hook)
        self.assertFalse((ROOT / "src" / "klimkit" / "apps" / "macos" / "codex-focus").exists())


if __name__ == "__main__":
    unittest.main()
