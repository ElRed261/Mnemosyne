from __future__ import annotations

import datetime as dt
import platform
import shutil
import socket
import sys
from pathlib import Path

try:
    import textual as _textual_pkg
    from textual import work
    from textual.app import App, ComposeResult
    from textual.containers import Horizontal
    from textual.theme import Theme
    from textual.widgets import Footer, Header

    from mnemo_tui.screens.dashboard import DashboardScreen
    from mnemo_tui.widgets.banner import Banner
    from mnemo_tui.widgets.log_panel import LogPanel

    TEXTUAL_AVAILABLE = True
except Exception:  # noqa: BLE001
    TEXTUAL_AVAILABLE = False
    App = object  # type: ignore[assignment,misc]
    ComposeResult = object  # type: ignore[assignment]
    Theme = object  # type: ignore[assignment]


def _ts() -> str:
    return dt.datetime.now().strftime("[%H:%M:%S]")  # noqa: DTZ005


if TEXTUAL_AVAILABLE:

    class MnemoApp(App):  # type: ignore[valid-type]
        """Dark-only Mnemosyne TUI."""

        CSS_PATH = Path(__file__).with_name("theme.tcss")
        TITLE = "Mnemosyne"
        SUB_TITLE = "Data Engineering Zoomcamp"

        def __init__(self, **kwargs):  # type: ignore[no-untyped-def]
            super().__init__(**kwargs)
            self.online: bool = True

        def compose(self) -> ComposeResult:
            yield Header(show_clock=True)
            yield Banner(id="banner")
            yield DashboardScreen(id="dashboard")
            with Horizontal(id="logs"):
                yield LogPanel(title="General Log", id="log-general")
                yield LogPanel(title="Errors / Audit", id="log-errors")
            yield Footer()

        def on_mount(self) -> None:
            # Theme mnemosyne-dark — registers once, dark=True tokens
            try:
                self.register_theme(
                    Theme(
                        name="mnemosyne-dark",
                        primary="#7c5cff",
                        background="#0e0e10",
                        surface="#1a1a1e",
                        success="#2ecc71",
                        error="#ff4d4d",
                        dark=True,
                        variables={
                            "block-cursor-background": "#7c5cff",
                            "footer-key-foreground": "#7c5cff",
                        },
                    )
                )
                self.theme = "mnemosyne-dark"
            except Exception:  # noqa: BLE001,S110
                pass
            # ready log <1s — Mnemosyne ready — <device> (<os>/x64) — textual X — online bool
            try:
                self.log_general(self._ready_message())
            except Exception:  # noqa: BLE001,S110
                pass
            self.check_online()
            self.set_interval(15, self.check_online)

        def _ready_message(self) -> str:
            try:
                from mnemo_tui.services.system import _get_mnemo

                mnemo = _get_mnemo()
                root = Path.cwd()
                try:
                    cfg = mnemo.load_config(root)  # type: ignore[attr-defined]
                    device, _role = mnemo.detect_device(root, cfg)  # type: ignore[attr-defined]
                except Exception:  # noqa: BLE001
                    device = socket.gethostname()
                release = mnemo.os_release()  # type: ignore[attr-defined]
                os_name = release.get("PRETTY_NAME", platform.system())
            except Exception:  # noqa: BLE001
                device = socket.gethostname()
                os_name = platform.system()
            arch = platform.machine()
            py_ver = platform.python_version()
            try:
                textual_ver = _textual_pkg.__version__  # type: ignore[attr-defined]
            except Exception:  # noqa: BLE001
                textual_ver = "8.2.8"
            return f"Mnemosyne ready — {device} ({os_name}/{arch}) — textual {textual_ver} — online {self.online} — python {py_ver}"

        def log_general(self, message: str) -> None:
            try:
                panel = self.query_one("#log-general", LogPanel)
                # LogPanel.write auto-prefixes timestamp; we also prefix to match design
                if not message.lstrip().startswith("["):
                    message = f"{_ts()} {message}"
                panel.write(message)
            except Exception:  # noqa: BLE001,S110
                pass

        def log_error(self, message: str) -> None:
            try:
                panel = self.query_one("#log-errors", LogPanel)
                if not message.lstrip().startswith("["):
                    message = f"{_ts()} {message}"
                panel.write(message)
            except Exception:  # noqa: BLE001,S110
                pass

        @work(thread=True)
        def check_online(self) -> None:
            # reuse banner_info for internet+gh+updates with 5s timeouts, socket 3s degrade
            try:
                from mnemo_tui.services.system import banner_info

                info = banner_info()
                online = bool(info.get("internet"))
                gh_connected = bool(info.get("gh_connected"))
                updates = info.get("updates")
            except Exception:  # noqa: BLE001
                # fallback socket only
                try:
                    socket.create_connection(("1.1.1.1", 53), timeout=3)
                    online = True
                except OSError:
                    online = False
                gh_connected = False
                updates = None
            self.call_from_thread(self.update_banner, online, gh_connected, updates)
            # log status timestamped
            try:
                status = "Online" if online else "Offline"
                self.call_from_thread(self.log_general, f"{status} check — online={online} gh={gh_connected}")
                if not online:
                    self.call_from_thread(self.log_error, "Offline — network unavailable")
            except Exception:  # noqa: BLE001,S110
                pass

        def update_banner(self, online: bool, gh_connected: bool = False, updates: int | None = None) -> None:  # type: ignore[override]
            self.online = online
            try:
                banner = self.query_one("#banner", Banner)
                # new polished API
                if hasattr(banner, "set_banner"):
                    banner.set_banner(online=online, gh_connected=gh_connected, updates=updates)  # type: ignore[attr-defined]
                else:
                    banner.set_online(online)
            except Exception:  # noqa: BLE001,S110
                pass

        def action_quit(self) -> None:
            self.exit(0)

else:

    class MnemoApp:  # type: ignore[no-redef]
        def run(self) -> int:
            print("TUI not installed — run `uv sync` to enable")
            return 0


def run_tui() -> int:
    if not TEXTUAL_AVAILABLE:
        print("TUI not installed — run `uv sync` to enable")
        return 0
    # guard 80x24
    try:
        size = shutil.get_terminal_size()
        if size.columns < 80 or size.lines < 24:
            print("Terminal too small — need at least 80x24", file=sys.stderr)
            return 1
    except Exception:  # noqa: BLE001,S110
        pass
    app = MnemoApp()
    return int(app.run() or 0)
