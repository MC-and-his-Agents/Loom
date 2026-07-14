# Loom CLI Release Surface

## Generated distribution boundary

Release and package jobs consume `tools/build_distribution.py` output. Python
runtime code is authored only under `src/skills`; npm `prepack` generates the
Codex plugin launchers and shared scripts, while `postpack` removes the ignored
materialized files. Package checks build the same payload in isolation, verify
its manifest digest and assert that the final npm artifact contains the plugin
entrypoints. `.loom/bin`, demo runtime and install/plugin Python copies are not
tracked release sources.

This document defines the release surface for the CLI-first Loom line after #1001.

## Authority

The `loom` CLI release line is the primary release line for Loom execution behavior.

| Surface | Authority | Published evidence |
| --- | --- | --- |
| Loom CLI release candidate | `VERSION` | A `v*` value that names the next root Loom CLI release candidate. |
| Published Loom CLI release | GitHub `v*` tag and GitHub Release | The tag must point at the release commit. Release notes must describe the CLI/runtime behavior being shipped or explicitly state that no CLI behavior changed. |
| Deprecated installer legacy artifact | npm `@mc-and-his-agents/loom-installer@0.1.119` / tag `loom-installer-v0.1.119` | Historical host evidence only; no installer tombstone remains in the source tree and this is not a current publish path. |

The `loom` CLI release line is the only active CLI release line. It is not synchronized with the deprecated installer package version, plugin surface version, skill contract version, runtime contract version, or schema version. The Codex plugin payload version follows the root Loom release because the payload is published inside the root `@mc-and-his-agents/loom` package, while the plugin surface version remains a separate host-interface compatibility line.

## Distribution Channel

The primary user-facing `loom` CLI distribution channel is the root npm package
plus matching GitHub release evidence:

- `VERSION` declares the candidate version.
- `package.json` publishes `@mc-and-his-agents/loom` with `loom` as the bin name.
- A GitHub `v*` tag identifies the published source revision.
- The GitHub Release is the release evidence for `tools/loom.py`, `tools/loom_*.py`, `.loom/bin/`, generated `skills/`, plugins, and the CLI-backed runtime contracts committed in the repository.
- npm registry state for `@mc-and-his-agents/loom` is the install-channel evidence for the root CLI package.

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

- `publish-required`: the current `VERSION` is not published as a GitHub `v*` tag and the matching npm package version is not present.
- `already-published-and-released`: the `VERSION` tag, GitHub Release, and npm package version already represent the current release commit.
- `release-missing`: the tag exists and npm package version is present, but the GitHub Release is missing.
- `npm-version-missing`: the tag points at the current release commit, but the matching npm package version is missing.
- `tag-release-missing-npm-version-exists`: the npm package version exists, but the matching GitHub tag and release evidence are missing.
- `release_pending`: a normal `main` push changed CLI behavior while the current `VERSION` tag already names an earlier release. It succeeds without publishing; a later release Work Item must merge a new, unoccupied candidate version.
- `version-already-published-on-different-commit`: an explicit `workflow_dispatch` publish request names a `VERSION` tag that points at another commit. The workflow must fail instead of overwriting history.
- `release-judgment-only`: CLI publish behavior changed on an event that is not allowed to publish; the workflow records the judgment and must not create tags, publish npm, or create releases.
- `no-cli-behavior-change`: the merge did not touch CLI publish behavior.

For pull requests, the read-only `release-judgment` job records judgment and runs npm package dry-run checks but must not create tags, publish npm, or create releases. It has only `contents: read`, no `id-token`, and no persisted checkout credential. The separate `release-publisher` job is never scheduled for pull requests. For `push` events on `main`, `loom-cli-release` automatically creates the GitHub `v*` tag, publishes `@mc-and-his-agents/loom` to npm, and creates the GitHub Release only when the root `VERSION` is a new, unoccupied candidate. A later CLI source merge with an already published version returns `release_pending` and never republishes that version. `workflow_dispatch` with `publish=true` remains a repair path for missing tag, npm, or release evidence bound to the current release commit, not the only publish path.

An explicit publish request must fail closed when CLI publish behavior changed but the current `VERSION` is already published on a different commit, when `package.json` does not match `VERSION`, or when the `NPM_TOKEN` secret is missing for an npm publish. A normal `main` push with an earlier published version returns `release_pending` instead. The workflow must never overwrite an existing tag, npm version, or release. Installer npm state is never publish evidence for this judgment.

## Release Resume Readback

`loom release readback` is the local read-only entry for a release intent. It
reads the target `VERSION`, matching GitHub `v*` tag, GitHub Release, npm
`@mc-and-his-agents/loom` package version, and the `loom-cli-release` workflow
run. It classifies the release state as:

