from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from mnemo_tui.services.github import (
    default_repo_name,
    gh_auth_login_with_token,
    gh_auth_status,
    gh_repo_create,
)


class TestGhAuthStatus:
    def test_connected_when_gh_succeeds(self) -> None:
        mock_ok = MagicMock(returncode=0, stdout='{"hosts": {}}', stderr="")
        mock_user = MagicMock(returncode=0, stdout="andry\n", stderr="")
        with patch("subprocess.run", side_effect=[mock_ok, mock_user]):
            res = gh_auth_status(timeout=5)
            assert res["connected"] is True
            assert res["user"] == "andry"

    def test_not_connected_when_gh_fails(self) -> None:
        mock_fail = MagicMock(returncode=1, stdout="", stderr="not logged in")
        with patch("subprocess.run", return_value=mock_fail):
            res = gh_auth_status(timeout=5)
            assert res["connected"] is False
            assert "not logged in" in res["detail"]

    def test_timeout_returns_not_connected(self) -> None:
        import subprocess

        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="gh", timeout=5)):
            res = gh_auth_status(timeout=5)
            assert res["connected"] is False
            assert "Timeout" in res["detail"]

    def test_gh_not_installed(self) -> None:
        with patch("subprocess.run", side_effect=FileNotFoundError):
            res = gh_auth_status()
            assert res["connected"] is False
            assert "not installed" in res["detail"]

    def test_token_passed_via_stdin_not_logged(self) -> None:
        mock = MagicMock(returncode=0, stdout="", stderr="")
        with patch("subprocess.run", return_value=mock) as m:
            res = gh_auth_login_with_token("secret12345", timeout=5)
            assert res["ok"] is True
            # verify call used input, not shell, and token not in command
            args, kwargs = m.call_args
            assert "secret12345" not in str(args[0])
            assert kwargs.get("input") == "secret12345"

    def test_token_empty_rejected(self) -> None:
        with pytest.raises(ValueError):
            gh_auth_login_with_token("")

    def test_token_injection_rejected(self) -> None:
        with pytest.raises(ValueError):
            gh_auth_login_with_token("bad; echo pwn")


class TestGhRepoCreate:
    def test_create_valid(self) -> None:
        mock = MagicMock(returncode=0, stdout="created", stderr="")
        with patch("subprocess.run", return_value=mock) as m:
            res = gh_repo_create("my-repo", private=True)
            assert res["ok"] is True
            # check list run, no shell, validate private flag
            args = m.call_args[0][0]
            assert args == ["gh", "repo", "create", "my-repo", "--private", "--confirm"]

    def test_create_public_flag(self) -> None:
        mock = MagicMock(returncode=0, stdout="", stderr="")
        with patch("subprocess.run", return_value=mock) as m:
            gh_repo_create("my-repo", private=False)
            assert "--public" in m.call_args[0][0]

    def test_empty_rejected(self) -> None:
        with pytest.raises(ValueError, match="Repository name is required"):
            gh_repo_create("", private=True)

    def test_injection_rejected(self) -> None:
        with pytest.raises(ValueError):
            gh_repo_create("bad; rm", private=True)


class TestDefaultRepoName:
    def test_reads_from_toml(self, tmp_path: Path) -> None:
        (tmp_path / "mnemosyne.toml").write_text('[project]\nname="custom-name"\n', encoding="utf-8")
        assert default_repo_name(tmp_path) == "custom-name"

    def test_fallback_when_missing(self, tmp_path: Path) -> None:
        assert default_repo_name(tmp_path) == "andry-de-zoomcamp"

    def test_triangulate_different_name(self, tmp_path: Path) -> None:
        (tmp_path / "mnemosyne.toml").write_text('[project]\nname="another-project"\n', encoding="utf-8")
        assert default_repo_name(tmp_path) == "another-project"
