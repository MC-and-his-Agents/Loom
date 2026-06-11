# WI-1406 Implementation Contract

- Work Item: WI-1406
- Issue: #1406
- PR: #1433
- Branch: work/1406-runtime-env-purity-surface

## Work Item

WI-1406 implements the subprocess environment purity validation surface split for the existing runtime regression checker.

The execution entrypoints are:

- `tools/check_loom_check_runtime_regressions.py`
- `make loom-check-runtime-subprocess-env-purity`
- `make loom-check-runtime-locking`
- `make loom-check-runtime-regression`

## Approved Spec

This implementation consumes:

- `.loom/specs/WI-1406/spec.md`
- `.loom/specs/WI-1406/plan.md`

The scheduler-owned spec and implementation review records are retained under `.loom/reviews/` and must bind to the current PR head or be accepted by gate as carrier-only drift.

## Implementation Scope

This implementation covers:

- selectable runtime subprocess environment purity surface:
  - `subprocess-env-purity`
- fixture group `environment-purity` for subprocess environment purity diagnostics
- stable evidence locators for default subprocess environment stripping, default env probe inheritance, explicit env fixture probe, and explicit fixture preservation failures
- aggregate runtime regression preservation through the default checker and `make loom-check-runtime-regression`
- Makefile target for the subprocess environment purity surface
- WI-1406 Loom progress, work-item, review, status, suite, and PR metadata carriers

This implementation does not cover:

- #1405 locking surface rename or semantic rewrite
- #1407 tempdir cleanup or demo fixture cleanliness split
- #1408 aggregate runtime evidence closeout
- parent #1263 closeout
- release/package validation behavior
- skills validation behavior
- demo bootstrap behavior
- hosted workflow policy, permissions, or external-visible runtime behavior

## Validation Plan

Required validation before merge-ready consumption:

- `git diff --check`
- `python3 tools/check_loom_check_runtime_regressions.py --list-surfaces`
- `python3 tools/py_compile_clean.py tools/check_loom_check_runtime_regressions.py`
- `python3 tools/loom.py suite inspect --target . --item WI-1406 --json`
- `python3 tools/loom.py suite validate --target . --item WI-1406 --json`
- `python3 tools/loom.py suite evidence validate --target . --item WI-1406 --json`
- `python3 tools/loom.py suite carrier validate --target . --item WI-1406 --json`
- `make loom-check-runtime-subprocess-env-purity`
- `make loom-check-runtime-locking`
- `make loom-check-runtime-regression`
- PR metadata preflight for PR #1433 and the current head
- hosted required checks on the current head
- scheduler-owned PR gate and controlled merge check

Validation must leave no lock residue at `.loom/runtime/loom_check.lock`, `packages/loom-installer/.installer-regression-lock`, or new `loom-check-*` temporary directories.

## Risks And Rollback

Primary risks:

- selector drift could make aggregate runtime regression omit environment purity checks
- Makefile target drift could hide the selectable environment purity surface
- environment fixture checks could accidentally inherit host-only variables or mutate runtime state

Rollback boundary:

- revert the WI-1406 commits on PR #1433
- restore the aggregate checker behavior in `tools/check_loom_check_runtime_regressions.py`
- remove the WI-1406 Makefile alias and Loom carriers if the PR is abandoned

## Host Binding

The implementation binds to:

- issue #1406
- PR #1433
- branch `work/1406-runtime-env-purity-surface`

The PR body machine carrier must name the exact branch and current `head_sha`. If any commit changes the head, PR metadata preflight, hosted checks, review head binding, PR gate, and controlled merge check must be refreshed.
