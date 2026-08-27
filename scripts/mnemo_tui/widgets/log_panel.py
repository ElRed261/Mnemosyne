from __future__ import annotations

import datetime as dt
import re

_TS_RE = re.compile(r"^\[\d{2}:\d{2}:\d{2}\]")


def _ts() -> str:
    return dt.datetime.now().strftime("[%H:%M:%S]")  # noqa: DTZ005


try:
    from textual.widgets import RichLog

    HAS_TEXTUAL = True
except Exception:  # noqa: BLE001
    HAS_TEXTUAL = False
    RichLog = object  # type: ignore[assignment]


if HAS_TEXTUAL:

    class LogPanel(RichLog):  # type: ignore[valid-type]
        def __init__(self, title: str = "Log", **kwargs):  # type: ignore[no-untyped-def]
            # ponytail: highlight/markup/max_lines are native RichLog features, no extra dep
            kwargs.setdefault("highlight", True)
            kwargs.setdefault("markup", True)
            kwargs.setdefault("max_lines", 2000)
            kwargs.setdefault("wrap", True)
            super().__init__(**kwargs)
            self.title_text = title

        def write(self, content: str, *args, **kwargs) -> None:  # type: ignore[override]
            # ensure timestamp prefix unless already present
            text = str(content)
            if not _TS_RE.search(text[:12]):
                text = f"{_ts()} {text}"
            # textual RichLog expects str/Renderable
            super().write(text, *args, **kwargs)  # type: ignore[arg-type]

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

        def write(self, content: str, *args, **kwargs) -> None:  # type: ignore[no-untyped-def]
            text = str(content)
            if not _TS_RE.search(text[:12]):
                text = f"{_ts()} {text}"
            self.lines.append(text)

        def log(self, message: str, *, error: bool = False) -> None:
            prefix = "[error] " if error else ""
            self.write(f"{prefix}{message}")

        def clear_log(self) -> None:
            self.lines.clear()
