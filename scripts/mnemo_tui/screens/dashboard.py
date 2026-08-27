from __future__ import annotations

try:
    from textual import work
    from textual.app import ComposeResult
    from textual.containers import Container, Vertical
    from textual.widgets import Button, Markdown, Static


    HAS_TEXTUAL = True
except Exception:  # noqa: BLE001
    HAS_TEXTUAL = False
    ComposeResult = object  # type: ignore[assignment]
    Container = object  # type: ignore[assignment]
    Static = object  # type: ignore[assignment]


if HAS_TEXTUAL:

    class DashboardScreen(Container):  # type: ignore[valid-type]
        def compose(self) -> ComposeResult:
            # ponytail: native Markdown for System (rich), Static for rest — minimal deps
            yield Markdown("**System**\n\nLoading…", id="panel-system", classes="panel skeleton")
            yield Static("Tools\nLoading…", id="panel-tools", classes="panel skeleton")
            yield Static("Git\nLoading…", id="panel-git", classes="panel skeleton")
            yield Static("Uranus\nLoading…", id="panel-uranus", classes="panel skeleton")
            with Vertical(id="panel-actions", classes="panel"):
                yield Static("Quick Actions", classes="panel-title")
                for label in ("doctor", "start", "end", "sync", "bootstrap", "device", "roadmap"):
                    yield Button(label, id=f"btn-{label}")

        def on_mount(self) -> None:
            self.refresh_panels()

        @work(thread=True)
        def refresh_panels(self) -> None:
            try:
                from pathlib import Path

                from mnemo_tui.services.system import (
                    banner_info,
                    collect_system,
                    collect_tools,
                    git_status_summary,
                    resolve_repo_safe,
                )
                from mnemo_tui.services.tailscale import tailscale_status

                # pony: repo discovery must work from any cwd (e.g. home) — fallback to install location, not just cwd
                try:
                    root = resolve_repo_safe(None, required=False)
                    if root is None or not (root / "mnemosyne.toml").exists():
                        fallback = Path(__file__).resolve().parents[3]
                        root = fallback if (fallback / "mnemosyne.toml").exists() else Path.cwd()
                except Exception:  # noqa: BLE001
                    fallback = Path(__file__).resolve().parents[3]
                    root = fallback if (fallback / "mnemosyne.toml").exists() else Path.cwd()
                sys_data = collect_system(root)
                tools_data = collect_tools()
                git_data = git_status_summary(root)
                # tailscale with 5s list-form
                try:
                    tail_data = tailscale_status(timeout=5)
                except Exception:  # noqa: BLE001
                    tail_data = {"ok": False, "ip": None, "detail": "not detected"}
                # also fetch banner for completeness (gh+updates) — offline degrade
                try:
                    _banner = banner_info()
                except Exception:  # noqa: BLE001
                    _banner = {}

                self.app.call_from_thread(self._update_system, sys_data)
                self.app.call_from_thread(self._update_tools, tools_data)
                self.app.call_from_thread(self._update_git, git_data)
                self.app.call_from_thread(self._update_uranus, tail_data)
                self.app.call_from_thread(self._clear_skeletons)
                # log timestamped to General
                try:
                    self.app.call_from_thread(self.app.log_general, "Panels refreshed")
                except Exception:  # noqa: BLE001,S110
                    pass
            except Exception as exc:  # noqa: BLE001
                try:
                    self.app.call_from_thread(self.app.log_error, f"refresh failed: {exc}")
                    self.app.call_from_thread(self._clear_skeletons)
                except Exception:  # noqa: BLE001,S110
                    pass

        def _update_system(self, data: dict) -> None:
            try:
                w = self.query_one("#panel-system", Markdown)
                lines = [
                    "**System**",
                    "",
                    f"- Hostname: {data.get('hostname', 'unknown')}",
                    f"- OS: {data.get('os', 'unknown')}",
                    f"- Arch: {data.get('arch', 'unknown')}",
                    f"- Python: {data.get('python', 'unknown')}",
                    f"- Device: {data.get('device', 'unknown')} ({data.get('role', 'unknown')})",
                    f"- Project: {data.get('project', 'unknown')}",
                ]
                w.update("\n".join(lines))
                w.remove_class("skeleton")
            except Exception:  # noqa: BLE001,S110
                pass

        def _update_tools(self, data: list[dict]) -> None:
            try:
                w = self.query_one("#panel-tools", Static)
                rows = ["**Tools**", ""]
                for item in data:
                    name = item.get("name", "?")
                    ok = item.get("ok")
                    detail = item.get("detail", "")
                    marker = "OK" if ok else "FALTA"
                    rows.append(f"{marker} {name}: {detail}")
                    if not ok and name in {"uv", "terraform", "docker", "jq"}:
                        rows.append(f"  → Install: {name} preview")
                w.update("\n".join(rows))
                w.remove_class("skeleton")
            except Exception:  # noqa: BLE001,S110
                pass

        def _update_git(self, data: dict) -> None:
            try:
                w = self.query_one("#panel-git", Static)
                branch = data.get("branch", "unknown")
                dirty = data.get("dirty")
                ahead = data.get("ahead", 0)
                behind = data.get("behind", 0)
                dirty_str = "dirty" if dirty else "clean"
                rows = [
                    "**Git**",
                    "",
                    f"Branch: {branch}",
                    f"Status: {dirty_str}",
                    f"Ahead: {ahead} Behind: {behind}",
                ]
                w.update("\n".join(rows))
                w.remove_class("skeleton")
            except Exception:  # noqa: BLE001,S110
                pass

        def _update_uranus(self, data: dict) -> None:
            try:
                w = self.query_one("#panel-uranus", Static)
                ok = data.get("ok")
                ip = data.get("ip")
                detail = data.get("detail", "")
                uranus_ip = data.get("uranus_ip")
                # try to get tui prefs for host/user/key
                host = "uranus-core-vnic"
                user = "unknown"
                key = "not set"
                try:
                    from pathlib import Path

                    from mnemo_tui.widgets.key_picker import load_tui_prefs

                    prefs = load_tui_prefs(Path.cwd())
                    host = prefs.get("last_host", host)
                    user = prefs.get("last_user", user)
                    kd = prefs.get("last_key_dir", "")
                    if kd:
                        key = kd
                except Exception:  # noqa: BLE001,S110
                    pass
                if ok and ip:
                    status = "✅ Connected" if ok else "❌ Unreachable"
                    rows = [
                        "**Uranus**",
                        "",
                        f"Host: {host}",
                        f"User: {user}",
                        f"Key: {key}",
                        f"Tailscale IP: {ip}",
                        f"Uranus IP: {uranus_ip or 'not detected'}",
                        f"Status: {status}",
                    ]
                else:
                    # degrade: not detected / unreachable
                    reason = detail or "not detected"
                    rows = [
                        "**Uranus**",
                        "",
                        f"Host: {host}",
                        f"User: {user}",
                        f"Key: {key}",
                        f"Tailscale: {reason}",
                        "❌ Unreachable — not detected" if "not detected" in reason.lower() else f"❌ Unreachable: {reason}",
                    ]
                w.update("\n".join(rows))
                w.remove_class("skeleton")
            except Exception:  # noqa: BLE001,S110
                pass

        def _clear_skeletons(self) -> None:
            for sid in ("#panel-system", "#panel-tools", "#panel-git", "#panel-uranus"):
                try:
                    w = self.query_one(sid)
                    w.remove_class("skeleton")
                except Exception:  # noqa: BLE001,S110
                    pass

        def _handle_error(self, msg: str) -> None:
            try:
                self.app.log_error(msg)  # type: ignore[attr-defined]
            except Exception:  # noqa: BLE001,S110
                pass

        def on_button_pressed(self, event: Button.Pressed) -> None:  # type: ignore[no-untyped-def]
            label = str(event.button.label)
            # ponytail: roadmap opens in-process screen, not subprocess
            if label == "roadmap":
                try:
                    # prefer App action, fallback to show_roadmap
                    if hasattr(self.app, "action_show_roadmap"):
                        self.app.action_show_roadmap()  # type: ignore[attr-defined]
                    elif hasattr(self.app, "show_roadmap"):
                        self.app.show_roadmap()  # type: ignore[attr-defined]
                    else:
                        self.app.log_general("Roadmap")  # type: ignore[attr-defined]
                except Exception as exc:  # noqa: BLE001
                    self._handle_error(f"roadmap open failed: {exc}")
                return
            # ponytail: delegate to worker, keep UI responsive <1s
            try:
                self.run_action(label)
            except Exception:  # noqa: BLE001
                try:
                    from mnemo_tui.widgets.log_panel import LogPanel  # noqa: WPS433

                    general = self.app.query_one("#log-general", LogPanel)
                    general.log(f"> {label}")
                except Exception:  # noqa: BLE001,S110
                    pass

        @work(thread=True)
        def run_action(self, label: str) -> None:
            # initial timestamped log
            try:
                self.app.call_from_thread(self.app.log_general, f"> {label}")  # type: ignore[attr-defined]
            except Exception:  # noqa: BLE001,S110
                pass
            # pony: absolute repo path + cwd ensures mnemo runs from any launch dir (home vs repo)
            from pathlib import Path as _P

            repo_root = _P(__file__).resolve().parents[3]
            if not (repo_root / "mnemosyne.toml").exists():
                try:
                    from mnemo_tui.services.system import resolve_repo_safe

                    cand = resolve_repo_safe(None, required=False)
                    if cand is not None and (cand / "mnemosyne.toml").exists():
                        repo_root = cand
                except Exception:  # noqa: BLE001,S110
                    pass
            mnemo_script = str(repo_root / "scripts" / "mnemo.py")
            # list-form command, never shell=True, 10s timeout per spec
            # map button labels to mnemo commands; device -> "device show"
            cmd_map = {
                "doctor": ["uv", "run", "python", mnemo_script, "doctor"],
                "start": ["uv", "run", "python", mnemo_script, "start"],
                "end": ["uv", "run", "python", mnemo_script, "end", "--help"],
                "sync": ["uv", "run", "python", mnemo_script, "sync"],
                "bootstrap": ["uv", "run", "python", mnemo_script, "bootstrap", "--help"],
                "device": ["uv", "run", "python", mnemo_script, "device", "show"],
                "roadmap": ["uv", "run", "python", mnemo_script, "roadmap", "show"],
            }
            cmd = cmd_map.get(label, ["uv", "run", "python", mnemo_script, label])
            try:
                import subprocess  # noqa: WPS433

                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10, check=False, cwd=str(repo_root))
                if result.stdout:
                    for line in result.stdout.splitlines():
                        if line.strip():
                            self.app.call_from_thread(self.app.log_general, line)  # type: ignore[attr-defined]
                if result.stderr:
                    for line in result.stderr.splitlines():
                        if line.strip():
                            self.app.call_from_thread(self.app.log_error, line)  # type: ignore[attr-defined]
                if result.returncode != 0 and not result.stderr and not result.stdout:
                    self.app.call_from_thread(self.app.log_error, f"{label} failed code {result.returncode}")  # type: ignore[attr-defined]
            except subprocess.TimeoutExpired:
                try:
                    self.app.call_from_thread(self.app.log_error, f"{label} timed out (10s)")  # type: ignore[attr-defined]
                except Exception:  # noqa: BLE001,S110
                    pass
            except Exception as exc:  # noqa: BLE001
                try:
                    self.app.call_from_thread(self.app.log_error, str(exc))  # type: ignore[attr-defined]
                except Exception:  # noqa: BLE001,S110
                    pass

else:

    class DashboardScreen:  # type: ignore[no-redef]
        pass
