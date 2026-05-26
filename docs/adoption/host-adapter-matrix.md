# Host Adapter Matrix

This matrix defines consistent Loom semantics across supported hosts. Implementations may differ, but user-visible meaning must not.

| Host | Support status | Default install path | Discovery surface | Bootstrap/session-start surface | Tool mapping surface | Upgrade surface | Verification surface |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Codex | primary | `npm install -g @mc-and-his-agents/loom`; `loom host install --host codex --mode plugin --target . --apply --json` | CLI-managed `skills/` and `plugins/loom/` payloads in the target repository | host discovery reloads, then start from `loom-init` | Codex tools remain host-owned; Loom skills describe required actions | update root CLI, then rerun `loom host install ... --force` | `loom host verify --host codex --mode plugin --target . --json`; `loom skills check --target . --json` |
| Claude Code | adapter | root `loom` CLI plus CLI-managed Claude plugin or project skills registration | CLI-managed generated `skills/` payload or host plugin | plugin/session guidance must point to `loom-init` | Claude tools remain adapter-owned | update root CLI, then rerun host install/verify | host verify plus static plugin/skills checks |
| OpenCode | adapter contract | root `loom` CLI plus CLI-managed OpenCode plugin/path injection | configured skills path pointing at CLI-managed generated `skills/` | plugin injects startup guidance for `loom-init` | plugin maps OpenCode tools to Loom host-action expectations | update root CLI and reload plugin | static adapter check until OpenCode CLI is available |
| Gemini | adapter contract | root `loom` CLI plus CLI-managed extension/context import | extension/context references CLI-managed generated `skills/` | context import names `loom-init` as root entry | Gemini tool use is documented as adapter mapping | update root CLI and reload extension/context | static adapter check until Gemini extension CLI is available |
| Cursor | adapter contract | root `loom` CLI plus CLI-managed Cursor plugin/hooks | plugin manifest points at CLI-managed generated `skills/` | hooks surface `loom-init` startup guidance | Cursor tool mapping is adapter-owned | update root CLI and reload plugin/hooks | static adapter check until Cursor plugin CLI is available |

Each supported host has exactly one default path: the root `loom` CLI installs
and verifies host plugin/SKILLS payloads. Single-skill payload consumption is
compatibility-only. Installer-driven plugin installation is deprecated legacy
behavior and must not be described as a default path.

## Required Fields

Each host adapter must define:

- `host`
- `support_status`
- `default_install_path`
- `advanced_single_skill_path`
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

## Single-Skill Boundary

Every host may install `skills/<skill-id>` as an advanced path. The host must present it as a single named skill, not as a complete Loom installation.

The package source is the checked-in generated root directory. The editable source remains `src/skills/<skill-id>`, but host adapters and generic skill installers consume `skills/<skill-id>` because it contains `loom-package.json` and `.loom-runtime/`.

## Version Metadata

Adapters must surface machine-readable version context instead of implying one global Loom version. The minimum version metadata locations are:

- root CLI install: `@mc-and-his-agents/loom`, `VERSION`, and the matching GitHub `v*` tag/release evidence
- generated skill surface: `skills/registry.json` and `skills/upgrade-contract.json`
- single-skill package: `skills/<skill-id>/loom-package.json`
- plugin surface: the host plugin manifest, such as `plugins/loom/.codex-plugin/plugin.json`
- deprecated installer evidence: `packages/loom-installer/package.json`

The authority rules for these surfaces live in `version-authority-map.md`.

## Fail-Closed Conditions

Adapters must fail closed and report failure instead of partial success when:

- `SKILL.md` is missing
- `contract.json` or `loom-package.json` is missing
- `.loom-runtime/` is missing
- the launcher cannot report `installed-runtime`
- host discovery cannot observe the installed skill
- version metadata cannot be read
- a conflicting user override shadows Loom without explicit operator intent

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
