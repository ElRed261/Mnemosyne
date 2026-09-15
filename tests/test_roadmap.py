from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from mnemo_tui.services.roadmap import (
    get_next_pending,
    get_progress,
    load_progress,
    load_roadmap,
    mark_done,
    mark_undone,
    save_progress,
)

SAMPLE_MD = """# Roadmap

## B0. Fundamentos
**Tipo:** refuerzo personal. **Entrada:** test

### B0.1. SQL
- [ ] Tablas y filas
- [ ] DDL y DML

### B0.2. Python
- [ ] Variables y bucles

## M1A. Docker e ingesta
**Tipo:** troncal, primera parte.

### Qué aprender
- [ ] Imagen y contenedor
- [x] Dockerfile

## Entorno personal y continuidad
- [ ] Este no debe contarse
"""

EXPECTED_MODULES = 2
EXPECTED_TOTAL = 5  # 3 in B0 + 2 in M1A, outside ignored


def _write_roadmap(tmp_path: Path, content: str = SAMPLE_MD) -> Path:
    docs = tmp_path / "docs"
    docs.mkdir(parents=True)
    p = docs / "ROADMAP.md"
    p.write_text(content, encoding="utf-8")
    return p


def test_parser_finds_modules_and_total(tmp_path: Path) -> None:
    _write_roadmap(tmp_path)
    rm = load_roadmap(tmp_path)
    assert len(rm["modules"]) == EXPECTED_MODULES
    assert rm["total"] == EXPECTED_TOTAL
    assert len(rm["steps"]) == EXPECTED_TOTAL


def test_parser_step_ids_sequential(tmp_path: Path) -> None:
    _write_roadmap(tmp_path)
    rm = load_roadmap(tmp_path)
    b0 = [s for s in rm["steps"] if s["module"] == "b0"]
    m1a = [s for s in rm["steps"] if s["module"] == "m1a"]
    assert [s["id"] for s in b0] == ["b0-001", "b0-002", "b0-003"]
    assert [s["id"] for s in m1a] == ["m1a-001", "m1a-002"]
    # section grouping: first two under B0.1, third under B0.2
    assert b0[0]["section"] == "B0.1. SQL"
    assert b0[2]["section"] == "B0.2. Python"
    # type extraction
    assert rm["modules"][0]["type"] == "refuerzo personal"
    assert "troncal" in rm["modules"][1]["type"]


def test_parser_real_roadmap_counts() -> None:
    # use the copied docs/ROADMAP.md in repo root
    repo = Path(__file__).resolve().parents[1]
    rm = load_roadmap(repo)
    # 154 steps inside modules, outside 26 ignored, X2 has 0
    assert rm["total"] == 154
    ids = [m["id"] for m in rm["modules"]]
    assert ids == ["b0", "m1a", "m1b", "m2", "t1", "m3", "m4", "m5", "m6", "m7", "pf", "x1", "x2"]
    # X2 vacío
    x2 = next(m for m in rm["modules"] if m["id"] == "x2")
    assert len(x2["steps"]) == 0
    # B0 should have 27, M1A 12 etc
    by_id = {m["id"]: len(m["steps"]) for m in rm["modules"]}
    assert by_id["b0"] == 27
    assert by_id["m1a"] == 12
    assert by_id["pf"] == 16


def test_progress_load_save_cycle(tmp_path: Path) -> None:
    _write_roadmap(tmp_path)
    # initially empty
    prog = load_progress(tmp_path)
    assert prog["done"] == []
    save_progress(tmp_path, {"done": ["b0-001", "m1a-001"]})
    reloaded = load_progress(tmp_path)
    assert set(reloaded["done"]) == {"b0-001", "m1a-001"}
    assert reloaded["updated"] is not None
    # file exists and is valid json with indent
    raw = (tmp_path / ".mnemosyne" / "progress.json").read_text(encoding="utf-8")
    data = json.loads(raw)
    assert "done" in data and "updated" in data


def test_mark_done_and_undone(tmp_path: Path) -> None:
    _write_roadmap(tmp_path)
    # mark
    mark_done(tmp_path, "b0-001")
    prog = load_progress(tmp_path)
    assert "b0-001" in prog["done"]
    # dedup: marking again does not duplicate
    mark_done(tmp_path, "b0-001")
    prog2 = load_progress(tmp_path)
    assert prog2["done"].count("b0-001") == 1
    # ordering: mark m1a-002 then b0-002 should sort by roadmap order
    mark_done(tmp_path, "m1a-002")
    mark_done(tmp_path, "b0-002")
    prog3 = load_progress(tmp_path)
    # order should be b0-001, b0-002, m1a-002 (roadmap order)
    assert prog3["done"] == ["b0-001", "b0-002", "m1a-002"]
    # undo
    mark_undone(tmp_path, "b0-001")
    prog4 = load_progress(tmp_path)
    assert "b0-001" not in prog4["done"]
    assert "b0-002" in prog4["done"]


