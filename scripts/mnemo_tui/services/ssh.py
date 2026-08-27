from __future__ import annotations

import re
import subprocess
from pathlib import Path

HOST_RE = re.compile(r"^[A-Za-z0-9.-]+$")
USER_RE = re.compile(r"^[A-Za-z0-9_.-]+$")


def _validate_host(host: str) -> None:
    if not host or not host.strip():
        raise ValueError("Host is required")
    if any(c in host for c in [";", "&", "|", "`", "$", "(", ")"]):
        raise ValueError("Invalid host")
    if not HOST_RE.fullmatch(host.strip()):
        raise ValueError("Invalid host")


def _validate_user(user: str) -> None:
    if not user or not user.strip():
        raise ValueError("User is required")
    if any(c in user for c in [";", "&", "|", "`", "$"]):
        raise ValueError("Invalid user")
    if not USER_RE.fullmatch(user.strip()):
        raise ValueError("Invalid user")


def _validate_key(key: str) -> None:
    if not key:
        raise ValueError("Key path required")
    if any(c in key for c in [";", "&", "|", "`", "$"]):
        raise ValueError("Invalid key path")
    p = Path(key).expanduser()
    if not p.exists():
        raise ValueError("Key file not found")


def test_ssh(key_path: str, user: str, host: str, timeout: int = 5) -> dict:
    """Test ssh -i key -o ConnectTimeout=5 user@host "echo ok" → ✅/❌"""
    _validate_key(key_path)
    _validate_user(user)
    _validate_host(host)
    target = f"{user.strip()}@{host.strip()}"
    cmd = [
        "ssh",
        "-i",
        str(Path(key_path).expanduser()),
        "-o",
        "ConnectTimeout=5",
        "-o",
        "StrictHostKeyChecking=accept-new",
        target,
        "echo ok",
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 1, check=False)
        if result.returncode == 0 and "ok" in result.stdout:
            return {"ok": True, "detail": "✅ Connected"}
        detail = (result.stderr.strip() or result.stdout.strip()).splitlines()[0] if (result.stderr or result.stdout) else "Unknown error"
        return {"ok": False, "detail": f"❌ Unreachable: {detail}"}
    except subprocess.TimeoutExpired:
        return {"ok": False, "detail": "❌ Unreachable: timeout"}
    except FileNotFoundError:
        return {"ok": False, "detail": "❌ Unreachable: ssh not found"}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "detail": f"❌ Unreachable: {exc}"}
