from __future__ import annotations

import asyncio
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))


def test_import_roadmap_screen() -> None:
    from mnemo_tui.screens.roadmap import HAS_TEXTUAL, RoadmapScreen

    assert HAS_TEXTUAL is True
    assert RoadmapScreen is not None
    # ponytail: smoke import, no crash
    s = RoadmapScreen(id="roadmap")  # type: ignore[call-arg]
    assert s is not None


def test_roadmap_refresh_is_work_decorated() -> None:
    import inspect

    from mnemo_tui.screens.roadmap import RoadmapScreen

    fn = getattr(RoadmapScreen, "refresh_roadmap", None)
    assert fn is not None, "refresh_roadmap missing"
    has_work = False
    if hasattr(fn, "_work") or hasattr(fn, "__wrapped__"):
        has_work = True
    else:
        src = inspect.getsource(fn)
        has_work = "@work" in src or "work(" in src
    assert has_work, "refresh_roadmap must be @work(thread=True)"
    # also check call_from_thread usage
    src2 = inspect.getsource(fn)
    assert "call_from_thread" in inspect.getsource(RoadmapScreen._apply_refresh) or "call_from_thread" in src2


def test_dashboard_has_roadmap_button() -> None:
    import inspect

    from mnemo_tui.screens.dashboard import DashboardScreen

    src = inspect.getsource(DashboardScreen.compose)
    assert "roadmap" in src.lower(), "dashboard compose must include roadmap button"
    src2 = inspect.getsource(DashboardScreen.on_button_pressed)
    assert "roadmap" in src2.lower(), "dashboard button handler must handle roadmap"


def test_app_composes_roadmap_and_bindings() -> None:
    import inspect

    from mnemo_tui.app import MnemoApp

    app = MnemoApp()
    assert hasattr(app, "show_roadmap")
    assert hasattr(app, "hide_roadmap")
    assert hasattr(MnemoApp, "BINDINGS")
    bindings = getattr(MnemoApp, "BINDINGS", [])
    assert any("roadmap" in str(b).lower() for b in bindings), "BINDINGS must include roadmap"
    src = inspect.getsource(MnemoApp.compose)
    assert "roadmap" in src.lower(), "app compose must yield RoadmapScreen"
    # check action methods exist
    assert hasattr(MnemoApp, "action_show_roadmap")
    assert hasattr(MnemoApp, "action_hide_roadmap")


def test_roadmap_pilot_toggle_and_list() -> None:
    from mnemo_tui.app import MnemoApp

    async def _check() -> None:
        app = MnemoApp()
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.pause()
            road = pilot.app.query_one("#roadmap")
            # initially hidden (display False)
            assert getattr(road, "display", False) is False
            # need dashboard visible
            dash = pilot.app.query_one("#dashboard")
            assert getattr(dash, "display", True) is True
            # show roadmap
            pilot.app.action_show_roadmap()
            await pilot.pause()
            await asyncio.sleep(0.6)
            assert getattr(road, "display", False) is True
            assert getattr(dash, "display", True) is False
            # allow worker to populate list
            await asyncio.sleep(1.2)
            lv = road.query_one("#roadmap-list")
            # ListView should have items (headers + steps)
            # total steps 154 + 13 headers = ~167, allow >= 10
            assert len(lv) >= 10, f"list too small {len(lv)}"
            detail = road.query_one("#roadmap-detail")
            assert detail is not None
            # progress bar or static exists
            prog = road.query_one("#roadmap-progress")
            assert prog is not None
            # hide again
            pilot.app.action_hide_roadmap()
            await pilot.pause()
            assert getattr(road, "display", True) is False
            assert getattr(dash, "display", False) is True

    asyncio.run(_check())


def test_roadmap_mark_done_uses_service(tmp_path: Path) -> None:
    # smoke: mark_done via service still works, TUI wrapper should call it
    from mnemo_tui.services.roadmap import load_progress, load_roadmap, mark_done, mark_undone

    # copy real roadmap to tmp for isolated test
    repo = Path(__file__).resolve().parents[1]
    docs_src = repo / "docs" / "ROADMAP.md"
    docs_dst = tmp_path / "docs" / "ROADMAP.md"
    docs_dst.parent.mkdir(parents=True)
    shutil.copy(docs_src, docs_dst)

    rm = load_roadmap(tmp_path)
    _ = load_progress(tmp_path)
    first = rm["steps"][0]["id"]
    mark_done(tmp_path, first)
    prog2 = load_progress(tmp_path)
    assert first in prog2["done"]
    mark_undone(tmp_path, first)
    prog3 = load_progress(tmp_path)
    assert first not in prog3["done"]
