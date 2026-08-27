# Tasks: mnemo-tui-polish

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated lines | 480–550 |
| Real lines | 496 prod + 412 tests = 908 (budget 1200) |
| 400-line risk | High → exception-ok |
| Chained PRs | Yes (forecast) → overridden to single PR |
| Split | PR1 Phase1 → PR2 Phase2 → PR3 Phase3+4 (forecast) |
| Delivery | exception-ok (single PR approved for this run) |
| Chain | not applicable (single PR) |

Decision needed before apply: No (exception-ok approved)
Chained PRs recommended: Yes (forecast) → not applied, single PR with exception
Chain strategy: not applicable (single PR)
400-line budget risk: High → accepted as size:exception (908 < 1200)

### Suggested Work Units

| Unit | Goal | PR | Test command | Harness | Rollback |
|------|------|----|--------------|---------|----------|
| 1 | Logs+Theme | PR1 | `pytest -k timestamp` | `run_test(100,40) <1s` | `app.py,log_panel.py,banner.py,theme.tcss` |
| 2 | Panels | PR2→PR1 | `pytest -k collect` | `refresh_panels <6s` | `dashboard.py,services/*` |
| 3 | Actions+Tests | PR3→PR2 | `ruff check . && pytest -q` | `press doctor→General` | `dashboard.py,tests/*` |

## Phase 1: Logs vivos + Theme — ✅ DONE

| ID | Task | file | dep | size | RED → GREEN | Done |
|----|------|------|-----|------|-------------|------|
| 1.1 | [x] LogPanel `[HH:MM:SS]` `RichLog` | `widgets/log_panel.py` | — | S | RED `test_timestamp` fails → GREEN regex | ✅ |
| 1.2 | [x] Banner `Online Updates:N`/`Offline` | `widgets/banner.py` | 1.1 | S | RED `banner_text` fails → GREEN pass | ✅ |
| 1.3 | [x] Theme `mnemosyne-dark` + `theme.tcss` tokens | `app.py`,`theme.tcss` | 1.2 | M | RED `theme` fails → GREEN 80×24 | ✅ |
| 1.4 | [x] `on_mount` ready log + `check_online@work` | `app.py` | 1.3 | M | RED `ready <1s` fails → GREEN `run_test` | ✅ |

## Phase 2: Panels reales — ✅ DONE

| ID | Task | file | dep | size | RED → GREEN | Done |
|----|------|------|-----|------|-------------|------|
| 2.1 | [x] RED injection `REPO_RE`/`HOST_RE` | `tests/test_mnemo_tui_security.py` | — | S | RED no raise → GREEN `ValueError` | ✅ |
| 2.2 | [x] RED traversal `..` `/tmp` | `tests/test_mnemo_tui_security.py` | 2.1 | S | RED no raise → GREEN raise | ✅ |
| 2.3 | [x] RED ssh `host; echo pwn` | `tests/test_mnemo_tui_security.py` | 2.1 | S | RED no raise → GREEN `ValueError` | ✅ |
| 2.4 | [x] `collect_system`+`collect_tools`/`banner_info` 5s | `services/system.py` | 2.2 | S | GREEN `collect` OK/FALTA | ✅ |
| 2.5 | [x] `gh`/`tailscale`/`ssh` `ConnectTimeout=5` list-form | `services/github.py`,`tailscale.py`,`ssh.py` | 2.4 | M | GREEN `✅/❌ <6s` | ✅ |
| 2.6 | [x] `refresh_panels@work` skeletons offline degrade | `screens/dashboard.py` | 2.5 | M | GREEN `pilot` real data | ✅ |

## Phase 3: Actions ejecutan — ✅ DONE

| ID | Task | file | dep | size | RED → GREEN | Done |
|----|------|------|-----|------|-------------|------|
| 3.1 | [x] `on_button_pressed@work` list-form 10s `call_from_thread` | `screens/dashboard.py` | 2.6 | M | RED blocking fails → GREEN responsive | ✅ |
| 3.2 | [x] Dual route stdout→General stderr→Errors `HH:MM:SS` | `screens/dashboard.py`,`app.py` | 3.1 | S | GREEN `doctor→General` `fail→Errors` | ✅ |

## Phase 4: Tests + polish — ✅ DONE

| ID | Task | file | dep | size | RED → GREEN | Done |
|----|------|------|-----|------|-------------|------|
| 4.1 | [x] Unit `collect_*` `git dirty` mocked | `tests/test_mnemo_tui_system.py` | 1.4,2.5 | S | GREEN `pytest -k unit` | ✅ |
| 4.2 | [x] Integration `git init` dirty + `tui.json` | `tests/test_mnemo_tui_integration.py` | 4.1 | S | GREEN `tmp_path` | ✅ |
| 4.3 | [x] Pilot e2e `run_test(100,40)` + `ruff` | `tests/test_mnemo_tui_pilot.py` | 3.2 | M | GREEN `pilot.press tab` + `ruff check .` | ✅ |

All 15 tasks complete. Single PR 496+412=908 lines, ruff+pytest green.
