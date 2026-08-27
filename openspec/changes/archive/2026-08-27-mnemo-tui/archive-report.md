# Archive Report: mnemo-tui — Dark-only TUI

**Change**: mnemo-tui
**Date**: 2026-08-27
**Execution Mode**: interactive
**Artifact Store**: hybrid (engram + openspec)
**Delivery Strategy**: ask-on-risk → exception-ok (single PR, budget 1200, real ~980 lines, 50 files, 4377 insertions at c2cd728)
**Status**: archived
**Verdict (final-state authority)**: PASS WITH WARNINGS — no criticals, 22/22 tasks, ruff clean, 74 tests, 7/7 requirements, 16/16 scenarios

## Executive Summary
`mnemo-tui` shipped a dark-only Textual TUI (TTY no-args → TUI, else CLI pure) with guarded `textual` import, GitHub auth gate + repo create/link, Uranus SSH/Tailscale picker (ConnectTimeout 5, paths-only persistence), and a 5-panel dashboard with dual logs and Online/Offline banner. All 22 tasks complete, verification PASS WITH WARNINGS (2 ponytail-deliberate deviations), main specs created (3 domains), and change archived to `openspec/changes/archive/2026-08-27-mnemo-tui/` with hybrid Engram+filesystem persistence.

## Final-State Authority
This report reflects AT CLOSE, not snapshot time, per archive Final-State Authority hierarchy:

1. **Native review authority** — `reviewGate` ABSENT (no review discovered for this candidate). Kill switch off OR post-verify offer declined → ordinary repository policy, proceeds. No `disabled/unmanaged` value to check. `dependencies.archive: ready` means proceed.
2. **Persisted tasks artifact** — 22/22 `[x]` in `tasks.md`, 0 unchecked → Task Completion Gate PASS.
3. **Explicit final-state facts in orchestrator launch prompt** — repo `ElRed261/Mnemosyne` commit `c2cd728` pushed on `main` (50 files, 4377 ins), `origin/main` tracking, `apply` ~980 under 1200 exception-ok, verify `PASS WITH WARNINGS`, warnings are ponytail-deliberate (dashboard `on_button_pressed` log-only fallback `CLI --no-tui`, banner `Online/Offline` simplified vs `banner_info` detail), `.mnemosyne/tui.json` paths-only gitignored, models `opencode-go/muse-spark-1.2-contributor-free`.
4. **Intermediate snapshots** — `apply-progress` (22/22 Ready for verify) and `verify-report` (PASS WITH WARNINGS 74 tests, ruff clean) are consistent with above; no stale claims contradicted. Any delta (verify timing 0.97s→1.02s, hash `270da6f`→`07d2b90`) is test-runtime variance, not a blocker.

No contradictions requiring explicit dual-record. No CRITICAL findings to re-verify.

## Specs Synced

| Domain | Action | Source | Destination | Requirements | Verbatim diff |
|--------|--------|--------|-------------|--------------|---------------|
| mnemo-tui-shell | Created | `openspec/changes/mnemo-tui/specs/mnemo-tui-shell/spec.md` | `openspec/specs/mnemo-tui-shell/spec.md` | 2 req (Entrypoint/Guard, Theme/Nav/Logs), 5 scenarios | `diff -r src temp` empty, `diff -r src target` empty |
| mnemo-tui-onboarding | Created | `openspec/changes/mnemo-tui/specs/mnemo-tui-onboarding/spec.md` | `openspec/specs/mnemo-tui-onboarding/spec.md` | 3 req (GitHub Auth Gate, Repo Create/Link, Uranus/Picker), 7 scenarios | `diff -r src temp` empty, `diff -r src target` empty |
| mnemo-tui-dashboard | Created | `openspec/changes/mnemo-tui/specs/mnemo-tui-dashboard/spec.md` | `openspec/specs/mnemo-tui-dashboard/spec.md` | 2 req (Layout/Panels, Uranus/Actions/Banner), 4 scenarios | `diff -r src temp` empty, `diff -r src target` empty |

**Merge logic**: `openspec/specs/` was empty (only `.gitkeep`, 0 B). No existing main spec to merge; delta specs treated as full specs and copied mechanically via `cp`→`diff -r`→`mv` (Mechanical Copy Contract). `.gitkeep` preserved. No other domains affected.

Total: 7 requirements, 16 scenarios now source of truth in `openspec/specs/{domain}/spec.md`.

## Archive Contents
Staged via `git mv` (tracked) with byte-identity readback `diff -r snapshot vs archive` empty.

