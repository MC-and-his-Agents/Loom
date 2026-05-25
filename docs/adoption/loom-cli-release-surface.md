# Loom CLI Release Surface

This document defines the release surface for the CLI-first Loom line after #1001.

## Authority

The `loom` CLI release line is the primary release line for Loom execution behavior.

| Surface | Authority | Published evidence |
| --- | --- | --- |
| Loom CLI release candidate | `VERSION` | A `v*` value that names the next root Loom CLI release candidate. |
| Published Loom CLI release | GitHub `v*` tag and GitHub Release | The tag must point at the release commit. Release notes must describe the CLI/runtime behavior being shipped or explicitly state that no CLI behavior changed. |
| Installer compatibility shim | `packages/loom-installer/package.json` | Published only as `@mc-and-his-agents/loom-installer` with `loom-installer-v<version>` tags. |

The `loom` CLI release line is not synchronized with the installer package version, plugin surface version, skill package version, runtime contract version, or schema version.

## Minimal Distribution Channel

The current minimal `loom` CLI distribution channel is the root GitHub release:

- `VERSION` declares the candidate version.
- A GitHub `v*` tag identifies the published source revision.
- The GitHub Release is the release evidence for `tools/loom.py`, `tools/loom_*.py`, `.loom/bin/`, generated `skills/`, and the CLI-backed runtime contracts committed in the repository.

This deliberately avoids introducing a new npm package, Homebrew formula, or standalone binary before there is a separate work item for that channel.

## Release Judgment

Every merge that touches CLI/runtime release behavior must receive a `loom` CLI release judgment.

CLI release behavior includes:

- `VERSION`
- `tools/loom.py`
- `tools/loom_*.py`
- `tools/check_cli_contract.py`
- `skills/shared/scripts/`
- `src/skills/`
- `skills/`
- `docs/adoption/loom-cli-release-surface.md`
- `.github/workflows/loom-cli-release.yml`

The judgment may be:

- `publish-required`: the current `VERSION` is not published and the release operator requested a publish run.
- `already-published-and-released`: the `VERSION` tag and release already point at the current release commit.
- `release-missing`: the tag exists and npm is irrelevant, but the GitHub Release is missing.
- `no-cli-behavior-change`: the merge did not touch CLI/runtime release behavior.

For pull requests and normal `main` pushes, the workflow records judgment only. Publishing requires an explicit `workflow_dispatch` run with publish enabled.

## Installer Freeze

`loom-installer` is a compatibility and legacy maintenance line. It is not the primary `loom` CLI release signal.

Installer releases are limited to:

- security fixes in the installer package,
- compatibility fixes for adapter-managed installs,
- migration or legacy bridge fixes,
- installer verification output fixes,
- bootstrap breakage fixes.

Changes to CLI behavior, generated skills, runtime contracts, plugin discovery, or docs must not be treated as installer npm publish evidence by themselves. They require `loom` CLI release judgment instead.

## Closeout Evidence

A release closeout for this line must record:

- `VERSION`,
- the relevant commit SHA,
- GitHub `v*` tag and Release state, or the no-publish reason,
- the `loom-cli-release` workflow run,
- whether `@mc-and-his-agents/loom-installer` was intentionally unchanged.

Closeout must not use `@mc-and-his-agents/loom-installer` `latest` or `loom-installer-v*` tags as proof that the `loom` CLI was published.
