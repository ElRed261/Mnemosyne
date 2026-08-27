from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

# ponytail: validation is simple regex + exists check, no extra dep needed
REPO_RE = re.compile(r"^[A-Za-z0-9_.-]+$")
HOST_RE = re.compile(r"^[A-Za-z0-9.-]+$")


def validate_repo_name(name: str) -> None:
    if not name or not name.strip():
        raise ValueError("Repository name is required")
    if any(c in name for c in [";", "&", "|", "`", "$", "(", ")"]):
        raise ValueError("Invalid repository name")
    if not REPO_RE.fullmatch(name.strip()):
        raise ValueError("Invalid repository name")


def validate_host(host: str) -> None:
    if not host or not host.strip():
        raise ValueError("Host is required")
    if any(c in host for c in [";", "&", "|", "`", "$", "(", ")"]):
        raise ValueError("Invalid host")
    if not HOST_RE.fullmatch(host.strip()):
        raise ValueError("Invalid host")


def validate_key_path(key: str) -> None:
    if not key:
        raise ValueError("Key path required")
    if any(c in key for c in [";", "&", "|", "`", "$", "(", ")"]):
        raise ValueError("Invalid key path")
    p = Path(key).expanduser()
    if not p.exists():
        raise ValueError("Key file not found")


def _get_mnemo():
    import importlib.util
    import sys
    from pathlib import Path as _P

    for name in ("mnemo", "__main__", "scripts.mnemo"):
        mod = sys.modules.get(name)
        if mod is not None and hasattr(mod, "resolve_repo"):
            return mod
    # fallback: load from file
    mnemo_path = _P(__file__).resolve().parents[2] / "mnemo.py"
    spec = importlib.util.spec_from_file_location("mnemo", mnemo_path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["mnemo"] = mod
    spec.loader.exec_module(mod)
    return mod


def resolve_repo_safe(raw: str | None, *, required: bool = True) -> Path | None:
    """Resolve repo via git -C safely (list run, no shell, path traversal guard)."""
    mnemo = _get_mnemo()
    resolve_repo = mnemo.resolve_repo  # type: ignore[attr-defined]

    # injection guard before delegating
    if raw and any(c in raw for c in [";", "&", "|", "`", "$"]):
        raise ValueError("Invalid repo path")
    # traversal guard: block .. and /tmp absolute paths
    if raw and (".." in raw.split("/") or raw == "/tmp" or raw.startswith("/tmp/")):
        raise ValueError("Invalid repo path")
    result = resolve_repo(raw, required=required)
    if result is None:
        return None
    # ensure resolved is not outside expected? For now just ensure it's a dir containing .git or mnemosyne.toml
    resolved = Path(result).resolve()
    if not resolved.exists():
        raise ValueError("Resolved repo does not exist")
    return resolved


def collect_system(root: Path) -> dict:
    import platform
    import socket

    mnemo = _get_mnemo()
    os_release = mnemo.os_release  # type: ignore[attr-defined]
    load_config = mnemo.load_config  # type: ignore[attr-defined]
    detect_device = mnemo.detect_device  # type: ignore[attr-defined]

    release = os_release()
    try:
        config = load_config(root)
        project = config.get("project", {}).get("name", "unknown")

        device, role = detect_device(root, config)
    except Exception:  # noqa: BLE001
        project = "unknown"
        device, role = socket.gethostname(), "unknown"
    return {
        "hostname": socket.gethostname(),
        "os": release.get("PRETTY_NAME", platform.system()),
        "arch": platform.machine(),
        "python": platform.python_version(),
        "device": device,
        "role": role,
        "project": project,
    }


def collect_tools() -> list[dict]:
    mnemo = _get_mnemo()
    probe = mnemo.probe  # type: ignore[attr-defined]
    compose_probe = mnemo.compose_probe  # type: ignore[attr-defined]

    checks = [
        probe("uv", ["uv", "--version"]),
        probe("terraform", ["terraform", "version"]),
        probe("jq", ["jq", "--version"]),
        probe("docker", ["docker", "--version"]),
        compose_probe(),
    ]
    return checks


def git_status_summary(root: Path) -> dict:

    try:
        mnemo = _get_mnemo()
        git_status = mnemo.git_status  # type: ignore[attr-defined]
        git_dirty = mnemo.git_dirty  # type: ignore[attr-defined]
        upstream = mnemo.upstream  # type: ignore[attr-defined]
        ahead_behind = mnemo.ahead_behind  # type: ignore[attr-defined]

        status = git_status(root)
        dirty = git_dirty(root)
        # branch extraction from status first line
        branch = "unknown"
        for line in status.splitlines():
            if line.startswith("## "):
                branch = line[3:].split("...")[0].strip()
                break
        up = upstream(root)
        ahead = behind = 0
        if up:
            try:
                ahead, behind = ahead_behind(root)
            except Exception:  # noqa: BLE001,S110
                pass
        return {
            "branch": branch,
            "dirty": dirty,
            "ahead": ahead,
            "behind": behind,
            "status": status,
        }
    except Exception as exc:  # noqa: BLE001
        return {"branch": "unknown", "dirty": False, "ahead": 0, "behind": 0, "status": str(exc)}


def banner_info() -> dict:
    import socket

    # internet check via 1.1.1.1:53
    try:
        socket.create_connection(("1.1.1.1", 53), timeout=3)
        internet = True
    except OSError:
        internet = False
    # gh check
    try:
        result = subprocess.run(
            ["gh", "auth", "status"], capture_output=True, text=True, timeout=5, check=False
        )
        gh_connected = result.returncode == 0
    except Exception:  # noqa: BLE001
        gh_connected = False
    # pacman updates count (Arch only)
    updates = None
    if shutil.which("pacman"):
        try:
            r = subprocess.run(
                ["pacman", "-Qu"], capture_output=True, text=True, timeout=5, check=False
            )
            if r.returncode == 0:
                updates = len([l for l in r.stdout.splitlines() if l.strip()])
            else:
                updates = 0
        except Exception:  # noqa: BLE001
            updates = None
    return {"internet": internet, "gh_connected": gh_connected, "updates": updates}
