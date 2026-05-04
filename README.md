# Klimkit

![Klimkit. Agentic engineering across machines, under control.](assets/brand/klimkit-readme-hero.png)

Klimkit keeps an agent-ready machine reproducible. One repo owns the local instructions, harness packs, services, dashboards, and machine-specific settings needed to make a fresh VM behave like Klim's working environment. You edit the repo, preview exactly what will change, apply it locally, and use normal Git flow to carry the same operator setup to another machine.

## Quick Install

```bash
curl -fsSL https://raw.githubusercontent.com/klimentij/klimkit/main/install.sh | bash
```

Supported targets are macOS, Linux, and WSL2. Native Windows and Android/Termux are not supported targets yet.

After installation:

```bash
source ~/.zshrc    # or source ~/.bashrc
kk                 # show paths and setup commands
```

The installer clones or reuses `~/klimkit`, installs the `kk` launcher into `~/.local/bin`, and leaves config creation plus service changes to explicit `kk` commands.

## Tech Stack

- Python 3.11+ package with a stdlib `argparse` CLI
- `uv` for local execution, packaging, and dependency resolution
- TOML for the one local machine config
- SQLite for Switchboard server and agent state
- systemd user services and launchd LaunchAgents for the supervisor
- code-server for browser IDE access
- Tailscale Serve for private tailnet exposure
- Codex CLI projection for AGENTS guidance, config, hooks, subagents, and skills
- vanilla HTML/CSS/JS for Switchboard
- `unittest`, `coverage`, static pack validation, and optional live Codex startup smoke checks

`kk` reads the repo-local config, builds a previewable action plan, writes managed projections and services, and records ownership in a manifest so later applies can back up, prune, and uninstall only files Klimkit owns.

## Single Config

Klimkit uses one human-edited local config:

```text
~/klimkit/.klimkit/local/klimkit.toml
```

Runtime state lives beside it:

```text
~/klimkit/.klimkit/state/
~/klimkit/.klimkit/backups/
~/klimkit/.klimkit/logs/
```

Task artifacts and repo-work notes under `.klimkit/` are intentionally trackable in this repo. Machine-local config, runtime state, backups, and logs are ignored under `.klimkit/local/`, `.klimkit/state/`, `.klimkit/backups/`, and `.klimkit/logs/` because they can contain tokens or local DBs.

The default first VM enables both roles:

```toml
[components]
client = true
server = true
```

Client-only VMs report to the first VM:

```toml
[components]
client = true
server = false

[switchboard.agent]
enabled = true
backend_url = "https://<first-vm>.<tailnet>.ts.net/switchboard"
auth_token = ""
```

Server settings live in the same file:

```toml
[switchboard.server]
enabled = true
host = "127.0.0.1"
port = 4721
base_path = "/switchboard"
auth_token = ""
```

Telegram notifications are optional and also configured in the same TOML:

```toml
[notifications.telegram]
enabled = false
bot_token = ""
chat_id = ""
```

## Generated Projections

Generated projections are files Klimkit writes because another tool expects a specific location. Edit `.klimkit/local/klimkit.toml` and repo pack files, not generated projections.

Current projections include:

```text
~/.codex/AGENTS.md
~/.codex/config.toml
~/.codex/hooks/
~/.codex/agents/
~/.codex/skills/
~/.config/code-server/config.yaml
~/.local/share/code-server/User/
~/.config/systemd/user/klimkit.service
~/Library/LaunchAgents/com.klim.klimkit.plist
```

Codex keeps its default home at `~/.codex`. Klimkit treats that directory as a managed projection target, while Klimkit's own editable config and runtime state live under `~/klimkit/.klimkit`.

## Security Model

Klimkit is designed for a trusted personal machine or private tailnet, not arbitrary public internet exposure.

- Switchboard may run without a token only on loopback. Non-loopback server hosts require `switchboard.server.auth_token`.
- Tailscale Serve is the intended remote access boundary for Switchboard and code-server.
- code-server binds to loopback with `auth: none`; access should be delegated to Tailscale or another trusted local proxy.
- The code-server template disables workspace trust and allows automatic tasks so the operator box behaves consistently for agent work. Treat this as a trusted-workstation setting.
- Switchboard agent helper binds to loopback by default. Change `switchboard.agent.helper_host` only for a trusted proxy path.
- Switchboard-launched Codex terminals use trusted-local automation defaults, including sandbox/approval bypass flags when configured.
- If code-server is missing, `kk apply` may plan an external network installer. Review `kk preview` before applying, or set `code_server.install_if_missing = false`.

See `SECURITY.md` for the concise security notes.

## Workflow

On the VM where you are editing:

```bash
./install.sh
kk setup --skip-services
kk preview
kk apply
```

Use Git to move changes to another VM:

```bash
git status
git add <paths>
git commit -m "your change"
git push
```

Then run this on the other VM:

```bash
kk pull
```

`kk pull` fast-forwards the current branch from its upstream and then applies the local config. It refuses to pull over dirty local changes.

## Common Commands

```bash
kk                 # show config path and next steps
kk setup           # create .klimkit/local/klimkit.toml and show the plan
kk setup --client-only
kk setup --server-only
kk preview         # render planned projections, installers, and services
kk apply           # apply the plan, write backups, and update the manifest
kk doctor          # diagnose config, repo, uv, and git
kk serve           # run Switchboard in the foreground
kk update          # fast-forward the current checkout
kk pull            # fast-forward current branch, then apply this VM
```

Skip service operations during tests or inspection:

```bash
kk setup --skip-services
kk apply --skip-services
```

Switchboard runs locally at:

```text
http://127.0.0.1:4721/switchboard/
```

Expose it inside a tailnet with:

```bash
tailscale serve --bg --set-path /switchboard http://127.0.0.1:4721/switchboard
tailscale serve status
```

## Repository Layout

```text
src/klimkit/                 Python package and runtime modules
packs/codex/                 Codex AGENTS/config/hooks/agents/skills pack
templates/code-server/       code-server config and user settings
templates/systemd/user/      Linux user service template
templates/launchd/           macOS LaunchAgent template
.klimkit/tasks/              trackable task plans, proofs, and implementation notes
.klimkit/memory.md           trackable repo preferences and corrections
.klimkit/log.md              trackable repo work log
tests/                       unittest suite
install.sh                   one-line installer entrypoint
```

## Development

```bash
uv run python -m unittest discover -s tests -q
uv run coverage run -m unittest discover -s tests -q
uv run coverage report -m
```

Optional live Codex smoke test:

```bash
KLIMKIT_RUN_CODEX_SMOKE=1 uv run python -m unittest tests.test_codex_smoke -q
```

The smoke test is skipped by default because it requires an installed and signed-in Codex CLI.
