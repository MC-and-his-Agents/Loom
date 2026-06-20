# Host Adapter Matrix

This matrix defines consistent Loom semantics across supported hosts. Implementations may differ, but user-visible meaning must not.

| Host | Support status | Default install path | Discovery surface | Bootstrap/session-start surface | Tool mapping surface | Upgrade surface | Verification surface |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Codex | primary | `npm install -g @mc-and-his-agents/loom`; `loom host install --host codex --scope user --apply --json`; `loom host register --host codex --scope user --apply --json`; downstream repository adoption uses `loom install --mode metadata-only --target . --apply --json` | metadata-only repositories consume the user-level Codex Loom plugin provider; no repo-local Loom plugin or skills payload is written | new Codex session or Codex Desktop restart after registration, then start from `loom-init` | Codex tools remain host-owned; Loom skills describe required actions | update root CLI, rerun user-level host install/register, then rerun installed-state validation | metadata-only: `loom host verify --host codex --mode metadata-only --target . --json`; workstation dry-run: `loom host install --host codex --scope user --dry-run --json` and `loom host register --host codex --scope user --dry-run --json`; `loom skills check --target . --json` |
| Claude Code | adapter | root `loom` CLI plus CLI-managed Claude plugin or project skills registration | CLI-managed generated `skills/` payload or host plugin | plugin/session guidance must point to `loom-init` | Claude tools remain adapter-owned | update root CLI, then rerun host install/verify | host verify plus static plugin/skills checks |
| OpenCode | adapter contract | root `loom` CLI plus CLI-managed OpenCode plugin/path injection | configured skills path pointing at CLI-managed generated `skills/` | plugin injects startup guidance for `loom-init` | plugin maps OpenCode tools to Loom host-action expectations | update root CLI and reload plugin | static adapter check until OpenCode CLI is available |
| Gemini | adapter contract | root `loom` CLI plus CLI-managed extension/context import | extension/context references CLI-managed generated `skills/` | context import names `loom-init` as root entry | Gemini tool use is documented as adapter mapping | update root CLI and reload extension/context | static adapter check until Gemini extension CLI is available |
| Cursor | adapter contract | root `loom` CLI plus CLI-managed Cursor plugin/hooks | plugin manifest points at CLI-managed generated `skills/` | hooks surface `loom-init` startup guidance | Cursor tool mapping is adapter-owned | update root CLI and reload plugin/hooks | static adapter check until Cursor plugin CLI is available |

Each supported host has exactly one primary entry: the root `loom` CLI.
For Codex, metadata-only repository adoption is the supported downstream mode.
Repo-local plugin payload, repo-local runtime payload, single-skill payload
consumption, and installer-driven plugin installation are legacy behavior and
must not be described as default or compatible current paths.

For Codex, repository adoption truth and Codex Desktop workstation registration
state are separate. In metadata-only mode, repository truth is
`.loom/installed-state.json` plus repo-owned governance residue; the user-level
Codex Loom plugin provides skills. Workstation registration is explicit,
user-scoped, and mutating only with `--apply`; it writes Codex user state such
as the personal marketplace entry, user plugin cache payload, and config
enablement. It must not write Codex Desktop private state into target repository
truth.

For downstream metadata-only mode, `.loom/bin`, `plugins/loom/skills/`,
`plugins/loom/.codex-plugin/plugin.json`, `.agents/skills`, and root `skills/`
are intentionally absent. Existing Loom-generated copies from older installs
are unsupported legacy residue; mixed or target-owned `skills/` must fail closed
to manual review.

<!-- legacy-release-surface-anchor: embedded skills at `plugins/loom/skills/` -->

The legacy release-surface anchor above is retained only for checker continuity.
In the milestone #14 target it is historical vocabulary for unsupported
repo-local payload residue, not a compatible current install mode.

## Required Fields

Each host adapter must define:

- `host`
- `support_status`
- `default_install_path`
- `install_surface`
- `discovery_surface`
- `bootstrap_or_session_start_surface`
- `default_entry`
- `invocation_surface`
- `tool_mapping_surface`
- `override_or_shadowing_surface`
- `upgrade_surface`
- `verification_surface`
- `fail_closed_conditions`
- `version_metadata_location`
- `workstation_registration_surface` when host discovery needs user-level state

## Legacy Single-Skill Boundary

Single-skill package install is not part of the milestone #14 downstream install
target. The editable source may remain organized by skill, but user-facing Loom
distribution is the Codex user-level plugin payload installed from the global
Loom package.

## Version Metadata

Adapters must surface machine-readable version context instead of implying one global Loom version. The minimum version metadata locations are:

- root CLI install: `@mc-and-his-agents/loom`, `VERSION`, and the matching GitHub `v*` tag/release evidence
- plugin payload: `plugins/loom/skills/registry.json` and `plugins/loom/skills/upgrade-contract.json`
- generated skills mirror: `skills/registry.json` and `skills/upgrade-contract.json`
- plugin surface: the host plugin manifest, such as `plugins/loom/.codex-plugin/plugin.json`
- deprecated installer evidence: `packages/loom-installer/package.json`

The authority rules for these surfaces live in `version-authority-map.md`.

## Fail-Closed Conditions

Adapters must fail closed and report failure instead of partial success when:

- `SKILL.md` is missing
- `contract.json` is missing
- `plugins/loom/skills/registry.json` or shared runtime assets are missing
- the launcher cannot report `installed-runtime`
- host discovery cannot observe the installed skill
- version metadata cannot be read
- a conflicting user override shadows Loom without explicit operator intent
- GitHub host API readback cannot consume `gh api` or an explicit process token. When local `gh` auth is present but `GH_TOKEN` / `GITHUB_TOKEN` is not present, Loom runtime must not silently fall back to anonymous public REST; it reports `host_api_unreadable` or `permission` and the single-command bridge next action `CODEX_EXPORT_GH_TOKEN=1 <same loom command>`.

## Lifecycle Hook Mapping

Host adapters may install or generate host-native hook configuration from Loom
`hook_locators`, but generated host config remains downstream of the Loom locator
contract. Loom core does not store Codex or Claude Code native hook file shapes.

Adapters report hook mapping with:

- `supported`
- `not_applicable`
- `advisory`
- `unsafe`

Codex mapping:

- `before-run`: `SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PermissionRequest`
- `after-run`: `PostToolUse`, `Stop`, `PostCompact`
- `cleanup`: `not_applicable` or Loom explicit `workspace cleanup|retire` extension; never required native hook

Claude Code mapping:

- `before-run`: `SessionStart`, `UserPromptSubmit`, `PreToolUse`
- `after-run`: `PostToolUse`, `Stop`, `SubagentStop`, `PostCompact`
- `cleanup`: optional `SessionEnd`, constrained by Loom cleanup safety

Host-native hook output must be mapped into Loom runtime evidence and must not
write authored progress, recovery/status truth, review verdict, validation
summary, host action result, or closeout basis.
