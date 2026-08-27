from __future__ import annotations

import re
from pathlib import Path

try:
    from textual.app import ComposeResult
    from textual.containers import Container
    from textual.widgets import Static


    HAS_TEXTUAL = True
except Exception:  # noqa: BLE001
    HAS_TEXTUAL = False
    ComposeResult = object  # type: ignore[assignment]
    Container = object  # type: ignore[assignment]

REPO_RE = re.compile(r"^[A-Za-z0-9_.-]+$")
HOST_RE = re.compile(r"^[A-Za-z0-9.-]+$")


def validate_repo_name(name: str) -> str | None:
    if not name or not name.strip():
        return "Repository name is required"
    if not REPO_RE.fullmatch(name.strip()):
        return "Invalid repository name"
    return None


def validate_host(host: str) -> str | None:
    if not host or not host.strip():
        return "Host is required"
    if not HOST_RE.fullmatch(host.strip()):
        return "Invalid host"
    if any(c in host for c in [";", "&", "|", "`", "$", "(", ")"]):
        return "Invalid host"
    return None


def validate_key_path(key: str) -> str | None:
    if not key:
        return "Key path required"
    if any(c in key for c in [";", "&", "|", "`", "$"]):
        return "Invalid key path"
    p = Path(key).expanduser()
    if not p.exists():
        return "Key file not found"
    return None


if HAS_TEXTUAL:

    class OnboardingScreen(Container):  # type: ignore[valid-type]
        def compose(self) -> ComposeResult:
            yield Static("Connect GitHub", classes="panel-title")
            yield Static("Pick SSH key", classes="panel-title")
            yield Static("Uranus", classes="panel-title")

else:

    class OnboardingScreen:  # type: ignore[no-redef]
        pass
