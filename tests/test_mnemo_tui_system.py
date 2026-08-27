from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from mnemo_tui.services.system import banner_info, collect_system, collect_tools, git_status_summary


class TestCollectSystem:
    def test_collect_contains_expected_keys(self, tmp_path: Path) -> None:
        (tmp_path / "mnemosyne.toml").write_text('[project]\nname="test-proj"\n[devices.PCrda]\nhostnames=["pcrda"]\nrole="primary-x86"\n', encoding="utf-8")
        data = collect_system(tmp_path)
        assert "hostname" in data
        assert "os" in data
        assert "arch" in data
        assert "python" in data
        assert data["project"] == "test-proj"

    def test_fallback_when_no_config(self, tmp_path: Path) -> None:
        data = collect_system(tmp_path)
        assert data["project"] == "unknown"


class TestCollectTools:
    def test_returns_ok_missing(self) -> None:
        checks = collect_tools()
        assert isinstance(checks, list)
        assert len(checks) >= 4
        names = {c["name"] for c in checks}
        assert "uv" in names
        for c in checks:
            assert "ok" in c
            assert "detail" in c

    def test_triangulate_tools_have_detail(self) -> None:
        checks = collect_tools()
        for c in checks:
            assert isinstance(c["detail"], str)


class TestGitStatus:
    def test_git_summary_parses_branch(self, tmp_path: Path) -> None:
        # Use real git temp repo if available
        import subprocess

        # create temp git repo
        subprocess.run(["git", "init", str(tmp_path)], capture_output=True, check=False)
        subprocess.run(["git", "-C", str(tmp_path), "config", "user.email", "t@t.t"], capture_output=True, check=False)
        subprocess.run(["git", "-C", str(tmp_path), "config", "user.name", "t"], capture_output=True, check=False)
        (tmp_path / "README.md").write_text("hi")
        subprocess.run(["git", "-C", str(tmp_path), "add", "."], capture_output=True, check=False)
        subprocess.run(["git", "-C", str(tmp_path), "commit", "-m", "init"], capture_output=True, check=False)
        res = git_status_summary(tmp_path)
        assert "branch" in res
        assert "dirty" in res

    def test_git_dirty_detection(self, tmp_path: Path) -> None:
        import subprocess

        subprocess.run(["git", "init", str(tmp_path)], capture_output=True, check=False)
        subprocess.run(["git", "-C", str(tmp_path), "config", "user.email", "t@t.t"], capture_output=True, check=False)
        subprocess.run(["git", "-C", str(tmp_path), "config", "user.name", "t"], capture_output=True, check=False)
        (tmp_path / "f.txt").write_text("a")
        subprocess.run(["git", "-C", str(tmp_path), "add", "."], capture_output=True, check=False)
        subprocess.run(["git", "-C", str(tmp_path), "commit", "-m", "x"], capture_output=True, check=False)
        # make dirty
        (tmp_path / "f.txt").write_text("b")
        res = git_status_summary(tmp_path)
        assert res["dirty"] is True


class TestBanner:
    def test_banner_offline_when_no_connection(self) -> None:
        with (
            patch("socket.create_connection", side_effect=OSError),
            patch("subprocess.run") as m,
        ):
            m.return_value = MagicMock(returncode=1)
            data = banner_info()
            assert data["internet"] is False

    def test_banner_online(self) -> None:
        with (
            patch("socket.create_connection", return_value=MagicMock()),
            patch("subprocess.run") as m,
            patch("shutil.which", return_value=None),
        ):
            m.return_value = MagicMock(returncode=0)
            data = banner_info()
            assert data["internet"] is True
            assert data["gh_connected"] is True
