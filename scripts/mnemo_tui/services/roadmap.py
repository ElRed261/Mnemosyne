"""Roadmap service — stdlib-only parser and progress store (Fase 1)."""

from __future__ import annotations

import datetime as dt
import json
import os
import re
import tempfile
from pathlib import Path

# ponytail: naive markdown parser, assumes stable ## / ### + "- [ ]" structure, upgrade if roadmap evolves
REPO_RE = re.compile(r"^[A-Za-z0-9_.-]+$")
STEP_RE = re.compile(r"^[a-z0-9]+-\d{3}$")
MODULE_RE = re.compile(r"^(B0|M1A|M1B|M2|T1|M3|M4|M5|M6|M7|PF|X1|X2)\b", re.IGNORECASE)
CHECKBOX_RE = re.compile(r"^\s*-\s*\[( |x|X)\]\s*(.+)$")
HEADER_RE = re.compile(r"^##\s+(.+)$")
LESSON_RE = re.compile(r"^###\s+(.+)$")
TYPE_RE = re.compile(r"\*\*Tipo:\*\*\s*([^.\n]+)")


def _validate_step_id(step_id: str) -> str:
    raw = step_id.strip().lower()
    if not raw:
        raise ValueError("step_id requerido")
    if any(c in raw for c in [";", "&", "|", "`", "$", "(", ")"]):
        raise ValueError("step_id inválido")
    if not STEP_RE.fullmatch(raw):
        raise ValueError(f"step_id inválido `{step_id}` — esperado formato b0-001")
    return raw


def _roadmap_path(repo_root: Path) -> Path:
    return Path(repo_root).resolve() / "docs" / "ROADMAP.md"


def _progress_path(repo_root: Path) -> Path:
    return Path(repo_root).resolve() / ".mnemosyne" / "progress.json"


def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    tmp_path = Path(tmp)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(content)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp_path, path)
    finally:
        tmp_path.unlink(missing_ok=True)


def _resolve_repo_safe(repo_root: Path | str | None) -> Path:
    # ponytail: minimal guard, reuse pattern from system.py — block traversal and /tmp
    raw = str(repo_root) if repo_root is not None else ""
    if raw and any(c in raw for c in [";", "&", "|", "`", "$"]):
        raise ValueError("ruta de repo inválida")
    if raw and ".." in raw.split("/"):
        raise ValueError("ruta de repo inválida")
    p = Path(repo_root).resolve() if repo_root else Path.cwd().resolve()
    # ensure directory exists
    if not p.exists():
        raise ValueError("repositorio no existe")
    return p


def load_roadmap(repo_root: Path | str) -> dict:
    """Parse docs/ROADMAP.md into ordered modules/steps.

    Returns: {"modules": [...], "steps": [...], "total": int}
    Each module: {id, raw_id, title, type, steps: [...], lessons: [...]}
    Each step: {id, title, section, module, checked}
    """
    root = _resolve_repo_safe(repo_root)
    path = _roadmap_path(root)
    if not path.exists():
        raise FileNotFoundError(f"no se encontró ROADMAP en {path}")
    text = path.read_text(encoding="utf-8")
    modules: list[dict] = []
    steps_flat: list[dict] = []
    current: dict | None = None
    current_lesson: dict | None = None
    counters: dict[str, int] = {}
    # track type detection per module — look ahead for **Tipo:**
    lines = text.splitlines()
    for idx, line in enumerate(lines):
        h = HEADER_RE.match(line)
        if h:
            title = h.group(1).strip()
            m = MODULE_RE.match(title)
            if m:
                raw_id = m.group(1).upper()
                nid = raw_id.lower()
                current = {
                    "id": nid,
                    "raw_id": raw_id,
                    "title": title,
                    "type": "",
                    "steps": [],
                    "lessons": [],
                }
                modules.append(current)
                current_lesson = None
                counters.setdefault(nid, 0)
                # peek next lines for Tipo
                window = "\n".join(lines[idx : idx + 4])
                tm = TYPE_RE.search(window)
                if tm:
                    current["type"] = tm.group(1).strip().lower()
                continue
            else:
                current = None
                current_lesson = None
                continue
        lm = LESSON_RE.match(line)
        if lm and current is not None:
            t = lm.group(1).strip()
            current_lesson = {"title": t, "steps": []}
            current["lessons"].append(current_lesson)
            continue
        cb = CHECKBOX_RE.match(line)
        if cb and current is not None:
            # ponytail: ignore checkboxes outside modules — outside is not curriculum progress
            checked = cb.group(1).lower() == "x"
            title_raw = cb.group(2).strip()
            nid = current["id"]
            counters[nid] = counters.get(nid, 0) + 1
            step_id = f"{nid}-{counters[nid]:03d}"
            section = current_lesson["title"] if current_lesson else current["title"]
            step = {
                "id": step_id,
                "title": title_raw,
                "checked": checked,
                "section": section,
                "module": nid,
            }
            current["steps"].append(step)
            if current_lesson is not None:
                current_lesson["steps"].append(step)
            steps_flat.append(step)
    return {"modules": modules, "steps": steps_flat, "total": len(steps_flat)}


