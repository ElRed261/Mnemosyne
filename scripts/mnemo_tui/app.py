from __future__ import annotations

import shutil
import sys
from pathlib import Path

try:
    from textual import work
    from textual.app import App, ComposeResult
    from textual.containers import Horizontal
    from textual.widgets import Footer, Header

    from mnemo_tui.screens.dashboard import DashboardScreen
    from mnemo_tui.widgets.banner import Banner
    from mnemo_tui.widgets.log_panel import LogPanel

    TEXTUAL_AVAILABLE = True
except Exception:  # noqa: BLE001
    TEXTUAL_AVAILABLE = False
    App = object  # type: ignore[assignment,misc]
    ComposeResult = object  # type: ignore[assignment]


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
            self.check_online()
            self.set_interval(15, self.check_online)

        @work(thread=True)
        def check_online(self) -> None:
            # poll 1.1.1.1:53 via socket; simplified to avoid blocking
            import socket

            try:
                socket.create_connection(("1.1.1.1", 53), timeout=3)
                online = True
            except OSError:
                online = False
            self.call_from_thread(self.update_banner, online)

        def update_banner(self, online: bool) -> None:
            self.online = online
            try:
                banner = self.query_one("#banner", Banner)
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
