from __future__ import annotations

# import services for validation checks
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from mnemo_tui.services.github import gh_repo_create
from mnemo_tui.services.ssh import test_ssh as ssh_test
from mnemo_tui.services.system import (
    resolve_repo_safe,
    validate_host,
    validate_repo_name,
)
from mnemo_tui.services.system import validate_key_path as sys_validate_key


class TestInjection:
    def test_repo_injection_semicolon_rejected(self) -> None:
        with pytest.raises(ValueError, match="Invalid repository name"):
            validate_repo_name("a; echo pwn")

    def test_repo_injection_amp_rejected(self) -> None:
        with pytest.raises(ValueError, match="Invalid repository name"):
            validate_repo_name("x && id")

    def test_repo_injection_pipe_rejected(self) -> None:
        with pytest.raises(ValueError):
            gh_repo_create("bad; rm -rf /", private=True)

    def test_host_injection_semicolon(self) -> None:
        with pytest.raises(ValueError, match="Invalid host"):
            validate_host("host; echo pwn")

    def test_host_injection_and(self) -> None:
        with pytest.raises(ValueError):
            validate_host("x && id")

    def test_key_injection(self) -> None:
        with pytest.raises(ValueError):
            sys_validate_key("key; echo pwn")

    def test_ssh_host_injection(self) -> None:
        # key must exist to reach host validation; use /tmp existence mock
        # we test host validation before key existence? order is key, user, host.
        # Provide dummy key that exists via tmp_path
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".key", delete=False) as tf:
            key = tf.name
            tf.write(b"fake")
        try:
            with pytest.raises(ValueError, match="Invalid host"):
                ssh_test(key, "user", "host; echo pwn")
        finally:
            Path(key).unlink(missing_ok=True)

    def test_ssh_key_injection(self) -> None:
        with pytest.raises(ValueError, match="Invalid key path"):
            ssh_test("bad; echo pwn", "user", "host")

    def test_resolve_repo_injection(self) -> None:
        with pytest.raises(ValueError):
            resolve_repo_safe("a; echo pwn")


class TestGitC:
    def test_repo_traversal_dotdot(self, tmp_path: Path) -> None:
        # ".." should be rejected or not resolve to parent outside?
        # Our resolve_repo_safe should raise or not allow traversal
        with pytest.raises(ValueError):
            # we expect validation to reject ".." containing path
            resolve_repo_safe("../..")

    def test_repo_tmp_rejected(self) -> None:
        with pytest.raises(ValueError):
            resolve_repo_safe("/tmp")

    def test_repo_tmp_sub_rejected(self) -> None:
        with pytest.raises(ValueError):
            resolve_repo_safe("/tmp/repo")

    def test_resolve_safe_allows_current(self) -> None:
        # repo safe with None should resolve to cwd if inside git? may return None or Path
        # at least not raise ValueError for None
        result = resolve_repo_safe(None, required=False)
        # either Path or None is ok, just not raise
        assert result is None or isinstance(result, Path)
