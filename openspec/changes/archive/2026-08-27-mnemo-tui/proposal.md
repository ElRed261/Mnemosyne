# Proposal: mnemo-tui — Dark-only TUI

## Intent
TUI dark Opencode-style for onboarding + daily use. `mnemo` no-args → TUI; subcommands stay CLI pure for scripts/IA. Fixes invisible onboarding and opaque Git/device/Uranus state.

## Scope

### In Scope
- No-args TUI, `isatty()` + `--no-tui` guard (CI safe)
- Core `textual` dep (breaks 100% stdlib; doc trade-off)
- Dark-only, keyboard nav, 1-click `.key` picker (`~/.ssh`, filter `*.key,*.pem,id_*`), dual logs (general + error)
- GitHub: `gh auth login` + PAT paste, repo editable default `mnemosyne.toml:project.name`, public/private, `gh auth status` gate (user/avatar) before create, flows `Create` (`gh repo create`) + `Link existing`
- Uranus: editable host (`uranus-core-vnic`/`tailscale status --json`) + user, picker remembers last path in `.mnemosyne/tui.json` (paths only), test `ssh -i key -o ConnectTimeout=5 user@host "echo ok"` → ✅/❌
- Dashboard: System/Tools (`uv/terraform/jq/docker` OK/MISSING+Install)/Git (branch/dirty/ahead-behind)/Uranus (IP/key/tailscale/test/remote)/Quick actions (`doctor/start/end/sync/bootstrap/device`), footer shortcuts
- Online/offline banner (internet/GitHub/branch/services/pacman ` -Qu`); disables GitHub offline

### Out of Scope
- Light theme/plugins; CasaOS Postgres admin; `arca-pg/n8n/9router`; `0.0.0.0`/Caddy changes

## Capabilities

### New Capabilities
- `mnemo-tui-shell`: launcher, TTY guard, dark theme, nav, logs
- `mnemo-tui-onboarding`: GitHub auth+repo, Uranus/Tailscale+picker+validation
- `mnemo-tui-dashboard`: panels, actions, online banner

### Modified Capabilities
- None — `openspec/specs/` empty

## Approach
Add `textual` to `pyproject.toml`; guard import so CLI works without it (TUI error hint only). New `scripts/mnemo_tui/` reusing `run()` helper, no persistent tunnels. Prefs only in `.mnemosyne/tui.json` (gitignored).

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `pyproject.toml`/`uv.lock` | Modified | Add `textual` |
| `scripts/mnemo.py` | Modified | Dispatch + `--no-tui` + TTY guard |
| `scripts/mnemo_tui/**` | New | App/panels/clients |
| `.mnemosyne/tui.json` | New | Last key/host |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Stdlib break before `uv sync` | Med | Guard import; CLI unaffected |
| `textual` heavy on ARM/slow TTY | Low | Pinned ver, lazy launch |
| `gh`/`tailscale`/`ssh` flake | Med | 5s timeout, inline checks, offline gate |

## Alternatives Considered
`curses/urwid` — verbose, not "bonita"; `rich+questionary` — no dashboard; optional extra — violates CORE.

## Rollback Plan
Revert commit (`textual`+`mnemo_tui/`); `uv sync --locked`; delete `.mnemosyne/tui.json`. No remote state.

## Dependencies
`textual`, `gh`, `tailscale` (degrade), `ssh`. No new services.

## Success Criteria
- [ ] `mnemo` (TTY) opens TUI; `--no-tui`/non-TTY stays CLI
- [ ] `gh auth status` gates create; SSH test <6s ✅/❌ via `~/.ssh` picker
- [ ] Dashboard 5 panels + 2 logs + offline banner OK
- [ ] `uv run ruff check . && uv run pytest -q` green, no secrets

## Proposal question round
2 rounds pre-confirmed, locked as above. Assumptions: dark-only final, `textual` CORE, `tui.json` paths-only. No extra round needed.
