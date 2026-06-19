# Unified Install Experience

This document is the user-facing distribution target for Loom.

For the milestone #14 hard cut, the authoritative target-state contract is
[global-cli-user-plugin-contract.md](./global-cli-user-plugin-contract.md).

## Default Model

Loom defaults to a single root CLI install model:

- install `@mc-and-his-agents/loom`
- use `loom host install --host codex --scope user --apply --json` to install
  the Codex user-level Loom plugin from the global package
- use `loom host register --host codex --scope user --apply --json` to register
  the user-level plugin
- use `loom install --mode metadata-only` for downstream repository adoption
- use `loom installed-state validate`, `loom host verify`, `loom skills check`, and `loom doctor` to verify the selected repository mode
- start from `loom-init`
- keep host-specific wiring in CLI-managed adapter surfaces

The default path is not `@mc-and-his-agents/loom-installer` for Codex or any
other primary install journey. The installer remains deprecated historical
evidence only.

Install path status:

- Default: root `loom` CLI install plus Codex user-level plugin install/register
  plus metadata-only repository adoption.
- Managed payload: the user-level Codex Loom plugin payload installed from the
  global Loom package.
- Historical: `@mc-and-his-agents/loom-installer` references retained only for deprecated evidence and compatibility records.
- Unsupported: presenting repo-local plugin install, repo-local runtime install,
  SKILLS install, single-skill install, or installer commands as an independent
  primary Loom install surface.

<!-- legacy-release-surface-anchor: use `loom host install` to install host plugin payloads -->

The legacy release-surface anchor above is retained only for checker continuity.
In the milestone #14 target it refers to historical repo-local payload detection
and must not be read as a current downstream install instruction.

## Runtime Provider Modes

The root CLI install supports one current repository runtime provider mode:

- `global-cli`: the target repository records adoption metadata and depends on
  the installed root `loom` command as the runtime provider. No `.loom/bin`
  carrier is expected in this mode.
- `repo-local-wrapper`: legacy residue for migration diagnostics only, not a
  current downstream adoption target.

For `global-cli` repositories, validate the repository metadata and external
provider boundary with:

```bash
loom installed-state validate --target . --json
loom detect --target . --json
loom doctor --target . --json
loom verify --target . --json
loom repair plan --target . --json
```

These commands may report missing or incompatible workstation/global CLI state,
but user-level provider state is not repository truth. A detected `.loom/bin`
directory is unsupported legacy residue in the milestone #14 target.

## Source And Generated Surfaces

- `src/skills/` is the only editable source truth for Loom skills.
- The user-level Codex Loom plugin payload is the current skills publishing
  shape.
- `skills/` and single-skill package metadata are legacy/source compatibility
  surfaces until the plugin-payload-only generation work removes them.
- Downstream metadata-only adoption consumes the user-level Codex Loom plugin as
  its skills provider and does not write `plugins/loom/skills/`,
  `plugins/loom/.codex-plugin/plugin.json`, `.loom/bin`, `.agents/skills`, or
  downstream top-level `skills/`.

Do not hand-edit generated `skills/` content. Rebuild it with:

```bash
python3 tools/skills_surface.py generate
```

Verify it with:

```bash
make skills-check
```

This source repository payload surface is distinct from target repository
`.loom` governance carriers. When Loom adopts a target repository, stable
`.loom` carriers must follow
[loom-surfaces-version-control.md](./loom-surfaces-version-control.md);
CLI-managed host payloads must not hide them with a blanket `.loom/` ignore.

## CLI-Managed Install

The root CLI install is the default user journey. It exposes the complete Loom
scenario surface through the Codex user-level Loom plugin provider:

- root entry: `loom-init`
- scenario skills: `loom-adopt`, `loom-resume`, `loom-pre-review`, `loom-spec-review`, `loom-review`, `loom-merge-ready`, `loom-handoff`, `loom-retire`
- shared host semantics documented in `host-adapter-matrix.md`

Users should not need to understand `src/skills/`, `.loom-runtime/`, or adapter implementation details before starting.

This replaces the old full repo wording as the primary user journey. Repository
source remains the development truth, but user install guidance goes through the
root CLI and its managed payloads.

CLI-managed install does not mean the target repository receives a plugin
payload. It means Codex exposes the Loom scenario skills payload from user-level
state, preserves `loom-init` as the default entry, and keeps host-specific
discovery, bootstrap, tool mapping, and verification behind `loom host ...` and
`loom skills ...` commands.

## Target Payload Versus Workstation Registration

Loom separates two first-class states:

- Target repository adoption state: `.loom/installed-state.json` plus
  repo-owned governance residue for metadata-only adoption.
- Developer workstation host registration state: host-private user state that
  lets a local application discover or enable the payload, such as Codex
  Desktop's personal marketplace entry, user plugin cache payload, and config
  enablement.

`loom host verify --host codex --mode metadata-only --target . --json` verifies
repository adoption metadata. It is not evidence that Codex Desktop on this
machine has registered, enabled, loaded, or hot-loaded the plugin.

For Codex Desktop, use the explicit workstation registration surface:

```bash
loom host install --host codex --scope user --dry-run --json
loom host install --host codex --scope user --apply --json
loom host register --host codex --scope user --dry-run --json
loom host register --host codex --scope user --apply --json
```

Registration is a user workstation mutation and must require `--apply`. Repair
and upgrade planning may recommend it when the target repository payload is
current but local Codex registration is missing. `loom doctor` may report both
states, but Codex Desktop private registration state must not become target
repository truth.

If an adopted downstream repository still has `.loom/bin`, `.loom/bootstrap`,
`plugins/loom/`, `.agents/skills`, or Loom-generated top-level `skills/` from
older layouts, Loom treats those paths as unsupported legacy residue. `loom
repair plan` and `loom upgrade-plan` may recommend cleanup only when ownership
is clear. Mixed or target-owned top-level `skills/` fails closed to manual
review and must not be deleted automatically.

After applying registration, start a new Codex session or restart Codex Desktop
if discovery was already loaded. Loom does not claim current-session hot reload.

## Legacy Single-Skill Install

Single-skill payload distribution is not part of the milestone #14 install
target. The source tree may remain organized by skill, but the user-facing Loom
skills publishing shape is the Codex user-level plugin payload. Historical
`skills/<skill-id>` native discovery remains vocabulary for legacy detection and
migration checks only.

## User Semantics

Across Codex, Claude Code, OpenCode, Gemini, and Cursor, the user-facing experience should remain consistent:

- install entry is clear
- `loom-init` is the default starting point for CLI-managed installs
- scene skills are discoverable
- bootstrap or session-start guidance points to Loom entry semantics
- tool mapping remains adapter-owned and mostly invisible
- upgrades expose version context
- failures are visible and fail closed

## Version Context

Loom does not use one global version line for every surface. User-facing install and upgrade docs must refer to `version-authority-map.md` when describing repository versions, GitHub releases, installer versions, plugin surface versions, host adapter versions, generated single-skill package versions, skills registry and contract versions, runtime/core versions, or external runtime schemas.
