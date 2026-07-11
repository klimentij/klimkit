# Harness surface map

Use this as a discovery seed, not as authority. Before each inventory, record the installed harness version and refresh relevant locations from the official sources below. Add organization-managed, OS-managed, CLI-flag, environment-variable, wrapper-script, or vendor-specific layers found on the target.

## Official sources

- Codex customization: <https://learn.chatgpt.com/docs/customization/overview>
- Codex config layers: <https://learn.chatgpt.com/docs/config-file/config-basic>
- Codex `AGENTS.md`: <https://learn.chatgpt.com/docs/agent-configuration/agents-md>
- Codex subagents: <https://learn.chatgpt.com/docs/agent-configuration/subagents>
- Codex skills: <https://learn.chatgpt.com/docs/build-skills>
- Codex plugins: <https://learn.chatgpt.com/docs/plugins>
- Claude Code settings: <https://code.claude.com/docs/en/settings>
- Claude Code memory: <https://code.claude.com/docs/en/memory>
- Claude Code subagents: <https://code.claude.com/docs/en/subagents>
- Claude Code skills: <https://code.claude.com/docs/en/skills>
- Claude Code MCP: <https://code.claude.com/docs/en/mcp>
- Claude Code plugins: <https://code.claude.com/docs/en/plugins-reference>
- Claude Code configuration diagnostics: <https://code.claude.com/docs/en/debug-your-config>

## Codex seed surfaces

| Layer | Seed locations and checks |
|---|---|
| Instructions | User `~/.codex/AGENTS.md` and override; repository-root and nested `AGENTS.md`/override files; configured fallback filenames. |
| Settings | User `~/.codex/config.toml`; profile files; trusted-project `.codex/config.toml`; Unix `/etc/codex/config.toml`; CLI/config overrides. |
| Subagents | User `~/.codex/agents/`; project `.codex/agents/`; agent definitions embedded in config or supplied at launch. |
| Skills | User `$HOME/.agents/skills`; repository `.agents/skills` at applicable ancestors; admin `/etc/codex/skills`; bundled/system skills; legacy or installation-specific `~/.codex/skills`. |
| Rules, hooks, MCP | User, project, profile, and admin config layers; `.codex/rules/`, `.codex/hooks/`, hook scripts, and MCP entries in TOML. |
| Plugins | Enabled state in Codex config; installed plugin copies/cache; bundled catalogs; plugin skills, MCP, hooks, and apps. Prove enablement separately from cache presence. |
| State | Authentication, sessions/history, memories, databases, logs, app state, model caches, and worktrees. Default these to preservation or retention review. |

Codex only loads trusted project `.codex/` layers. Treat built-in/system skills and managed policy as separate from user customization. A fresh Codex process is required to prove the resolved post-cleanup surface.

## Claude Code seed surfaces

| Layer | Seed locations and checks |
|---|---|
| Instructions | User `~/.claude/CLAUDE.md`; project `CLAUDE.md` or `.claude/CLAUDE.md`; local `CLAUDE.local.md`; `.claude/rules/`; imports and ancestor/nested discovery. |
| Settings | User `~/.claude/settings.json`; project `.claude/settings.json`; local `.claude/settings.local.json`; managed settings/policy; CLI flags and environment variables. |
| Subagents | User `~/.claude/agents/`; project/ancestor `.claude/agents/`; plugin agents; managed agents; `--agents` launch definitions. |
| Skills and commands | User `~/.claude/skills/`; project/ancestor/nested `.claude/skills/`; `.claude/commands/`; plugin skills and commands; managed skills. |
| MCP | User and per-project entries in `~/.claude.json`; project `.mcp.json`; managed MCP; plugin MCP; subagent-inline MCP. Treat mixed state files as sensitive. |
| Plugins and hooks | Enabled plugin state in settings; installed marketplaces/cache/data; project and user hooks; plugin hooks, agents, skills, MCP, LSP, and monitors. |
| State | Credentials, project/session/task history, auto-memory, agent memory, policy, logs, caches, worktrees, and app/remote state. Default these to preservation or retention review. |

Use Claude's native views when available: `/status`, `/memory`, `/skills`, `/agents`, `/hooks`, `/mcp`, `/plugin`, and `/doctor`. Restart when a newly created or removed top-level discovery directory is not reflected live.

## Operating-system and transport layers

- macOS: LaunchAgents/LaunchDaemons, managed preferences/MDM, login items, Homebrew services, app support, shell startup, and cron.
- Linux/WSL: user/system systemd units and timers, `/etc` policy, XDG config/state/cache, shell startup, cron, containers, package managers, and lingering user services.
- Windows: managed policy/registry, Task Scheduler, services, AppData, PowerShell profiles, WSL boundaries, and package managers.
- Remote/container: SSH aliases and includes, bastions, provider exec tools, container images/volumes, devcontainer configuration, mounted homes, ephemeral filesystems, and distinct users on one host.

For every writer or synchronizer, trace both its live service and its source repository/template. Disabling only one side is not a stable cleanup.

## Classification rules

- `authoritative`: source intended to generate, install, or project another surface.
- `active`: proven loaded/enabled by precedence, runtime view, process, or service state.
- `derived`: installed/projected copy whose authority lives elsewhere.
- `cache`: reproducible catalog, package, download, or build cache.
- `evidence`: experiment/run snapshot, proof, trace, or immutable historical artifact.
- `state`: history, memory, database, worktree metadata, application state, or retention-governed data.
- `credential`: authentication, tokens, cookies, keys, or a mixed file likely to contain them.
- `unknown`: insufficient evidence; recommend manual review until resolved.
