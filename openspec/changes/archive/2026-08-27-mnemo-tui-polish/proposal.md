# Proposal: mnemo-tui-polish — Functional Logs & Dashboard Polish

## Intent
Close 2 WARNINGs from `mnemo-tui` (2026-08-27 PASS 22/22 74 tests): TUI renders dark but empty — `on_mount` only `check_online`, `LogPanel` never writes, `refresh_panels` pass, `on_button_pressed` logs `"> label"`. Polish makes it functional from boot.

## Scope

### In Scope
- **Logs**: `on_mount` → `Mnemosyne ready — <device> (<os/arch>) — textual 8.2.8 — online bool` in General; timestamp helpers → General vs Errors/Audit; each `check_online`/`gh`/`tailscale`/`ssh` appends `HH:MM:SS`.
- **Panels**: System (hostname/OS/arch/python/device/role/project); Tools (uv/terraform/docker/jq OK/FALTA+Install→preview); Git (branch/dirty/ahead-behind); Uranus (host/user/key/tailscale IP + `ssh -o ConnectTimeout=5` → ✅/❌ <6s + Up/Logs/Tunnel); banner `Online … Updates: N` / `Offline`.
- **Execution**: Actions `doctor/start/end/sync` via list-form 10s `@work(thread=True)` + `call_from_thread`; output→General, error→Audit; offline degrades.
- **Beauty**: `ui-ux-pro-max`+`impeccable` — tokens `#7c5cff/#0e0e10/#1a1a1e/#2ecc71/#ff4d4d`, `theme.tcss` spacing/borders/focus/skeletons, GSAP 150–300ms, Header clock, Footer dock; dark-only.

### Out of Scope
- Light theme/plugins; CasaOS postgres; `arca-pg/n8n/9router`; `0.0.0.0`/Caddy; new deps; PTY gh login.

## Capabilities

### New Capabilities
- None

### Modified Capabilities
- `mnemo-tui-shell`: startup logs, dual-log routing, theme tokens, clock/footer
- `mnemo-tui-dashboard`: real panels, worker execution, banner detail, skeletons
- `mnemo-tui-onboarding`: log integration (behavior polish)

## Approach
Reuse `mnemo.py:run/probe/banner_info/bootstrap_plan` via `_get_mnemo()`. Logs + `call_from_thread`; panels via `@work` workers; execution `["uv","run","python","scripts/mnemo.py",cmd]`; beauty registers `Theme` + CSS vars. Context7 Header/Footer/RichLog. `tui.json` paths-only.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `app.py` | Modified | on_mount logs, theme, workers |
| `screens/dashboard.py` | Modified | real panels + workers |
| `widgets/*`+`theme.tcss` | Modified | timestamps, banner, tokens/spacing/focus |
| `services/*` | Modified | list-run+timeouts, feed panels |
| `mnemo.py` | Unchanged | TTY/--no-tui guard |
| `pyproject.toml` | Unchanged | textual 8.2.8 pinned |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Probe blocks TUI | Med | @work thread + 3–5s timeout |
| Injection | Low | list-form + REPO_RE/HOST_RE |
| Pilot flakes | Low | find_spec guard + 80×24 + run_test |

## Alternatives Considered
Logs-only hotfix (leaves WARNING) vs `rich+questionary` (no grid) vs new JS deps — rejected; full polish reuses textual CSS.

## Rollback Plan
`git revert` + `uv sync --locked`; rm `.mnemosyne/tui.json`; `--no-tui` stays CLI pure.

## Dependencies
`textual 8.2.8`, `gh`/`tailscale`/`ssh` degrade 5s, `pacman -Qu` optional, `127.0.0.1` only.

## Success Criteria
- [ ] TTY shows `Mnemosyne ready — …` <1s; errors→Audit timestamped
- [ ] Panels real: Tools OK/FALTA, Git branch/dirty/ahead, Uranus ✅/❌ <6s; banner full text
- [ ] Actions non-blocking, output in logs (`script`+pilot verified)
- [ ] Dark tokens + spacing/borders/focus polished
- [ ] `ruff && pytest` green, 2 WARNINGs closed, `--no-tui doctor` unchanged

## Proposal question round
Interactive pre-locked: full polish, dark-only, textual 8.2.8, paths-only. No second round unless blocker.
