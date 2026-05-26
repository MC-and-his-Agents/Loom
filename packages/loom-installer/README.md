# @mc-and-his-agents/loom-installer

Language: English | [中文版本](./README.zh-CN.md)

Deprecated Loom npm / npx adapter helper and verifier.

The default Loom install model is the root `loom` CLI package,
`@mc-and-his-agents/loom`, which installs, synchronizes, and verifies host
plugin/SKILLS payloads. This package is a deprecated legacy artifact kept only
for historical compatibility evidence and verification output. Do not use it as
the current Loom CLI or recommended install path.

## Historical Commands

These commands are retained only for existing legacy consumers and evidence
records. They are not a current install path:

```bash
npx @mc-and-his-agents/loom-installer add plugin --host codex
npx @mc-and-his-agents/loom-installer add plugin --host claude
```

Single-skill compatibility path:

```bash
npx @mc-and-his-agents/loom-installer add skill <skill-id> --host codex
npx @mc-and-his-agents/loom-installer add skill <skill-id> --host claude
```

Read-only upgrade rehearsal and verification:

```bash
npx @mc-and-his-agents/loom-installer upgrade-plan plugin --host codex --json
npx @mc-and-his-agents/loom-installer verify-upgrade plugin --host codex --json
```

Historical pinned installer usage:

```bash
npm install -D @mc-and-his-agents/loom-installer
npx loom-installer add plugin --host codex
```

Options:

- `--host codex|claude|auto`
- `--target <repo-root>`
- `--force`
- `--json`

## Requirements

- Node `>=20`
- Python `>=3.10`, recommended `3.11+`

## Payload Model

The published package includes a generated payload. The payload is generated from the canonical `plugins/loom/.codex-plugin/` manifest and the checked-in generated `skills/` install surface during build, pack, and publish.

Generated payload directories are not committed to git. The build step recreates them deterministically, and `check:payload` verifies rebuild stability. The root `skills/` surface itself is committed and verified with `check:distribution`.

Installer JSON output reports `distribution_layer`, `version_context`, and `failed_layer` so callers can distinguish host adapter plugin installs from generated single-skill installs.

Installer-managed layers also write `loom-installed-surface-status/v1` metadata. `upgrade-plan` and `verify-upgrade` read that metadata, compare it to the package payload, and report `upgrade_eligibility`, `changed_paths`, `drift`, `rollback_path`, and fail-closed reasons without mutating the target repository. See `docs/adoption/installed-loom-status.md` for the status contract.

## Release Notes

The installer package is sunset. `main` validation can still inspect the package and legacy registry state, but it must not publish npm, create `loom-installer-v*` tags, or create installer GitHub Releases.

Release model:

- PRs run gates but do not publish npm.
- `main` is the validation truth source for the deprecated installer artifact.
- Loom repository releases and installer npm package versions are maintained separately.
- `loom` CLI releases use root `VERSION` plus GitHub `v*` tags and Releases; installer `latest` is not CLI release evidence.
- The last active installer baseline is `@mc-and-his-agents/loom-installer` `0.1.119` / `loom-installer-v0.1.119`.
- A later npm deprecation action may change registry metadata without advancing the package version.
