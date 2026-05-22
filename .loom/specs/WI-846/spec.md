# WI-846 Spec

## Outcome

`flow pre-review` and `loom_check.py` expose Governance Lint / Operating Lint evidence before formal review, so stale or blocking governance failures are visible without running a semantic review first.

## Acceptance

- `flow pre-review` emits a top-level `governance_lint` object using `loom-governance-lint-status/v1`.
- The pre-review step list includes `governance-lint` after deterministic runtime, fact-chain, state, runtime evidence, admission checkpoint, and workspace checks.
- Blocking derived lint evidence enters pre-review `missing_inputs` and blocks the pre-review surface with a stable fallback.
- Advisory or absent pre-review companion requirements do not change the pre-review verdict.
- `loom_check.py` validates the pre-review `governance_lint` envelope and includes a stale derived status negative fixture proving the lint blocks before review.
- The implementation does not add a standalone lint CLI, does not add advanced repo-specific lint content, and does not change review or merge-ready verdict semantics.

## Non Goals

- Do not implement #852 status or merge-ready consumption in this Work Item.
- Do not run heavyweight semantic review merely for carrier-only or status evidence updates.
- Do not make lint results an authored recovery, review, validation, merge, or closeout truth source.
