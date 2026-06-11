# WI-1396 Spec

- Suite path: minimal
- Work Item / FR locator: #1396 / #1260
- Path decision provenance: issue #1396 scopes a bounded docs/evidence convergence slice after #1383 froze release evidence labels and #1393/#1394/#1395 implemented targetable release/package validation surfaces.

## Suite Contract

- Full-suite-artifacts not_applicable: rationale: WI-1396 is a docs/evidence convergence slice that updates concise release/package evidence references and proves aggregate release/package validation remains available using existing checkers; consumer boundary: suite validate, implementation review, merge-ready, PR gate, hosted CI, parent #1260 closeout, and umbrella #1255 closeout consume this minimal suite plus command, PR metadata, and hosted check evidence; recheck condition: require full suite artifacts if scope expands into checker behavior, Makefile behavior, release workflow semantics, npm publish behavior, VERSION/package payload changes, runtime behavior, external-visible release actions, parent #1260 closeout, or umbrella #1255 closeout.

## Scope

Update release/package docs and evidence references so downstream release-required work can consume the named surfaces without treating release/package validation as one black-box bucket.

## Scenarios

### Scenario S1 Release Surface Readback

Given the merged #1393 and #1395 release surface split,
When `python3 tools/check_release_surface.py --list-surfaces` runs,
Then the output includes `aggregate-release-surface`, `release-doc-contract`, `release-workflow-contract`, `installer-sunset-guard`, `forbidden-release-surface-patterns`, and `installed-global-cli-smoke`.

### Scenario S2 Aggregate Release Evidence

Given the release surface split is targetable,
When `python3 tools/check_release_surface.py --surface aggregate-release-surface --show-surface-evidence` runs,
Then the aggregate release validation remains available and prints evidence for the named release surfaces.

### Scenario S3 Package Surface Readback

Given the merged #1394 package surface split,
When `python3 tools/check_npm_package.py --list-surfaces` and `python3 tools/check_npm_package.py` run,
Then the output exposes `aggregate`, `npm-package-manifest`, and `npm-pack-payload`, and the aggregate package validation reports both package evidence labels.

### Scenario S4 Evidence Reference Convergence

Given #1396 is docs/evidence only,
When release/package evidence references are updated,
Then they point to the named surface commands and retained aggregate commands without redefining release/no-release semantics or closing #1260/#1255.

## Acceptance Criteria

- AC-1: Release docs identify targetable release and package surfaces plus aggregate compatibility commands.
- AC-2: Evidence docs consume #1383/#1393/#1394/#1395 names and prove aggregate release/package validation remains available.
- AC-3: Closeout guidance distinguishes named surface evidence from aggregate evidence and requires label/head/run locator/consumer boundary when aggregate evidence is used.
- AC-4: Local validation proves the aggregate release and npm package commands remain available.
- AC-5: The diff stays within docs/evidence references and WI-1396 carriers; it does not change checker behavior, release semantics, package payload, workflow behavior, VERSION, tags, npm publish, parent #1260 closeout, or umbrella #1255 closeout.
