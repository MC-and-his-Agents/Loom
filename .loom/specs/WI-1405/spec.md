# WI-1405 Spec

- Suite path: minimal
- Work Item: WI-1405
- Parent: #1263

## Suite Contract

- Full-suite-artifacts not_applicable: rationale: WI-1405 is a narrow runtime regression surface split limited to the existing `tools/check_loom_check_runtime_regressions.py` locking checks and Makefile aliases; consumer boundary: suite validate, implementation review, merge-ready, PR gate, hosted checks, and issue closeout consume this minimal suite plus PR/local validation evidence; recheck condition: require full suite artifacts if the work expands into subprocess environment purity, tempdir cleanup, demo fixture cleanliness semantics, hosted workflow policy, release/package behavior, or broad `loom_check` runtime behavior changes.

## Goal

Split runtime locking validation into named surfaces for same-worktree single-flight locking, worktree-local lock paths, and installer regression lock output while preserving the aggregate runtime regression entrypoint.

## Scope

- Add selectable locking runtime regression surfaces for:
  - `single-flight-locking`
  - `worktree-local-lock-paths`
  - `installer-regression-lock-output`
- Keep `make loom-check-runtime-regression` fail-closed and aggregate.
- Keep existing environment purity, demo fixture cleanliness, and tempdir cleanup checks in aggregate validation without making them the WI-1405 named surfaces.
- Exclude #1406 subprocess environment purity split, #1407 tempdir cleanup / fixture cleanliness split, and #1408 aggregate closeout.

## Scenarios

### Scenario S1 Single-Flight Locking Surface

Given a synthetic existing loom_check owner lock in the current worktree,
When `single-flight-locking` runs,
Then the second loom_check invocation fails fast with exit status `3` and diagnostics that include owner and fallback fields.

### Scenario S2 Worktree-Local Lock Paths Surface

Given two distinct temporary worktree roots,
When `worktree-local-lock-paths` runs,
Then each root resolves to a different loom_check lock path and the locks are released.

### Scenario S3 Installer Regression Lock Output Surface

Given a synthetic package-root installer regression lock owner,
When `installer-regression-lock-output` runs,
Then the installer regression fails closed and emits owner diagnostics plus a recovery fallback.

### Scenario S4 Aggregate Runtime Regression

Given no surface filter,
When `tools/check_loom_check_runtime_regressions.py` or `make loom-check-runtime-regression` runs,
Then all existing runtime regression checks still run and any surface failure fails the aggregate command.

## Acceptance

- AC-1: `--list-surfaces` lists the three WI-1405 locking surfaces and does not promote #1406/#1407 surfaces as selectable WI-1405 outputs.
- AC-2: Makefile exposes stable targets for the locking group and each locking surface.
- AC-3: Runtime regression output includes `surface=<name>` and `fixture_group=locking` diagnostics for locking surface start/end/failure lines.
- AC-4: Aggregate runtime regression remains available through `make loom-check-runtime-regression` and remains fail-closed.
- AC-5: Validation leaves no tracked-file mutation or lock residue.
