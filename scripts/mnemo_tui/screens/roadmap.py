from __future__ import annotations

import re
from pathlib import Path

try:
    from textual import work
    from textual.app import ComposeResult
    from textual.containers import Container, Horizontal
    from textual.widgets import Button, Label, ListItem, ListView, Markdown, Static

    try:
        from textual.widgets import ProgressBar  # type: ignore[attr-defined]

        HAS_PROGRESS = True
    except Exception:  # noqa: BLE001
        ProgressBar = None  # type: ignore[assignment,misc]
        HAS_PROGRESS = False
    HAS_TEXTUAL = True
except Exception:  # noqa: BLE001
    HAS_TEXTUAL = False
    HAS_PROGRESS = False
    ComposeResult = object  # type: ignore[assignment]
    Container = object  # type: ignore[assignment]
    Static = object  # type: ignore[assignment]
    ProgressBar = None  # type: ignore[assignment]


if HAS_TEXTUAL:

    class RoadmapScreen(Container):  # type: ignore[valid-type]
        """Roadmap checklist B0..PF — ponytail: ListView + Label, no Tree/DataTable."""

        BINDINGS = [  # noqa: RUF012
            ("d", "mark_done", "Marcar hecho"),
            ("u", "mark_undone", "Desmarcar"),
            ("r", "refresh", "Refrescar"),
            ("q", "back", "Volver"),
            ("escape", "back", "Volver"),
        ]

        def __init__(self, **kwargs):  # type: ignore[no-untyped-def]
            super().__init__(**kwargs)
            # ponytail: naive state, global lock not needed — single thread worker
            self._roadmap: dict | None = None
            self._progress: dict | None = None
            self._stats: dict | None = None
            self._next_pending: dict | None = None
            self._selected_id: str | None = None
            try:
                self.display = False  # type: ignore[attr-defined]  # hidden until App shows
            except Exception:  # noqa: BLE001,S110
                pass

        def compose(self) -> ComposeResult:
            yield Static("Roadmap — Curso paso a paso", id="roadmap-title", classes="panel-title")
            yield Static("Progreso: 0/154 (0%)", id="roadmap-progress")
            if HAS_PROGRESS and ProgressBar is not None:
                try:
                    yield ProgressBar(total=154, id="roadmap-bar", show_eta=False)
                except Exception:  # noqa: BLE001,S110
                    pass
            yield Static("", id="roadmap-next", classes="muted")
            with Horizontal(id="roadmap-main"):
                yield ListView(id="roadmap-list", classes="panel")
                yield Markdown("Selecciona un paso…", id="roadmap-detail", classes="panel")
            with Horizontal(id="roadmap-actions", classes="panel"):
                yield Button("Marcar hecho (d)", id="btn-done", variant="success")
                yield Button("Desmarcar (u)", id="btn-undo")
                yield Button("Refrescar (r)", id="btn-refresh")
                yield Button("Volver (q)", id="btn-back")

        def on_mount(self) -> None:
            # ponytail: lazy refresh — only if visible, App.show_roadmap triggers otherwise
            try:
                if getattr(self, "display", True):
                    self.refresh_roadmap()
            except Exception:  # noqa: BLE001,S110
                pass

        def _resolve_repo(self) -> Path:
            try:
                from mnemo_tui.services.system import resolve_repo_safe

                root = resolve_repo_safe(None, required=False)
                if root is not None and (root / "mnemosyne.toml").exists():
                    return Path(root).resolve()
            except Exception:  # noqa: BLE001,S110
                pass
            # fallback: install location parents[3] mirrors dashboard.py
            fb = Path(__file__).resolve().parents[3]
            if (fb / "mnemosyne.toml").exists():
                return fb
            return Path.cwd().resolve()

        @work(thread=True)
        def refresh_roadmap(self) -> None:
            try:
                from mnemo_tui.services import roadmap as rm
                from mnemo_tui.services.system import resolve_repo_safe  # noqa: F401

                repo = self._resolve_repo()
                roadmap = rm.load_roadmap(repo)
                progress = rm.load_progress(repo)
                stats = rm.get_progress(progress, roadmap)
                nxt = rm.get_next_pending(progress, roadmap)
                self.app.call_from_thread(self._apply_refresh, roadmap, progress, stats, nxt)
            except Exception as exc:  # noqa: BLE001
                try:
                    self.app.call_from_thread(self.app.log_error, f"roadmap refresh failed: {exc}")  # type: ignore[attr-defined]
                except Exception:  # noqa: BLE001,S110
                    pass

        def _apply_refresh(
            self, roadmap: dict, progress: dict, stats: dict, nxt: dict | None
        ) -> None:
            self._roadmap = roadmap
            self._progress = progress
            self._stats = stats
            self._next_pending = nxt
            # header
            try:
                pct = stats.get("pct", 0)
                total = stats.get("total", 0)
                done = stats.get("done", 0)
                txt = f"Progreso: {done}/{total} ({pct}%)"
                if nxt:
                    txt += f"  ·  Siguiente: {nxt['id']}: {nxt['title'][:38]}"
                else:
                    txt += "  ·  ¡Completado!"
                self.query_one("#roadmap-progress", Static).update(txt)
            except Exception:  # noqa: BLE001,S110
                pass
            try:
                if HAS_PROGRESS and ProgressBar is not None:
                    bar = self.query_one("#roadmap-bar", ProgressBar)
                    # textual ProgressBar update signature: update(total=, progress=)
                    try:
                        bar.update(total=stats.get("total", 154), progress=stats.get("done", 0))
                    except Exception:  # noqa: BLE001
                        # fallback older api: progress attr
                        try:
                            bar.total = stats.get("total", 154)  # type: ignore[attr-defined]
                            bar.progress = stats.get("done", 0)  # type: ignore[attr-defined]
                        except Exception:  # noqa: BLE001,S110
                            pass
            except Exception:  # noqa: BLE001,S110
                pass
            try:
                nxt_w = self.query_one("#roadmap-next", Static)
                if nxt:
                    nxt_w.update(f"Siguiente: {nxt['id']}: {nxt['title']}  |  {nxt['section']}  |  {nxt['module']}")
                else:
                    nxt_w.update("¡Roadmap completado! 🎉")
            except Exception:  # noqa: BLE001,S110
                pass
            # list — ponytail: flat ListView, header + steps sequential, O(n) naive
            try:
                lv = self.query_one("#roadmap-list", ListView)
                lv.clear()
                done_set = set(progress.get("done", [])) if isinstance(progress, dict) else set()
                first_pending = nxt["id"] if nxt else None
                for mod in roadmap.get("modules", []):
                    mid = mod.get("id", "")
                    m_done = sum(1 for s in mod.get("steps", []) if s["id"] in done_set)
                    m_total = len(mod.get("steps", []))
                    m_pct = round(m_done / m_total * 100, 1) if m_total else 0
                    header = f"── {mod.get('raw_id', mid.upper())}. {mod.get('title','').split(' ',1)[-1] if ' ' in mod.get('title','') else mod.get('title','')}  {m_done}/{m_total} ({m_pct}%) ──"
                    # header disabled? keep enabled so detail can show module
                    try:
                        lv.append(ListItem(Label(header), id=f"header-{mid}"))
                    except Exception:  # noqa: BLE001
                        lv.append(ListItem(Label(header)))
                    for step in mod.get("steps", []):
                        sid = step.get("id", "")
                        checked = "[x]" if sid in done_set else "[ ]"
                        marker = "▸ " if sid == first_pending else "  "
                        label_txt = f"{marker}{sid} {checked} {step.get('title','')}"
                        # keep id as sid for selection mapping
                        try:
                            lv.append(ListItem(Label(label_txt), id=sid))
                        except Exception:  # noqa: BLE001
                            lv.append(ListItem(Label(label_txt)))
                # detail default: show next pending or first header
                if nxt:
                    self._selected_id = nxt["id"]
                    self._show_detail_for(nxt["id"])
                elif roadmap.get("steps"):
                    first = roadmap["steps"][0]
                    self._selected_id = first["id"]
                    self._show_detail_for(first["id"])
            except Exception as exc:  # noqa: BLE001
                try:
                    self.app.log_error(f"roadmap list update failed: {exc}")  # type: ignore[attr-defined]
                except Exception:  # noqa: BLE001,S110
                    pass

        def _show_detail_for(self, step_id: str) -> None:
            try:
                md = self.query_one("#roadmap-detail", Markdown)
            except Exception:  # noqa: BLE001
                return
            try:
                roadmap = self._roadmap or {}
                progress = self._progress or {}
                done_set = set(progress.get("done", [])) if isinstance(progress, dict) else set()
                # header case
                if step_id.startswith("header-"):
                    mid = step_id.replace("header-", "", 1)
                    mod = next((m for m in roadmap.get("modules", []) if m.get("id") == mid), None)
                    if mod:
                        md.update(
                            f"**{mod.get('title','')}**\n\n"
                            f"- Tipo: {mod.get('type','') or '—'}\n"
                            f"- Pasos: {len(mod.get('steps',[]))}\n"
                            f"- Estado: {m_done_status(mod, done_set)}\n"
                        )
                    return
                steps = roadmap.get("steps", []) if isinstance(roadmap, dict) else []
                step = next((s for s in steps if s.get("id") == step_id), None)
                if not step:
                    md.update(f"**{step_id}**\n\nPaso no encontrado.")
                    return
                status = "✅ Hecho" if step_id in done_set else "⏳ Pendiente"
                mod = next((m for m in roadmap.get("modules", []) if m.get("id") == step.get("module")), None)
                tipo = (mod.get("type") if mod else "") or "—"
                md.update(
                    f"**{step['id']} — {step['title']}**\n\n"
                    f"- Sección: {step.get('section','')}\n"
                    f"- Módulo: {step.get('module','')} ({tipo})\n"
                    f"- Estado: {status}\n"
                )
            except Exception:  # noqa: BLE001,S110
                pass

        def on_list_view_selected(self, event: ListView.Selected) -> None:  # type: ignore[no-untyped-def]
            try:
                item = event.item
                iid = getattr(item, "id", None) or getattr(item, "name", None) or ""
                if not iid:
                    # fallback parse label
                    try:
                        lab = item.query_one(Label)
                        txt = str(getattr(lab, "renderable", "") or lab)
                        m = re.search(r"([a-z0-9]+-\d{3})", txt.lower())
                        if m:
                            iid = m.group(1)
                    except Exception:  # noqa: BLE001,S110
                        pass
                if iid:
                    self._selected_id = iid
                    self._show_detail_for(iid)
                    # also log selection
                    try:
                        self.app.log_general(f"seleccionado {iid}")  # type: ignore[attr-defined]
                    except Exception:  # noqa: BLE001,S110
                        pass
            except Exception:  # noqa: BLE001,S110
                pass

        def on_button_pressed(self, event: Button.Pressed) -> None:  # type: ignore[no-untyped-def]
            label = str(event.button.label).lower()
            bid = (event.button.id or "").lower()
            try:
                if bid == "btn-done" or "marcar hecho" in label:
                    sid = self._get_selected_or_next()
                    if sid and not sid.startswith("header-"):
                        self.do_mark_done(sid)
                    elif sid and sid.startswith("header-"):
                        try:
                            self.app.log_error("Selecciona un paso, no un encabezado")  # type: ignore[attr-defined]
                        except Exception:  # noqa: BLE001,S110
                            pass
                    else:
                        try:
                            self.app.log_error("No hay paso seleccionado")  # type: ignore[attr-defined]
                        except Exception:  # noqa: BLE001,S110
                            pass
                elif bid == "btn-undo" or "desmarcar" in label:
                    sid = self._selected_id
                    if sid and not sid.startswith("header-"):
                        self.do_mark_undone(sid)
                    else:
                        try:
                            self.app.log_error("Selecciona un paso para desmarcar")  # type: ignore[attr-defined]
                        except Exception:  # noqa: BLE001,S110
                            pass
                elif bid == "btn-refresh" or "refrescar" in label:
                    self.refresh_roadmap()
                elif bid == "btn-back" or "volver" in label:
                    try:
                        self.app.action_hide_roadmap()  # type: ignore[attr-defined]
                    except Exception:  # noqa: BLE001
                        try:
                            self.display = False  # type: ignore[attr-defined]
                            self.app.query_one("#dashboard").display = True  # type: ignore[attr-defined]
                        except Exception:  # noqa: BLE001,S110
                            pass
            except Exception:  # noqa: BLE001,S110
                pass

        def _get_selected_or_next(self) -> str | None:
            sid = getattr(self, "_selected_id", None)
            if sid and not sid.startswith("header-"):
                return sid
            nxt = getattr(self, "_next_pending", None)
            if isinstance(nxt, dict) and nxt.get("id"):
                return str(nxt["id"])
            # fallback: first pending from progress
            try:
                if self._roadmap and self._progress:
                    from mnemo_tui.services.roadmap import get_next_pending

                    nxt2 = get_next_pending(self._progress, self._roadmap)
                    if nxt2:
                        return str(nxt2.get("id"))
            except Exception:  # noqa: BLE001,S110
                pass
            return sid

        @work(thread=True)
        def do_mark_done(self, step_id: str) -> None:
            try:
                from mnemo_tui.services import roadmap as rm

                repo = self._resolve_repo()
                rm.mark_done(repo, step_id)
                # ponytail: try CURRENT.md update via mnemo if available
                try:
                    from mnemo_tui.services.system import _get_mnemo

                    mnemo = _get_mnemo()
                    if hasattr(mnemo, "_roadmap_update_current"):
                        roadmap = rm.load_roadmap(repo)
                        prog = rm.load_progress(repo)
                        nxt = rm.get_next_pending(prog, roadmap)
                        step_map = {s["id"]: s for s in roadmap.get("steps", [])}
                        completed = step_map.get(step_id.strip().lower())
                        if completed:
                            mnemo._roadmap_update_current(repo, completed, nxt)  # type: ignore[attr-defined]
                except Exception:  # noqa: BLE001,S110
                    pass
                self.app.call_from_thread(self.app.log_general, f"[OK] marcado {step_id}")  # type: ignore[attr-defined]
                self.app.call_from_thread(self.refresh_roadmap)
            except Exception as exc:  # noqa: BLE001
                try:
                    self.app.call_from_thread(self.app.log_error, f"marcar hecho falló {step_id}: {exc}")  # type: ignore[attr-defined]
                except Exception:  # noqa: BLE001,S110
                    pass

        @work(thread=True)
        def do_mark_undone(self, step_id: str) -> None:
            try:
                from mnemo_tui.services import roadmap as rm

                repo = self._resolve_repo()
                rm.mark_undone(repo, step_id)
                self.app.call_from_thread(self.app.log_general, f"[OK] desmarcado {step_id}")  # type: ignore[attr-defined]
                self.app.call_from_thread(self.refresh_roadmap)
            except Exception as exc:  # noqa: BLE001
                try:
                    self.app.call_from_thread(self.app.log_error, f"desmarcar falló {step_id}: {exc}")  # type: ignore[attr-defined]
                except Exception:  # noqa: BLE001,S110
                    pass

        # textual actions for BINDINGS
        def action_mark_done(self) -> None:
            sid = self._get_selected_or_next()
            if sid and not sid.startswith("header-"):
                self.do_mark_done(sid)
            else:
                try:
                    self.app.log_error("Selecciona un paso")  # type: ignore[attr-defined]
                except Exception:  # noqa: BLE001,S110
                    pass

        def action_mark_undone(self) -> None:
            sid = getattr(self, "_selected_id", None)
            if sid and not sid.startswith("header-"):
                self.do_mark_undone(sid)
            else:
                try:
                    self.app.log_error("Selecciona un paso para desmarcar")  # type: ignore[attr-defined]
                except Exception:  # noqa: BLE001,S110
                    pass

        def action_refresh(self) -> None:
            self.refresh_roadmap()

        def action_back(self) -> None:
            try:
                self.app.action_hide_roadmap()  # type: ignore[attr-defined]
            except Exception:  # noqa: BLE001
                try:
                    self.display = False  # type: ignore[attr-defined]
                    self.app.query_one("#dashboard").display = True  # type: ignore[attr-defined]
                except Exception:  # noqa: BLE001,S110
                    pass


    def m_done_status(mod: dict, done_set: set[str]) -> str:
        m_total = len(mod.get("steps", []))
        if m_total == 0:
            return "vacío"
        m_done = sum(1 for s in mod.get("steps", []) if s["id"] in done_set)
        if m_done == 0:
            return "pendiente"
        if m_done == m_total:
            return "completado"
        return "en_progreso"

else:

    class RoadmapScreen:  # type: ignore[no-redef]
        pass

    def m_done_status(mod: dict, done_set: set[str]) -> str:  # type: ignore[no-redef]
        return "pendiente"
