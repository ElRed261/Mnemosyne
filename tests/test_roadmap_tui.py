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


def test_roadmap_mark_done_uses_service(tmp_path: Path) -> None:    # smoke: mark_done via service still works, TUI wrapper should call it
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


# --- Phase 1 (tui-codedex-missions): cards, XP, modal, 80x24 ---


def _fake_roadmap() -> dict:
    mods = []
    steps = []
    for mid, raw, n in (("b0", "B0", 2), ("m1a", "M1A", 3), ("x2", "X2", 0)):
        msteps = [{"id": f"{mid}-{i + 1:03d}", "title": f"s{i}", "module": mid} for i in range(n)]
        mods.append({"id": mid, "raw_id": raw, "title": f"{raw} title", "type": "troncal", "steps": msteps})
        steps.extend(msteps)
    return {"modules": mods, "steps": steps, "total": len(steps)}


def test_card_meta_states_linear_locks() -> None:
    from mnemo_tui.services.roadmap import module_cards

    rm = _fake_roadmap()
    cards = module_cards({"done": ["b0-001", "b0-002"]}, rm)
    by_id = {c["id"]: c for c in cards}
    assert by_id["b0"]["state"] == "done"
    assert by_id["m1a"]["state"] == "current"
    assert by_id["x2"]["state"] == "vacío"
    cards2 = module_cards({"done": []}, rm)
    assert {c["id"]: c["state"] for c in cards2}["b0"] == "current"
    assert {c["id"]: c["state"] for c in cards2}["m1a"] == "locked"


def test_static_xp_table() -> None:
    from mnemo_tui.services.roadmap import XP_BY_TYPE, module_cards, xp_for_module

    assert xp_for_module("troncal") == XP_BY_TYPE["troncal"] == 10
    assert xp_for_module("integración del curso") == 20
    assert xp_for_module("algo raro") == 10  # default
    rm = _fake_roadmap()
    cards = module_cards({"done": ["b0-001"]}, rm)
    b0 = next(c for c in cards if c["id"] == "b0")
    assert b0["xp_total"] == 2 * 10
    assert b0["xp_earned"] == 1 * 10


def test_stats_strip_shows_xp() -> None:
    from mnemo_tui.services.roadmap import stats_text

    txt = stats_text({"total": 5, "done": 1, "pct": 20.0}, 10, 50, {"id": "b0-002", "title": "s2"})
    assert "XP" in txt and "10/50" in txt and "b0-002" in txt


def test_mission_modal_opens_on_done() -> None:
    from mnemo_tui.app import MnemoApp
    from mnemo_tui.screens.roadmap import MissionModal

    async def _check() -> None:
        # ponytail: snapshot real repo state — do_mark_done writes progress.json + CURRENT.md
        repo = Path(__file__).resolve().parents[1]
        prog_path = repo / ".mnemosyne" / "progress.json"
        curr_path = repo / "CURRENT.md"
        prog_bak = prog_path.read_bytes() if prog_path.exists() else None
        curr_bak = curr_path.read_bytes() if curr_path.exists() else None
        try:
            app = MnemoApp()
            async with app.run_test(size=(120, 40)) as pilot:
                await pilot.pause()
                pilot.app.action_show_roadmap()
                await pilot.pause()
                await asyncio.sleep(1.5)
                road = pilot.app.query_one("#roadmap")
                nxt = road._next_pending
                assert nxt is not None
                road.do_mark_done(nxt["id"])
                await asyncio.sleep(1.5)
                modals = [w for w in pilot.app.screen_stack if isinstance(w, MissionModal)]
                assert modals, "MissionModal must open after done"
                assert modals[0].step_id == nxt["id"]
                # ponytail: plain sleeps, not pilot.pause — toasts keep the pump busy briefly
                for m in modals:
                    m.dismiss()
                await asyncio.sleep(2.0)
                assert all(not isinstance(w, MissionModal) for w in pilot.app.screen_stack)
        finally:
            if prog_bak is None:
                if prog_path.exists():
                    prog_path.unlink()
            else:
                prog_path.write_bytes(prog_bak)
            if curr_bak is not None:
                curr_path.write_bytes(curr_bak)

    asyncio.run(_check())


def test_roadmap_renders_at_80x24() -> None:
    from mnemo_tui.app import MnemoApp

    async def _check() -> None:
        app = MnemoApp()
        async with app.run_test(size=(80, 24)) as pilot:
            await pilot.pause()
            pilot.app.action_show_roadmap()
            await pilot.pause()
            await asyncio.sleep(1.5)
            road = pilot.app.query_one("#roadmap")
            assert road.query_one("#roadmap-cards") is not None
            assert road.query_one("#roadmap-stats") is not None
            assert road.query_one("#btn-next") is not None

    asyncio.run(_check())
