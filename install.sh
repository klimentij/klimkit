#!/usr/bin/env bash
set -euo pipefail

REPO_URL="https://github.com/klimentij/klimki.git"
BRANCH="os-prep"
CHECKOUT="$HOME/klimkit"
BIN_DIR="$HOME/.local/bin"
UV_VERSION="0.8.3"

usage() {
  cat <<'EOF'
Usage: install.sh

Installs Klimkit into ~/klimkit and writes kk/klimkit launchers into ~/.local/bin.
Agentic engineering across machines, under control.
Configuration and apply are intentionally handled by kk after installation.
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

if ! have_cmd uv; then
  install_uv
  export PATH="$BIN_DIR:$PATH"
fi

if [[ -d "$CHECKOUT/.git" ]]; then
  if ! git -C "$CHECKOUT" diff --quiet || ! git -C "$CHECKOUT" diff --cached --quiet; then
    printf 'Checkout has local changes: %s\n' "$CHECKOUT" >&2
    printf 'Resolve them, then rerun the installer.\n' >&2
    exit 1
  fi
  git -C "$CHECKOUT" fetch origin "$BRANCH"
  git -C "$CHECKOUT" checkout "$BRANCH"
  git -C "$CHECKOUT" pull --ff-only origin "$BRANCH"
else
  mkdir -p "$(dirname "$CHECKOUT")"
  git clone --branch "$BRANCH" "$REPO_URL" "$CHECKOUT"
fi

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
  kk setup           # create ~/.config/klimkit/klimkit.toml
  kk preview         # show the install plan
  kk apply --yes     # apply managed files and services
  kk doctor          # diagnose local setup
  kk serve           # run Switchboard
EOF
