# mnemo-tui-shell Specification

## Purpose
Dark-only shell: TTY no-args → TUI; else CLI pure.

## Requirements

### Requirement: Entrypoint and Textual Guard
MUST launch TUI only on TTY no-args without --no-tui; MUST route else to CLI; MUST run CLI without textual with hint "TUI not installed — run `uv sync` to enable".

#### Scenario: TTY opens TUI
- GIVEN TTY, `mnemo` no args
- WHEN run
- THEN TUI launches dark

#### Scenario: Non-TTY stays CLI
- GIVEN piped or --no-tui or subcommand
- WHEN run
- THEN CLI runs, TUI not loaded

#### Scenario: Missing textual
- GIVEN no textual, TTY no-args
- WHEN run
- THEN hint shown, exit 0

### Requirement: Theme, Nav, Logs
MUST single dark Opencode theme, keyboard nav with focus/footer shortcuts, two logs General + Errors/Audit.

#### Scenario: Nav
- GIVEN TUI open
- WHEN Tab/arrows/Enter
- THEN focus moves, action fires

#### Scenario: Offline
- GIVEN no network
- WHEN TUI open
- THEN shell/logs usable, network degraded

UI copy: "TUI not installed — run `uv sync` to enable" · "General Log" · "Errors / Audit" · "q Quit · ? Help · Tab Next"
