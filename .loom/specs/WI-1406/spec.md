# WI-1406 Spec

- Suite path: minimal
- Work Item: WI-1406
- Parent: #1263

## Suite Contract

- Full-suite-artifacts not_applicable: rationale: WI-1406 is a narrow runtime regression surface split limited to subprocess environment purity diagnostics in `tools/check_loom_check_runtime_regressions.py` and a Makefile alias; consumer boundary: suite validate, implementation review, merge-ready, PR gate, hosted checks, and issue closeout consume this minimal suite plus PR/local validation evidence; recheck condition: require full suite artifacts if the work expands into locking semantics, tempdir cleanup, fixture cleanliness, hosted workflow policy, release/package behavior, or broad `loom_check` runtime behavior.

## Goal

Split subprocess environment purity validation into a named, targetable runtime regression surface while preserving the merged #1405 locking surfaces and the aggregate runtime regression entrypoint.

## Scope

- Add a selectable `subprocess-env-purity` runtime regression surface.
- Emit stable failure evidence locators for default subprocess environment stripping, default env probe inheritance, explicit env fixture probe, and explicit fixture preservation failures.
- Keep `make loom-check-runtime-regression` fail-closed and aggregate.
- Preserve #1405 locking surface names, fixture group, failure labels, and Makefile aliases.
- Keep tempdir cleanup and demo fixture cleanliness in aggregate validation without making them WI-1406 named surfaces.
- Exclude #1407 tempdir cleanup / fixture cleanliness split, #1408 aggregate closeout, parent #1263 closeout, release/package behavior, broad runtime behavior changes, and external-visible behavior.

## Scenarios

### Scenario S1 Subprocess Env Purity Surface

Given host-only Codex, GitHub token, and Loom runtime variables are present in the parent process,
When `subprocess-env-purity` runs,
Then the default subprocess environment strips host-only variables, explicit fixture env injection remains preserved, and any failure reports `surface=subprocess-env-purity`, `fixture_group=environment-purity`, and an `evidence_locator=...` value.

### Scenario S2 Locking Surface Preservation

Given the merged #1405 runtime locking surfaces,
When the single-flight, worktree-local lock path, installer lock output, and locking fixture group targets run,
Then their surface names, fixture group `locking`, and existing busy-owner diagnostics remain unchanged.

### Scenario S3 Aggregate Runtime Regression

Given no surface filter,
When `tools/check_loom_check_runtime_regressions.py` or `make loom-check-runtime-regression` runs,
Then all runtime regression surfaces still run and any surface failure fails the aggregate command.

## Acceptance

- AC-1: `--list-surfaces` lists `subprocess-env-purity` with fixture group `environment-purity`.
- AC-2: Makefile exposes `loom-check-runtime-subprocess-env-purity`.
- AC-3: Subprocess environment purity failures include `surface=subprocess-env-purity`, `fixture_group=environment-purity`, and stable `evidence_locator=...` diagnostics.
- AC-4: The #1405 locking targets and `--fixture-group locking` continue to pass without renamed surfaces or fixture groups.
- AC-5: Aggregate runtime regression remains available through `make loom-check-runtime-regression` and remains fail-closed.
- AC-6: Validation leaves no tracked-file mutation outside the intended diff, no loom_check lock residue, no installer lock residue, and no new loom-check temporary directories.
