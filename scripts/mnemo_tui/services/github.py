from __future__ import annotations

import re
import subprocess
from pathlib import Path

REPO_RE = re.compile(r"^[A-Za-z0-9_.-]+$")


def _validate_repo(name: str) -> None:
    if not name or not name.strip():
        raise ValueError("Repository name is required")
    if any(c in name for c in [";", "&", "|", "`", "$"]):
        raise ValueError("Invalid repository name")
    if not REPO_RE.fullmatch(name.strip()):
        raise ValueError("Invalid repository name")


def gh_auth_status(timeout: int = 5) -> dict:
    """Check gh auth status, never logs PAT."""
    try:
        result = subprocess.run(
            ["gh", "auth", "status", "--json", "hosts"],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        if result.returncode == 0:
            # try to extract user via gh api user?
            try:
                api = subprocess.run(
                    ["gh", "api", "user", "--jq", ".login"],
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    check=False,
                )
                user = api.stdout.strip() if api.returncode == 0 else "unknown"
            except Exception:  # noqa: BLE001
                user = "unknown"
            return {"connected": True, "user": user, "detail": result.stdout.strip()}
        return {"connected": False, "user": None, "detail": result.stderr.strip() or "Not connected"}
    except subprocess.TimeoutExpired:
        return {"connected": False, "user": None, "detail": "Timeout"}
    except FileNotFoundError:
        return {"connected": False, "user": None, "detail": "gh not installed"}
    except Exception as exc:  # noqa: BLE001
        return {"connected": False, "user": None, "detail": str(exc)}


def gh_auth_login_with_token(token: str, timeout: int = 10) -> dict:
    if not token or not token.strip():
        raise ValueError("Token is required")
    if any(c in token for c in [";", "&", "|"]):
        raise ValueError("Invalid token")
    # token is passed via stdin, never via shell
    try:
        result = subprocess.run(
            ["gh", "auth", "login", "--with-token"],
            input=token,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return {"ok": result.returncode == 0, "detail": result.stderr.strip() or result.stdout.strip()}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "detail": str(exc)}


def gh_repo_create(name: str, *, private: bool = True, timeout: int = 10) -> dict:
    _validate_repo(name)
    visibility = "--private" if private else "--public"
    try:
        result = subprocess.run(
            ["gh", "repo", "create", name, visibility, "--confirm"],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return {"ok": result.returncode == 0, "detail": result.stderr.strip() or result.stdout.strip()}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "detail": str(exc)}


def default_repo_name(root: Path) -> str:
    try:
        import importlib.util
        import sys
        from pathlib import Path as _P

        mod = None
        for name in ("mnemo", "__main__", "scripts.mnemo"):
            mod = sys.modules.get(name)
            if mod is not None and hasattr(mod, "load_config"):
                break
        else:
            mnemo_path = _P(__file__).resolve().parents[2] / "mnemo.py"
            spec = importlib.util.spec_from_file_location("mnemo", mnemo_path)
            assert spec and spec.loader
            mod = importlib.util.module_from_spec(spec)
            sys.modules["mnemo"] = mod
            spec.loader.exec_module(mod)
        load_config = mod.load_config  # type: ignore[attr-defined]
        cfg = load_config(root)
        return str(cfg.get("project", {}).get("name", "andry-de-zoomcamp"))
    except Exception:  # noqa: BLE001
        return "andry-de-zoomcamp"
