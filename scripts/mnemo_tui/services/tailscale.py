from __future__ import annotations

import json
import subprocess


def tailscale_status(timeout: int = 5) -> dict:
    try:
        result = subprocess.run(
            ["tailscale", "status", "--json"],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        if result.returncode != 0:
            return {"ok": False, "ip": None, "detail": result.stderr.strip() or "not detected"}
        data = json.loads(result.stdout)
        # try to extract self IP
        self_info = data.get("Self", {})
        ips = self_info.get("TailscaleIPs", [])
        ip = ips[0] if ips else None
        # host mapping
        peers = data.get("Peer", {})
        # find uranus
        uranus_ip = None
        for v in peers.values():
            if "uranus" in str(v.get("HostName", "")).lower():
                uranus_ip = (v.get("TailscaleIPs") or [None])[0]
                break
        return {"ok": True, "ip": ip, "uranus_ip": uranus_ip, "detail": "ok"}
    except FileNotFoundError:
        return {"ok": False, "ip": None, "detail": "tailscale not installed"}
    except subprocess.TimeoutExpired:
        return {"ok": False, "ip": None, "detail": "timeout"}
    except json.JSONDecodeError as exc:
        return {"ok": False, "ip": None, "detail": f"parse error: {exc}"}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "ip": None, "detail": str(exc)}


def tailscale_ip_for_host(host: str, timeout: int = 5) -> str | None:
    # best effort: if host is uranus-core-vnic and tailscale knows IP, return it
    status = tailscale_status(timeout=timeout)
    if status.get("uranus_ip") and host == "uranus-core-vnic":
        return str(status["uranus_ip"])
    return None
