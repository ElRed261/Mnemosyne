from __future__ import annotations

try:
    from textual.widgets import Static

    HAS_TEXTUAL = True
except Exception:  # noqa: BLE001
    HAS_TEXTUAL = False
    Static = object  # type: ignore[assignment]


if HAS_TEXTUAL:

    class Banner(Static):  # type: ignore[valid-type]
        def __init__(self, **kwargs):  # type: ignore[no-untyped-def]
            super().__init__("Offline — checking…", **kwargs)
            self.online = False
            self.gh_connected = False
            self.updates: int | None = None

        def _render_text(self) -> str:
            if not self.online:
                return "Offline — GitHub unavailable"
            parts = ["Online"]
            parts.append("GitHub connected" if self.gh_connected else "GitHub not connected")
            if self.updates is not None:
                parts.append(f"Updates: {self.updates}")
            return " · ".join(parts)

        def set_online(self, online: bool) -> None:
            self.online = online
            self.update(self._render_text())

        def set_gh(self, connected: bool) -> None:
            self.gh_connected = connected
            self.update(self._render_text())

        def set_updates(self, n: int | None) -> None:
            self.updates = n
            self.update(self._render_text())

        def set_banner(self, *, online: bool, gh_connected: bool = False, updates: int | None = None) -> None:
            self.online = online
            self.gh_connected = gh_connected
            self.updates = updates
            self.update(self._render_text())

        def set_text(self, text: str) -> None:
            self.update(text)

else:

    class Banner:  # type: ignore[no-redef]
        def __init__(self, **kwargs):  # type: ignore[no-untyped-def]
            self.online = False
            self.gh_connected = False
            self.updates: int | None = None

        def _render_text(self) -> str:
            if not self.online:
                return "Offline — GitHub unavailable"
            parts = ["Online"]
            parts.append("GitHub connected" if self.gh_connected else "GitHub not connected")
            if self.updates is not None:
                parts.append(f"Updates: {self.updates}")
            return " · ".join(parts)

        def set_online(self, online: bool) -> None:
            self.online = online

        def set_gh(self, connected: bool) -> None:
            self.gh_connected = connected

        def set_updates(self, n: int | None) -> None:
            self.updates = n

        def set_banner(self, *, online: bool, gh_connected: bool = False, updates: int | None = None) -> None:
            self.online = online
            self.gh_connected = gh_connected
            self.updates = updates

        def set_text(self, text: str) -> None:
            pass
