# WI-1533 Spec

## Suite Path

- Suite path: minimal
- Full-suite-artifacts not_applicable: rationale: WI-1533 is a bounded runtime/fixture contract slice that exposes closeout-specific gate verdict fields over existing closeout freeze and PR gate behavior. It does not create new product workflows, host mutations, release execution, or documentation convergence. consumer boundary: suite validate, implementation review, PR gate, hosted checks, and downstream #1534/#1515 may consume this minimal suite only for closeout-specific gate verdict, escalation reason, and next-action fields. recheck condition: require full suite artifacts if scope expands into host writes, release/no-release final judgment, batch closeout orchestration, behavior changes outside closeout gate policy, or docs/skills convergence.

## Objective

Expose a stable `loom-closeout-specific-gate/v1` verdict so closeout-only PR consumers can tell when terminal carrier drift is allowed and when the change must escalate to full review / guardian.

## Acceptance Scenarios

### S1: Passing closeout freeze emits a closeout-specific verdict

Given terminal issue, PR, branch, release/no-release, retained review, carrier refresh, shadow freshness, readback, and allowed path inputs are stable, when `gate-freeze --profile closeout` runs, then the payload includes `closeout_specific_gate.result == pass`, `verdict == closeout_pr_allowed`, and `next_action == closeout_pr_allowed`.

### S2: Release evidence gaps escalate

Given release/no-release evidence is missing or unreadable, when closeout freeze runs, then the payload fails closed and exposes a closeout-specific escalation reason tied to `closeout_release_evidence_gap`.

### S3: Closeout PR gate consumes retained review without merge-ready approval substitution

Given a terminal closeout PR has `surface=closeout` and only terminal carrier drift, when `pr-gate check --surface closeout` runs, then it emits a passing closeout-specific gate verdict while keeping retained implementation review separate from current-head implementation approval.

### S4: Non-closeout drift still fails closed

Given a closeout-only PR includes implementation, contract, behavior, or unclassified drift, when closeout freeze or PR gate evaluates it, then the closeout-specific gate blocks and points to full review / guardian instead of silently admitting the PR.

## Non-Goals

- Do not implement #1534 docs/skills/fixture convergence.
- Do not perform #1515 release/no-release final closeout.
- Do not change #1555 `closeout run` orchestration.
- Do not add host writes, issue closure, Project mutation, release/tag/npm publishing, or batch closeout behavior.
- Do not alter existing closeout freeze or PR gate pass/block semantics beyond adding stable verdict fields.
