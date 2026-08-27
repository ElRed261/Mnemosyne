from __future__ import annotations

import fnmatch
from pathlib import Path

ALLOWED_PATTERNS = ["*.key", "*.pem", "id_*"]

# ponytail: naive glob scan, per-account locks if throughput matters (not needed for ~/.ssh)
def list_keys(directory: Path) -> list[Path]:
    if not directory.exists() or not directory.is_dir():
        return []
    results: list[Path] = []
    for p in directory.iterdir():
        if not p.is_file():
            continue
        name = p.name
        for pat in ALLOWED_PATTERNS:
            if fnmatch.fnmatch(name, pat):
                # filter out *.pub and directories
                if name.endswith(".pub"):
                    break
                results.append(p)
                break
    return sorted(results)


def filter_keys(paths: list[Path]) -> list[Path]:
    out: list[Path] = []
    for p in paths:
        name = p.name
        if name.endswith(".pub"):
            continue
        for pat in ALLOWED_PATTERNS:
            if fnmatch.fnmatch(name, pat):
                out.append(p)
                break
    return sorted(out)


def load_tui_prefs(root: Path) -> dict:
    import json

    p = root / ".mnemosyne" / "tui.json"
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}


def save_tui_prefs(root: Path, data: dict) -> None:
    import importlib.util
    import json
    import sys
    from pathlib import Path as _P

    # only persist allowed keys, never secrets
    allowed = {"last_key_dir", "last_host", "last_user"}
    filtered = {k: v for k, v in data.items() if k in allowed}
    p = root / ".mnemosyne" / "tui.json"
    # resolve atomic_write without hard dependency on package path
    mod = None
    for name in ("mnemo", "__main__", "scripts.mnemo"):
        mod = sys.modules.get(name)
        if mod is not None and hasattr(mod, "atomic_write"):
            break
    else:
        mnemo_path = _P(__file__).resolve().parents[2] / "mnemo.py"
        spec = importlib.util.spec_from_file_location("mnemo", mnemo_path)
        assert spec and spec.loader
        mod = importlib.util.module_from_spec(spec)
        sys.modules["mnemo"] = mod
        spec.loader.exec_module(mod)
    atomic_write = mod.atomic_write  # type: ignore[attr-defined]
    atomic_write(p, json.dumps(filtered, indent=2))


try:
    from textual.containers import Container

    HAS_TEXTUAL = True
except Exception:  # noqa: BLE001
    HAS_TEXTUAL = False
    Container = object  # type: ignore[assignment]


if HAS_TEXTUAL:

    class KeyPicker(Container):  # type: ignore[valid-type]
        def __init__(self, initial_dir: Path | None = None, **kwargs):  # type: ignore[no-untyped-def]
            super().__init__(**kwargs)
            self.current_dir = initial_dir or Path.home() / ".ssh"
            self.selected: Path | None = None

        def get_keys(self) -> list[Path]:
            return list_keys(self.current_dir)

else:

    class KeyPicker:  # type: ignore[no-redef]
        def __init__(self, initial_dir: Path | None = None, **kwargs):  # type: ignore[no-untyped-def]
            self.current_dir = initial_dir or Path.home() / ".ssh"
            self.selected: Path | None = None

        def get_keys(self) -> list[Path]:
            return list_keys(self.current_dir)
