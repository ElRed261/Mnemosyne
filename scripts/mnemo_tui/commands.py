"""Command palette provider — ponytail: 5 commands, fuzzy stdlib match, no new deps."""

from __future__ import annotations

try:
    from textual.command import Hit, Hits, Provider

    HAS_COMMAND = True
except Exception:  # noqa: BLE001
    HAS_COMMAND = False
    Hit = object  # type: ignore[assignment,misc]
    Hits = object  # type: ignore[assignment,misc]
    Provider = object  # type: ignore[assignment,misc]


_COMMANDS: tuple[tuple[str, str, str], ...] = (
    ("doctor", "Run diagnostics", "Diagnose tools, git and environment"),
    ("start", "Start session", "Sync repo and show continuity point"),
    ("current", "Show current", "Display CURRENT.md point of continuation"),
    ("sync", "Sync repo", "Fast-forward pull/push a clean tree"),
    ("roadmap", "Open roadmap", "Show curriculum checklist"),
)


def _score(query: str, name: str) -> float:
    # ponytail: subsequence fuzzy score, O(n*m) trivial for 5 items
    q, n = query.lower().strip(), name.lower()
    if not q:
        return 1.0
    if q == n:
        return 1.0
    if n.startswith(q):
        return 0.9
    if q in n:
        return 0.7
    it = iter(n)
    if all(c in it for c in q):
        return 0.5
    return 0.0


if HAS_COMMAND:

    class MnemoProvider(Provider):  # type: ignore[valid-type]
        """Palette commands for daily work (Ctrl+P)."""

        async def discover(self) -> Hits:
            for name, title, help_text in _COMMANDS:
                yield Hit(1.0, f"{name} — {title}", self._run(name), help=help_text)

        async def search(self, query: str) -> Hits:
            for name, title, help_text in _COMMANDS:
                score = _score(query, f"{name} {title}")
                if score > 0:
                    yield Hit(score, f"{name} — {title}", self._run(name), help=help_text)

        def _run(self, name: str):  # type: ignore[no-untyped-def]
            def _cmd() -> None:
                app = self.app
                if name == "roadmap":
                    try:
                        app.action_show_roadmap()  # type: ignore[attr-defined]
                    except Exception:  # noqa: BLE001,S110
                        pass
                    return
                try:
                    runner = getattr(app, "run_mnemo_action", None)
                    if callable(runner):
                        runner(name)
                    else:
                        dash = app.query_one("#dashboard")
                        dash.run_action(name)  # type: ignore[attr-defined]
                except Exception:  # noqa: BLE001,S110
                    pass

            return _cmd

else:

    class MnemoProvider:  # type: ignore[no-redef]
        pass
