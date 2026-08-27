# Design: mnemo-tui — Dark-only TUI

## Technical Approach

Guarded `textual` TUI preserving stdlib `scripts/mnemo.py`. `mnemo.py` router: no-args+TTY+no `--no-tui`+`textual` present → TUI, else CLI pure. `scripts/mnemo_tui/` reuses `run()`/`load_config()`/`atomic_write()`; no services, no `arca-pg/n8n/9router`, Postgres via `127.0.0.1` tunnel only. List-form `run([...])`, 5s timeouts, textual workers. Only `.mnemosyne/tui.json` persists (paths only, gitignored).

## Architecture Decisions

| Decision | Option | Trade-off | Chosen |
|----------|--------|-----------|--------|
| Lib | textual / curses / rich+questionary | curses no grid/theme, rich no dashboard | **textual ≥0.80** |
| Isolation | guarded vs always-import | always breaks pre-`uv sync`/CI | **guarded `find_spec()==None → hint`** |
| Router | thin `mnemo.py` vs inline | inline bloats 1k stdlib file | **`mnemo.py` dispatch, `app.py` owns TUI** |
| Theme | dark-only vs light+dark | light doubles tokens | **dark-only** `bg#0e0e10 surface#1a1a1e accent#7c5cff ok#2ecc71 err#ff4d4d muted#8a8a93` |
| Online | 15s poll vs event | event misses flaps | **poll `1.1.1.1:53` + `gh auth status` → `App.online` banner** |
| Persist | paths-only vs full | full leaks secrets | **`.mnemosyne/tui.json` `{last_key_dir,last_host,last_user}`** |

## Data Flow

```
mnemo(no-args,TTY) → mnemo.py → textual? yes→MnemoApp.run() / no→"TUI not installed — run `uv sync`…"
                 └subcommand/--no-tui/non-TTY → CLI handlers (unchanged)
MnemoApp: Header(device/role/branch) + Banner(poll) + Grid 3×2(System/Tools/Git/Uranus/Actions) → Dual RichLog(General,Errors/Audit) + Footer(q/?/Tab/Enter)
 Workers: System(os_release), Tools(probe×5 3s), Git(git_status/ahead_behind), Uranus(tailscale --json, ssh test), Actions(run→logs)
```
Services `github/ssh/tailscale/system.py`; Screens `onboarding.py`; Widgets `banner/log_panel/key_picker/panels/*`.

## Sequence Diagrams

### (1) GitHub Auth Gate
```
open onboarding → `gh auth status --json`(5s worker)
 ├0 → "Connected as @andry" → enable Create
 └≠0 → "Not connected" → Create disabled "Connect GitHub to continue"
[gh auth login] or PAT(Password, never logged) → `gh auth login --with-token` → re-probe
```

### (2) SSH Test
```
picker glob ~/.ssh/{*.key,*.pem,id_*} → select → persist last_key_dir
[Test] → `ssh -i <key> -o ConnectTimeout=5 -o StrictHostKeyChecking=accept-new user@host "echo ok"`
 ├ok<6s → ✅ Connected
 └timeout/rc≠0 → ❌ Unreachable: first_line
```

### (3) Bootstrap
```
Actions[bootstrap workstation] → modal `bootstrap_plan()` preview (`pacman -Syu …`+notes)
[Apply]→confirm→worker `run(check=True)` per cmd → General/Errors
 └ok → hint `uv sync --locked` + doctor refresh; offline→preview only
```

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `pyproject.toml` | Modify | add `textual>=0.80` |
| `scripts/mnemo.py` | Modify | `--no-tui` + `maybe_launch_tui()` (isatty+find_spec) |
| `scripts/mnemo_tui/__init__.py` | Create | pkg |
| `scripts/mnemo_tui/app.py` | Create | `MnemoApp` dark CSS, 80×24 guard, poll |
| `scripts/mnemo_tui/screens/dashboard.py` | Create | 5 panels + logs |
| `scripts/mnemo_tui/screens/onboarding.py` | Create | GitHub+Uranus modals |
| `scripts/mnemo_tui/widgets/*` | Create | banner, log_panel, key_picker, panels/* |
| `scripts/mnemo_tui/services/*` | Create | github, ssh, tailscale, system wrappers |
| `scripts/mnemo_tui/theme.tcss` | Create | tokens |
| `.mnemosyne/tui.json` | Create runtime | gitignored, atomic_write |

## Interfaces / Contracts

```python
def maybe_launch_tui(argv: list[str]) -> int | None:
    if "--no-tui" in argv or argv: return None
    if not sys.stdin.isatty() or not sys.stdout.isatty(): return None
    if importlib.util.find_spec("textual") is None:
        print("TUI not installed — run `uv sync` to enable"); return 0
    from mnemo_tui.app import run_tui; return run_tui()
# list run([...]) only; validate repo ^[A-Za-z0-9_.-]+$ host ^[A-Za-z0-9.-]+$ key exists
```

## Testing Strategy

| Layer | What | Approach |
|-------|------|----------|
| Unit | `maybe_launch_tui`, `gh_auth_status` parse, picker filter, `tui.json` | `pytest` mock `isatty`/`find_spec`/`run`; no textual |
| Integration | panels data (Tools OK/MISSING, Git dirty/ahead, tailscale IP) | `pytest` temp repo `collect_tools()`/`git_status()` |
| E2E | pilot: open, Tab nav, gate, SSH ✅/❌, banner, 80×24 | `textual.pilot` snapshot, `WORKER_TIMEOUT=6` |
| Lint | `ruff check . && pytest -q` | `mnemosyne.toml:check_commands` |

## Threat Matrix

Subprocess + `git -C` ⇒ matrix required.

| Boundary | Cases | Applicability | Response | RED tests |
|----------|-------|---------------|----------|-----------|
| Docs paths | `requirements.txt`, MD exec | N/A: never executed | — | — |
| Git repo selection | `git -C`, relative/absolute | **Applicable** | reuse `resolve_repo()` | RED: `..`, `/tmp/repo`, `git -C /tmp` same root |
| Commit state | staged, `commit -a` | N/A: delegates to CLI | — | — |
| Push state | tracking, first push | N/A: `sync_repository` unchanged | — | — |
| PR commands | `--head`, env prefix | N/A: no PR automation | — | — |
| Shell injection | `; rm`, `&& id` in repo/host/key | **Applicable** | `shell=False` list run, regex + exists | RED: `a; echo pwn`, `x && id` rejected |

## Migration / Rollout

No migration. `uv sync --locked` installs textual. Rollback `git revert && uv sync --locked && rm .mnemosyne/tui.json`. `--no-tui`/non-TTY disables. No Caddy/`0.0.0.0`, no volume wipe.

## Open Questions

- [ ] `gh auth login` PTY in worker vs external handoff → pilot validates; fallback hint "Run `gh auth login` then Refresh"
- [ ] `pacman -Qu` banner interval → 60s proposal, confirm on slow TTY
