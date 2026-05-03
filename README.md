# Klimkit

![Klimkit. Agentic engineering across machines, under control.](assets/brand/klimkit-readme-hero.png)

Klimkit is a Python operator kit for setting up Codex-oriented machines without
a TUI or prompt-driven wizard. The install script installs the `kk` command.
`kk` creates a local TOML config, previews the exact file and service changes,
and applies them when you choose.

## Quick Install

```bash
curl -fsSL https://raw.githubusercontent.com/klimentij/klimkit/main/install.sh | bash
```

Supported targets are macOS, Linux, and WSL2. Native Windows is not supported;
install WSL2 and run the command inside Linux. Android/Termux is not a supported
target yet.

After installation:

```bash
source ~/.zshrc    # reload shell on zsh, or: source ~/.bashrc
kk                 # show config and setup instructions
```

The installer:

- clones the checkout at `~/klimkit` when it is missing
- uses the existing local checkout as-is on later runs, including uncommitted edits
- installs the `kk` launcher into `~/.local/bin`
- adds `~/.local/bin` to `.zshrc` or `.bashrc` when needed
- leaves config creation and service changes to explicit `kk` commands

## Local-First Workflow

Klimkit is intended to be forked, edited, tuned, and reapplied. Treat the Git
checkout as the source of truth for harness packs, templates, services, and app
code.

On the VM where you are editing:

```bash
./install.sh       # refresh the kk launcher from this local checkout
kk preview         # inspect what the local checkout would write
kk apply           # apply local changes to the current VM
```

The installer does not pull over an existing checkout. First install clones the
repo; after that, updates are explicit Git operations.

To send changes to another VM, use normal Git flow:

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

`kk pull` fast-forwards the current branch from its Git upstream and then runs
the same apply path as `kk apply`. It refuses to pull over local changes,
so a VM with its own edits must commit, stash, or apply its local checkout
directly with `kk apply`.

There is no automatic cross-VM sync by default. `[workers] live_sync = false`
keeps the supervisor from periodically fetching Git and copying Codex assets
into `$HOME`. Use `kk sync-live` only when you explicitly want that one-shot
Codex-pack sync on the current VM.

## First VM

The default setup assumes this is the first Klimkit VM. It enables both roles:

```toml
[components]
client = true
server = true
```

That means the VM gets local Codex/client assets and also runs the central
Switchboard server.

```bash
kk setup           # create ~/.config/klimkit/klimkit.toml and show the plan
kk preview         # review planned files and service actions
kk apply           # write files and enable/restart the supervisor service
kk doctor          # check config, repo, uv, and git
```

Switchboard runs locally at:

```text
http://127.0.0.1:4721/switchboard/
```

To expose it inside your tailnet with Tailscale Serve:

```bash
tailscale serve --bg --set-path /switchboard http://127.0.0.1:4721/switchboard
tailscale serve status
```

The tailnet URL will look like:

```text
https://<machine>.<tailnet>.ts.net/switchboard/
```

## Second VM

Use a client-only config on non-central VMs:

```bash
kk setup --client-only
```

This writes:

```toml
[components]
client = true
server = false
```

If a config already exists, `kk setup --client-only` updates the role flags in
`~/.config/klimkit/klimkit.toml` before showing the new preview.

Then point the second VM at the first VM's Switchboard server:

```toml
[workers]
switchboard_agent = true

[switchboard]
backend_url = "https://<first-vm>.<tailnet>.ts.net/switchboard"
auth_token = ""
```

If the first VM uses a Switchboard token, put the same token in
`switchboard.auth_token` on each client VM. Then run:

```bash
kk preview
kk apply
```

Klimkit generates the client agent config at:

```text
~/.config/klimkit/switchboard-agent.toml
```

The agent state DB lives at:

```text
~/.local/state/klimkit/switchboard-agent/state.sqlite3
```

## Roles And Components

Most machines only need these role switches:

```toml
[components]
client = true   # Codex pack, code-server settings, local client support
server = true   # central Switchboard server on this machine
```

Advanced component switches remain available in the same section:

```toml
codex = true
code_server = true
supervisor = true
switchboard = true
cc_connect = false
```

`cc_connect` is off by default because it needs a Telegram bot token, chat/admin
ids, and the cc-connect binary. Turn it on only after the private config is in
place.