- `unpublished`: no tag, GitHub Release, or npm package version exists for a release-required intent.
- `published`: tag, GitHub Release, npm package version, and workflow run read back consistently.
- `partial_published`: at least one release artifact exists but the release evidence set is incomplete or mismatched.
- `no_release`: the release judgment explicitly declares that no publish is required.

`loom release readback` returns the current classification and next recovery
action. It must not trigger `workflow_dispatch`, create tags, publish npm,
create GitHub Releases, update PR metadata, or write closeout carriers. Host API
or registry read failures are classified as readback blockers; auth and host-access diagnosis remains owned by #1597.

The v0.14.2 manual recovery sample is retained in
`docs/evidence/fixtures/release-readback-fixtures.json`: the first main-push
release run failed, and a later `workflow_dispatch` run restored tag,
GitHub Release, npm package, and workflow run readback for the same release
line.

## Release Validation Evidence Contract

This section records the release/package validation evidence contract that release-required work may consume after the #1383 evidence freeze and the #1393/#1394/#1395 checker surface split.

The labels below are stable evidence labels. Named release/package checks are targetable through `tools/check_release_surface.py` and `tools/check_npm_package.py`; the aggregate commands remain compatible when the retained validation summary names the label, the command, the current head or merge commit, and the result.

| Evidence label | Current compatible check | Required role |
| --- | --- | --- |
| `release-doc-contract` | `python3 tools/check_release_surface.py --surface release-doc-contract` | Proves release authority docs keep the `loom` CLI line, GitHub `v*` tag/Release, npm package, and deprecated installer boundary separated. |
| `release-workflow-contract` | `python3 tools/check_release_surface.py --surface release-workflow-contract` | Proves `loom-cli-release` keeps PR judgment read-only, main-push publishing, `workflow_dispatch` repair, fail-closed duplicate version handling, and `NPM_TOKEN` checks. |
| `installer-sunset-guard` | `python3 tools/check_release_surface.py --surface installer-sunset-guard` | Proves `loom-installer` remains deprecated legacy evidence and does not regain npm publish, installer tag, installer GitHub Release, or active CLI release authority. |
| `forbidden-release-surface-patterns` | `python3 tools/check_release_surface.py --surface forbidden-release-surface-patterns` | Proves active install/release docs do not present `loom-installer`, direct `SKILLS`, or host plugins as separate primary install or release evidence. |
| `npm-package-manifest` | `python3 tools/check_npm_package.py --surface npm-package-manifest` | Proves root `package.json` keeps `@mc-and-his-agents/loom`, the `loom` bin, version alignment with `VERSION`, public publish config, and required managed payload declarations. |
| `npm-pack-payload` | `python3 tools/check_npm_package.py --surface npm-pack-payload`, `npm pack --dry-run --json --ignore-scripts`, or `npm run test:package` when it consumes the same payload proof | Proves the dry-run package payload contains required CLI/runtime/docs/skills/plugin files and excludes repository-internal or deprecated installer surfaces. |
| `plugin-payload-hash` | `python3 tools/check_npm_package.py --surface plugin-payload-hash` | Proves the installable `plugins/loom` payload has a deterministic SHA-256 digest over sorted relative paths and bytes, ignoring OS/Python cache artifacts. |
| `installed-global-cli-smoke` | `python3 tools/check_release_surface.py --surface installed-global-cli-smoke` | Proves the packed package can be installed into a temporary global prefix, exposes the `loom` bin, and runs release-required version/help smoke from the installed package instead of only the source checkout. |

Aggregate release/package validation remains available through:

- `python3 tools/check_release_surface.py` or explicit `python3 tools/check_release_surface.py --surface aggregate-release-surface`, which runs the named release contract, workflow, installer sunset, forbidden-pattern, and installed/global CLI smoke surfaces.
- `python3 tools/check_npm_package.py` or explicit `python3 tools/check_npm_package.py --surface aggregate`, which runs the named `npm-package-manifest`, `npm-pack-payload`, and `plugin-payload-hash` surfaces.
- `npm run test:package`, when a release/package validation summary needs the packaged npm payload proof as well as the raw checker output.

All release validation evidence must retain:

- evidence label;
- command or hosted workflow step;
- result: `pass`, `block`, `not_applicable`, or explicit pending/failure classification;
- current PR head for pre-merge evidence, or merge commit for post-merge evidence;
- release version or `VERSION` value when the label is version-bound;
- run locator, transcript locator, or registry/API readback locator;
- failure summary and fallback when result is not `pass`.

