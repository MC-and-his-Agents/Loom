# Host Adapter Matrix

This matrix defines consistent Loom semantics across supported hosts. Implementations may differ, but user-visible meaning must not.

| Host | Support status | Default install path | Discovery surface | Bootstrap/session-start surface | Tool mapping surface | Upgrade surface | Verification surface |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Codex | primary | clone full repo, link `skills/loom-*` into native skill discovery | `~/.agents/skills/<skill-id>` or host-native equivalent | restart Codex, start from `loom-init` | Codex tools remain host-owned; Loom skills describe required actions | `git pull` on clone, then restart discovery | `make skills-check`; `ls ~/.agents/skills/loom-init/SKILL.md` |
| Claude Code | adapter | full repo plus Claude plugin or project skills registration | `.claude/skills/<skill-id>` or marketplace plugin | plugin/session guidance must point to `loom-init` | Claude tools remain adapter-owned | refresh repo clone or reinstall adapter package | installer verify plus static plugin/skills checks |
| OpenCode | adapter contract | full repo plus OpenCode plugin/path injection | configured skills path pointing at generated `skills/` | plugin injects startup guidance for `loom-init` | plugin maps OpenCode tools to Loom host-action expectations | refresh clone and reload plugin | static adapter check until OpenCode CLI is available |
| Gemini | adapter contract | full repo plus extension/context import | extension/context references generated `skills/` | context import names `loom-init` as root entry | Gemini tool use is documented as adapter mapping | refresh clone and reload extension/context | static adapter check until Gemini extension CLI is available |
| Cursor | adapter contract | full repo plus Cursor plugin/hooks | plugin manifest points at generated `skills/` | hooks surface `loom-init` startup guidance | Cursor tool mapping is adapter-owned | refresh clone and reload plugin/hooks | static adapter check until Cursor plugin CLI is available |

Each supported host has exactly one default path: full repository install plus that host's native or adapter discovery of the generated root `skills/` surface. Single-skill install is always advanced. Installer-driven plugin installation is adapter-managed and must not be described as the Codex default path.

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

- full repository install: `VERSION` and the git revision of the clone
- generated skill surface: `skills/registry.json` and `skills/upgrade-contract.json`
- single-skill package: `skills/<skill-id>/loom-package.json`
- plugin surface: the host plugin manifest, such as `plugins/loom/.codex-plugin/plugin.json`
- installer: `packages/loom-installer/package.json`

The authority rules for these surfaces live in [version-authority-map.md](./version-authority-map.md).

## Fail-Closed Conditions

Adapters must fail closed and report failure instead of partial success when:

- `SKILL.md` is missing
- `contract.json` or `loom-package.json` is missing
- `.loom-runtime/` is missing
- the launcher cannot report `installed-runtime`
- host discovery cannot observe the installed skill
- version metadata cannot be read
- a conflicting user override shadows Loom without explicit operator intent
