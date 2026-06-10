# WI-1394 Plan

- Suite path: minimal

## Implementation

1. Refactor `tools/check_npm_package.py` so manifest checks and dry-run payload checks are separate functions with stable surface names.
2. Add CLI targeting through `--surface npm-package-manifest`, `--surface npm-pack-payload`, and a read-only surface discovery command.
3. Keep no-argument `python3 tools/check_npm_package.py` as the aggregate compatibility check that runs both surfaces.
4. Add narrowly named Makefile targets for the manifest and payload package checks.
5. Bind WI-1394 progress and PR metadata to the final head, then stop for scheduler-owned gate.

## Validation Mapping

- S1 -> automated validation evidence: `python3 tools/check_npm_package.py --surface npm-package-manifest` and `make npm-package-manifest-check`.
- S2 -> automated validation evidence: `python3 tools/check_npm_package.py --surface npm-pack-payload` and `make npm-pack-payload-check`.
- S3 -> automated validation evidence: `python3 tools/check_npm_package.py`, `make npm-package-check`, and `npm run test:package`.
- AC-1 -> structural and command evidence: `python3 tools/check_npm_package.py --list-surfaces` lists `npm-package-manifest`.
- AC-2 -> structural and command evidence: `python3 tools/check_npm_package.py --list-surfaces` lists `npm-pack-payload`.
- AC-3 -> test evidence: the aggregate validator keeps schema `loom-npm-package-check/v1`, returns `result: pass`, and reports both evidence labels.
- AC-4 -> structural check: targeted and aggregate failure handlers include `failed_layer`, `failure_label`, `evidence_label`, and `evidence_locators`.
- AC-5 -> manual evidence: changed files remain limited to npm package checker surfaces, Makefile targets, and WI-1394 carriers; no release workflow, publish, VERSION, tag, runtime smoke, or #1393 release-surface semantics change.

## Minimal Path Applicability Records

- full-path-artifacts not_applicable rationale: WI-1394 is bounded to an existing package checker split and can be verified through focused command outputs, Makefile targets, aggregate compatibility, npm package smoke tests, PR metadata, and hosted checks. consumer boundary: suite validate, review, merge-ready, PR gate, hosted CI, parent #1260 closeout, and release-required downstream work consume this minimal spec/plan plus command and PR evidence; fact-chain, current-head review, release/no-release judgment, controlled merge, and closeout remain separately required. recheck condition: require a full suite if scope expands into release workflow semantics, npm publish behavior, installed/global CLI smoke, package runtime behavior, external-visible actions, #1393/#1395/#1396 scope, or parent #1260/#1255 closeout.

## Deferred Items

- #1393 release validator split remains out of scope. Statement: deferred is not completed.
- #1395 installed/global CLI smoke remains out of scope. Statement: deferred is not completed.
- #1396 docs/evidence convergence remains out of scope. Statement: deferred is not completed.
- Parent #1260 and umbrella #1255 closeout remain scheduler-owned/out of scope. Statement: deferred is not completed.
