# Archive Report: mnemo-tui-polish — Functional Logs & Dashboard Polish

**Change**: mnemo-tui-polish
**Date**: 2026-08-27
**Execution Mode**: interactive
**Artifact Store**: hybrid (engram + openspec)
**Delivery Strategy**: ask-on-risk → exception-ok (single PR, budget 1200, real 496 prod + 412 tests = 908 lines)
**Status**: archived
**Verdict (final-state authority)**: PASS — 0 blockers, 0 criticals, 8/8 requirements, 14/14 scenarios

## Executive Summary
`mnemo-tui-polish` closed 2 WARNINGs from `mnemo-tui` (empty logs, empty panels): `on_mount` now logs `Mnemosyne ready — <device> (<os>/x64) — textual 8.2.8 — online bool` <1s to General with `[HH:MM:SS]`, `LogPanel(RichLog)` dual-routing stdout→General stderr→Errors/Audit, panels System/Tools/Git/Uranus render real data via `@work(thread=True)` workers <6s with skeletons, actions `doctor/start/sync/bootstrap/device` execute list-form `["uv","run","python","scripts/mnemo.py",cmd]` 10s non-blocking via `call_from_thread`, Theme `mnemosyne-dark` #7c5cff/#0e0e10/#1a1a1e/#2ecc71/#ff4d4d registered. All 15 tasks DONE, 91 tests PASS, `uv run ruff check .` clean, source of truth merged into `openspec/specs/mnemo-tui-*/spec.md`, change archived to `openspec/changes/archive/2026-08-27-mnemo-tui-polish/` with byte-identical readback, hybrid Engram+filesystem persistence.

## Final-State Authority
This report reflects AT CLOSE, not snapshot time, per archive Final-State Authority hierarchy:

1. **Native review authority** — `reviewGate` ABSENT (no review discovered for this candidate). Kill switch off OR post-verify offer declined → ordinary repository policy, proceeds. No `disabled/unmanaged` value to check. `dependencies.archive: ready` means proceed.
2. **Persisted tasks artifact** — `openspec/changes/archive/2026-08-27-mnemo-tui-polish/tasks.md` shows 15 `[x]` checked, 0 unchecked `[ ]` → Task Completion Gate PASS. Table-format parser reports 0/0 but manual count 15/15; Engram `sdd/mnemo-tui-polish/apply-progress` #167 confirms 15/15. No stale checkboxes.
3. **Explicit final-state facts in orchestrator launch prompt** — repo `https://github.com/ElRed261/Mnemosyne` `main` with fix `53213ab` already pushed, polish implemented 15/15, 91 tests, `ruff` clean, verify PASS 8/8 14/14, `apply-progress` and `verify-report` in `hybrid` vigente non-blocking, models `muse-spark-1.2-contributor-free` via Opencode GO, strict_tdd true, preflight interactive/both/ask-on-risk exception-ok 1200. All corroborated by repository evidence below.
4. **Intermediate snapshots** — `apply-progress` #167 (15/15 Ready) and `verify-report` #168 (PASS 8/8 14/14 91 tests ruff clean, 6/6 Strict TDD checks) are consistent with above; no stale claims contradicted. No CRITICAL to re-verify; `blockers:0 critical_findings:0` gates pass.

No contradictions requiring dual-record. `verify-report` WARNINGs from prior `mnemo-tui` already closed (this polish); current `verify-report` reports 0 WARNINGs.

## Engram Traceability — Observation IDs Actually Read

| Artifact | Engram Topic | Obs ID | Sync ID | Project | Timestamp |
|----------|--------------|--------|---------|---------|-----------|
| proposal | `sdd/mnemo-tui-polish/proposal` | #163 | obs-* | mnemosyne-starter | 2026-08-27 13:46:09 |
| spec | `sdd/mnemo-tui-polish/spec` | #164 | obs-* | mnemosyne-starter | 2026-08-27 13:52:32 |
| design | `sdd/mnemo-tui-polish/design` | #165 | obs-* | mnemosyne-starter | 2026-08-27 13:57:19 |
| tasks | `sdd/mnemo-tui-polish/tasks` | #166 | obs-* | mnemosyne-starter | 2026-08-27 14:38:02 |
| apply-progress | `sdd/mnemo-tui-polish/apply-progress` | #167 | obs-ee32a2b5ddcee704 | mnemosyne-starter | 2026-08-27 15:03:54 |
| verify-report | `sdd/mnemo-tui-polish/verify-report` | #168 | obs-* | mnemosyne-starter | 2026-08-27 15:09:58 |
| archive-report | `sdd/mnemo-tui-polish/archive-report` | (this) | — | mnemosyne-starter | 2026-08-27 |

All IDs retrieved via `engram search` + export JSON before archive; full contents verified.

## Specs Synced — Delta → Source of Truth

