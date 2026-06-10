# WI-1405 Implementation Contract

- Work Item: WI-1405
- Issue: #1405
- PR: #1418
- Branch: work/1405-runtime-locking-validation-surfaces

## Work Item

WI-1405 implements the runtime locking validation surface split for the existing runtime regression checker.

The execution entrypoints are:

- `tools/check_loom_check_runtime_regressions.py`
- `make loom-check-runtime-locking`
- `make loom-check-runtime-single-flight-locking`
- `make loom-check-runtime-worktree-local-lock-paths`
- `make loom-check-runtime-installer-regression-lock-output`
- `make loom-check-runtime-regression`

## Approved Spec

This implementation consumes:

- `.loom/specs/WI-1405/spec.md`
- `.loom/specs/WI-1405/plan.md`

The scheduler-owned spec and implementation review records are retained under `.loom/reviews/` and must bind to the current PR head or be accepted by gate as carrier-only drift.

## Implementation Scope

This implementation covers:

- selectable runtime locking surfaces:
  - `single-flight-locking`
  - `worktree-local-lock-paths`
  - `installer-regression-lock-output`
- `--surface` and `--fixture-group locking` selection in `tools/check_loom_check_runtime_regressions.py`
- aggregate runtime regression preservation through the default checker and `make loom-check-runtime-regression`
- Makefile targets for the locking group and each locking surface
- WI-1405 Loom progress, work-item, review, status, and PR metadata carriers

This implementation does not cover:

- #1406 subprocess environment purity split
- #1407 tempdir cleanup or demo fixture cleanliness split
- #1408 aggregate runtime evidence closeout
- release/package validation behavior
- skills validation behavior
- demo bootstrap behavior
- external-visible runtime behavior

## Validation Plan

Required validation before merge-ready consumption:

- `git diff --check`
- `python3 tools/check_loom_check_runtime_regressions.py --list-surfaces`
- `python3 tools/py_compile_clean.py tools/check_loom_check_runtime_regressions.py`
- `python3 tools/loom.py suite inspect --target . --item WI-1405 --json`
- `python3 tools/loom.py suite validate --target . --item WI-1405 --json`
- `make loom-check-runtime-single-flight-locking`
- `make loom-check-runtime-worktree-local-lock-paths`
- `make loom-check-runtime-installer-regression-lock-output`
- `make loom-check-runtime-locking`
- `make loom-check-runtime-regression`
- PR metadata preflight for PR #1418 and the current head
- hosted required checks on the current head
- scheduler-owned PR gate and controlled merge check

Validation must leave no lock residue at `.loom/runtime/loom_check.lock` or `packages/loom-installer/.installer-regression-lock`.

## Risks And Rollback

Primary risks:

- selector drift could make the aggregate runtime regression omit an existing check
- Makefile target drift could hide a selectable locking surface
- lock checks could leave residue that affects later validation

Rollback boundary:

- revert the WI-1405 commits on PR #1418
- restore the aggregate checker-only behavior in `tools/check_loom_check_runtime_regressions.py`
- remove the WI-1405 Makefile locking aliases and Loom carriers if the PR is abandoned

## Host Binding

The implementation binds to:

- issue #1405
- PR #1418
- branch `work/1405-runtime-locking-validation-surfaces`

The PR body machine carrier must name the exact branch and current `head_sha`. If any commit changes the head, PR metadata preflight, hosted checks, review head binding, PR gate, and controlled merge check must be refreshed.
