# Delta for mnemo-tui-shell

## MODIFIED Requirements

### Requirement: Entrypoint and Textual Guard

The system MUST launch TUI only TTY no-args without --no-tui; else CLI; without textual show hint "TUI not installed — run `uv sync` to enable".
(Previously: unchanged — guard retained)

#### Scenario: TTY opens TUI
- GIVEN TTY no args textual installed
- WHEN run
- THEN TUI dark and on_mount fires

## ADDED Requirements

### Requirement: LogsFunctional

The system MUST log "Mnemosyne ready — <device> (<os> x86_64) — textual <ver> — online <bool>" to General <1s on mount; MUST timestamp HH:MM:SS; MUST route stdout→General stderr→Errors / Audit; MUST never block TUI via workers + call_from_thread.

#### Scenario: Ready on mount
- GIVEN PCrda Ubuntu x86_64 textual 8.2.8 online true
- WHEN mounts
- THEN General shows ready line HH:MM:SS <1s

#### Scenario: Dual routing non-blocking
- GIVEN probe 5s and doctor output
- WHEN run
- THEN UI responsive <1s stdout→General stderr→Errors / Audit timestamped

### Requirement: ThemePolish

The system MUST register Theme "mnemosyne-dark" dark=True tokens #7c5cff #0e0e10 #1a1a1e #2ecc71 #ff4d4d via CSS vars; MUST apply theme.tcss spacing/borders/focus/skeletons dark-only.

#### Scenario: Theme applied
- GIVEN TUI 80×24
- WHEN rendered
- THEN bg #0e0e10 surface #1a1a1e accent #7c5cff visible Header clock ticks Footer dock

UI copy: "General Log" · "Errors / Audit"
