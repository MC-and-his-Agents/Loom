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

#1063 introduces that separate npm channel work. Its frozen install and package
contract is [cli-only-install-contract.md](./cli-only-install-contract.md): the
root `loom` CLI is the only primary user-facing install surface, and the target
npm package is `@mc-and-his-agents/loom` with `loom` as the bin name.

## Release Judgment

Every merge that touches CLI/runtime release behavior must receive a `loom` CLI release judgment.

CLI publish behavior includes:

- `VERSION`
- `tools/loom.py`
- `tools/loom_*.py`
- `skills/shared/scripts/`
- `src/skills/`
- `skills/`

CLI release-control behavior also receives release-surface checks but does not create a release by itself:

- `tools/check_cli_contract.py`
- `docs/adoption/loom-cli-release-surface.md`
- `.github/workflows/loom-cli-release.yml`

The judgment may be:

- `publish-required`: the current `VERSION` is not published and CLI publish behavior changed.
- `already-published-and-released`: the `VERSION` tag and release already point at the current release commit.
- `release-missing`: the tag exists and npm is irrelevant, but the GitHub Release is missing.
- `version-already-published-on-different-commit`: CLI publish behavior changed but the current `VERSION` tag already points at another commit; the workflow must fail instead of overwriting history.
- `no-cli-behavior-change`: the merge did not touch CLI publish behavior.

For pull requests, the workflow records judgment but must not create tags or releases. For `push` events on `main`, `loom-cli-release` automatically creates the GitHub `v*` tag and GitHub Release when CLI publish behavior changed and the root `VERSION` is an unpublished candidate. `workflow_dispatch` with `publish=true` remains a repair path for missing tag/release evidence, not the only publish path.

The workflow must fail closed when CLI publish behavior changed but the current `VERSION` is already published on a different commit. It must never overwrite an existing tag or release. Installer npm state is never publish evidence for this judgment.

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
