# Unified Install Experience

This document is the user-facing distribution target for Loom.

## Default Model

Loom defaults to a single root CLI install model:

- install `@mc-and-his-agents/loom`
- use `loom host install` to install host plugin payloads when embedded
  repository payload mode is explicitly selected
- use `loom install --mode metadata-only` for default downstream repository adoption
- use `loom host install --mode plugin` only when an embedded repository payload is explicitly needed
- use `loom installed-state validate`, `loom host verify`, `loom skills check`, and `loom doctor` to verify the selected repository mode
- use an explicit host registration command when a workstation, such as Codex Desktop, needs user-level plugin registration
- start from `loom-init`
- keep host-specific wiring in CLI-managed adapter surfaces

The default path is not `@mc-and-his-agents/loom-installer` for Codex or any
other primary install journey. The installer remains deprecated historical
evidence only.

Install path status:

- Default: root `loom` CLI install plus metadata-only repository adoption with a user-level skills provider.
- Managed payload: the Loom source repository's generated `skills/` surface and
  explicit embedded downstream host plugin payloads installed or verified by `loom`.
- Historical: `@mc-and-his-agents/loom-installer` references retained only for deprecated evidence and compatibility records.
- Unsupported: presenting plugin install, SKILLS install, single-skill install, or installer commands as an independent primary Loom install surface.

## Source And Generated Surfaces

- `src/skills/` is the only editable source truth for Loom skills.
- `skills/` is the Loom source repository's checked-in generated payload surface.
- `skills/<skill-id>` is directly consumable by host-native skill discovery after the root CLI installs or synchronizes it.
- `skills/<skill-id>` is also a self-contained skill payload.
- `skills/<skill-id>/loom-package.json` is the machine-readable package metadata location.
- `skills/<skill-id>/.loom-runtime/` is the package-internal runtime closure.
- Downstream metadata-only adoption consumes the user-level Codex Loom plugin as
  its skills provider and does not write `plugins/loom/skills/`,
  `.agents/skills`, or downstream top-level `skills/` by default.
- Downstream embedded Codex plugin mode embeds this generated payload at
  `plugins/loom/skills/` and does not write or require downstream top-level
  `skills/` by default.

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
scenario surface through user-level providers or explicit CLI-managed host
payloads:

- root entry: `loom-init`
- scenario skills: `loom-adopt`, `loom-resume`, `loom-pre-review`, `loom-spec-review`, `loom-review`, `loom-merge-ready`, `loom-handoff`, `loom-retire`
- package-internal runtime for each skill
- shared host semantics documented in `host-adapter-matrix.md`

Users should not need to understand `src/skills/`, `.loom-runtime/`, or adapter implementation details before starting.

This replaces the old full repo wording as the primary user journey. Repository
source remains the development truth, but user install guidance goes through the
root CLI and its managed payloads.

CLI-managed install does not mean every host uses the same filesystem path. It
means each host exposes the same Loom scenario skills payload, preserves
`loom-init` as the default entry, and keeps host-specific discovery, bootstrap,
tool mapping, and verification behind `loom host ...` and `loom skills ...`
commands. For downstream metadata-only Codex adoption, the payload comes from
the user-level Codex Loom plugin provider. For downstream embedded Codex plugin
mode, that payload lives under `plugins/loom/skills/`.

## Target Payload Versus Workstation Registration

Loom separates two first-class states:

- Target repository adoption state: `.loom/installed-state.json` plus
  repo-owned governance residue for metadata-only adoption, or the explicit
  embedded repository payload including `plugins/loom/.codex-plugin/plugin.json`
  and `plugins/loom/skills/` for Codex plugin mode.
- Developer workstation host registration state: host-private user state that
  lets a local application discover or enable the payload, such as Codex
  Desktop's personal marketplace entry, user plugin cache payload, and config
  enablement.

`loom host verify --host codex --mode metadata-only --target . --json` verifies
repository adoption metadata. `loom host verify --host codex --mode plugin
--target . --json` verifies the embedded target repository payload. Neither is
evidence that Codex Desktop on this machine has registered, enabled, loaded, or
hot-loaded the plugin.

For Codex Desktop, use the explicit workstation registration surface:

```bash
loom host register --host codex --source ./plugins/loom --scope user --dry-run --json
loom host register --host codex --source ./plugins/loom --scope user --apply --json
```

Registration is a user workstation mutation and must require `--apply`. Repair
and upgrade planning may recommend it when the target repository payload is
current but local Codex registration is missing. `loom doctor` may report both
states, but Codex Desktop private registration state must not become target
repository truth.

If an adopted downstream repository still has Loom-generated top-level
`skills/` from the older plugin layout, plugin mode treats it as legacy residue.
`loom repair plan` and `loom upgrade-plan` may recommend a safe migration only
when ownership is clear. Mixed or target-owned top-level `skills/` fails closed
to manual review and must not be deleted automatically.

After applying registration, start a new Codex session or restart Codex Desktop
if discovery was already loaded. Loom does not claim current-session hot reload.

## Single-Skill Install

Single-skill payloads remain a package shape for compatibility and generic skill
consumers. They are not a primary Loom install path.

Single-skill install must:

- be discoverable by the host
- include `SKILL.md`, `contract.json`, `loom-package.json`, launcher, and `.loom-runtime/`
- fail closed when runtime or metadata is missing
- expose machine-readable version context

Single-skill install must not claim that the full Loom scenario surface is installed.

Single-skill payload consumption remains valid for compatibility with generic
skill tooling and hosts that intentionally expose only one Loom capability. It
is not a replacement for root CLI install.

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
