# Unified Install Experience

This document is the user-facing distribution target for Loom Phase #496.

## Default Model

Loom defaults to a Superpowers-style install model:

- clone the full Loom repository
- let each host discover the generated root `skills/` surface through its native mechanism
- start from `loom-init`
- keep host-specific wiring in adapter surfaces

The default path is not `@mc-and-his-agents/loom-installer` for Codex. The installer remains an adapter helper, single-skill helper, and verifier.

Install path status:

- Default: full repository install plus native or host skill discovery.
- Advanced: install one generated `skills/<skill-id>` package as a single skill.
- Adapter-managed: use `@mc-and-his-agents/loom-installer` or a host plugin when the host needs orchestration.
- Deprecated: historical docs that present generated installer payloads or plugin-only setup as the source truth.
- Unsupported: presenting a single-skill install as the full Loom scenario surface.

## Source And Generated Surfaces

- `src/skills/` is the only editable source truth for Loom skills.
- `skills/` is a checked-in generated install surface.
- `skills/<skill-id>` is directly consumable by host-native skill discovery.
- `skills/<skill-id>` is also a self-contained single-skill package.
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

This install surface is distinct from target repository `.loom` governance carriers. When Loom adopts a target repository, stable `.loom` carriers must follow [loom-surfaces-version-control.md](./loom-surfaces-version-control.md); installers and adapters must not hide them with a blanket `.loom/` ignore.

## Full Repo Install

Full repo install is the default user journey. It exposes the complete Loom scenario surface:

- root entry: `loom-init`
- scenario skills: `loom-adopt`, `loom-resume`, `loom-pre-review`, `loom-spec-review`, `loom-review`, `loom-merge-ready`, `loom-handoff`, `loom-retire`
- package-internal runtime for each skill
- shared host semantics documented in `host-adapter-matrix.md`

Users should not need to understand `src/skills/`, `.loom-runtime/`, or adapter implementation details before starting.

Full repo install does not mean every host uses the same filesystem path. It means each host exposes the same generated `skills/` surface, preserves `loom-init` as the default entry, and keeps host-specific discovery, bootstrap, tool mapping, and verification in adapter-owned surfaces.

## Single-Skill Install

Single-skill install is a supported advanced path. It installs exactly one `skills/<skill-id>` directory and exposes only that named skill.

Single-skill install must:

- be discoverable by the host
- include `SKILL.md`, `contract.json`, `loom-package.json`, launcher, and `.loom-runtime/`
- fail closed when runtime or metadata is missing
- expose machine-readable version context

Single-skill install must not claim that the full Loom scenario surface is installed.

Single-skill install remains valid for targeted use, compatibility with generic skill installers, and hosts that intentionally expose only one Loom capability. It is not a replacement for full repo install.

## User Semantics

Across Codex, Claude Code, OpenCode, Gemini, and Cursor, the user-facing experience should remain consistent:

- install entry is clear
- `loom-init` is the default starting point for full repo installs
- scene skills are discoverable
- bootstrap or session-start guidance points to Loom entry semantics
- tool mapping remains adapter-owned and mostly invisible
- upgrades expose version context
- failures are visible and fail closed

## Version Context

Loom does not use one global version line for every surface. User-facing install and upgrade docs must refer to `version-authority-map.md` when describing repository versions, GitHub releases, installer versions, plugin surface versions, host adapter versions, generated single-skill package versions, skills registry and contract versions, runtime/core versions, or external runtime schemas.
