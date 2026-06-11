# WI-1407 Implementation Contract

- Work Item: WI-1407
- Issue: #1407
- PR: pending
- Branch: `work/1407-tempdir-cleanup-fixture-cleanliness`

## Work Item

WI-1407 implements the tempdir cleanup and demo fixture cleanliness validation surface split for the existing runtime regression checker.

The execution entrypoints are:

- `tools/check_loom_check_runtime_regressions.py`
- `make loom-check-runtime-temp-dir-cleanup`
- `make loom-check-runtime-demo-fixture-cleanliness`
- `make loom-check-runtime-locking`
- `make loom-check-runtime-subprocess-env-purity`
- `make loom-check-runtime-regression`

## Approved Spec

This implementation consumes:

- `.loom/specs/WI-1407/spec.md`
- `.loom/specs/WI-1407/plan.md`

Scheduler-owned review records must be created after code, carrier, PR metadata, and validation evidence are stable and must bind to the current PR head unless the gate explicitly accepts carrier-only drift.

## Implementation Scope

This implementation covers:

- selectable runtime tempdir cleanup surface:
  - `temp-dir-cleanup`
- selectable runtime demo fixture cleanliness surface:
  - `demo-fixture-cleanliness`
- fixture group `tempdir-cleanup` for tempdir cleanup diagnostics
- fixture group `fixture-cleanliness` for demo fixture cleanliness diagnostics
- stable `failure_label=...` and `evidence_locator=...` labels for tempdir cleanup and demo fixture cleanliness failure modes
- aggregate runtime regression preservation through the default checker and `make loom-check-runtime-regression`
- Makefile targets for the two #1407 surfaces
- WI-1407 Loom progress, work-item, suite, and PR metadata carriers

This implementation does not cover:

- #1405 locking surface rename or semantic rewrite
- #1406 subprocess environment purity surface rename or semantic rewrite
- demo bootstrap generation/drift/canonicalization split under #1262
- #1408 aggregate runtime evidence closeout
- parent #1263/#1255 closeout
- release/package validation behavior
- skills validation behavior
- hosted workflow policy, permissions, or external-visible runtime behavior

## Validation Plan

Required validation before merge-ready consumption:

- `git diff --check`
- `python3 tools/check_loom_check_runtime_regressions.py --list-surfaces`
- `make loom-check-runtime-temp-dir-cleanup`
- `make loom-check-runtime-demo-fixture-cleanliness`
- `make loom-check-runtime-single-flight-locking`
- `make loom-check-runtime-worktree-local-lock-paths`
- `make loom-check-runtime-installer-regression-lock-output`
- `make loom-check-runtime-locking`
- `make loom-check-runtime-subprocess-env-purity`
- `make loom-check-runtime-regression`
- `python3 tools/py_compile_clean.py tools/check_loom_check_runtime_regressions.py`
- `python3 tools/loom.py suite inspect --target . --item WI-1407 --json`
- `python3 tools/loom.py suite validate --target . --item WI-1407 --json`
- `python3 tools/loom.py suite evidence validate --target . --item WI-1407 --json`
- `python3 tools/loom.py suite carrier validate --target . --item WI-1407 --json`
- PR metadata preflight for the current PR and head
- hosted required checks on the current head
- scheduler-owned PR gate and controlled merge check

Validation must leave no lock residue at `.loom/runtime/loom_check.lock`, `packages/loom-installer/.installer-regression-lock`, or new `loom-check-*` temporary directories.

## Risks And Rollback

Primary risks:

- selector drift could make aggregate runtime regression omit cleanup or fixture cleanliness checks
- Makefile target drift could hide a selectable #1407 surface
- demo fixture cleanliness validation could accidentally mutate tracked files
- tempdir cleanup validation could miss residue from the runtime checker

Rollback boundary:

- revert the WI-1407 commits on the PR
- restore the aggregate checker behavior in `tools/check_loom_check_runtime_regressions.py`
- remove the WI-1407 Makefile aliases and Loom carriers if the PR is abandoned

## Host Binding

The implementation binds to:

- issue #1407
- PR pending
- branch `work/1407-tempdir-cleanup-fixture-cleanliness`

The PR body machine carrier must name the exact branch and current `head_sha`. If any commit changes the head, PR metadata preflight, hosted checks, review head binding, PR gate, and controlled merge check must be refreshed.
