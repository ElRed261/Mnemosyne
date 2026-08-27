# Design: mnemo-tui-polish — Functional Logs & Dashboard Polish

## Technical Approach

Reuse `mnemo.py` via `_get_mnemo()`. Services list-form `subprocess.run` 5-10s. Blocking I/O → `@work(thread=True)` + `call_from_thread` to `LogPanel`/`Banner`. Dual logs `[HH:MM:SS]`. `Theme("mnemosyne-dark")` in `App.on_mount` + `theme.tcss` vars. textual 8.2.8.

## Architecture Decisions

| Decision | Option A | Option B | Tradeoff | Chosen |
|---|---|---|---|---|
| Loader | Duplicate logic | `_get_mnemo()` import | Drift vs indirection | **`_get_mnemo()` per `services/*`** |
| Concurrency | `asyncio.create_task` | `@work(thread=True)`+`call_from_thread` | async blocks on `run` | **`check_online/refresh_panels/run_action` as `@work(thread=True)`** |
| Subprocess | `shell=True` | list-form `["uv","run","python","scripts/mnemo.py",cmd]` | Injection | **List-form + `REPO_RE`/`HOST_RE`, 5s probe/10s action, `ConnectTimeout=5`** |
| Theme | Hardcode `theme.tcss` | `Theme("mnemosyne-dark")+CSS vars` | Scattered tokens | **`Theme mnemosyne-dark #7c5cff/#0e0e10/#1a1a1e/#2ecc71/#ff4d4d dark+vars`** |
| Logs | `Static` | `RichLog` | Scroll/highlight | **`LogPanel(RichLog)+timestamp [HH:MM:SS]`** |
| System render | `Static` all | `Markdown` System | Cost vs list | **`Markdown` System, `Static` Tools/Git/Uranus** |
| Motion | GSAP | CSS `transition 150ms` | GSAP unavailable | **`transition 150ms` + opacity pulse skeletons** |

Beauty: **ui-ux-pro-max** dark + **impeccable** spacing/focus/rounded.

## Data Flow

```
App.on_mount → register_theme → log "[HH:MM:SS] Mnemosyne ready — <device> (<os>/x64) — textual 8.2.8 — online bool"
 ├─► @work check_online (socket 1.1.1.1:53 3s) → call_from_thread(update_banner+log)
 ├─► set_interval(15, check_online)
 └─► Dashboard.on_mount → @work refresh_panels (collect_* 5s) → call_from_thread(update+log)
Button.Pressed → @work run_action (list-form 10s) → call_from_thread(stdout→General, stderr→Errors)
```

### Seq 1 — Boot logs
```
on_mount → General "[HH:MM:SS] Mnemosyne ready…" <1s
       → check_online@work → call_from_thread(Banner Online/Offline + log)
```

### Seq 2 — Panel refresh
```
Dashboard.on_mount → refresh_panels@work
  collect_system|collect_tools|git_status_summary|tailscale_status (5s list-form)
  → call_from_thread: System(Markdown) Tools(OK/FALTA) Git(branch/dirty/ahead) Uranus(✅/❌/not detected)
  Skeleton Static("skeleton") clears on data; offline → degraded non-blocking
```

### Seq 3 — Action execute
```
Button.Pressed "doctor" → on_button_pressed@work → log "[HH:MM:SS] > doctor"
 → subprocess.run(["uv","run","python","scripts/mnemo.py","doctor"], timeout=10)
 → call_from_thread: stdout→General "[HH:MM:SS] …" stderr→Errors "[HH:MM:SS] …" banner Online/Offline
```

