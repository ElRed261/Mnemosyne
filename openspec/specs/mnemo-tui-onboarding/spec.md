# mnemo-tui-onboarding Specification

## Purpose
GitHub + Uranus onboarding with gated auth, repo create/link, key validation.

## Requirements

### Requirement: GitHub Auth and Gate
MUST offer `gh auth login` + PAT, validate `gh auth status` → "Connected as @user", MUST block Create until authenticated, PAT never logged.

#### Scenario: Auth success
- GIVEN `gh auth status` → @andry
- WHEN check
- THEN "Connected as @andry", Create enabled

#### Scenario: Blocked
- GIVEN not authenticated
- WHEN Create attempt
- THEN disabled, "Connect GitHub to continue"

#### Scenario: Offline
- GIVEN offline
- WHEN load
- THEN "Offline — GitHub unavailable", actions disabled

### Requirement: Repo Create/Link
MUST editable name default `mnemosyne.toml:project.name` fallback `andry-de-zoomcamp`, Public/Private, Create via `gh repo create` and Link existing; reject empty.

#### Scenario: Create
- GIVEN connected, name `andry-de-zoomcamp` Private
- WHEN confirm
- THEN `gh repo create` runs

#### Scenario: Empty rejected
- GIVEN name cleared
- WHEN Create
- THEN "Repository name is required"

### Requirement: Uranus and Picker
MUST editable host default `uranus-core-vnic` autodetect `tailscale status --json` + user, picker `~/.ssh` filter `*.key,*.pem,id_*` persisting only path in `.mnemosyne/tui.json`, test `ssh -i <key> -o ConnectTimeout=5 <user>@<host> "echo ok"` → ✅/❌ <6s.

#### Scenario: Pick success
- GIVEN pick `~/.ssh/id_test.key`
- WHEN test
- THEN "✅ Connected" <6s, path persists

#### Scenario: Remember/degrade
- GIVEN previous key, tailscale missing/timeout
- WHEN reopen/test
- THEN start at previous dir, show "❌ Unreachable" no block

UI copy: "Connect GitHub" · "Connected as @user" · "Create repository" · "Link existing" · "Pick SSH key" · "Test connection" · "✅ Connected · ❌ Unreachable"
