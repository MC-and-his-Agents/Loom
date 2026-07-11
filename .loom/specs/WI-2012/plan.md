# Plan

## Suite Contract

- Suite path consumed: minimal
- Spec locator: `.loom/specs/WI-2012/spec.md`
- Freshness: rerun package and release checks after any change to release surfaces.

## Implementation Goal

Publish the existing #2028 repair as v0.28.1 without changing its runtime semantics.

## Phases

### Phase 1

- Objective: align root version and plugin payload metadata.
- Exit condition: version and package validation pass.

### Phase 2

- Objective: merge the release PR and read back tag, release, npm package, and Harbor #246 gate.
- Exit condition: all distribution evidence is bound to the merge commit.

## Constraints

- The main-push release workflow owns npm publication, tags, and GitHub Release creation.
- No WebEnvoy repository, production browser, account, or external-site behavior changes.

## Validation

- `python3 tools/version_surface_check.py`
- `python3 -m unittest test.work_item_audit_test.WorkItemAuditTest.test_metadata_only_global_cli_refresh_skips_only_intentionally_absent_manifest`
- `python3 tools/check_release_surface.py --surface aggregate-release-surface`
- `python3 tools/check_npm_package.py --surface aggregate`
- `npm pack --dry-run --json --ignore-scripts`
- Post-merge: `loom release readback` and Harbor PR #246 hosted-gate readback.

## Scenario Mapping

- S1 -> automated validation: `python3 tools/version_surface_check.py`, `python3 tools/check_npm_package.py --surface aggregate`, `npm pack --dry-run --json --ignore-scripts`; post-merge tag, GitHub Release, and npm registry readback binds the published version to the merge commit.
- S2 -> manual hosted validation: after the published CLI is available, rerun and read Harbor PR #246 `loom-pr-merge-gate`; it must no longer require an intentionally absent bootstrap manifest for the metadata-only carrier refresh.

## Acceptance Mapping

- A1 -> test evidence: `python3 tools/version_surface_check.py` verifies `VERSION`, `package.json`, and plugin payload metadata.
- A2 -> test evidence: `python3 tools/check_npm_package.py --surface aggregate`, `python3 tools/check_release_surface.py --surface installed-global-cli-smoke`, and `npm pack --dry-run --json --ignore-scripts` verify package payload and installed CLI surface.
- A3 -> manual evidence: post-merge release workflow plus npm, tag, and GitHub Release readback identifies the merge commit and version.
- A4 -> manual evidence: current-head Harbor PR #246 hosted `loom-pr-merge-gate` readback after npm publication proves the downstream consumer has the repair.

## Ready For Review

- [x] Scope and non-goals are explicit.
- [x] Minimal-suite validation path is defined.
- [x] S1 and S2 map to package and hosted-gate evidence.
