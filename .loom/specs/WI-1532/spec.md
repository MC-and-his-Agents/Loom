# WI-1532 Spec

## Suite Path

- Suite path: minimal
- Full-suite-artifacts not_applicable: rationale: WI-1532 is a bounded runtime admission slice with deterministic contract fixtures and no host write, release execution, closeout-specific hosted gate, or user-facing workflow; consumer boundary: suite validate, build checkpoint, implementation review, PR gate, hosted checks, and downstream #1533/#1534/#1515 may consume this minimal suite only for local closeout freeze admission; recheck condition: require full suite artifacts if scope expands into host mutation, one-shot closeout orchestration, release execution, closeout-specific hosted gate semantics, security/privacy behavior, or external service writes.

## Objective

Add a local closeout freeze admission profile that tells operators whether terminal closeout facts are stable enough for a closeout-only PR, and why not when they are not.

## Acceptance Scenarios

### S1: Terminal subject binding is required

Given a closeout freeze check runs without closed issue, merged PR, merge commit, Work Item, and target branch readback, the admission result is blocking with terminal subject next action.

### S2: Carrier and shadow freshness block closeout PR creation

Given carrier refresh or shadow freshness reports stale inputs, closeout freeze blocks `closeout_pr_allowed` and returns carrier/shadow next actions.

### S3: Release/no-release evidence is consumed explicitly

Given release judgment is missing evidence readback, closeout freeze blocks with a release evidence next action instead of trusting PR metadata alone.

### S4: PR body readback drift blocks admission

Given PR body metadata or readback hash drifts from the freeze input, closeout freeze blocks before a closeout-only PR can be admitted.

### S5: Closeout-only allowed paths are enforced

Given the diff contains non-terminal carrier paths, closeout freeze blocks and points the operator back to full review instead of closeout-only admission.

## Non-Goals

- Do not implement #1533 closeout-specific hosted gate or final risk escalation.
- Do not implement #1534 docs/skills convergence.
- Do not implement #1555 one-shot post-merge closeout run.
- Do not perform GitHub issue, PR, Project, release, or carrier repair writes.
- Do not perform #1515 final release/no-release closeout.
