# Klimkit Harness Reference

This directory carries public-safe reference copies of Klimkit's repo-managed Codex harness pack.

| Source Pack File | Plugin Treatment |
| --- | --- |
| `packs/codex/AGENTS.md` | Copied to `reference/AGENTS.md` for workflow reference and summarized in `skills/klimkit-workflow/`. |
| `packs/codex/agents/` | Copied to `reference/agents/` for users who want the repo-managed subagent setup. |
| `packs/codex/skills/` | Copied into the plugin's installable `skills/` surface. |
| `packs/codex/hooks/` | Copied to `reference/hooks/`; activation remains a repo-managed `kk apply` responsibility. |
| `packs/codex/config.toml` | Copied to `reference/config.toml`; machine-level Codex config stays outside plugin installation. |

Codex plugins load bundled skills. Machine-level Codex files such as `AGENTS.md`, `config.toml`, subagent TOML, and Stop hooks still need explicit user configuration or Klimkit's repo-managed projection path.

The reference config intentionally omits VM-local plugin/connector tables, auth state, project trust, and hook trust. Those belong in each user's local Codex config, not in a public plugin package.
