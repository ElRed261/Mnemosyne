# Delta for mnemo-tui-onboarding

## MODIFIED Requirements

### Requirement: GitHub Auth and Gate

The system MUST offer gh auth login + PAT → "Connected as @user" block Create PAT never logged; MUST log gh auth status and REPO_RE ^[A-Za-z0-9_.-]+$ validation HH:MM:SS to General/Errors.
(Previously: gate without logs)

#### Scenario: Auth success logs
- GIVEN gh status @andry
- WHEN check
- THEN "Connected as @andry" enabled General log HH:MM:SS

#### Scenario: Blocked invalid logs
- GIVEN not auth name "bad;rm"
- WHEN Create
- THEN disabled "Connect GitHub to continue" Errors REPO_RE HH:MM:SS PAT not logged

### Requirement: Repo Create/Link

The system MUST provide editable name default mnemosyne.toml:project.name fallback andry-de-zoomcamp Public/Private via gh repo create list-form; MUST reject empty/invalid REPO_RE with Errors log HH:MM:SS.

#### Scenario: Create valid logs
- GIVEN connected name andry-de-zoomcamp Private
- WHEN confirm
- THEN gh repo create General log HH:MM:SS

#### Scenario: Empty rejected
- GIVEN name cleared
- WHEN Create
- THEN "Repository name is required" Errors HH:MM:SS

### Requirement: Uranus and Picker

The system MUST host uranus-core-vnic tailscale --json picker ~/.ssh *.key,*.pem,id_* path-only tui.json ssh ConnectTimeout=5 → ✅/❌ <6s; MUST log picker/test HH:MM:SS; offline banner degrade.

#### Scenario: Picker logs
- GIVEN pick ~/.ssh/id_test.key
- WHEN test
- THEN "✅ Connected" <6s General log HH:MM:SS persist

#### Scenario: Offline degrade
- GIVEN offline
- WHEN load
- THEN "Offline — GitHub unavailable" disabled banner Offline picker usable

UI copy: "Connected as @user" · "✅ Connected · ❌ Unreachable"
