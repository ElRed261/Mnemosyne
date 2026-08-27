# mnemo-tui-dashboard Specification

## Purpose
Dashboard: five panels + banner + dual logs.

## Requirements

### Requirement: Layout and Panels
MUST show System/Tools/Git/Uranus/Quick Actions + General/Errors-Audit logs; panels refresh independently. System→hostname/OS/arch/Python/device/role/project.name; Tools→uv/terraform/jq/docker OK/MISSING; Git→branch/dirty/ahead-behind/merge-rebase.

#### Scenario: Visible
- GIVEN dashboard open
- WHEN rendered
- THEN 5 panels + 2 logs visible

#### Scenario: Tools/Git content
- GIVEN uv OK, terraform missing, main dirty 1 ahead
- WHEN rendered
- THEN Tools "uv OK ..." "terraform MISSING ..."; Git "dirty" "1 ahead"

### Requirement: Uranus, Actions, Banner
Uranus→host/user/key/tailscale IP or "not detected"/last test/remote status. Actions→doctor/start/end/sync/bootstrap/device. Banner→internet/GitHub/branch/services/updates (`pacman -Qu` on Arch) → "Offline" if unreachable; footer shortcuts.

#### Scenario: Online
- GIVEN reachable, 3 updates
- WHEN banner
- THEN "Online · GitHub connected · Updates: 3"

#### Scenario: Offline/logs
- GIVEN offline, doctor triggered
- WHEN load/complete
- THEN banner "Offline", GitHub/Uranus disabled, System/Git remain; output→General, error→Errors/Audit

UI copy: "System" · "Tools" · "Git" · "Uranus" · "Quick Actions" · "General Log" · "Errors / Audit" · "Online · Offline · Updates:" · "q Quit · ? Help · Tab Next · Enter Run"
