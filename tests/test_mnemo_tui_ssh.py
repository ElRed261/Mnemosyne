from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from mnemo_tui.services.ssh import test_ssh as ssh_test
from mnemo_tui.services.tailscale import tailscale_status


class TestSsh:
    def test_ssh_success_returns_connected(self, tmp_path: Path) -> None:
        key = tmp_path / "id_test.key"
        key.write_text("fake")
        mock = MagicMock(returncode=0, stdout="ok\n", stderr="")
        with patch("subprocess.run", return_value=mock) as m:
            res = ssh_test(str(key), "user", "uranus-core-vnic", timeout=5)
            assert res["ok"] is True
            assert "✅ Connected" in res["detail"]
            # ensure list run, correct timeout and ConnectTimeout=5
            args = m.call_args[0][0]
            assert "-o" in args
            assert "ConnectTimeout=5" in args
            assert "echo ok" in args

    def test_ssh_timeout(self, tmp_path: Path) -> None:
        key = tmp_path / "id_test.key"
        key.write_text("k")
        import subprocess

        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="ssh", timeout=5)):
            res = ssh_test(str(key), "user", "host", timeout=5)
            assert res["ok"] is False
            assert "timeout" in res["detail"].lower()

    def test_ssh_unreachable_shows_first_line(self, tmp_path: Path) -> None:
        key = tmp_path / "id_test.key"
        key.write_text("k")
        mock = MagicMock(returncode=255, stdout="", stderr="ssh: connect to host host port 22: No route\nsecond line")
        with patch("subprocess.run", return_value=mock):
            res = ssh_test(str(key), "user", "host")
            assert res["ok"] is False
            assert "No route" in res["detail"]

    def test_ssh_key_not_found(self) -> None:
        with pytest.raises(ValueError, match="Key file not found"):
            ssh_test("/nope.key", "user", "host")

    def test_ssh_host_validation(self, tmp_path: Path) -> None:
        key = tmp_path / "a.key"
        key.write_text("k")
        with pytest.raises(ValueError):
            ssh_test(str(key), "user", "bad;host")


class TestTailscale:
    def test_tailscale_parses_ip(self) -> None:
        data = {"Self": {"TailscaleIPs": ["100.1.2.3"]}, "Peer": {"1": {"HostName": "uranus-core-vnic", "TailscaleIPs": ["100.9.9.9"]}}}
        mock = MagicMock(returncode=0, stdout=json.dumps(data), stderr="")
        with patch("subprocess.run", return_value=mock):
            res = tailscale_status(timeout=5)
            assert res["ok"] is True
            assert res["ip"] == "100.1.2.3"
            assert res["uranus_ip"] == "100.9.9.9"

    def test_tailscale_not_installed(self) -> None:
        with patch("subprocess.run", side_effect=FileNotFoundError):
            res = tailscale_status()
            assert res["ok"] is False
            assert "not installed" in res["detail"]

    def test_tailscale_timeout(self) -> None:
        import subprocess

        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="tailscale", timeout=5)):
            res = tailscale_status()
            assert res["ok"] is False
            assert "timeout" in res["detail"]
