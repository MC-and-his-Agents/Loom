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
- `version-already-published-on-different-commit`: CLI publish behavior changed but the current `VERSION` tag already points at another commit; the workflow must fail instead of overwriting history.
- `release-judgment-only`: CLI publish behavior changed on an event that is not allowed to publish; the workflow records the judgment and must not create tags, publish npm, or create releases.
- `no-cli-behavior-change`: the merge did not touch CLI publish behavior.

For pull requests, the workflow records judgment and runs npm package dry-run checks but must not create tags, publish npm, or create releases. For `push` events on `main`, `loom-cli-release` automatically creates the GitHub `v*` tag, publishes `@mc-and-his-agents/loom` to npm, and creates the GitHub Release when CLI publish behavior changed and the root `VERSION` is an unpublished candidate. `workflow_dispatch` with `publish=true` remains a repair path for missing tag, npm, or release evidence, not the only publish path.

When publishing is allowed or explicitly requested, the workflow must fail closed when CLI publish behavior changed but the current `VERSION` is already published on a different commit, when `package.json` does not match `VERSION`, or when the `NPM_TOKEN` secret is missing for an npm publish. It must never overwrite an existing tag, npm version, or release. Installer npm state is never publish evidence for this judgment.

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
| `installed-global-cli-smoke` | `python3 tools/check_release_surface.py --surface installed-global-cli-smoke` | Proves the packed package can be installed into a temporary global prefix, exposes the `loom` bin, and runs release-required version/help smoke from the installed package instead of only the source checkout. |

Aggregate release/package validation remains available through:

- `python3 tools/check_release_surface.py` or explicit `python3 tools/check_release_surface.py --surface aggregate-release-surface`, which runs the named release contract, workflow, installer sunset, forbidden-pattern, and installed/global CLI smoke surfaces.
- `python3 tools/check_npm_package.py` or explicit `python3 tools/check_npm_package.py --surface aggregate`, which runs the named `npm-package-manifest` and `npm-pack-payload` surfaces.
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
- generated `skills/*/loom-package.json` repo version surfaces synchronized when the release ships generated skills/runtime payloads;
- target GitHub `v*` tag and npm `@mc-and-his-agents/loom` version are unoccupied before publish;
- `release-doc-contract`, `release-workflow-contract`, `installer-sunset-guard`, `forbidden-release-surface-patterns`, `npm-package-manifest`, `npm-pack-payload`, `installed-global-cli-smoke`, CLI contract, skills, and any issue-specific regression checks pass on the release PR head;
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
- `VERSION`, `package.json`, generated `skills/*/loom-package.json`, release workflows, npm publish behavior, and package payload semantics were not changed, or any touched release-control docs/checks are contract-only and do not publish by themselves;
- release-surface validation that is relevant to the touched docs/checks passed or was intentionally not required with a recheck condition;
- PR-event `release-judgment-only` is not being used as final no-release proof;
- current head, PR, merge commit or target branch readback, review/gate status, and closeout evidence locator remain bound to the same Work Item.

No-release evidence does not replace review, fact-chain, PR metadata preflight, hosted checks, controlled merge, target branch readback, reconciliation audit, or closeout.

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
- npm `@mc-and-his-agents/loom` version and dist-tag state, or the no-publish reason,
- the `loom-cli-release` workflow run,
- whether `@mc-and-his-agents/loom-installer` stayed at the legacy baseline or only changed deprecation metadata.

Closeout must not use `@mc-and-his-agents/loom-installer` `latest` or `loom-installer-v*` tags as proof that the `loom` CLI was published.
