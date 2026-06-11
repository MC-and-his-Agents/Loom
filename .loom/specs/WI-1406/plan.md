# WI-1406 Plan

- Suite path: minimal
- Work Item: WI-1406

## Suite Contract

- Full-suite-artifacts not_applicable: rationale: the implementation is constrained to splitting existing subprocess environment purity checks into a named selector and Makefile alias; consumer boundary: no separate research, external contract, or readiness checklist artifact is required for this bounded change; recheck condition: require full suite artifacts if this work changes locking, cleanup, fixture cleanliness, installer release behavior, hosted workflow policy, or broad `loom_check` runtime implementation.

## Implementation

1. Add a selectable `subprocess-env-purity` surface to `tools/check_loom_check_runtime_regressions.py`.
2. Keep the #1405 locking surfaces and `locking` fixture group unchanged.
3. Keep aggregate execution as the default.
4. Add stable `evidence_locator=...` labels for subprocess environment pollution failure modes.
5. Add a Makefile alias for the subprocess environment purity surface.

## Validation

| Scenario | Validation |
| --- | --- |
| S1 Subprocess Env Purity Surface | automated validation strategy -> `make loom-check-runtime-subprocess-env-purity` |
| S2 Locking Surface Preservation | automated validation strategy -> `make loom-check-runtime-single-flight-locking`; `make loom-check-runtime-worktree-local-lock-paths`; `make loom-check-runtime-installer-regression-lock-output`; `make loom-check-runtime-locking` |
| S3 Aggregate Runtime Regression | automated validation strategy -> `make loom-check-runtime-regression` |

## Acceptance Mapping

- AC-1 -> automated validation strategy: `python3 tools/check_loom_check_runtime_regressions.py --list-surfaces`.
- AC-2 -> structural validation strategy: Makefile readback for `loom-check-runtime-subprocess-env-purity`.
- AC-3 -> structural validation strategy: runner failure output includes `surface=subprocess-env-purity`, `fixture_group=environment-purity`, and `evidence_locator=...` when subprocess environment purity fails.
- AC-4 -> automated validation strategy: existing #1405 locking Makefile targets.
- AC-5 -> automated validation strategy: `make loom-check-runtime-regression`.
- AC-6 -> structural validation strategy: `git status --short`, lock path absence checks, and tempdir residue audit after validation.

## Commands

- `git diff --check`
- `python3 tools/check_loom_check_runtime_regressions.py --list-surfaces`
- `make loom-check-runtime-subprocess-env-purity`
- `make loom-check-runtime-single-flight-locking`
- `make loom-check-runtime-worktree-local-lock-paths`
- `make loom-check-runtime-installer-regression-lock-output`
- `make loom-check-runtime-locking`
- `make loom-check-runtime-regression`
- `python3 tools/py_compile_clean.py tools/check_loom_check_runtime_regressions.py`
- `python3 tools/loom.py suite inspect --target . --item WI-1406 --json`
- `python3 tools/loom.py suite validate --target . --item WI-1406 --json`

## Boundaries

- No #1405 locking surface rename or semantic rewrite.
- No #1407 tempdir cleanup or demo fixture cleanliness split.
- No #1408 aggregate runtime evidence closeout.
- No review artifact, guardian, formal review, controlled merge, release, or closeout in the worker scope.
