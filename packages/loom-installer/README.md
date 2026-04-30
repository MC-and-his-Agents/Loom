# @mc-and-his-agents/loom-installer

Language: English | [中文版本](./README.zh-CN.md)

Loom npm / npx adapter helper and verifier.

The default Loom install model is full repository install plus native or host skill discovery. This package remains available for adapter-managed plugin installs, single-skill helper flows, and verification output.

## Commands

```bash
npx @mc-and-his-agents/loom-installer add plugin --host codex
npx @mc-and-his-agents/loom-installer add plugin --host claude
```

Single-skill compatibility path:

```bash
npx @mc-and-his-agents/loom-installer add skill <skill-id> --host codex
npx @mc-and-his-agents/loom-installer add skill <skill-id> --host claude
```

You can also pin the installer first:

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

## Release Notes

Publishing only happens from `main`.

Release model:

- PRs run gates but do not publish npm.
- `main` is the only release truth source.
- Loom repository releases and installer npm package versions are maintained separately.
- Create the `loom-installer-v<version>` git tag and matching GitHub Release only after npm publish succeeds.
