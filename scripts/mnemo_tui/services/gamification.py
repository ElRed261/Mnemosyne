"""Gamification service — XP ledger, levels, badges, streak (Phase 3).

Pure computation plus one append-only ledger file (.mnemosyne/xp_ledger.json).
Stdlib only. XP is awarded only on verified done (CLI --with-check);
manual done never mints XP.
"""

from __future__ import annotations

import datetime as dt
import json
import os
import re
import tempfile
from pathlib import Path

# ponytail: explicit table to level 25, CodeDex-style thresholds; capped, no formula drift
LEVEL_THRESHOLDS: list[int] = [
    0, 100, 250, 500, 750, 1000, 1500, 2000, 2500, 3000,
    4000, 5000, 6000, 7000, 8000, 9000, 10000, 11000, 12000, 13000,
    14000, 15000, 16000, 17000, 18000,
]
MAX_LEVEL = 25

RANKS: tuple[tuple[int, str], ...] = (
    (1, "Bronze"),
    (6, "Silver"),
    (11, "Gold"),
    (16, "Platinum"),
    (21, "Diamond"),
)

_STEP_RE = re.compile(r"^[a-z0-9]+-\d{3}$")


def _ledger_path(repo_root: Path | str) -> Path:
    raw = str(repo_root) if repo_root is not None else ""
    if raw and any(c in raw for c in [";", "&", "|", "`", "$"]):
        raise ValueError("ruta de repo inválida")
    if raw and ".." in raw.split("/"):
        raise ValueError("ruta de repo inválida")
    p = Path(repo_root).resolve() if repo_root else Path.cwd().resolve()
    if not p.exists():
        raise ValueError("repositorio no existe")
    return p / ".mnemosyne" / "xp_ledger.json"


def _atomic_write_json(path: Path, payload: dict) -> None:
    # ponytail: same atomic pattern as roadmap service, kept local to avoid private imports
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".xp_ledger.", dir=path.parent)
    tmp_path = Path(tmp)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp_path, path)
    finally:
        tmp_path.unlink(missing_ok=True)


def load_ledger(repo_root: Path | str) -> dict:
    """Load ledger — {"awards": [{step_id, xp, source, at}]}. Empty when absent/corrupt."""
    try:
        path = _ledger_path(repo_root)
    except ValueError:
        return {"awards": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return {"awards": []}
    if not isinstance(data, dict):
        return {"awards": []}
    awards = data.get("awards", [])
    if not isinstance(awards, list):
        return {"awards": []}
    clean = [a for a in awards if isinstance(a, dict) and isinstance(a.get("step_id"), str)]
    return {"awards": clean}


def award_xp(repo_root: Path | str, step_id: str, xp: int, source: str = "verify") -> dict:
    """Append one XP award. Idempotent per step (XP-once): replays add nothing."""
    sid = str(step_id).strip().lower()
    if not _STEP_RE.fullmatch(sid):
        raise ValueError(f"step_id inválido `{step_id}`")
    if not isinstance(xp, int) or isinstance(xp, bool) or xp <= 0:
        raise ValueError("xp debe ser entero positivo")
    ledger = load_ledger(repo_root)
    awards = ledger["awards"]
    if any(a.get("step_id") == sid for a in awards):
        return ledger
    awards.append(
        {
            "step_id": sid,
            "xp": xp,
            "source": str(source),
            "at": dt.datetime.now(dt.UTC).isoformat(),
        }
    )
    _atomic_write_json(_ledger_path(repo_root), {"awards": awards})
    return {"awards": awards}


def total_xp(repo_root: Path | str) -> int:
    """Sum of awarded XP. Accepts a repo root or a loaded ledger dict."""
    if isinstance(repo_root, dict):
        awards = repo_root.get("awards", [])
    else:
        awards = load_ledger(repo_root).get("awards", [])
    total = 0
    for a in awards:
        xp = a.get("xp", 0) if isinstance(a, dict) else 0
        if isinstance(xp, int) and not isinstance(xp, bool) and xp > 0:
            total += xp
    return total


def level_for_xp(xp: int) -> int:
    """Level 1..25 from cumulative XP. Pure function."""
    xp = max(0, int(xp))
    level = 1
    for idx, threshold in enumerate(LEVEL_THRESHOLDS, start=1):
        if xp >= threshold:
            level = idx
    return min(level, MAX_LEVEL)


def rank_for_level(level: int) -> str:
    """Rank name for a level. Pure function."""
    level = max(1, min(int(level), MAX_LEVEL))
    name = RANKS[0][1]
    for start, title in RANKS:
        if level >= start:
            name = title
    return name


def badges_for(progress: dict, roadmap: dict) -> list[str]:
    """Module ids with every step done. Pure function."""
    done_set = set(progress.get("done", [])) if isinstance(progress, dict) else set()
    badges: list[str] = []
    for m in roadmap.get("modules", []):
        steps = m.get("steps", [])
        if steps and all(s["id"] in done_set for s in steps):
            badges.append(m.get("id", ""))
    return [b for b in badges if b]


def _as_utc_date(value: str) -> dt.date | None:
    try:
        parsed = dt.datetime.fromisoformat(str(value))
    except (ValueError, TypeError):
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.UTC)
    return parsed.astimezone(dt.UTC).date()


def streak_days(iso_dates: list[str], today: dt.date | None = None) -> int:
    """Trailing consecutive-day run ending today (or yesterday counts as active).

    Timezone-explicit (UTC); gaps break the run; backfilled old dates never extend it.
    Pure function.
    """
    ref = today or dt.datetime.now(dt.UTC).date()
    days = {d for v in (iso_dates or []) if (d := _as_utc_date(v)) is not None}
    if not days:
        return 0
    cursor = ref
    if cursor not in days:
        cursor = ref - dt.timedelta(days=1)
        if cursor not in days:
            return 0
    run = 0
    while cursor in days:
        run += 1
        cursor -= dt.timedelta(days=1)
    return run
