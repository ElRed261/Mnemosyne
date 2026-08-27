# Mnemosyne

> Local-first lab for Data Engineering Zoomcamp — with a beautiful dark TUI.

Mnemosyne keeps your Zoomcamp work reproducible across machines. Git is the source of truth, `uv` locks the Python env, and `Uranus` is just staging. The new `mnemo` TUI (Textual, dark Opencode-style) makes onboarding and daily work one-click.

**Stack:** Python 3.12 · uv · Textual 8.2.8 · Ruff · Pytest · Docker Compose (MinIO)

## Quick start

```bash
git clone git@github.com:ElRed261/Mnemosyne.git
cd Mnemosyne

# check everything
./mnemo doctor

# preview install (Arch/Manjaro) — then apply
./mnemo bootstrap --profile workstation
./mnemo bootstrap --profile workstation --apply

# one-time per machine (registers node + syncs deps + shows CURRENT.md)
./mnemo onboard PCrda --apply        # or laptop / tecnologia04 / Uranus --profile uranus

# daily loop
./mnemo start                        # sync + uv sync --locked + CURRENT.md
# ... small goal → run → verify → evidence ...
./mnemo end --done "what you proved" --next "next goal" --command "uv run ..." --expected "signal"
```

No network? Add `--offline` to `start`/`end` and later `./mnemo sync`.

## TUI

`mnemo` without args opens the TUI (TTY only). All classic commands stay headless for scripts/AI:

```bash
mnemo                 # → TUI (dark, panels System/Tools/Git/Uranus/Actions + dual logs)
mnemo --no-tui        # force CLI
echo | mnemo          # non-TTY → CLI
mnemo doctor --json
mnemo start --offline
```

**Inside the TUI:**
- **GitHub onboarding:** `gh auth login` or PAT, repo name editable (default `andry-de-zoomcamp`), public/private toggle, `gh auth status` gate
- **Uranus via Tailscale:** pick `.key` in 1 click (`~/.ssh` filtered `*.key,*.pem,id_*`), host + user editable, `tailscale status --json` autodetect, `ssh -o ConnectTimeout=5` test → ✅/❌
- **Dashboard:** 5 panels + General/Errors logs (auditable) + Online/Offline banner + shortcuts `d/s/e/b/q`
- **Safety:** never writes secrets to Git (only paths in `.mnemosyne/tui.json`), list-form subprocesses, `ConnectTimeout 5s`

Needs `uv sync` once — `textual` is a CORE dep (stdlib guard + hint if missing).

## Project layout

```
mnemo                      # sh wrapper → scripts/mnemo.py
scripts/mnemo.py           # CLI router (TTY guard, --no-tui)
scripts/mnemo_tui/         # TUI app, screens, widgets, services, theme.tcss
infra/uranus/compose.yaml  # MinIO datalake only, 127.0.0.1, ARM64 pinned
mnemosyne.toml             # nodes + remote + check_commands
CURRENT.md                 # continuity point (read after AGENTS.md)
AGENTS.md / GUIA_MNEMOSYNE.md  # operating contract
tests/                     # pytest + textual pilot
```

## Nodes

| Node | Arch | Role |
|------|------|------|
| PCrda | x86_64 | primary |
| laptop | x86_64 | mobile |
| tecnologia04 | x86_64 | institutional (isolated) |
| Uranus | ARM64 | staging only |

`arca-pg`, `n8n`, `9router` were removed — do not recreate. CasaOS Postgres is external (tunnel only).

## Remote (Uranus staging)

```bash
./mnemo remote status
./mnemo remote up datalake
./mnemo remote tunnel datalake   # 9100/9101 → localhost
./mnemo remote tunnel postgres   # 5432 → 15432
```

Ports are `127.0.0.1` only. ARM64 image pinned via `MNEMOSYNE_OBJECTSTORE_IMAGE`.

## Tests

```bash
uv run ruff check .
uv run pytest -q   # 74 tests (unit + integration + textual pilot)
```

## License

Private lab — not yet licensed for public reuse.