| Artifact | Archived Path | Status |
|----------|---------------|--------|
| proposal.md | `openspec/changes/archive/2026-08-27-mnemo-tui/proposal.md` | ✅ |
| specs/mnemo-tui-shell/spec.md | `.../specs/mnemo-tui-shell/spec.md` | ✅ |
| specs/mnemo-tui-onboarding/spec.md | `.../specs/mnemo-tui-onboarding/spec.md` | ✅ |
| specs/mnemo-tui-dashboard/spec.md | `.../specs/mnemo-tui-dashboard/spec.md` | ✅ |
| design.md | `.../design.md` | ✅ |
| tasks.md | `.../tasks.md` (22/22 complete) | ✅ |
| apply-progress.md | `.../apply-progress.md` | ✅ |
| verify-report.md | `.../verify-report.md` (PASS WITH WARNINGS) | ✅ |
| archive-report.md | `.../archive-report.md` (additive, excluded from diff) | ✅ (this file) |

Active change directory `openspec/changes/mnemo-tui/` no longer exists (source gone verified).

## Verification — Archive Mechanical Copy Contract

### Spec sync readback (Step 2)
```
--- Processing mnemo-tui-shell ---
cp done, diff src vs temp:
diff src->temp: EMPTY (pass)
mv to openspec/specs/mnemo-tui-shell/spec.md done
verify target exists and diff src vs target:
diff src->target: EMPTY (pass)

--- Processing mnemo-tui-onboarding ---
diff src->temp: EMPTY (pass)
diff src->target: EMPTY (pass)

--- Processing mnemo-tui-dashboard ---
diff src->temp: EMPTY (pass)
diff src->target: EMPTY (pass)
```
Only passing evidence is empty diff; any difference would have failed phase. Shell access was available; no Read→Write fallback used.

### Archive move readback (Step 3)
```
snapshot_root: /tmp/sdd-archive.QxMrBe
snapshot created: /tmp/sdd-archive.QxMrBe/source
--- attempting mechanical move ---
git mv succeeded
--- verify source gone ---
source gone: PASS
--- diff snapshot vs archive (MANDATORY readback, empty = pass) ---
diff exit: 0
diff EMPTY - PASS (byte-identical)
```
`snapshot_root` removed via EXIT trap after readback. `archive-report.md` excluded as additive-only per contract.

### Additional checks
- [x] Main specs updated correctly (3 domains created)
- [x] Change folder moved to archive
- [x] Archive contains all artifacts (proposal, specs, design, tasks, apply-progress, verify-report, archive-report)
- [x] Archived `tasks.md` has no unchecked tasks (22/22, 0 ` - [ ]`)
- [x] Active changes directory no longer has this change
- [x] Verbatim `diff -r` readback included and empty

## Tasks — Final State
22/22 complete, no reconciliation needed.

| Phase | Tasks | Complete |
|-------|-------|----------|
| 1 Shell/Guard+Deps | 1.1–1.8 | 8/8 ✅ |
| 2 Onboarding GitHub | 2.1–2.3 | 3/3 ✅ |
| 3 Uranus/SSH | 3.1–3.3 | 3/3 ✅ |
| 4 Dashboard | 4.1–4.4 | 4/4 ✅ |
| 5 Tests+Polish | 5.1–5.4 | 4/4 ✅ |

Persisted `tasks.md` is source of truth; no stale unchecked boxes. `sdd-apply` owned completion; `sdd-archive` validated.

## Verify — Final Numbers (highest-ranked source)

| Metric | Value | Source |
|--------|-------|--------|
| Tasks | 22/22 | tasks.md + verify-report Completeness |
| Requirements | 7/7 | verify-report Spec Compliance Matrix |
| Scenarios | 16/16 (14 fully compliant, 2 partial—see warnings) | verify-report |
| Build | `uv run ruff check .` → All checks passed! exit 0 `sha256:82b3e6a6...` | verify-report build_output_hash |
| Tests | `uv run pytest -q` → 74 passed, 10 subtests in 1.02s exit 0 `sha256:07d2b90b...` | verify-report test_output_hash (final-state: 0.97s→1.02s variance is runtime, not failure) |
| Focused harnesses | launch 7, inject/git_c 11, picker 9, pilot 7, github 14 | verify-report |
| Linter | ruff clean | verify-report Quality Metrics |
| Type checker | not available (config) | — |
| Coverage | not available (config threshold 0) | — |
| Critical findings | 0 | verify-report Issues |
| Blockers | 0 | verify-report |

