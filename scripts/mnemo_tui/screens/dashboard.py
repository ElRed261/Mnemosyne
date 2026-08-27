from __future__ import annotations

try:
    from textual.app import ComposeResult
    from textual.containers import Container, Vertical
    from textual.widgets import Button, Static


    HAS_TEXTUAL = True
except Exception:  # noqa: BLE001
    HAS_TEXTUAL = False
    ComposeResult = object  # type: ignore[assignment]
    Container = object  # type: ignore[assignment]
    Static = object  # type: ignore[assignment]


if HAS_TEXTUAL:

    class DashboardScreen(Container):  # type: ignore[valid-type]
        def compose(self) -> ComposeResult:
            yield Static("System", classes="panel-title", id="panel-system")
            yield Static("Tools", classes="panel-title", id="panel-tools")
            yield Static("Git", classes="panel-title", id="panel-git")
            yield Static("Uranus", classes="panel-title", id="panel-uranus")
            with Vertical(id="panel-actions"):
                yield Static("Quick Actions", classes="panel-title")
                for label in ("doctor", "start", "end", "sync", "bootstrap", "device"):
                    yield Button(label, id=f"btn-{label}")

        def on_mount(self) -> None:
            self.refresh_panels()

        def refresh_panels(self) -> None:
            # placeholder: real panels refresh via workers in full impl
            pass

        def on_button_pressed(self, event: Button.Pressed) -> None:  # type: ignore[no-untyped-def]
            label = str(event.button.label)
            try:
                from mnemo_tui.widgets.log_panel import LogPanel  # noqa: WPS433

                general = self.app.query_one("#log-general", LogPanel)
                general.log(f"> {label}")
            except Exception:  # noqa: BLE001,S110
                pass
            # degrade: if no worker, just log. Real impl would run mnemo commands via subprocess.

else:

    class DashboardScreen:  # type: ignore[no-redef]
        pass
