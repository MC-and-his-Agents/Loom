# WI-1394 Spec

- Suite path: minimal
- Work Item / FR locator: #1394 / #1260
- Path decision provenance: issue #1394 scopes a bounded npm package validation surface split over an existing checker and requires concrete command evidence for manifest, payload, and aggregate behavior.

## Scope

Split `tools/check_npm_package.py` into targetable npm package manifest and packed payload validation surfaces while preserving the existing aggregate npm package check.

## Scenarios

- Scenario S1: `python3 tools/check_npm_package.py --surface npm-package-manifest` validates the root package manifest and reports `npm-package-manifest` evidence with locators for `package.json` and `VERSION`.
- Scenario S2: `python3 tools/check_npm_package.py --surface npm-pack-payload` validates the dry-run npm pack payload and reports `npm-pack-payload` evidence with locators for `package.json` and `npm pack --dry-run --json --ignore-scripts`.
- Scenario S3: `python3 tools/check_npm_package.py` remains an aggregate compatibility check that runs both manifest and payload validation and reports both evidence labels.

## Acceptance Criteria

- AC-1: Manifest validation is a stable targetable surface named `npm-package-manifest`.
- AC-2: Payload validation is a stable targetable surface named `npm-pack-payload`.
- AC-3: The no-argument aggregate npm package validator remains available and compatible with release/package validation consumers.
- AC-4: Manifest and payload failures emit stable `failed_layer`, `failure_label`, `evidence_label`, and `evidence_locators` fields.
- AC-5: #1383 release validation evidence labels are preserved without redefining release/no-release semantics or implementing #1393 release-surface scope.

## Full Suite Artifact Applicability

- Full suite artifacts not_applicable: rationale: WI-1394 is a narrow executable checker surface split with issue-authored acceptance criteria, minimal spec/plan coverage, existing release evidence labels, and direct command validation; separate suite-index, research, contracts, readiness-checklist, consistency-analysis, execution-breakdown, or full-suite artifact inventory would duplicate the issue and command evidence for this slice. consumer boundary: suite validate, review, merge-ready, PR gate, hosted CI, parent #1260 closeout, and release-required downstream work may consume this minimal suite plus PR metadata, command output, hosted checks, and scheduler-owned review/gate evidence; fact-chain, current-head review, PR metadata/readback, hosted checks, release/no-release judgment, controlled merge, and closeout evidence remain required. recheck condition: require a full suite if the scope expands into #1393 release validator splitting, #1395 installed/global CLI smoke, #1396 evidence convergence, release workflow semantics, npm publishing, package runtime behavior, external-visible release actions, or parent #1260/#1255 closeout.