def load_progress(repo_root: Path | str) -> dict:
    """Load .mnemosyne/progress.json — returns {"done": [...], "updated": str|None}."""
    root = _resolve_repo_safe(repo_root)
    path = _progress_path(root)
    if not path.exists():
        return {"done": [], "updated": None}
    try:
        raw = path.read_text(encoding="utf-8")
        data = json.loads(raw)
        if not isinstance(data, dict):
            return {"done": [], "updated": None}
        done = data.get("done", [])
        if not isinstance(done, list):
            done = []
        cleaned: list[str] = []
        seen: set[str] = set()
        for item in done:
            if not isinstance(item, str):
                continue
            nid = item.strip().lower()
            if not nid or nid in seen:
                continue
            # ponytail: allow any lower id, validation done on mark_done — keep permissive here
            if STEP_RE.fullmatch(nid):
                cleaned.append(nid)
                seen.add(nid)
            else:
                # keep unknown format but deduped
                cleaned.append(nid)
                seen.add(nid)
        return {"done": cleaned, "updated": data.get("updated")}
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return {"done": [], "updated": None}


def save_progress(repo_root: Path | str, data: dict) -> None:
    """Save progress atomically to .mnemosyne/progress.json."""
    root = _resolve_repo_safe(repo_root)
    path = _progress_path(root)
    done = data.get("done", []) if isinstance(data, dict) else []
    # dedup + sort by roadmap order if possible, fallback lexical
    if isinstance(done, list):
        seen: set[str] = set()
        uniq: list[str] = []
        for item in done:
            if not isinstance(item, str):
                continue
            nid = item.strip().lower()
            if nid and nid not in seen and STEP_RE.fullmatch(nid):
                # ponytail: filter only valid step ids on save
                uniq.append(nid)
                seen.add(nid)
        try:
            roadmap = load_roadmap(root)
            order = {s["id"]: i for i, s in enumerate(roadmap["steps"])}
            uniq.sort(key=lambda x: order.get(x, 9999))
        except Exception:  # noqa: BLE001
            uniq.sort()
        payload = {
            "done": uniq,
            "updated": data.get("updated")
            or dt.datetime.now(dt.UTC).isoformat(),
        }
    else:
        payload = {"done": [], "updated": dt.datetime.now(dt.UTC).isoformat()}
    content = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    _atomic_write(path, content)


def get_next_pending(progress: dict, roadmap: dict) -> dict | None:
    """Return first pending step or None if completed."""
    done = set(progress.get("done", [])) if isinstance(progress, dict) else set()
    for step in roadmap.get("steps", []):
        if step["id"] not in done:
            return step
    return None


def get_progress(progress: dict, roadmap: dict) -> dict:
    """Compute {total, done, pct, by_module}."""
    steps = roadmap.get("steps", [])
    modules = roadmap.get("modules", [])
    total = len(steps)
    done_set = set(progress.get("done", [])) if isinstance(progress, dict) else set()
    done = sum(1 for s in steps if s["id"] in done_set)
    pct = round(done / total * 100, 1) if total else 0.0
    by_module: list[dict] = []
    for m in modules:
        m_steps = m.get("steps", [])
        m_total = len(m_steps)
        m_done = sum(1 for s in m_steps if s["id"] in done_set)
        m_pct = round(m_done / m_total * 100, 1) if m_total else 0.0
        if m_total == 0:
            status = "vacío"
        elif m_done == 0:
            status = "pendiente"
        elif m_done == m_total:
            status = "completado"
        else:
            status = "en_progreso"
        by_module.append(
            {
                "id": m["id"],
                "title": m["title"],
                "type": m.get("type", ""),
                "total": m_total,
                "done": m_done,
                "pct": m_pct,
                "status": status,
            }
        )
    return {"total": total, "done": done, "pct": pct, "by_module": by_module}


def mark_done(repo_root: Path | str, step_id: str) -> dict:
    """Mark step as done, persist, return new progress."""
    nid = _validate_step_id(step_id)
    root = _resolve_repo_safe(repo_root)
    roadmap = load_roadmap(root)
    valid = {s["id"] for s in roadmap["steps"]}
    if nid not in valid:
        raise ValueError(f"paso desconocido `{step_id}`")
    progress = load_progress(root)
    done = progress.get("done", [])
    if nid not in done:
        done.append(nid)
        order = {s["id"]: i for i, s in enumerate(roadmap["steps"])}
        done = sorted(set(done), key=lambda x: order.get(x, 9999))
    payload = {"done": done, "updated": dt.datetime.now(dt.UTC).isoformat()}
    save_progress(root, payload)
    return payload


def mark_undone(repo_root: Path | str, step_id: str) -> dict:
    """Remove step from done, persist, return new progress."""
    nid = _validate_step_id(step_id)
    root = _resolve_repo_safe(repo_root)
    # validate exists in roadmap (optional — allow undone even if invalid? require valid)
    try:
        roadmap = load_roadmap(root)
        valid = {s["id"] for s in roadmap["steps"]}
        if nid not in valid:
            raise ValueError(f"paso desconocido `{step_id}`")
    except FileNotFoundError:
        pass
    progress = load_progress(root)
    done = [d for d in progress.get("done", []) if d != nid]
    payload = {"done": done, "updated": dt.datetime.now(dt.UTC).isoformat()}
    save_progress(root, payload)
    return payload
