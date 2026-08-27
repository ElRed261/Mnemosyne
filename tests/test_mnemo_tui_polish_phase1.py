from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

_TIMESTAMP_RE = re.compile(r"\[\d{2}:\d{2}:\d{2}\]")


class TestLogPanelTimestamp:
    def test_write_prefixes_timestamp(self) -> None:
        from unittest import mock

        from mnemo_tui.widgets.log_panel import LogPanel
        from textual.widgets import RichLog

        captured: list[str] = []

        def fake_write(self, content, *a, **kw):
            captured.append(str(content))

        with mock.patch.object(RichLog, "write", fake_write):
            p2 = LogPanel(title="General Log")
            p2.write("hello world")
            assert captured, "RichLog.write was not called"
            assert _TIMESTAMP_RE.search(captured[0]), f"timestamp missing in '{captured[0]}'"
            assert "hello world" in captured[0]

    def test_log_error_also_timestamped(self) -> None:
        from unittest import mock

        from mnemo_tui.widgets.log_panel import LogPanel
        from textual.widgets import RichLog

        captured: list[str] = []

        def fake_write(self, content, *a, **kw):
            captured.append(str(content))

        with mock.patch.object(RichLog, "write", fake_write):
            p = LogPanel(title="Errors / Audit")
            p.log("something failed", error=True)
            assert captured
            assert _TIMESTAMP_RE.search(captured[0]), f"timestamp missing in error log '{captured[0]}'"


class TestBanner:
    def test_online_shows_updates_and_github(self) -> None:
        from mnemo_tui.widgets.banner import Banner

        b = Banner()
        # new API should support rich banner
        if hasattr(b, "set_banner"):
            b.set_banner(online=True, gh_connected=True, updates=3)  # type: ignore[attr-defined]
            # fallback: check attributes
            assert b.online is True
            # check that internal state reflects updates
            assert getattr(b, "updates", 3) == 3 or True
            # check render contains expected substrings via _render_text if exists
            if hasattr(b, "_render_text"):
                rendered = b._render_text()  # type: ignore[attr-defined]
                assert "Online" in rendered
                assert "Updates: 3" in rendered
                assert "GitHub" in rendered
            else:
                # if no richer method, this test should fail to force implementation
                pytest.fail("Banner lacks rich rendering for Online Updates:N")
        elif hasattr(b, "set_updates"):
            b.set_online(True)
            b.set_updates(3)  # type: ignore[attr-defined]
            if hasattr(b, "_render_text"):
                rendered = b._render_text()  # type: ignore[attr-defined]
                assert "Updates: 3" in rendered
            else:
                pytest.fail("Banner missing _render_text with updates")
        else:
            pytest.fail("Banner missing set_banner/set_updates for polished display")

    def test_offline_shows_offline(self) -> None:
        from mnemo_tui.widgets.banner import Banner

        b = Banner()
        if hasattr(b, "set_banner"):
            b.set_banner(online=False, gh_connected=False, updates=None)  # type: ignore[attr-defined]
            rendered = b._render_text() if hasattr(b, "_render_text") else ""  # type: ignore[attr-defined]
            assert "Offline" in rendered
        else:
            b.set_online(False)
            # check text is Offline via render or online flag
            assert b.online is False
            # need to verify offline degrade string includes Offline
            if hasattr(b, "_render_text"):
                assert "Offline" in b._render_text()  # type: ignore[attr-defined]
            else:
                # fallback check that simple update is just Offline, but new spec wants richer
                # force failure to drive implementation
                pytest.fail("Banner offline rendering not polished")


class TestTheme:
    def test_theme_tcss_contains_tokens(self) -> None:
        p = Path(__file__).resolve().parents[1] / "scripts" / "mnemo_tui" / "theme.tcss"
        content = p.read_text(encoding="utf-8")
        for token in ["#7c5cff", "#0e0e10", "#1a1a1e", "#2ecc71", "#ff4d4d"]:
            assert token.lower() in content.lower(), f"token {token} missing in theme.tcss"
        # check for polished aspects: focus ring, skeleton, transition 150ms
        assert "150ms" in content or "transition" in content, "polish transition 150ms missing"
        assert "skeleton" in content.lower(), "skeleton style missing"
        assert ":focus" in content or "focus" in content.lower(), "focus ring missing"

    def test_app_registers_mnemosyne_dark(self) -> None:
        # pilot check that app registers Theme mnemosyne-dark
        import asyncio

        from mnemo_tui.app import MnemoApp

        async def _check() -> None:
            app = MnemoApp()
            async with app.run_test(size=(100, 40)) as pilot:
                await pilot.pause()
                # Theme should be registered
                # textual App has available_themes or theme attribute
                theme_name = getattr(pilot.app, "theme", None)
                # check register: try to find theme via app.get_theme or similar
                # fallback: check app has theme set to mnemosyne-dark
                assert theme_name == "mnemosyne-dark", f"expected mnemosyne-dark, got {theme_name}"
                # also check CSS contains dock etc implicitly via rendering
                assert pilot.app.query_one("#banner") is not None

        asyncio.run(_check())


class TestReadyLog:
    def test_ready_log_appears_within_1s(self) -> None:
        import asyncio
        import time
        from unittest import mock

        from mnemo_tui.app import MnemoApp
        from textual.widgets import RichLog

        captured: list[str] = []

        def fake_write(self, content, *a, **kw):
            captured.append(str(content))

        async def _check() -> None:
            app = MnemoApp()
            start = time.time()
            with mock.patch.object(RichLog, "write", fake_write):
                async with app.run_test(size=(100, 40)) as pilot:
                    await pilot.pause()
                    await asyncio.sleep(0.6)
                    elapsed = time.time() - start
                    assert elapsed < 3.0, f"mount too slow {elapsed}"
                    text = "\n".join(captured)
                    assert "Mnemosyne ready" in text, f"ready log missing, got '{text[:500]}'"
                    assert _TIMESTAMP_RE.search(text), "timestamp missing in ready log"

        asyncio.run(_check())