Layout: `Header(show_clock)` → `Banner` → `DashboardScreen(grid 2x2+Vertical)` → `Horizontal logs`; 80×24 guard.

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `scripts/mnemo_tui/app.py` | Modify | `on_mount` register theme + `_ts()`/`log_general`/`log_error`, `check_online@work` + banner `Online…Updates:N/Offline` |
| `screens/dashboard.py` | Modify | `refresh_panels@work` real collectors, `on_button_pressed@work` 10s dual routing, skeletons |
| `widgets/log_panel.py` | Modify | `timestamp [HH:MM:SS]` + `write(highlight,markup,max_lines)` |
| `widgets/banner.py` | Modify | `set_text` full Online/Offline + `set_updates()` |
| `theme.tcss` | Modify | Tokens `#7c5cff…`, dock, highlight, focus ring, skeleton 150ms, spacing 1 rounded |
| `services/system.py, github.py, ssh.py, tailscale.py` | Modify | List-form 5-10s, `REPO_RE`/`HOST_RE`/`USER_RE`, PAT stdin, `ConnectTimeout=5`, `tailscale --json` |
| `scripts/mnemo.py` | Unchanged | `maybe_launch_tui` TTY/`--no-tui`/`--repo` filter guard |
| `widgets/key_picker.py` | Unchanged | `tui.json` paths-only `atomic_write` allowed keys only |

## Interfaces / Contracts

```python
def _ts(): return dt.now().strftime("[%H:%M:%S]")
def log_general(self, m): self.query_one("#log-general", LogPanel).write(f"{_ts()} {m}")
def log_error(self, m): self.query_one("#log-errors", LogPanel).write(f"{_ts()} {m}", error=True)
@work(thread=True)
def check_online(self): ...  # socket 3s → call_from_thread
@work(thread=True, exclusive=True)
def refresh_panels(self): ...  # collectors 5s → call_from_thread
@work(thread=True)
def run_action(self, cmd: list[str]): subprocess.run(cmd, timeout=10)

register_theme(Theme(name="mnemosyne-dark", primary="#7c5cff", background="#0e0e10",
  surface="#1a1a1e", success="#2ecc71", error="#ff4d4d", dark=True,
  variables={"block-cursor-background":"#7c5cff","footer-key-foreground":"#7c5cff"}))
# tui.json: {"last_key_dir":"~/.ssh","last_host":"uranus-core-vnic"} # atomic_write filtered
```

Contracts: 80x24 guard, `--no-tui` pure CLI, `127.0.0.1` only, `tui.json` atomic paths-only, textual 8.2.8.

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Unit | `timestamp`, `collect_*`, `git dirty/ahead`, `banner online/offline`, `REPO_RE` | mock `run/socket/which`; assert `r"\[\d{2}:\d{2}:\d{2}\]"` |
| Integration | temp `git init` dirty, probe `uv --version`, `tui.json` roundtrip | `tmp_path` real git, `load/save_tui_prefs` |
| E2E (pilot) | `run_test(100,40)` → ready <1s, panels+skeletons, `doctor`→General, Tab, banner | `asyncio.run(pilot.press("tab"))`, `query_one("#log-general/#banner")` |

## Threat Matrix

Subprocess + `git -C` present — matrix applicable.

| Boundary | Cases | Applicability | Design response | Planned RED tests |
|---|---|---|---|---|
| Docs paths | `requirements.txt`, MDX exec | N/A — no doc execution | — | — |
| Git repo selection | `git -C` relative/absolute | **Applicable** — `resolve_repo` `git -C` | List-form + guard (`..`/`/tmp`/`; & \|`) `required=False` | `test_resolve_traversal_block`, `test_resolve_injection_block` |
| Commit state | staged/`commit -a`/empty | N/A — TUI never commits | — | — |
| Push state | tracking/first/refspec | N/A — delegated to `mnemo.py` | — | — |
| PR commands | `--head`/env/composed | N/A — no `gh pr create` | — | — |
| Shell injection | `; rm`/`$(cmd)`/`\|`/`` ` `` | **Applicable** — all `gh/ssh/tailscale/uv` | List-form never `shell=True`, `REPO_RE ^[A-Za-z0-9_.-]+$`, `HOST_RE ^[A-Za-z0-9.-]+$`, PAT stdin | `test_gh_repo_create_injection`, `test_ssh_host_injection`, `test_tailscale_timeout` |

Applicable timeout 5-10s, carry to `tasks.md` RED.

## Migration / Rollout

No migration. Archive merges deltas into `openspec/specs/mnemo-tui-*/spec.md`. Rollback `git revert` + `uv sync --locked` + `rm .mnemosyne/tui.json`. Dark-only, no flag.

## Open Questions

- [ ] Lazy-import `Markdown` for System to keep <1s cold start on Uranus ARM64?
- [ ] Hide `Updates: N` when not Arch (`which pacman is None`)?

