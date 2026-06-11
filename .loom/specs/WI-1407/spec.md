# WI-1407 Spec

- Suite path: minimal
- Work Item: WI-1407
- Parent: #1263

## Suite Contract

- Full-suite-artifacts not_applicable: rationale: WI-1407 is a narrow runtime regression surface split limited to tempdir cleanup and demo fixture cleanliness diagnostics in `tools/check_loom_check_runtime_regressions.py` plus Makefile aliases; consumer boundary: suite validate, implementation review, merge-ready, PR gate, hosted checks, and issue closeout consume this minimal suite plus PR/local validation evidence; recheck condition: require full suite artifacts if the work expands into locking semantics, subprocess environment purity, demo bootstrap generation/drift/canonicalization under #1262, hosted workflow policy, release/package behavior, or broad `loom_check` runtime behavior.

## Goal

Split tempdir cleanup and demo fixture cleanliness validation into named, targetable runtime regression surfaces while preserving the merged #1405 locking surfaces, #1406 subprocess environment purity surface, and the aggregate runtime regression entrypoint.

## Scope

- Add selectable runtime regression surfaces:
  - `temp-dir-cleanup`
  - `demo-fixture-cleanliness`
- Emit stable `failure_label=...` and `evidence_locator=...` diagnostics for tempdir cleanup residue and demo fixture cleanliness failures.
- Keep `make loom-check-runtime-regression` fail-closed and aggregate.
- Preserve #1405 locking surface names, fixture group, busy-owner diagnostics, and Makefile aliases.
- Preserve #1406 `subprocess-env-purity` surface name, fixture group, evidence locators, and Makefile alias.
- Exclude demo bootstrap generation/drift/canonicalization surface work under #1262, #1408 aggregate closeout, parent #1263/#1255 closeout, release/package behavior, broad runtime behavior changes, and external-visible behavior.

## Scenarios

### Scenario S1 Tempdir Cleanup Surface

Given runtime regression checks create loom_check temporary directories only within their execution window,
When `temp-dir-cleanup` runs,
Then new `loom-check-*` temp directories created after the baseline are detected as failures and reported with `surface=temp-dir-cleanup`, `fixture_group=tempdir-cleanup`, `failure_label=tempdir-cleanup-residue`, and an `evidence_locator=...` value.

### Scenario S2 Demo Fixture Cleanliness Surface

Given the demo bootstrap fixture starts with its current tracked-file status,
When `demo-fixture-cleanliness` runs,
Then the check remains non-mutating for `examples/new-project` and any status-read, checker, or tracked-drift failure reports `surface=demo-fixture-cleanliness`, `fixture_group=fixture-cleanliness`, `failure_label=...`, and an `evidence_locator=...` value.

### Scenario S3 Runtime Surface Preservation

Given the merged #1405 locking surfaces and #1406 subprocess environment purity surface,
When targeted and aggregate runtime regression commands run,
Then their existing names, fixture groups, diagnostics, and Makefile aliases remain available and the aggregate runtime regression command still runs all surfaces fail-closed.

## Acceptance

- AC-1: `--list-surfaces` lists `temp-dir-cleanup` with fixture group `tempdir-cleanup`.
- AC-2: `--list-surfaces` lists `demo-fixture-cleanliness` with fixture group `fixture-cleanliness`.
- AC-3: Makefile exposes `loom-check-runtime-temp-dir-cleanup` and `loom-check-runtime-demo-fixture-cleanliness`.
- AC-4: Tempdir cleanup failures include `surface=temp-dir-cleanup`, `fixture_group=tempdir-cleanup`, `failure_label=tempdir-cleanup-residue`, and a stable `evidence_locator=...` diagnostic.
- AC-5: Demo fixture cleanliness failures include `surface=demo-fixture-cleanliness`, `fixture_group=fixture-cleanliness`, `failure_label=...`, and stable `evidence_locator=...` diagnostics.
- AC-6: The #1405 locking targets and #1406 subprocess-env-purity target continue to pass without renamed surfaces or fixture groups.
- AC-7: Aggregate runtime regression remains available through `make loom-check-runtime-regression` and remains fail-closed.
- AC-8: Validation leaves no tracked-file mutation outside the intended diff, no loom_check lock residue, no installer lock residue, and no new `loom-check-*` temporary directories.