Older configs with `[machine] profile = "client"` or `profile = "server"` still
load. New configs use `components.client` and `components.server` instead.

## Sensitive Local Config

Do not put tokens, chat ids, private hostnames, or machine-specific secrets in
tracked repo files. Use the home-local config files below.

Main Klimkit config:

```text
~/.config/klimkit/klimkit.toml
```

Use this for local role flags, Switchboard backend URLs, and Switchboard auth
tokens:

```toml
[switchboard]
backend_url = "https://<first-vm>.<tailnet>.ts.net/switchboard"
auth_token = "<shared-switchboard-token>"
```

Generated Switchboard server config:

```text
~/.config/klimkit/switchboard.toml
```

Klimkit rewrites this from `klimkit.toml` during `kk apply`, so edit
`klimkit.toml` rather than this generated file.

cc-connect Telegram config:

```text
~/.cc-connect/config.toml
```

Set Telegram secrets there:

```toml
[[projects]]
admin_from = "<telegram-user-id>"

[[projects.platforms]]
type = "telegram"

[projects.platforms.options]
allow_from = "<telegram-user-id-or-chat-id>"
token = "<telegram-bot-token>"
```

When `components.cc_connect = true`, Klimkit creates missing cc-connect config
files from blank templates, but it does not overwrite existing cc-connect files.
This keeps real Telegram secrets local.

Install the bundled cc-connect binary before enabling that component:

```bash
~/klimkit/src/klimkit/cc_connect/install.sh
```

Then set:

```toml
[components]
cc_connect = true
```

and apply:

```bash
kk preview
kk apply
```

## Important Paths

Klimkit writes only the paths represented in the preview and manifest.

```text
~/.config/klimkit/klimkit.toml
~/.config/klimkit/switchboard.toml
~/.config/klimkit/switchboard-agent.toml
~/.local/state/klimkit/
~/.local/state/klimkit/install/manifest.json
~/AGENTS.md
~/.codex/
~/.config/code-server/
~/.local/share/code-server/User/
~/.cc-connect/
```

Switchboard server DB:

```text
~/.local/state/klimkit/switchboard/switchboard.sqlite3
```

When backing up a running Switchboard DB, include the SQLite sidecars:

```text
switchboard.sqlite3
switchboard.sqlite3-wal
switchboard.sqlite3-shm
```

Supervisor service and logs:

```text
~/.config/systemd/user/klimkit.service
~/.local/state/klimkit/supervisor/state.json
~/.local/state/klimkit/supervisor/logs/
```

Every changed file is backed up before replacement. Repeated applies prune only
files that were owned by the previous manifest and are no longer in the new
plan.

## Common Commands

```bash
kk                 # show config path and next steps
kk setup           # first VM: client=true, server=true
kk setup --client-only
                   # second VM: client=true, server=false
kk setup --server-only
                   # central service VM without local client assets
kk preview         # render planned file writes, syncs, installs, and services
kk apply           # apply the plan, write backups, and write the manifest
kk doctor          # diagnose config, repo, uv, and git
kk serve           # run Switchboard in the foreground
kk update          # fast-forward the current checkout
kk pull            # fast-forward current branch, then apply this VM
```

Services are enabled only when you apply the plan. During testing or inspection,
skip service operations:

```bash
kk setup --skip-services
kk apply --skip-services
```

Client VMs install code-server by default when it is missing. Review the
preview first; the action is shown as the upstream `code-server` installer. To
manage code-server yourself, set `code_server.install_if_missing = false` in
`~/.config/klimkit/klimkit.toml` before applying.

## Repository Layout

```text
src/klimkit/                 Python package and runtime modules
packs/codex/                 Codex AGENTS/config/hooks/agents/skills pack
templates/code-server/       code-server config and user settings
templates/systemd/user/      Linux user service template
templates/launchd/           macOS LaunchAgent template
templates/cc-connect/        optional cc-connect defaults
tests/                       unittest suite
install.sh                   one-line installer entrypoint
```

## Development

```bash
uv run python -m unittest discover -s tests -q
./kk
```

Useful local checks:

```bash
bash -n install.sh
./kk setup --help
./kk apply --help
./kk serve --config src/klimkit/apps/switchboard/switchboard.toml --print-projections
```
