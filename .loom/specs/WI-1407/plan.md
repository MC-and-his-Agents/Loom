# WI-1407 Plan

- Suite path: minimal
- Work Item: WI-1407

## Suite Contract

- Full-suite-artifacts not_applicable: rationale: the implementation is constrained to splitting existing cleanup and fixture cleanliness checks into named selectors and Makefile aliases; consumer boundary: no separate research, external contract, or readiness checklist artifact is required for this bounded change; recheck condition: require full suite artifacts if this work changes locking, subprocess environment purity, installer release behavior, demo bootstrap generation/drift/canonicalization, hosted workflow policy, or broad `loom_check` runtime implementation.

## Implementation

1. Mark `temp-dir-cleanup` as a selectable runtime regression surface with fixture group `tempdir-cleanup`.
2. Mark `demo-fixture-cleanliness` as a selectable runtime regression surface with fixture group `fixture-cleanliness`.
3. Keep #1405 locking surfaces and #1406 subprocess environment purity surface unchanged.
4. Keep aggregate execution as the default.
5. Add stable `failure_label=...` and `evidence_locator=...` labels for tempdir cleanup and demo fixture cleanliness failure modes.
6. Add Makefile aliases for the two #1407 runtime surfaces.

## Validation

| Scenario | Validation |
| --- | --- |
| S1 Tempdir Cleanup Surface | automated validation strategy -> `make loom-check-runtime-temp-dir-cleanup` |
| S2 Demo Fixture Cleanliness Surface | automated validation strategy -> `make loom-check-runtime-demo-fixture-cleanliness` |
| S3 Runtime Surface Preservation | automated validation strategy -> existing #1405 locking targets, existing #1406 subprocess-env-purity target, and `make loom-check-runtime-regression` |

## Acceptance Mapping

- AC-1 -> automated validation strategy: `python3 tools/check_loom_check_runtime_regressions.py --list-surfaces`.
- AC-2 -> automated validation strategy: `python3 tools/check_loom_check_runtime_regressions.py --list-surfaces`.
- AC-3 -> structural validation strategy: Makefile readback for `loom-check-runtime-temp-dir-cleanup` and `loom-check-runtime-demo-fixture-cleanliness`.
- AC-4 -> structural validation strategy: runner failure output includes stable tempdir cleanup labels.
- AC-5 -> structural validation strategy: runner failure output includes stable demo fixture cleanliness labels.
- AC-6 -> automated validation strategy: existing #1405 locking Makefile targets and #1406 subprocess-env-purity Makefile target.
- AC-7 -> automated validation strategy: `make loom-check-runtime-regression`.
- AC-8 -> structural validation strategy: `git status --short`, lock path absence checks, and tempdir residue audit after validation.

## Commands

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

## Boundaries

- No #1405 locking surface rename or semantic rewrite.
- No #1406 subprocess environment purity rename or semantic rewrite.
- No demo bootstrap generation/drift/canonicalization split under #1262.
- No #1408 aggregate runtime evidence closeout.
- No review artifact, guardian, formal review, controlled merge, release, or closeout in the worker scope.