def test_mark_done_invalid_raises(tmp_path: Path) -> None:
    _write_roadmap(tmp_path)
    try:
        mark_done(tmp_path, "bad-id")
        assert False, "should raise"
    except ValueError as exc:
        assert "válido" in str(exc) or "inválido" in str(exc).lower()
    try:
        mark_done(tmp_path, "b0-999")
        assert False, "should raise for unknown"
    except ValueError as exc:
        assert "desconocido" in str(exc)


def test_next_pending_and_progress(tmp_path: Path) -> None:
    _write_roadmap(tmp_path)
    rm = load_roadmap(tmp_path)
    prog = load_progress(tmp_path)
    nxt = get_next_pending(prog, rm)
    assert nxt is not None and nxt["id"] == "b0-001"
    # after marking b0-001, next is b0-002
    mark_done(tmp_path, "b0-001")
    prog = load_progress(tmp_path)
    nxt2 = get_next_pending(prog, rm)
    assert nxt2 is not None and nxt2["id"] == "b0-002"
    # progress stats
    stats = get_progress(prog, rm)
    assert stats["total"] == EXPECTED_TOTAL
    assert stats["done"] == 1
    assert stats["pct"] == round(1 / EXPECTED_TOTAL * 100, 1)
    assert len(stats["by_module"]) == EXPECTED_MODULES
    b0_stat = next(m for m in stats["by_module"] if m["id"] == "b0")
    assert b0_stat["done"] == 1 and b0_stat["total"] == 3
    # complete all
    for sid in ["b0-002", "b0-003", "m1a-001", "m1a-002"]:
        mark_done(tmp_path, sid)
    prog_all = load_progress(tmp_path)
    assert get_next_pending(prog_all, rm) is None
    stats_all = get_progress(prog_all, rm)
    assert stats_all["done"] == EXPECTED_TOTAL
    assert stats_all["pct"] == 100.0


# --- Phase 2 (tui-codedex-missions): MANIFEST, scan, allowlisted verify ---


def _write_manifest(tmp_path: Path, mid: str, payload: object, raw: str | None = None) -> Path:
    d = tmp_path / "evidence" / mid
    d.mkdir(parents=True, exist_ok=True)
    p = d / "MANIFEST.json"
    if raw is not None:
        p.write_text(raw, encoding="utf-8")
    else:
        import json as _json

        p.write_text(_json.dumps(payload), encoding="utf-8")
    return p


def test_scan_marks_present_missing(tmp_path: Path) -> None:
    from mnemo_tui.services.roadmap import evidence_state, scan_evidence

    _write_roadmap(tmp_path)
    _write_manifest(tmp_path, "b0", {"version": 1, "module": "b0", "steps": {"b0-001": ["a.txt", "sub/b.txt"]}})
    (tmp_path / "evidence" / "b0" / "a.txt").write_text("x", encoding="utf-8")
    scan = scan_evidence(tmp_path, "b0")
    assert scan["b0-001"] is False  # sub/b.txt missing
    (tmp_path / "evidence" / "b0" / "sub").mkdir()
    (tmp_path / "evidence" / "b0" / "sub" / "b.txt").write_text("y", encoding="utf-8")
    assert scan_evidence(tmp_path, "b0")["b0-001"] is True
    rm = load_roadmap(tmp_path)
    assert evidence_state(tmp_path, rm, {"done": []})["b0-001"] == "ok"


def test_manifest_corrupt_falls_back_manual(tmp_path: Path) -> None:
    from mnemo_tui.services.roadmap import evidence_state

    _write_roadmap(tmp_path)
    _write_manifest(tmp_path, "b0", None, raw="{no es json")
    rm = load_roadmap(tmp_path)
    st = evidence_state(tmp_path, rm, {"done": []})
    assert st["b0-001"] == "error"  # corrupt manifest never blocks manual done
    assert st["m1a-001"] == "none"  # no manifest at all


def test_executable_evidence_never_run(tmp_path: Path) -> None:
    from mnemo_tui.services.roadmap import scan_evidence

    _write_roadmap(tmp_path)
    evil = tmp_path / "evidence" / "b0" / "runme.sh"
    evil.parent.mkdir(parents=True)
    evil.write_text("#!/bin/sh\ntouch MARKER_EXECUTED\n", encoding="utf-8")
    _write_manifest(tmp_path, "b0", {"version": 1, "module": "b0", "steps": {"b0-001": ["runme.sh"]}})
    assert scan_evidence(tmp_path, "b0")["b0-001"] is True  # exists, not executed
    assert not (tmp_path / "evidence" / "b0" / "MARKER_EXECUTED").exists()
    assert not (tmp_path / "MARKER_EXECUTED").exists()


def test_manifest_path_escape_treated_missing(tmp_path: Path) -> None:
    from mnemo_tui.services.roadmap import scan_evidence

    _write_roadmap(tmp_path)
    _write_manifest(
        tmp_path,
        "b0",
        {"version": 1, "module": "b0", "steps": {"b0-001": ["../escape.txt", "/abs.txt"]}},
    )
    (tmp_path / "escape.txt").write_text("sensitive", encoding="utf-8")
    assert scan_evidence(tmp_path, "b0")["b0-001"] is False