Release-required downstream work may cite these labels without treating release/package validation as a single black-box bucket. Future #1260 closeout may refine output shape, but it must preserve these labels or provide an explicit compatibility alias before downstream release closeout consumes the split.

## Release-Required Closeout Evidence

When release-required work publishes a Loom CLI release, pre-merge evidence must show:

- the Work Item, branch, PR, current head, base, and parent release-required issue;
- the chosen `VERSION` and matching `package.json` npm version;
- plugin payload release metadata, `plugin_payload_hash`, `plugins/loom/skills/registry.json`, generated skills mirror, and skill `contract.json` surfaces synchronized when the release ships skills payload changes;
- target GitHub `v*` tag and npm `@mc-and-his-agents/loom` version are unoccupied before publish;
- `release-doc-contract`, `release-workflow-contract`, `installer-sunset-guard`, `forbidden-release-surface-patterns`, `npm-package-manifest`, `npm-pack-payload`, `plugin-payload-hash`, `installed-global-cli-smoke`, CLI contract, skills, and any issue-specific regression checks pass on the release PR head;
- PR-event `release-judgment-only`, if present, is recorded only as pre-merge judgment evidence and not as final release evidence.

Post-merge release closeout evidence must show:

- PR number, PR head, merge commit, target branch, and target branch readback;
- `loom-cli-release` run id or URL, event `push`, ref `main`, conclusion, and checked-out SHA bound to the merge commit;
- GitHub `vX.Y.Z` tag resolves to the merge commit;
- GitHub Release URL/state for the same tag;
- npm registry readback for `@mc-and-his-agents/loom@X.Y.Z`, including relevant dist-tag state;
- `installed-global-cli-smoke` command, package source, observed `loom` version output, behavior smoke result, and failure summary when blocked;
- installer non-advancement evidence when relevant: `@mc-and-his-agents/loom-installer` remains at the legacy baseline or only carries explicit deprecation metadata.

If release execution is unavailable, blocked, or partially complete, closeout must classify the gap as release evidence. It must not fold it into generic CI, PR, or host drift.

## No-Release Rationale Evidence

When a Work Item does not publish a release, closeout must record an explicit `no_release` rationale. The rationale is valid only when it states:

- the changed scope does not ship user-visible CLI, skills, package, workflow, release validation, npm payload, runtime provider, or external-visible behavior;
- `VERSION`, `package.json`, plugin payload registry/contract surfaces, release workflows, npm publish behavior, and package payload semantics were not changed, or any touched release-control docs/checks are contract-only and do not publish by themselves;
- release-surface validation that is relevant to the touched docs/checks passed or was intentionally not required with a recheck condition;
- PR-event `release-judgment-only` is not being used as final no-release proof;
- current head, PR, merge commit or target branch readback, review/gate status, and closeout evidence locator remain bound to the same Work Item.

No-release evidence does not replace current-head host attestation, PR binding,
hosted delivery gate, controlled merge, target branch readback, release
readback, or host-derived closeout.

For local cleanup after a completed delivery, the evidence must show:

- `workspace retire` remains local-only and does not write versioned carriers;
- host-derived closeout reads issue, PR, checks, merge commit, and target branch
  from GitHub;
- no repository closeout carrier, current pointer, progress, review, or shadow
  file is created or refreshed.

Release readiness checks must cover the user-facing command names and the
host-derived cleanup story so release/no-release closeout can distinguish
documentation/checker-only work from a CLI behavior shipment.

## Installer Sunset

`loom-installer` is a deprecated legacy artifact. It is not the `loom` CLI, not a recommended install path, and not the primary `loom` CLI release signal.

The final active legacy baseline is:

- GitHub Release / tag: `loom-installer-v0.1.119`
- npm package: `@mc-and-his-agents/loom-installer` `0.1.119`

The repository retains only private historical package metadata for readback.
There is no installer build, test, PR gate, release workflow, npm publish, tag,
or GitHub Release path. A later npm deprecation action may change registry
metadata without advancing the package version.

Changes to CLI behavior, generated skills, runtime contracts, plugin discovery, or docs must not be treated as installer npm publish evidence. They require `loom` CLI release judgment instead.

## Closeout Evidence

A release closeout for this line must record:

- `VERSION`,
- the relevant commit SHA,
- GitHub `v*` tag and Release state, or the no-publish reason,
- npm `@mc-and-his-agents/loom` version and dist-tag state, or the no-publish reason,
- the `loom-cli-release` workflow run,
- whether `@mc-and-his-agents/loom-installer` stayed at the legacy baseline or only changed deprecation metadata.

Closeout must not use `@mc-and-his-agents/loom-installer` `latest` or `loom-installer-v*` tags as proof that the `loom` CLI was published.