Warnings carried as final (non-blocking, ponytail deliberate with upgrade path):
- **Dashboard Actions log-only**: `screens/dashboard.py:on_button_pressed` logs `> label` to General, does not spawn `run([...])` worker. Impact: `--no-tui` fallback. Add when worker latency justifies.
- **Banner simplified**: `widgets/banner.py` `Online/Offline` only; `services/system.py:banner_info` computes full `internet/gh/updates` but not rendered. Add when `pacman -Qu` interval confirmed.
- Non-bugs: `.mnemosyne/tui.json` absent pre-onboarding (expected), no git repo in starter (graceful degrade).

No CRITICAL issues → archive not blocked.

## Git State — Final
- Remote: `https://github.com/ElRed261/Mnemosyne.git` tracking `main`
- Prior commit: `c2cd728 feat: initial Mnemosyne with dark TUI (mnemo-tui)` pushed, 50 files, 4377 ins, README + SDD trail in commit message
- After archive (staged, not yet committed at close):
  ```
  R  openspec/changes/mnemo-tui/* → openspec/changes/archive/2026-08-27-mnemo-tui/*
  RM openspec/changes/mnemo-tui/verify-report.md → .../verify-report.md (hash/timing update)
  ?? openspec/specs/mnemo-tui-dashboard/spec.md
  ?? openspec/specs/mnemo-tui-onboarding/spec.md
  ?? openspec/specs/mnemo-tui-shell/spec.md
  ?? openspec/changes/archive/2026-08-27-mnemo-tui/archive-report.md (additive)
  ```
  Next commit should include: main specs created (3), archive move (git mv renames), and `archive-report.md`. No data/secrets versioned (`.mnemosyne/tui.json` gitignored, paths-only).

## Deviations from Design (final)
All ponytail deliberate, documented in `apply-progress.md Deviations` and `verify-report Coherence`:
- Single `check_online` 15s poll vs per-panel workers → add if latency shows
- `gh auth login --with-token` stdin + hint vs PTY
- `pacman -Qu` fixed interval vs configurable
- `tui.json` 3 keys filtered via `atomic_write`
- Dashboard actions minimal (see warnings)

## Risks
- **None blocking**. Two warnings above are intentional deferrals; hybrid store shows only `verify-report` had Engram observation before archive (others filesystem-primary) — no data loss, but future hybrid runs should persist proposal/spec/design/tasks to Engram for full traceability. Marked `risks: intentional-with-warnings` only.

## Source of Truth Updated
The following specs now reflect shipped behavior:
- `openspec/specs/mnemo-tui-shell/spec.md`
- `openspec/specs/mnemo-tui-onboarding/spec.md`
- `openspec/specs/mnemo-tui-dashboard/spec.md`

## SDD Cycle Complete
Change `mnemo-tui` planned → implemented (22/22, strict TDD 74 tests) → verified (PASS WITH WARNINGS, ruff clean, no criticals) → archived (specs synced mechanically, byte-identity diff, hybrid persisted). Ready for next change.

## Traceability
- **Filesystem artifacts read**: `openspec/changes/mnemo-tui/proposal.md`, `openspec/changes/mnemo-tui/specs/mnemo-tui-shell/spec.md`, `openspec/changes/mnemo-tui/specs/mnemo-tui-onboarding/spec.md`, `openspec/changes/mnemo-tui/specs/mnemo-tui-dashboard/spec.md`, `openspec/changes/mnemo-tui/design.md`, `openspec/changes/mnemo-tui/tasks.md`, `openspec/changes/mnemo-tui/apply-progress.md`, `openspec/changes/mnemo-tui/verify-report.md` (all required, verified present before archive; `apply-progress` 10.8K, `verify-report` 15.9K)
- **Engram observations read**: `sdd/mnemo-tui/verify-report` #161 `obs-1e99dd7a1c19cd30` (full content retrieved via `mem_get_observation` 2026-08-27); `sdd/mnemo-tui/proposal`, `sdd/mnemo-tui/spec`, `sdd/mnemo-tui/design`, `sdd/mnemo-tui/tasks`, `sdd/mnemo-tui/apply-progress` not found in Engram at archive time (filesystem-primary) — no observation IDs to record.
- **Review artifacts**: `reviewGate` absent → per Native Review Receipt Gate, no `sdd/{change}/review/{transaction,ledger,receipt,gate-context}` topics read (none exist).
- **Archive report persisted**: Engram `sdd/mnemo-tui/archive-report` (this report, topic_key `sdd/mnemo-tui/archive-report`, type `architecture`, capture_prompt false) + filesystem `openspec/changes/archive/2026-08-27-mnemo-tui/archive-report.md`
- **Mechanical evidence**: spec-sync `diff -r` empty ×3, archive-move `diff -r snapshot vs archive` empty, included verbatim above.

