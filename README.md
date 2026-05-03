# Klimkit

![Klimkit. Agentic engineering across machines, under control.](assets/brand/klimkit-readme-hero.png)

Klimkit is a Python operator kit for setting up Codex-oriented machines without a
TUI or prompt-driven wizard. The install script only installs the command. The
`kk` command then shows where config lives, how to preview changes, and how to
apply them when you are ready.

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

- clones or updates the checkout at `~/klimkit`
- installs `kk` and `klimkit` launchers into `~/.local/bin`
- adds `~/.local/bin` to `.zshrc` or `.bashrc` when needed
- leaves config creation and apply to explicit `kk` commands

## Getting Started

```bash
kk                 # show config path and next steps
kk setup           # create ~/.config/klimkit/klimkit.toml and show the plan
kk preview         # render planned file writes, syncs, installs, and services
kk apply --yes     # apply the plan, write backups, and write the manifest
kk doctor          # diagnose config, repo, uv, and git
kk serve           # run Switchboard on http://127.0.0.1:4721/switchboard2/
kk update          # fast-forward the current checkout
```

`klimkit` is the full command name. `kk` is the short alias and behaves the same
way.

There is no interactive TUI. To change behavior, edit:

```text
~/.config/klimkit/klimkit.toml
```

Then run:

```bash
kk preview
kk apply --yes
```

## Profiles

`kk setup` defaults to the `client` profile. It installs the Codex harness pack,
code-server settings, and the Klimkit supervisor.

```bash
kk setup
```

Use `server` for a central machine that should also run Switchboard and
cc-connect:

```bash
kk setup --profile server
```

Services are enabled only when you apply the plan. During testing or inspection,
skip service operations:

```bash
kk setup --skip-services
kk apply --yes --skip-services
```

Klimkit does not install code-server by default during `apply`. If you want
Klimkit to run the upstream code-server installer when the binary is missing,
set `code_server.install_if_missing = true` in the TOML first and review the
preview before applying.

## Managed Paths

Klimkit writes only the paths represented in the preview and manifest.

```text
~/.config/klimkit/klimkit.toml
~/.local/state/klimkit/
~/.local/state/klimkit/install/manifest.json
~/AGENTS.md
~/.codex/
~/.config/code-server/
~/.local/share/code-server/User/
~/.cc-connect/
```

Every changed file is backed up before replacement. Repeated applies prune only
files that were owned by the previous manifest and are no longer in the new
plan.

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

Klimkit intentionally keeps machine-private values out of tracked templates.
Tokens, private hostnames, and machine-specific paths belong in local TOML or
environment files.

## Development

```bash
uv run python -m unittest discover -s tests -q
./klimkit --help
./kk
```

Useful local checks:

```bash
bash -n install.sh
./klimkit setup --help
./klimkit apply --help
./klimkit serve --config src/klimkit/apps/switchboard2/switchboard2.toml --print-projections
```
