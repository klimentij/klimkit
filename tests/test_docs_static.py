import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class DocsStaticTests(unittest.TestCase):
    def test_readme_has_product_first_sections(self) -> None:
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        first_paragraph = next(
            paragraph
            for paragraph in text.split("\n\n")
            if paragraph and not paragraph.startswith("#") and not paragraph.startswith("!")
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


if __name__ == "__main__":
    unittest.main()
