# Delta for mnemo-tui-dashboard

## MODIFIED Requirements

### Requirement: PanelsReal

The system MUST show System hostname/OS/arch/Python/device/role/project; Tools uv/terraform/docker/jq OK/FALTA+detail+Install preview; Git branch/dirty/ahead-behind; Uranus host/user/key/tailscale IP + ssh ConnectTimeout=5 → ✅/❌ <6s; skeleton until worker.
(Previously: Layout and Panels vague)

#### Scenario: Real data
- GIVEN uv OK terraform FALTA main dirty 1 ahead tailscale IP
- WHEN workers done
- THEN System/Tools/Git/Uranus correct Install visible ✅ <6s

#### Scenario: Offline degrade
- GIVEN offline tailscale missing
- WHEN load
- THEN banner Offline Uranus "not detected" / "❌ Unreachable" no block

### Requirement: ActionsExecute

The system MUST provide buttons doctor/start/sync/bootstrap/device via list-form ["uv","run","python","scripts/mnemo.py",cmd] @work 10s + call_from_thread → stdout General stderr Errors / Audit HH:MM:SS; responsive.

#### Scenario: Action non-blocking
- GIVEN online press doctor
- WHEN worker runs
- THEN responsive output→General HH:MM:SS banner Online

#### Scenario: Error routing
- GIVEN sync fails offline
- WHEN done
- THEN error→Errors / Audit HH:MM:SS banner Offline skeleton cleared

UI copy: "System" · "Tools" · "Git" · "Uranus"
