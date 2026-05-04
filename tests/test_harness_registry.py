import unittest
from pathlib import Path

from klimkit.harnesses import SUPPORTED_HARNESSES, enabled_harnesses, harness_by_name
from klimkit.harnesses.codex import codex_harness


class HarnessRegistryTests(unittest.TestCase):
    def test_only_codex_is_supported_now(self) -> None:
        self.assertEqual(sorted(SUPPORTED_HARNESSES), ["codex"])
        self.assertEqual([harness.name for harness in enabled_harnesses(codex_enabled=True)], ["codex"])
        self.assertEqual(enabled_harnesses(codex_enabled=False), [])
        with self.assertRaisesRegex(ValueError, "Unsupported harness: claude"):
            harness_by_name("claude")

    def test_codex_projection_contract(self) -> None:
        harness = codex_harness(home=Path("/home/user"), repo_root=Path("/repo"))
        projections = {projection.id: projection for projection in harness.projections}

        self.assertEqual(projections["codex-agents-md"].target, Path("/home/user/.codex/AGENTS.md"))
        self.assertEqual(projections["codex-config"].source, Path("/repo/packs/codex/config.toml"))
        self.assertNotIn("codex-hooks-json", projections)
        self.assertEqual(projections["codex-skills"].exclude_prefixes, (".system/",))
        self.assertEqual(harness.managed_roots, (Path("/home/user/.codex"),))


if __name__ == "__main__":
    unittest.main()