**Mode**: `hybrid` → filesystem merge (main specs existed) + Engram report. No `cp` mechanical copy for deltas that are patches; merge applied, preserved other domains, verified no destructive loss outside declared MODIFIED/ADDED.

| Domain | Action | Source Delta | Destination (source of truth) | Requirements | Details |
|--------|--------|--------------|-------------------------------|--------------|---------|
| mnemo-tui-shell | Updated | `openspec/changes/archive/2026-08-27-mnemo-tui-polish/specs/mnemo-tui-shell/spec.md` (MODIFIED Entrypoint, ADDED LogsFunctional + ThemePolish) | `openspec/specs/mnemo-tui-shell/spec.md` | 1 MODIFIED (Entrypoint and Textual Guard — guard retained, updated scenario), 2 ADDED (LogsFunctional 2 scenarios, ThemePolish 1 scenario) → 3 req, 4 scenarios | Replaced old `Theme, Nav, Logs` vague requirement with two explicit polished reqs; kept Purpose dark-only; UI copy General/Errors preserved |
| mnemo-tui-onboarding | Updated | `.../specs/mnemo-tui-onboarding/spec.md` (3 MODIFIED) | `openspec/specs/mnemo-tui-onboarding/spec.md` | 3 MODIFIED (GitHub Auth and Gate, Repo Create/Link, Uranus and Picker) → 3 req, 6 scenarios | Each req replaced with HH:MM:SS logging + REPO_RE/HOST_RE guards; scenarios now log-aware (Auth success logs, Blocked invalid logs, Create valid logs, Empty rejected, Picker logs, Offline degrade) |
| mnemo-tui-dashboard | Updated | `.../specs/mnemo-tui-dashboard/spec.md` (2 MODIFIED renamed) | `openspec/specs/mnemo-tui-dashboard/spec.md` | 2 MODIFIED renamed (Layout and Panels → PanelsReal, Uranus/Actions/Banner → ActionsExecute) → 2 req, 4 scenarios | Replaced vague Layout/Panels + Uranus/Actions/Banner with PanelsReal (System/Tools/Git/Uranus real data + skeletons <6s) + ActionsExecute (list-form @work 10s dual routing); UI copy System/Tools/Git/Uranus |

**Total**: 8 requirements, 14 scenarios now source of truth (was 7/16 before polish). Merge preserved Markdown heading hierarchy, no other domains affected.

**Merge verification**: After merge, each destination contains delta requirements verbatim plus Purpose; diff against delta is non-empty by design (delta is `# Delta for…` header, destination is `# mnemo-tui-* Specification` with Purpose) — not a mechanical `cp` case. Correctness verified by content inspection: `grep -c "PanelsReal\|ActionsExecute\|LogsFunctional\|ThemePolish"` on destinations returns expected counts.

## Archive Contents
Mechanical move via `mv` (fallback after `git mv` failed — source untracked, expected) with byte-identity readback `diff -r snapshot vs archive` EMPTY.

| Artifact | Archived Path | Status |
|----------|---------------|--------|
| proposal.md | `openspec/changes/archive/2026-08-27-mnemo-tui-polish/proposal.md` | ✅ |
| specs/mnemo-tui-shell/spec.md | `.../specs/mnemo-tui-shell/spec.md` | ✅ |
| specs/mnemo-tui-onboarding/spec.md | `.../specs/mnemo-tui-onboarding/spec.md` | ✅ |
| specs/mnemo-tui-dashboard/spec.md | `.../specs/mnemo-tui-dashboard/spec.md` | ✅ |
| design.md | `.../design.md` | ✅ |
| tasks.md | `.../tasks.md` (15/15 complete) | ✅ |
| verify-report.md | `.../verify-report.md` (PASS 8/8 14/14) | ✅ |
| archive-report.md | `.../archive-report.md` (additive, excluded from diff — this file) | ✅ (this file) |

Active change directory `openspec/changes/mnemo-tui-polish/` no longer exists (source gone verified). `apply-progress.md` lives only in Engram hybrid (not filesystem) per execution — archived Engram observation #167 covers it; no filesystem duplication needed.

## Verification — Archive Mechanical Copy Contract

### Spec sync readback (Step 2)
Not a pure `cp` case — deltas are patches (`## MODIFIED/ADDED`) merged into existing specs (which had Purpose + prior requirements). No `diff -r src vs target` empty expected; merge validated by requirement presence checks:

```text
$ grep -n "Requirement:" openspec/specs/mnemo-tui-shell/spec.md
→ Entrypoint and Textual Guard, LogsFunctional, ThemePolish (3 req)
$ grep -n "Requirement:" openspec/specs/mnemo-tui-onboarding/spec.md
→ GitHub Auth and Gate, Repo Create/Link, Uranus and Picker (3 req)
$ grep -n "Requirement:" openspec/specs/mnemo-tui-dashboard/spec.md
→ PanelsReal, ActionsExecute (2 req)
Total 8 requirements, 14 scenarios — matches verify-report 8/8 14/14
```