def test_missions_overlay_ignores_unknown_keys(tmp_path: Path) -> None:
    from mnemo_tui.services.roadmap import missions_overlay

    cfg = {"missions": {"b0": {"xp": 99, "verify": [["echo", "hi"]], "nonsense": 1, "nested": {"a": 1}}}}
    ov = missions_overlay(cfg, "b0")
    assert ov["xp"] == 99
    assert ov["verify"] == [["echo", "hi"]]
    assert "nonsense" not in ov and "nested" not in ov
    assert missions_overlay(cfg, "m1a") == {}
    assert missions_overlay({}, "b0") == {}


def _load_mnemo_cli():
    import importlib.util
    import sys as _sys

    script = Path(__file__).resolve().parents[1] / "scripts" / "mnemo.py"
    spec = importlib.util.spec_from_file_location("mnemo_cli_p2", script)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    _sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def test_malicious_verify_refused(tmp_path: Path) -> None:
    mnemo = _load_mnemo_cli()
    marker = tmp_path / "PWNED"
    for bad in (
        [["rm", "-rf", "/"]],
        [["/bin/echo", "hi"]],
        [["../evil.sh"]],
        [["echo", "a;b"]],
        [["echo", "$(touch PWNED)"]],
        ["not-a-list"],
    ):
        cfg = {"missions": {"b0": {"verify": bad}}}
        try:
            mnemo.run_module_verify(tmp_path, cfg, "b0")
            assert False, f"must refuse {bad}"
        except mnemo.MnemoError:
            pass
    assert not marker.exists()


def test_module_verify_runs_allowlisted_command(tmp_path: Path) -> None:
    mnemo = _load_mnemo_cli()
    cfg = {"missions": {"b0": {"verify": [["true"]]}}}
    assert mnemo.run_module_verify(tmp_path, cfg, "b0") == 0
    cfg2 = {"missions": {"b0": {"verify": [["false"]]}}}
    try:
        mnemo.run_module_verify(tmp_path, cfg2, "b0")
        assert False, "failing verify must raise"
    except mnemo.MnemoError:
        pass


# --- Phase 3 (tui-codedex-missions): XP ledger, levels, streak ---


def test_xp_awarded_once(tmp_path: Path) -> None:
    from mnemo_tui.services.gamification import award_xp, total_xp

    award_xp(tmp_path, "b0-001", 10, source="verify")
    award_xp(tmp_path, "b0-001", 10, source="verify")  # replay must not double count
    award_xp(tmp_path, "b0-002", 10, source="verify")
    assert total_xp(tmp_path) == 20


def test_level_and_rank_boundaries() -> None:
    from mnemo_tui.services.gamification import level_for_xp, rank_for_level

    assert level_for_xp(0) == 1
    assert level_for_xp(99) == 1
    assert level_for_xp(100) == 2
    assert level_for_xp(250) == 3
    assert level_for_xp(18000) == 25
    assert level_for_xp(999999) == 25  # capped
    assert rank_for_level(1) == "Bronze"
    assert rank_for_level(5) == "Bronze"
    assert rank_for_level(6) == "Silver"
    assert rank_for_level(11) == "Gold"
    assert rank_for_level(16) == "Platinum"
    assert rank_for_level(21) == "Diamond"
    assert rank_for_level(25) == "Diamond"


def test_streak_gap_no_backfill() -> None:
    import datetime as dt

    from mnemo_tui.services.gamification import streak_days

    today = dt.date(2026, 9, 15)
    iso = lambda d: dt.datetime(d.year, d.month, d.day, 12, tzinfo=dt.UTC).isoformat()
    d = lambda n: today - dt.timedelta(days=n)
    # run D-2..D0 with a gap at D-3 -> streak 3, older dates do not extend
    assert streak_days([iso(d(4)), iso(d(2)), iso(d(1)), iso(d(0))], today) == 3
    assert streak_days([iso(d(4)), iso(d(2)), iso(d(1)), iso(d(0)), iso(d(10))], today) == 3
    assert streak_days([], today) == 0
    # yesterday only still counts as active streak of 1
    assert streak_days([iso(d(1))], today) == 1
    # last activity 3 days ago -> streak over
    assert streak_days([iso(d(3))], today) == 0


def test_badges_per_completed_module(tmp_path: Path) -> None:
    from mnemo_tui.services.gamification import badges_for
    from mnemo_tui.services.roadmap import load_roadmap

    _write_roadmap(tmp_path)
    rm = load_roadmap(tmp_path)
    assert badges_for({"done": []}, rm) == []
    all_b0 = [s["id"] for s in rm["steps"] if s["module"] == "b0"]
    assert badges_for({"done": all_b0}, rm) == ["b0"]
