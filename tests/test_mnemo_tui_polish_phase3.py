from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import re

_TS_RE = re.compile(r"\[\d{2}:\d{2}:\d{2}\]")


class TestActionsNonBlocking:
    def test_on_button_pressed_is_work_decorated(self) -> None:
        import inspect

        from mnemo_tui.screens.dashboard import DashboardScreen

        # check on_button_pressed delegates to a worker or itself is work
        # look for run_action worker
        assert hasattr(DashboardScreen, "run_action"), "run_action worker missing"
        fn = DashboardScreen.run_action
        has_work = False
        if hasattr(fn, "_work") or hasattr(fn, "__wrapped__"):
            has_work = True
        else:
            src = inspect.getsource(fn)
            has_work = "@work" in src or "work(" in src
        assert has_work, "run_action must be @work(thread=True) non-blocking"
        # on_button_pressed should be non-blocking (return quickly)
        src2 = inspect.getsource(DashboardScreen.on_button_pressed)
        assert "run_action" in src2 or "work" in src2.lower(), "on_button_pressed should delegate to run_action"

    def test_press_doctor_is_non_blocking_and_list_form(self) -> None:
        import asyncio
        import time

        from mnemo_tui.app import MnemoApp
        from textual.widgets import RichLog

        captured: list[str] = []

        def fake_write(self, content, *a, **kw):
            captured.append(str(content))

        # mock subprocess.run to simulate doctor output without blocking
        def fake_run(cmd, capture_output=False, text=False, timeout=None, check=False, **kwargs):
            # verify list-form and timeout 10, absolute path, cwd set to repo
            assert isinstance(cmd, list), "must be list-form"
            assert cmd[:3] == ["uv", "run", "python"], f"wrong prefix {cmd}"
            assert cmd[3].endswith("scripts/mnemo.py"), f"mnemo.py path should be absolute {cmd}"
            assert Path(cmd[3]).is_absolute(), "mnemo.py must be absolute path"
            assert timeout == 10, f"timeout should be 10, got {timeout}"
            assert kwargs.get("cwd"), "cwd must be repo root"
            # simulate success
            return MagicMock(returncode=0, stdout="doctor ok output", stderr="")

        async def _check() -> None:
            app = MnemoApp()
            with (
                patch("subprocess.run", side_effect=fake_run),
                patch.object(RichLog, "write", fake_write),
            ):
                async with app.run_test(size=(100, 40)) as pilot:
                    await pilot.pause()
                    await asyncio.sleep(0.3)
                    start = time.time()
                    # find doctor button and press
                    pilot.app.query_one("#dashboard").on_button_pressed(MagicMock(button=MagicMock(label="doctor")))
                    # should return immediately <1s even though subprocess mocked
                    elapsed = time.time() - start
                    assert elapsed < 1.0, f"on_button_pressed blocked {elapsed}"
                    await asyncio.sleep(0.8)
                    text = "\n".join(captured)
                    assert "doctor" in text.lower(), f"doctor output missing in {text!r}"
                    assert _TS_RE.search(text), "timestamp missing in action log"

        asyncio.run(_check())

    def test_action_uses_call_from_thread(self) -> None:
        import inspect

        from mnemo_tui.screens.dashboard import DashboardScreen

        src = inspect.getsource(DashboardScreen.run_action)
        assert "call_from_thread" in src, "run_action must use call_from_thread for UI updates"
        assert "subprocess.run" in src, "run_action must use subprocess.run list-form"


class TestDualRouting:
    def test_stdout_goes_general_stderr_goes_errors(self) -> None:
        import asyncio

        from mnemo_tui.app import MnemoApp

        general_captured: list[str] = []
        error_captured: list[str] = []

        # we need to distinguish General vs Errors logs: patch each panel separately?
        # Instead, patch RichLog.write and inspect which panel id was used via call stack or separate patch
        # Simpler: patch app.log_general and log_error separately
        async def _check() -> None:
            app = MnemoApp()

            def fake_run(cmd, capture_output=False, text=False, timeout=None, check=False, **kwargs):
                # first call stdout, second via stderr simulation? We'll return both
                return MagicMock(returncode=1, stdout="out line", stderr="err line")

            with patch("subprocess.run", side_effect=fake_run):
                async with app.run_test(size=(100, 40)) as pilot:
                    await pilot.pause()
                    # patch the app's log methods to capture routing
                    orig_general = pilot.app.log_general
                    orig_error = pilot.app.log_error

                    def cap_general(msg):
                        general_captured.append(msg)
                        return orig_general(msg)

                    def cap_error(msg):
                        error_captured.append(msg)
                        return orig_error(msg)

                    with (
                        patch.object(pilot.app, "log_general", side_effect=cap_general),
                        patch.object(pilot.app, "log_error", side_effect=cap_error),
                    ):
                        from unittest.mock import MagicMock as M

                        pilot.app.query_one("#dashboard").on_button_pressed(M(button=M(label="doctor")))
                        await asyncio.sleep(1.0)
                        # after worker, check routing
                        gen_text = "\n".join(general_captured)
                        err_text = "\n".join(error_captured)
                        # stdout should be in general
                        assert "out line" in gen_text or "doctor" in gen_text.lower(), f"stdout not in general {gen_text!r}"
                        # stderr should be in errors
                        assert "err line" in err_text, f"stderr not in errors {err_text!r}"

        asyncio.run(_check())
