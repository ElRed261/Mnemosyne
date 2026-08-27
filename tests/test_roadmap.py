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
