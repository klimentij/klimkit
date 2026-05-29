#!/usr/bin/env bash
set -euo pipefail

BIN_DIR="$HOME/.local/bin"
UV_VERSION="0.8.3"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"

usage() {
  cat <<'EOF'
Usage: install.sh

Installs or refreshes Klimkit from the current checkout and writes the kk launcher into ~/.local/bin.
Agentic engineering across machines, under control.
Configuration and apply are intentionally handled by kk after installation.

Clone Klimkit first, then run ./install.sh from that checkout. A fork is
recommended for syncing your own operator profile across machines, but any local
Klimkit checkout works:

  git clone https://github.com/<you>/klimkit.git ~/klimkit
  cd ~/klimkit
  ./install.sh

The installer never downloads Klimkit or clones the upstream repo for you. It
uses the local checkout exactly as-is, including uncommitted edits. Use kk update
or kk pull when you explicitly want to pull from Git.
EOF
}

if (($# > 0)); then
  case "$1" in
    -h|--help)
      usage
      exit 0
      ;;
    *)
      printf 'install.sh does not accept options. Run it without arguments.\n\n' >&2
      usage >&2
      exit 2
      ;;
  esac
fi

have_cmd() {
  command -v "$1" >/dev/null 2>&1
}

install_uv() {
  local os arch target asset base url tmp checksum_file actual expected
  if ! have_cmd curl || ! have_cmd tar; then
    printf 'curl and tar are required to install uv.\n' >&2
    exit 1
  fi
  os="$(uname -s)"
  arch="$(uname -m)"
  case "${os}:${arch}" in
    Darwin:arm64) target="aarch64-apple-darwin" ;;
    Darwin:x86_64) target="x86_64-apple-darwin" ;;
    Linux:aarch64|Linux:arm64) target="aarch64-unknown-linux-gnu" ;;
    Linux:x86_64) target="x86_64-unknown-linux-gnu" ;;
    *)
      printf 'Unsupported uv bootstrap platform: %s %s\n' "$os" "$arch" >&2
      printf 'Install uv manually, then rerun this installer.\n' >&2
      exit 1
      ;;
  esac
  asset="uv-${target}.tar.gz"
  base="https://github.com/astral-sh/uv/releases/download/${UV_VERSION}"
  url="${base}/${asset}"
  tmp="$(mktemp -d)"
  trap 'rm -rf "$tmp"' RETURN
  curl -fsSL "$url" -o "$tmp/$asset"
  curl -fsSL "${url}.sha256" -o "$tmp/${asset}.sha256"
  checksum_file="$(cat "$tmp/${asset}.sha256")"
  expected="${checksum_file%% *}"
  if have_cmd shasum; then
    actual="$(shasum -a 256 "$tmp/$asset" | awk '{print $1}')"
  else
    actual="$(sha256sum "$tmp/$asset" | awk '{print $1}')"
  fi
  if [[ "$actual" != "$expected" ]]; then
    printf 'uv checksum mismatch for %s\n' "$asset" >&2
    exit 1
  fi
  tar -xzf "$tmp/$asset" -C "$tmp"
  mkdir -p "$BIN_DIR"
  cp "$(find "$tmp" -type f -name uv -perm -111 | head -1)" "$BIN_DIR/uv"
  cp "$(find "$tmp" -type f -name uvx -perm -111 | head -1)" "$BIN_DIR/uvx"
  chmod +x "$BIN_DIR/uv" "$BIN_DIR/uvx"
}

append_path_hint() {
  local rc_file=""
  case "${SHELL:-}" in
    */zsh) rc_file="$HOME/.zshrc" ;;
    */bash) rc_file="$HOME/.bashrc" ;;
  esac
  if [[ -z "$rc_file" || ":$PATH:" == *":$BIN_DIR:"* ]]; then
    return
  fi
  mkdir -p "$(dirname "$rc_file")"
  touch "$rc_file"
  if ! grep -Fq "$BIN_DIR" "$rc_file"; then
    {
      printf '\n# Klimkit\n'
      printf 'export PATH="$HOME/.local/bin:$PATH"\n'
    } >>"$rc_file"
  fi
}

if ! have_cmd git; then
  printf 'git is required to install Klimkit.\n' >&2
  exit 1
fi

if [[ -f "$SCRIPT_DIR/pyproject.toml" && -d "$SCRIPT_DIR/src/klimkit" ]]; then
  CHECKOUT="$SCRIPT_DIR"
else
  CHECKOUT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null || true)"
fi
if [[ -z "$CHECKOUT" || ! -f "$CHECKOUT/pyproject.toml" || ! -d "$CHECKOUT/src/klimkit" ]]; then
  cat >&2 <<'EOF'
install.sh must be run from a local Klimkit checkout.

Clone the repo first, then run ./install.sh from the checkout.
Forking is recommended for syncing your own operator profile, but not required:

  git clone https://github.com/<you>/klimkit.git ~/klimkit
  cd ~/klimkit
  ./install.sh

This installer does not download Klimkit or clone the upstream repo for you.
EOF
  exit 1
fi

if ! have_cmd uv; then
  install_uv
  export PATH="$BIN_DIR:$PATH"
fi

printf 'Using local checkout: %s\n' "$CHECKOUT"

mkdir -p "$BIN_DIR"

cat >"$BIN_DIR/klimkit" <<EOF
#!/usr/bin/env bash
set -euo pipefail
export KLIMKIT_REPO_ROOT="${CHECKOUT}"
export KLIMKIT_PROG="klimkit"
exec uv run --project "${CHECKOUT}" klimkit "\$@"
EOF
chmod +x "$BIN_DIR/klimkit"

cat >"$BIN_DIR/kk" <<EOF
#!/usr/bin/env bash
set -euo pipefail
export KLIMKIT_REPO_ROOT="${CHECKOUT}"
export KLIMKIT_PROG="kk"
exec uv run --project "${CHECKOUT}" kk "\$@"
EOF
chmod +x "$BIN_DIR/kk"

append_path_hint

cat <<EOF
Klimkit
Agentic engineering across machines, under control.

Installed.

Next:
  source ~/.zshrc    # or: source ~/.bashrc
  kk                 # show config and setup instructions

Common commands:
  kk setup           # first VM: client=true, server=true
  kk setup --client-only
                     # second VM: client=true, server=false
  kk preview         # show the install plan
  kk apply           # apply managed files and services
  kk doctor          # diagnose local setup
  kk pull            # pull current branch and apply on this VM
  kk serve           # run Switchboard
EOF
