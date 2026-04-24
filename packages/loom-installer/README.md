# @mc-and-his-agents/loom-installer

Language: English | [中文版本](./README.zh-CN.md)

Loom npm / npx installer.

The primary install mode is the complete Loom plugin surface. Single-skill install remains available for compatibility and advanced use.

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

The published package includes a generated payload. The payload is generated from the canonical root `.codex-plugin/` and `skills/` sources during build, pack, and publish.

Generated payload directories are not committed to git. The build step recreates them deterministically, and `check:payload` verifies rebuild stability.

## Release Notes

Publishing only happens from `main`.

Release model:

- PRs run gates but do not publish npm.
- `main` is the only release truth source.
- Loom repository releases and installer npm package versions are maintained separately.
- Create the `loom-installer-v<version>` git tag and matching GitHub Release only after npm publish succeeds.
