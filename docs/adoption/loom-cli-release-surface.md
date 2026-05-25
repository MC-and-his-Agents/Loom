# Loom CLI Release Surface

This document defines the release surface for the CLI-first Loom line after #1001.

## Authority

The `loom` CLI release line is the primary release line for Loom execution behavior.

| Surface | Authority | Published evidence |
| --- | --- | --- |
| Loom CLI release candidate | `VERSION` | A `v*` value that names the next root Loom CLI release candidate. |
| Published Loom CLI release | GitHub `v*` tag and GitHub Release | The tag must point at the release commit. Release notes must describe the CLI/runtime behavior being shipped or explicitly state that no CLI behavior changed. |
| Deprecated installer legacy artifact | `packages/loom-installer/package.json` | Historical evidence only. The last active release baseline is `@mc-and-his-agents/loom-installer` `0.1.119` / `loom-installer-v0.1.119`; it is not a current publish path. |

The `loom` CLI release line is the only active CLI release line. It is not synchronized with the deprecated installer package version, plugin surface version, skill package version, runtime contract version, or schema version.

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

For pull requests and normal `main` pushes, the workflow records judgment only until #1008 enables automatic `loom` CLI publishing. Installer npm state is never publish evidence for this judgment.

## Installer Sunset

`loom-installer` is a deprecated legacy artifact. It is not the `loom` CLI, not a recommended install path, and not the primary `loom` CLI release signal.

The final active legacy baseline is:

- GitHub Release / tag: `loom-installer-v0.1.119`
- npm package: `@mc-and-his-agents/loom-installer` `0.1.119`

After #1005, the `node-installer-release` workflow keeps validation and read-only legacy evidence but must not publish npm, create `loom-installer-v*` tags, or create installer GitHub Releases. A later npm deprecation action may change registry metadata without advancing the package version.

Changes to CLI behavior, generated skills, runtime contracts, plugin discovery, or docs must not be treated as installer npm publish evidence. They require `loom` CLI release judgment instead.

## Closeout Evidence

A release closeout for this line must record:

- `VERSION`,
- the relevant commit SHA,
- GitHub `v*` tag and Release state, or the no-publish reason,
- the `loom-cli-release` workflow run,
- whether `@mc-and-his-agents/loom-installer` stayed at the legacy baseline or only changed deprecation metadata.

Closeout must not use `@mc-and-his-agents/loom-installer` `latest` or `loom-installer-v*` tags as proof that the `loom` CLI was published.