Shell access was available; no Read→Write truncation for archive move (merge used model Write but verified via grep).

### Archive move readback (Step 3) — MANDATORY
```
snapshot_root: /tmp/sdd-archive.jnXErK
snapshot created: /tmp/sdd-archive.jnXErK/source
/tmp/sdd-archive.jnXErK/source:
design.md
proposal.md
specs
tasks.md
verify-report.md

/tmp/sdd-archive.jnXErK/source/specs:
mnemo-tui-dashboard
mnemo-tui-onboarding
mnemo-tui-shell

--- attempting mechanical move ---
fatal: directorio de fuente está vacío, fuente=openspec/changes/mnemo-tui-polish, destino=openspec/changes/archive/2026-08-27-mnemo-tui-polish
git mv failed, trying mv
mv succeeded
--- verify source gone ---
source gone: PASS
--- diff snapshot vs archive (MANDATORY readback, empty = pass) ---
diff exit: 0
diff EMPTY - PASS (byte-identical)
snapshot_root removed via EXIT trap after readback
archive-report.md excluded as additive-only per contract
```
Only passing evidence is empty diff; any difference would have failed phase. `git mv` failed because change folder was untracked (`??` per `git status`) — fallback `mv` is correct per skill. Snapshot comparison done against pre-move recursive `cp -R` snapshot, not staged tree.

### Additional checks
- [x] Main specs updated correctly (3 domains merged, 8 req 14 scenarios)
- [x] Change folder moved to archive
- [x] Archive contains all artifacts (proposal, specs×3, design, tasks, verify-report, archive-report)
- [x] Archived `tasks.md` has no unchecked tasks (15/15, 0 ` - [ ]`)
- [x] Active changes directory no longer has this change
- [x] Verbatim `diff -r` readback included and empty

## Tasks — Final State
15/15 complete, no reconciliation needed.

| Phase | Tasks | Complete |
|-------|-------|----------|
| Phase 1: Logs vivos + Theme | 1.1–1.4 | 4/4 ✅ |
| Phase 2: Panels reales | 2.1–2.6 | 6/6 ✅ |
| Phase 3: Actions ejecutan | 3.1–3.2 | 2/2 ✅ |
| Phase 4: Tests + polish | 4.1–4.3 | 3/3 ✅ |
| **Total** | | **15/15** |

All task IDs checked `[x]` in archived `tasks.md`; no ` - [ ]` remains.

## Build & Tests — Final Evidence

**Build**: ✅ `uv run ruff check .` → `All checks passed!` (re-run 2026-08-27 post-merge confirms clean)
**Tests**: ✅ `uv run pytest -q` → `91 passed, 10 subtests passed in 9.83s` (re-run 2026-08-27 post-merge; original verify-report hash `sha256:48406d1f…` matches)
**Coverage**: ➖ Not available (openspec/config.yaml `testing.coverage.available: false`, threshold 0 — not a failure)
**TDD**: Strict TDD 6/6 checks passed (see verify-report #168)
**Specs**: 8/8 requirements, 14/14 scenarios COMPLIANT

## Risks & Next
- **Risks**: None — no CRITICAL, no WARNINGs to carry, offline degrade <6s verified, REPO_RE/HOST_RE injection blocked, PAT stdin, 5–10s timeouts.
- **Next**: SDD cycle complete for `mnemo-tui-polish`. Remaining polish debt (design open questions) is intentional ponytail debt: Lazy-import `Markdown` for <1s cold start on Uranus ARM64, hide `Updates: N` when not Arch — tracked in `design.md` Open Questions, not blocking. Ready for next change.

## Source of Truth Updated
The following specs now reflect the new behavior:
- `openspec/specs/mnemo-tui-shell/spec.md` (3 req, 4 scenarios)
- `openspec/specs/mnemo-tui-onboarding/spec.md` (3 req, 6 scenarios)
- `openspec/specs/mnemo-tui-dashboard/spec.md` (2 req, 4 scenarios)

## SDD Cycle Complete
The change has been fully planned, implemented, verified, and archived via hybrid persistence. Engram observations #163–#168 preserved, filesystem specs merged, change folder byte-identically archived to `openspec/changes/archive/2026-08-27-mnemo-tui-polish/`.

## Key Learnings

1. Delta MODIFIED Requirements with renamed titles still require explicit replacement mapping to avoid duplicating vague legacy requirements in the source of truth.
2. Hybrid archive with untracked change folder correctly falls back from git mv to mv while preserving byte-identity verified by pre-move snapshot diff.
3. Strict TDD verify PASS with 91 tests remains valid after spec merge because ruff and pytest re-run empty confirms no post-verify drift.
