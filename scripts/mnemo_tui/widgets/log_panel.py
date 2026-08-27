from __future__ import annotations

try:
    from textual.widgets import RichLog

    HAS_TEXTUAL = True
except Exception:  # noqa: BLE001
    HAS_TEXTUAL = False
    RichLog = object  # type: ignore[assignment]


if HAS_TEXTUAL:

    class LogPanel(RichLog):  # type: ignore[valid-type]
        def __init__(self, title: str = "Log", **kwargs):  # type: ignore[no-untyped-def]
            super().__init__(**kwargs)
            self.title_text = title

        def log(self, message: str, *, error: bool = False) -> None:
            prefix = "[error] " if error else ""
            self.write(f"{prefix}{message}")

        def clear_log(self) -> None:
            self.clear()

else:

    class LogPanel:  # type: ignore[no-redef]
        def __init__(self, title: str = "Log", **kwargs):  # type: ignore[no-untyped-def]
            self.title_text = title
            self.lines: list[str] = []

        def log(self, message: str, *, error: bool = False) -> None:
            self.lines.append(message)

        def clear_log(self) -> None:
            self.lines.clear()
