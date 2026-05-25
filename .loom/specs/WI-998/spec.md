# WI-998 Spec

## Goal

Make the public README entrypoints match the #885 CLI-first operating layer.

## Acceptance

- `README.md` presents `loom` as the primary execution control plane.
- `README.zh-CN.md` presents the same CLI-first entrypoint semantics in Chinese.
- Both READMEs include concrete CLI examples for diagnosis, upgrade planning, verification, and skills release checks.
- Both READMEs describe `loom-installer` as a compatibility shim, adapter-managed install path, single-skill helper, or legacy bridge instead of the default execution layer.
- The README language stays consistent with `docs/methodology/harness/cli-command-matrix.md`, `docs/methodology/harness/cli-first-control-plane.md`, #896, and #996.

## Non-Goals

- Do not redefine the CLI command contract in README.
- Do not change `tools/loom.py`, installer behavior, package versions, release tags, or publishing workflow behavior.
- Do not make root `VERSION`, npm package version, plugin version, skills/runtime contract version, or schema version globally synchronized.
