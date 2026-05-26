# Unified Install Experience

This document is the user-facing distribution target for Loom.

## Default Model

Loom defaults to a single root CLI install model:

- install `@mc-and-his-agents/loom`
- use `loom host install` to install host plugin/SKILLS payloads
- use `loom host verify`, `loom skills check`, and `loom doctor` to verify the target repository
- start from `loom-init`
- keep host-specific wiring in CLI-managed adapter surfaces

The default path is not `@mc-and-his-agents/loom-installer` for Codex or any
other primary install journey. The installer remains deprecated historical
evidence only.

Install path status:

- Default: root `loom` CLI install plus CLI-managed host plugin/SKILLS payloads.
- Managed payload: generated `skills/` and `plugins/` surfaces installed or verified by `loom`.
- Historical: `@mc-and-his-agents/loom-installer` references retained only for deprecated evidence and compatibility records.
- Unsupported: presenting plugin install, SKILLS install, single-skill install, or installer commands as an independent primary Loom install surface.

## Source And Generated Surfaces

- `src/skills/` is the only editable source truth for Loom skills.
- `skills/` is a checked-in generated payload surface.
- `skills/<skill-id>` is directly consumable by host-native skill discovery after the root CLI installs or synchronizes it.
- `skills/<skill-id>` is also a self-contained skill payload.
- `skills/<skill-id>/loom-package.json` is the machine-readable package metadata location.
- `skills/<skill-id>/.loom-runtime/` is the package-internal runtime closure.

Do not hand-edit generated `skills/` content. Rebuild it with:

```bash
python3 tools/skills_surface.py generate
```

Verify it with:

```bash
make skills-check
```

This payload surface is distinct from target repository `.loom` governance
carriers. When Loom adopts a target repository, stable `.loom` carriers must
follow [loom-surfaces-version-control.md](./loom-surfaces-version-control.md);
CLI-managed host payloads must not hide them with a blanket `.loom/` ignore.

## CLI-Managed Install

The root CLI install is the default user journey. It exposes the complete Loom
scenario surface through CLI-managed host payloads:

- root entry: `loom-init`
- scenario skills: `loom-adopt`, `loom-resume`, `loom-pre-review`, `loom-spec-review`, `loom-review`, `loom-merge-ready`, `loom-handoff`, `loom-retire`
- package-internal runtime for each skill
- shared host semantics documented in `host-adapter-matrix.md`

Users should not need to understand `src/skills/`, `.loom-runtime/`, or adapter implementation details before starting.

This replaces the old full repo wording as the primary user journey. Repository
source remains the development truth, but user install guidance goes through the
root CLI and its managed payloads.

CLI-managed install does not mean every host uses the same filesystem path. It
means each host exposes the same generated `skills/` surface, preserves
`loom-init` as the default entry, and keeps host-specific discovery, bootstrap,
tool mapping, and verification behind `loom host ...` and `loom skills ...`
commands.

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
