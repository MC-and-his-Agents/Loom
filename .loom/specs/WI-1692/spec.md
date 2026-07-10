# Spec

## Suite Contract

- Suite path: minimal
- Suite index locator: `.loom/specs/WI-1692/`
- Full-suite-artifacts not_applicable: rationale: WI-1692 uses the minimal suite because the work is bounded to one CLI wrapper transition, focused contract tests, and Work Item/review carrier refresh; consumer boundary: suite validate, spec review, implementation review, merge-ready, PR gate, hosted CI, and closeout consume this minimal suite plus current-head review and PR metadata; recheck condition: require full suite artifacts if the scope expands into runtime `loom_flow.py` behavior, release/version mechanics, security or permission behavior, destructive host writes, or user-facing documentation beyond #1694.
- Consumes:
  - Work Item / FR locator: issue #1692 and #1695 closeout policy.
  - Story Readiness confirmed locator or blocking locator: no separate story readiness artifact is required because this is an internal CLI transition Work Item under milestone #15.
  - Story scenario locator: scenarios are defined by issue #1692 and contract tests.
  - Story Business Confirmation confirmed locator or blocking locator: no business confirmation artifact is required because there is no product-facing business semantics change.
- Produces:
  - Scenario ids / locators: S1 through S4 in this spec.
  - Acceptance ids / locators: A1 through A5 in this spec.
  - Behavior evidence expectation: focused CLI wrapper contract tests and PR gate readback.
- Locator:
  - Spec locator: `.loom/specs/WI-1692/spec.md`
- Provenance:
  - Source issue / PR / doc / conversation locator: issue #1692, issue #1695, PR #1707.
  - Freshness rule: valid for head `f60c6b9ae58c0290fb18c0c1f71f66aa7be5c618`; review must be refreshed after code, carrier, or PR metadata changes.

## Goal

- Add an explicit `loom merge run <pr> --apply --closeout-run` transition so controlled merge can hand off directly into closeout when the caller opts in.
- Preserve existing `loom merge check` and `loom merge run --apply` behavior when `--closeout-run` is absent.
- Consume closeout policy from #1695 so low-risk work can use `inline` or `host_only`, while `batched_carrier_pr` and `full_closeout_pr` fail closed before merge.

## Scope

- In scope:
  - Root CLI wrapper behavior in `tools/loom.py`.
  - Reuse of the existing closeout-run payload helper for `inline`.
  - Host-only reconciliation and closeout readback for `host_only`.
  - Pre-merge blocking for `batched_carrier_pr` and `full_closeout_pr`.
  - Focused regression coverage in `tools/check_cli_contract.py`.
- Out of scope:
  - Making closeout-run the default merge behavior.
  - Replacing `loom ship` as the user-facing main path.
  - Creating closeout PRs from `controlled-merge --closeout-run`.
  - Changing runtime `controlled-merge` internals in `loom_flow.py`.

## Key Scenarios

### Scenario S1

Given a caller runs `loom merge run <pr> --apply` without `--closeout-run`

When the wrapper delegates to controlled merge

Then the existing `controlled-merge merge --execute` delegation and output shape remain compatible.

### Scenario S2

Given a caller runs `loom merge run <pr> --apply --closeout-run --closeout-mode inline`

When controlled merge passes

Then the wrapper runs the existing closeout-run sequence and reports `creates_closeout_pr=false`.

### Scenario S3

Given a caller runs `loom merge run <pr> --apply --closeout-run --closeout-mode host_only`

When controlled merge passes

Then the wrapper applies host reconciliation and closeout readback without running carrier closeout-run or creating a closeout PR.

### Scenario S4

Given a caller requests `batched_carrier_pr` or `full_closeout_pr`

When `--closeout-run` is evaluated before merge

Then the wrapper blocks before controlled merge and directs the caller to the explicit carrier queue or full closeout path.

## Behavior Evidence

- Story scenario mapping: scenarios are defined in this spec.
- Story readiness locator: no separate story readiness artifact is required for this CLI governance Work Item.
- Story business confirmation locator: no business-domain behavior is changed.
- Scenario coverage:
  - S1 -> `assert_merge_wrapper_pr_argument_contract`.
  - S2 -> `assert_merge_closeout_run_wrapper_contract` inline branch.
  - S3 -> `assert_merge_closeout_run_wrapper_contract` host-only branch.
  - S4 -> `assert_merge_closeout_run_wrapper_contract` full-closeout fail-closed branch.
- Expected evidence locator: `tools/check_cli_contract.py --fixture-group merge-wrapper`.
- Freshness rule: evidence must be rerun after changes to `tools/loom.py`, `tools/check_cli_contract.py`, or PR metadata.
- Execution ledger acceptance locator: issue #1692 and PR #1707.
- Rationale if this is not a behavior-bearing change: not needed; this is behavior-bearing CLI wrapper work.

## Exceptions And Boundaries

- Failure modes:
  - Missing `--work-item`, `--issue`, or target branch blocks closeout-run.
  - Controlled merge failure blocks closeout-run.
  - `batched_carrier_pr` and `full_closeout_pr` block before merge.
- Operational boundaries:
  - No default write behavior changes.
  - No PR creation side effects.
  - No runtime `loom_flow.py` controlled-merge contract expansion.
- Rollback or fallback expectations:
  - Call existing `loom merge run --apply` without `--closeout-run`.
  - Use `loom ship --apply` for the user-facing delivery path.
  - Use explicit closeout queue or full closeout PR path for upgraded policies.

## Acceptance Criteria

- [x] A1: `loom merge run --apply` remains compatible without closeout-run.
- [x] A2: `inline` closeout runs only after controlled merge passes.
- [x] A3: `host_only` closeout does not run carrier closeout-run or create a closeout PR.
- [x] A4: upgraded closeout modes block before merge.
- [x] A5: focused wrapper, closeout, ship, and controlled-merge regression checks pass locally.
