from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "mnemo.py"
SPEC = importlib.util.spec_from_file_location("mnemo_shell", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
mnemo = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = mnemo
SPEC.loader.exec_module(mnemo)


class TestMaybeLaunchTui:
    def test_no_args_tty_with_textual_calls_run_tui(self) -> None:
        mock_app = MagicMock(run_tui=MagicMock(return_value=0))
        mock_pkg = MagicMock()
        with (
            patch.object(sys.stdin, "isatty", return_value=True),
            patch.object(sys.stdout, "isatty", return_value=True),
            patch("importlib.util.find_spec", return_value=MagicMock()),
            patch.dict("sys.modules", {"mnemo_tui": mock_pkg, "mnemo_tui.app": mock_app}),
        ):
            result = mnemo.maybe_launch_tui([])  # type: ignore[attr-defined]
            assert result == 0
            assert mock_app.run_tui.called

    def test_non_tty_returns_none(self) -> None:
        with (
            patch.object(sys.stdin, "isatty", return_value=False),
            patch.object(sys.stdout, "isatty", return_value=True),
        ):
            assert mnemo.maybe_launch_tui([]) is None  # type: ignore[attr-defined]

    def test_stdout_non_tty_returns_none(self) -> None:
        with (
            patch.object(sys.stdin, "isatty", return_value=True),
            patch.object(sys.stdout, "isatty", return_value=False),
        ):
            assert mnemo.maybe_launch_tui([]) is None  # type: ignore[attr-defined]

    def test_with_arg_returns_none(self) -> None:
        with (
            patch.object(sys.stdin, "isatty", return_value=True),
            patch.object(sys.stdout, "isatty", return_value=True),
        ):
            assert mnemo.maybe_launch_tui(["doctor"]) is None  # type: ignore[attr-defined]
            assert mnemo.maybe_launch_tui(["--help"]) is None  # type: ignore[attr-defined]

    def test_no_tui_flag_returns_none(self) -> None:
        with (
            patch.object(sys.stdin, "isatty", return_value=True),
            patch.object(sys.stdout, "isatty", return_value=True),
        ):
            assert mnemo.maybe_launch_tui(["--no-tui"]) is None  # type: ignore[attr-defined]
            assert mnemo.maybe_launch_tui(["--no-tui", "doctor"]) is None  # type: ignore[attr-defined]

    def test_missing_textual_shows_hint_and_returns_0(self, capsys: pytest.CaptureFixture[str]) -> None:
        with (
            patch.object(sys.stdin, "isatty", return_value=True),
            patch.object(sys.stdout, "isatty", return_value=True),
            patch("importlib.util.find_spec", return_value=None),
        ):
            result = mnemo.maybe_launch_tui([])  # type: ignore[attr-defined]
            assert result == 0
            out = capsys.readouterr().out
            assert "TUI not installed" in out
            assert "uv sync" in out

    def test_piped_input_stays_cli(self) -> None:
        # piped = stdin not tty
        with patch.object(sys.stdin, "isatty", return_value=False):
            assert mnemo.maybe_launch_tui([]) is None  # type: ignore[attr-defined]
