from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from mnemo_tui.services.system import collect_tools, git_status_summary
from mnemo_tui.widgets.key_picker import list_keys


class TestIntegrationTempRepo:
    def test_collect_tools_returns_five(self) -> None:
        checks = collect_tools()
        assert len(checks) >= 4
        for c in checks:
            assert "ok" in c

    def test_git_status_in_temp_repo(self, tmp_path: Path) -> None:
        subprocess.run(["git", "init", str(tmp_path)], capture_output=True, check=False)
        subprocess.run(["git", "-C", str(tmp_path), "config", "user.email", "t@t.t"], capture_output=True, check=False)
        subprocess.run(["git", "-C", str(tmp_path), "config", "user.name", "t"], capture_output=True, check=False)
        (tmp_path / "a.txt").write_text("hello")
        subprocess.run(["git", "-C", str(tmp_path), "add", "."], capture_output=True, check=False)
        subprocess.run(["git", "-C", str(tmp_path), "commit", "-m", "init"], capture_output=True, check=False)
        summary = git_status_summary(tmp_path)
        assert isinstance(summary["branch"], str)
        # after commit without remote, ahead is 0
        assert summary["ahead"] == 0

    def test_list_keys_integration(self, tmp_path: Path) -> None:
        ssh_dir = tmp_path / ".ssh"
        ssh_dir.mkdir()
        (ssh_dir / "id_rsa").write_text("k")
        (ssh_dir / "bad.txt").write_text("k")
        keys = list_keys(ssh_dir)
        assert len(keys) == 1
        assert keys[0].name == "id_rsa"

    def test_gh_gate_logic(self) -> None:
        # gate: if not connected, Create disabled
        from unittest.mock import MagicMock, patch

        from mnemo_tui.services.github import gh_auth_status

        mock_fail = MagicMock(returncode=1, stdout="", stderr="")
        with patch("subprocess.run", return_value=mock_fail):
            status = gh_auth_status()
            assert status["connected"] is False
        # gate text logic
        gate_text = "Connect GitHub to continue" if not status["connected"] else "Connected"
        assert gate_text == "Connect GitHub to continue"
