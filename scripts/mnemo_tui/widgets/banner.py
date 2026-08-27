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
            super().__init__("Online", **kwargs)
            self.online = True

        def set_online(self, online: bool) -> None:
            self.online = online
            self.update("Online" if online else "Offline")

        def set_text(self, text: str) -> None:
            self.update(text)

else:

    class Banner:  # type: ignore[no-redef]
        def __init__(self, **kwargs):  # type: ignore[no-untyped-def]
            self.online = True

        def set_online(self, online: bool) -> None:
            self.online = online
