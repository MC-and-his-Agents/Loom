# WI-1405 Plan

- Suite path: minimal
- Work Item: WI-1405

## Suite Contract

- Full-suite-artifacts not_applicable: rationale: the implementation is constrained to splitting existing runtime locking checks into narrow selectors and Makefile aliases; consumer boundary: no separate research, external contract, or readiness checklist artifact is required for this bounded change; recheck condition: require full suite artifacts if this work changes subprocess environment purity, cleanup semantics, installer release behavior, hosted workflow policy, or broad `loom_check` runtime locking implementation.

## Implementation

1. Add a small surface registry to `tools/check_loom_check_runtime_regressions.py`.
2. Make only the three locking checks selectable with `--surface` and `--fixture-group locking`.
3. Keep aggregate execution as the default and keep non-lock checks aggregate-only for #1406/#1407 ownership.
4. Emit start/end/failure diagnostics that include surface name, fixture group, duration, and failure detail.
5. Add Makefile aliases for the locking group and each locking surface.

## Validation

| Scenario | Validation |
| --- | --- |
| S1 Single-Flight Locking Surface | automated validation strategy -> `make loom-check-runtime-single-flight-locking` |
| S2 Worktree-Local Lock Paths Surface | automated validation strategy -> `make loom-check-runtime-worktree-local-lock-paths` |
| S3 Installer Regression Lock Output Surface | automated validation strategy -> `make loom-check-runtime-installer-regression-lock-output` |
| S4 Aggregate Runtime Regression | automated validation strategy -> `make loom-check-runtime-locking`; `make loom-check-runtime-regression` |

## Acceptance Mapping

- AC-1 -> automated validation strategy: `python3 tools/check_loom_check_runtime_regressions.py --list-surfaces`.
- AC-2 -> structural validation strategy: Makefile readback for `loom-check-runtime-locking` and the three per-surface targets.
- AC-3 -> automated validation strategy: targeted Make outputs expose `surface=<name>` and `fixture_group=locking`.
- AC-4 -> automated validation strategy: `make loom-check-runtime-regression`.
- AC-5 -> structural validation strategy: `git status --short` and lock path absence checks after validation.

## Commands

- `python3 tools/check_loom_check_runtime_regressions.py --list-surfaces`
- `make loom-check-runtime-single-flight-locking`
- `make loom-check-runtime-worktree-local-lock-paths`
- `make loom-check-runtime-installer-regression-lock-output`
- `make loom-check-runtime-locking`
- `make loom-check-runtime-regression`
- `python3 tools/py_compile_clean.py tools/check_loom_check_runtime_regressions.py`
- `git diff --check`
- `python3 tools/loom.py suite inspect --target . --item WI-1405 --json`
- `python3 tools/loom.py suite validate --target . --item WI-1405 --json`

## Boundaries

- No subprocess environment purity split for #1406.
- No tempdir cleanup or demo fixture cleanliness split for #1407.
- No aggregate runner closeout or evidence convergence for #1408.
- No review artifact, guardian, formal review, controlled merge, release, or closeout in the worker scope.
