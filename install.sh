#!/usr/bin/env bash
set -euo pipefail
# Mnemosyne one-line installer — ponytail: minimal, idempotent, no deps beyond git/curl
# Usage:  curl -fsSL https://raw.githubusercontent.com/ElRed261/Mnemosyne/main/install.sh | bash
# Env:    MNEMO_DIR=~/my-mnemo  MNEMO_REPO=https://github.com/ElRed261/Mnemosyne.git

REPO_URL="${MNEMO_REPO:-https://github.com/ElRed261/Mnemosyne.git}"
INSTALL_DIR="${MNEMO_DIR:-$HOME/Mnemosyne}"
BIN_DIR="${HOME}/.local/bin"

say() { printf "\033[1;34m==>\033[0m %s\n" "$*"; }
ok()  { printf "\033[1;32m✔\033[0m %s\n" "$*"; }
warn(){ printf "\033[1;33m!\033[0m %s\n" "$*" >&2; }

# ponytail: detect existing checkout to avoid double clone
if [ -d "$INSTALL_DIR/.git" ] && [ -f "$INSTALL_DIR/mnemosyne.toml" ]; then
  say "Mnemosyne already at $INSTALL_DIR — updating"
  git -C "$INSTALL_DIR" pull --ff-only || warn "pull failed, keeping local"
else
  if [ -e "$INSTALL_DIR" ] && [ ! -d "$INSTALL_DIR/.git" ]; then
    warn "$INSTALL_DIR exists and is not a git repo — choose another MNEMO_DIR"
    exit 1
  fi
  if ! command -v git >/dev/null 2>&1; then
    echo "git not found — install git first" >&2; exit 1
  fi
  say "Cloning $REPO_URL → $INSTALL_DIR"
  git clone "$REPO_URL" "$INSTALL_DIR"
fi

cd "$INSTALL_DIR"

# ponytail: uv is the only hard dep for TUI; install via official script if missing
if ! command -v uv >/dev/null 2>&1; then
  if [ -x "$HOME/.local/bin/uv" ]; then
    export PATH="$HOME/.local/bin:$PATH"
  else
    say "uv not found — installing via astral.sh"
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
  fi
fi

# ponytail: ensure Python 3.12 for project (system may be 3.14), uv handles isolated
if command -v uv >/dev/null 2>&1; then
  uv python install 3.12 >/dev/null 2>&1 || true
  say "Syncing Python env (uv sync --locked)"
  uv sync --locked
else
  warn "uv still not in PATH — open new shell and run: uv sync"
fi

# ponytail: global `mnemo` via ~/.local/bin symlink — no sudo needed, no pipx, no entry_points
mkdir -p "$BIN_DIR"
ln -sf "$INSTALL_DIR/mnemo" "$BIN_DIR/mnemo"
chmod +x "$INSTALL_DIR/mnemo"

# ensure BIN_DIR in PATH for current shell check
case ":$PATH:" in
  *":$BIN_DIR:"*) ;;
  *) warn "Add to your shell: export PATH=\"\$HOME/.local/bin:\$PATH\"  (zsh: ~/.zshrc, bash: ~/.bashrc)";;
esac

say "Verifying install"
if "$BIN_DIR/mnemo" --no-tui doctor --soft >/dev/null 2>&1; then
  ok "mnemo doctor OK"
else
  "$BIN_DIR/mnemo" --no-tui doctor --soft || true
fi

cat <<EOF

✔ Mnemosyne installed at $INSTALL_DIR
  Global command: $BIN_DIR/mnemo  (ensure ~/.local/bin is in PATH)

  Try:
    mnemo              # TUI dark (TTY)
    mnemo --no-tui doctor
    mnemo --no-tui start

  Update later:  git -C $INSTALL_DIR pull --ff-only && uv sync --locked
  Docs:          $INSTALL_DIR/README.md  +  GUIA_MNEMOSYNE.md

EOF
