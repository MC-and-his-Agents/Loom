# WI-1542 Spec

## Suite Path

- Suite path: minimal
- Full-suite-artifacts not_applicable: rationale: WI-1542 is a bounded retained lookup implementation slice with explicit issue scope, focused regression, generated runtime parity, and live #1544 closeout readback evidence; consumer boundary: suite validate, build checkpoint, review, merge-ready, PR/CI, target branch validation, issue closeout, and milestone closeout consumers may use this minimal suite plus Work Item evidence without separate full-suite artifacts; recheck condition: require full suite artifacts if scope expands into closeout queue orchestration, hosted admission, classifier vocabulary, closeout profile semantics, release behavior, security/privacy behavior, or external host writes.

## Objective

Prevent closeout/active-carrier audits from treating historical downstream issue mentions in recovery text as equal to canonical Work Item ownership evidence.

## Acceptance Scenarios

### S1: Canonical WI ownership wins over historical recovery mentions

Given issue 1544 has canonical retained carrier `WI-1544`, and other closed Work Items mention `#1544` only in recovery text, retained lookup resolves issue 1544 to `WI-1544` and does not report ambiguity.

### S2: True same-strength ambiguity remains blocking

Given multiple Work Items have equally strong canonical or exact issue-locator ownership evidence for the same issue, retained lookup fails closed with an ambiguity diagnostic.

### S3: Weak-only retained lookup still works

Given a legacy Work Item has only weak evidence such as recovery entry evidence and no stronger competing candidate exists, retained lookup can still resolve it for backwards compatibility.

## Non-Goals

- No closeout queue/status UX implementation.
- No hosted admission or classifier vocabulary changes.
- No closeout freeze profile semantic changes.
- No GitHub issue/PR body writes.
