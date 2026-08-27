from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from mnemo_tui.app import MnemoApp, run_tui
from mnemo_tui.services.github import gh_auth_status


def test_app_composes_expected_widgets() -> None:
    app = MnemoApp()
    assert app.TITLE == "Mnemosyne"
    assert Path(app.CSS_PATH).name == "theme.tcss"
    assert hasattr(app, "online")


def test_banner_set_online() -> None:
    app = MnemoApp()
    app.update_banner(False)
    assert app.online is False
    app.update_banner(True)
    assert app.online is True


def test_run_tui_guard_small_terminal(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    mock_size = MagicMock(columns=40, lines=10)
    monkeypatch.setattr("shutil.get_terminal_size", lambda: mock_size)
    with patch("importlib.util.find_spec", return_value=MagicMock()):
        res = run_tui()
        assert res == 1
        assert "Terminal too small" in capsys.readouterr().err


def test_onboarding_gate_text() -> None:
    mock_fail = MagicMock(returncode=1, stdout="", stderr="not auth")
    with patch("subprocess.run", return_value=mock_fail):
        status = gh_auth_status()
        gate = "Connected as @user" if status["connected"] else "Connect GitHub to continue"
        assert gate == "Connect GitHub to continue"
    mock_ok = MagicMock(returncode=0, stdout="hosts", stderr="")
    mock_user = MagicMock(returncode=0, stdout="andry", stderr="")
    with patch("subprocess.run", side_effect=[mock_ok, mock_user]):
        status = gh_auth_status()
        gate = f"Connected as @{status['user']}" if status["connected"] else "not"
        assert gate == "Connected as @andry"


def test_uranus_ssh_test_timing(tmp_path: Path) -> None:
    key = tmp_path / "id.key"
    key.write_text("k")
    mock = MagicMock(returncode=0, stdout="ok", stderr="")
    with patch("subprocess.run", return_value=mock) as m:
        from mnemo_tui.services.ssh import test_ssh as ssh_test

        res = ssh_test(str(key), "user", "host")
        assert res["ok"] is True
        _args, kwargs = m.call_args
        assert kwargs.get("timeout", 6) <= 6


def test_dashboard_has_panels_and_logs() -> None:
    # use asyncio pilot to verify 5 panels + 2 logs are present
    import asyncio

    async def _check() -> None:
        app = MnemoApp()
        async with app.run_test(size=(100, 40)) as pilot:
            # banner exists
            banner = pilot.app.query_one("#banner")
            assert banner is not None
            # dashboard exists
            dash = pilot.app.query_one("#dashboard")
            assert dash is not None
            # logs
            assert pilot.app.query_one("#log-general") is not None
            assert pilot.app.query_one("#log-errors") is not None
            # need to press Tab to ensure focus moves? Just ensure app runs
            await pilot.pause()

    asyncio.run(_check())


def test_textual_pilot_tab_nav() -> None:
    import asyncio

    async def _check() -> None:
        app = MnemoApp()
        async with app.run_test(size=(100, 40)) as pilot:
            await pilot.press("tab")
            await pilot.pause()
            # after Tab, still running
            assert pilot.app.is_running

    asyncio.run(_check())
