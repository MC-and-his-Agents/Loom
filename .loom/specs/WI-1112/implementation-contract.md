# WI-1112 Implementation Contract

## Owned Files

- `tools/check_cli_contract.py`
- `.loom/work-items/WI-1112.md`
- `.loom/progress/WI-1112.md`
- `.loom/progress/WI-1111.md`
- `.loom/status/current.md`
- `.loom/specs/WI-1112/spec.md`
- `.loom/specs/WI-1112/plan.md`
- `.loom/specs/WI-1112/implementation-contract.md`
- `.loom/reviews/WI-1112.spec.json`
- `.loom/reviews/WI-1112.json`
- `.loom/shadow/merge-ready-loom.json`
- `.loom/shadow/closeout-loom.json`

## Contract

- `tools/check_cli_contract.py` remains the regression surface for suite inspect CLI behavior.
- Every suite inspect fixture checks that the fixture target tree is unchanged after inspect runs.
- Every suite inspect fixture checks the shared JSON envelope: `command: suite inspect`, `result: pass`, item binding, and `mutates: false`.
- Unknown, minimal, full, not_applicable, and full-missing states retain explicit payload checks.
- Suite inspect continues to be read-only and advisory; it does not create, edit, or replace governance truth.

## Non-Goals

- No `suite scaffold`.
- No `suite validate`.
- No evidence, consistency, or carrier suite subcommands.
- No readiness, review, merge-ready, closeout, Project, or host truth decisions.
