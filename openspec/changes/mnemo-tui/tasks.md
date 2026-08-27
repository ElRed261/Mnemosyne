# Tasks: mnemo-tui — Dark-only TUI

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 850–1050 |
| Real changed lines | ~920 (single PR) |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | PR1→PR2→PR3→PR4→PR5 |
| Delivery strategy | ask-on-risk → **exception-ok (single PR, size:exception approved, budget 1200)** |
| Chain strategy | no aplica (single PR exception-ok) |

Decision needed before apply: Resolved — user approved single PR exception-ok (1200 budget) for this run.
Chained PRs recommended: Yes → waived for this batch, kept autonomous work-unit commits
Chain strategy: single PR (no chain)
400-line budget risk: High → accepted as exception

### Suggested Work Units

| Unit | Goal | PR | Test | Harness | Rollback |
|------|------|----|------|---------|----------|
| 1 | Shell | PR1 | `pytest -k launch` | TTY | `pyproject+mnemo` |
| 2 | GitHub | PR2 | `pytest -k github` | gh gate | `github+onboarding` |
| 3 | Uranus | PR3 | `pytest -k ssh` | picker ssh<6s | `ssh+picker+tui.json` |
| 4 | Dashboard | PR4 | `pytest -k dash` | 5p+2logs+banner | `dash+banner+panels` |
| 5 | Tests | PR5 | `ruff&&pytest` | pilot | `tests/*` |

## Phase 1: Shell / Guard + Deps

- [x] 1.1 textual>=0.80 `pyproject.toml` none S `uv sync`
- [x] 1.2 RED launch isatty/find_spec `tests/test_mnemo_tui_shell.py` 1.1 S `pytest -k launch` RED
- [x] 1.3 Impl launch router `scripts/mnemo.py` 1.2 S `pytest -k launch` GREEN
- [x] 1.4 Scaffold app/theme `scripts/mnemo_tui/*` 1.3 M `ruff check`
- [x] 1.5 RED inject `;pwn`/`&&id` `tests/test_mnemo_tui_security.py` 1.4 S `pytest -k inject` RED
- [x] 1.6 Fix shell=False+regex `services/*` 1.5 S GREEN `test_inject`
- [x] 1.7 RED git-C `..`/`/tmp` `tests/test_mnemo_tui_security.py` 1.6 S `pytest -k git_c` RED
- [x] 1.8 Fix resolve_repo `services/system.py` 1.7 S GREEN `test_git_c`

## Phase 2: Onboarding — GitHub / Repo

- [x] 2.1 RED+impl gh status 5s PAT `services/github.py` 1.8 M `pytest -k github`
- [x] 2.2 RED+impl repo default project.name `services/github.py,screens/onboarding.py` 2.1 M `pytest -k repo`
- [x] 2.3 Gate Connected/Offline `screens/onboarding.py` 2.2 M pilot gate

## Phase 3: Uranus / SSH / Tailscale

- [x] 3.1 ssh ConnectTimeout5+tailscale `services/ssh.py,tailscale.py` 2.3 M `pytest -k ssh`
- [x] 3.2 RED+impl picker `*.key,*.pem,id_*`+tui.json `widgets/key_picker.py` 3.1 M `pytest -k picker`
- [x] 3.3 Uranus host+Test ✅/❌<6s `screens/onboarding.py` 3.2 M pilot timeout6

## Phase 4: Dashboard + Logs + Banner

- [x] 4.1 System/Tools/Git panels `services/system.py,widgets/panels/*` 3.3 M `pytest -k panels`
- [x] 4.2 Banner poll 1.1.1.1+gh+pacman `widgets/banner.py,app.py` 4.1 M `pytest -k banner`
- [x] 4.3 Grid 3×2+RichLog `screens/dashboard.py,widgets/log_panel.py` 4.2 L pilot 5+2
- [x] 4.4 Actions doctor/start/end/sync `screens/dashboard.py` 4.3 M pilot actions

## Phase 5: Tests + Polish (strict TDD)

- [x] 5.1 Unit picker/tui.json `tests/test_mnemo_tui_*.py` 4.4 M `pytest -q`
- [x] 5.2 Integration temp repo `tests/test_mnemo_tui_integration.py` 5.1 M `pytest -k integ`
- [x] 5.3 Pilot e2e Tab/SSH/banner `tests/test_mnemo_tui_pilot.py` 5.2 M `pytest -k pilot`
- [x] 5.4 Polish ruff+secrets+CURRENT `*` 5.3 S `ruff&&pytest -q`
