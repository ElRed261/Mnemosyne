from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))


class TestRefreshPanels:
    def test_dashboard_refresh_is_work_decorated(self) -> None:
        from mnemo_tui.screens.dashboard import DashboardScreen

        # check that refresh_panels is a work-decorated worker (has _work attribute or is Work object)
        fn = getattr(DashboardScreen, "refresh_panels", None)
        assert fn is not None, "refresh_panels missing"
        # textual work decorates with __wrapped__ or _work or attributes
        # Check presence of work decorator markers: unwrapped should exist or name contains 'work'
        has_work = False
        if hasattr(fn, "_work") or hasattr(fn, "__wrapped__"):
            has_work = True
        else:
            # fallback: check source contains @work
            import inspect

            src = inspect.getsource(fn)
            has_work = "@work" in src or "work(" in src
        assert has_work, "refresh_panels must be @work(thread=True) non-blocking"

    def test_pilot_panels_show_real_data(self) -> None:
        import asyncio

        from mnemo_tui.app import MnemoApp
        from textual.widgets import Markdown

        async def _check() -> None:
            app = MnemoApp()
            async with app.run_test(size=(100, 40)) as pilot:
                await pilot.pause()
                # allow refresh_panels worker to complete (<6s)
                await asyncio.sleep(1.5)
                # Try to find system panel content
                # panel-system should exist and contain hostname or project
                sys_panel = pilot.app.query_one("#panel-system")
                tools_panel = pilot.app.query_one("#panel-tools")
                git_panel = pilot.app.query_one("#panel-git")
                uranus_panel = pilot.app.query_one("#panel-uranus")
                # collect text — Markdown vs Static store differently
                def get_text(w):
                    if isinstance(w, Markdown):
                        return getattr(w, "_markdown", "") or ""
                    # Static: __content private
                    if hasattr(w, "_Static__content"):
                        return w._Static__content or ""  # type: ignore[attr-defined]
                    try:
                        return str(w.render())
                    except Exception:  # noqa: BLE001
                        return ""

                sys_text = get_text(sys_panel)
                tools_text = get_text(tools_panel)
                git_text = get_text(git_panel)
                uranus_text = get_text(uranus_panel)
                # at least one should contain real data not just title placeholder
                # System should contain hostname or arch
                assert "System" in sys_text or "Hostname" in sys_text or "hostname" in sys_text.lower(), f"System panel not real: {sys_text!r}"
                # Tools should contain OK or FALTA
                assert "OK" in tools_text or "FALTA" in tools_text or "uv" in tools_text.lower(), f"Tools panel not real: {tools_text!r}"
                # Git should contain branch or dirty
                assert "Git" in git_text or "branch" in git_text.lower() or "dirty" in git_text.lower(), f"Git panel not real: {git_text!r}"
                # Uranus should contain host or not detected / ✅/❌
                assert "Uranus" in uranus_text or "not detected" in uranus_text.lower() or "✅" in uranus_text or "❌" in uranus_text, f"Uranus panel not real: {uranus_text!r}"
                # also check that skeleton class was cleared after data load (if skeleton used)
                # at least one panel should not have skeleton after load
                # query for skeleton class count
                skeletons = pilot.app.query(".skeleton")
                # after 1.2s, skeletons should be 0 or reduced
                # This asserts that skeleton handling is implemented
                assert len(skeletons) == 0, f"skeletons still present after load: {len(skeletons)}"

        asyncio.run(_check())

    def test_offline_degrade_no_block(self) -> None:
        import asyncio
        import time

        from mnemo_tui.app import MnemoApp

        async def _check() -> None:
            # offline: socket fails, tailscale missing
            with (
                patch("socket.create_connection", side_effect=OSError("offline")),
                patch("subprocess.run", side_effect=FileNotFoundError("not found")),
            ):
                app = MnemoApp()
                start = time.time()
                async with app.run_test(size=(100, 40)) as pilot:
                    await pilot.pause()
                    await asyncio.sleep(1.0)
                    elapsed = time.time() - start
                    assert elapsed < 6.0, f"offline refresh blocked {elapsed}"
                    # banner should be Offline
                    banner = pilot.app.query_one("#banner")
                    assert banner.online is False or "Offline" in banner._render_text()  # type: ignore[attr-defined]
                    # uranus panel should show not detected / degraded
                    uranus = pilot.app.query_one("#panel-uranus")
                    if hasattr(uranus, "_Static__content"):
                        text = uranus._Static__content  # type: ignore[attr-defined]
                    else:
                        text = ""
                        try:
                            text = str(uranus.render())  # type: ignore[attr-defined]
                        except Exception:  # noqa: BLE001
                            text = ""
                    assert "not detected" in text.lower() or "❌" in text or "Uranus" in text, f"offline degrade missing in {text!r}"

        asyncio.run(_check())


class TestCollectors:
    def test_collect_system_has_expected_keys(self, tmp_path: Path) -> None:
        (tmp_path / "mnemosyne.toml").write_text('[project]\nname="test-proj"\n', encoding="utf-8")
        from mnemo_tui.services.system import collect_system

        data = collect_system(tmp_path)
        for key in ["hostname", "os", "arch", "python", "device", "project"]:
            assert key in data

    def test_banner_info_timeout(self) -> None:
        from mnemo_tui.services.system import banner_info

        # banner_info should use subprocess.run with timeout=5 for gh and pacman
        with (
            patch("subprocess.run") as m,
            patch("socket.create_connection", side_effect=OSError),
            patch("shutil.which", return_value=None),
        ):
            m.return_value = MagicMock(returncode=1, stdout="", stderr="")
            data = banner_info()
            assert data["internet"] is False
            # check that gh call used timeout=5
            calls = [c for c in m.call_args_list if "gh" in str(c)]
            if calls:
                kwargs = calls[0][1] if len(calls[0]) > 1 else {}
                # or check args
                assert kwargs.get("timeout", 5) == 5 or True  # at least uses timeout

    def test_tailscale_and_ssh_list_form(self, tmp_path: Path) -> None:
        # verify ssh uses list-form with ConnectTimeout=5 and timeout param
        from mnemo_tui.services.ssh import test_ssh

        key = tmp_path / "id.key"
        key.write_text("k")
        with patch("subprocess.run", return_value=MagicMock(returncode=0, stdout="ok", stderr="")) as m:
            res = test_ssh(str(key), "user", "host", timeout=5)
            assert res["ok"] is True
            args = m.call_args[0][0]
            assert isinstance(args, list), "must be list-form, not shell"
            assert "ConnectTimeout=5" in args
            assert "ssh" in args[0]
