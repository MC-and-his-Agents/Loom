# WI-1494 Spec

## Suite Path

- Suite path: minimal
- Full-suite-artifacts not_applicable: rationale: WI-1494 is a bounded closeout/reconciliation retained Work Item binding slice with explicit issue scope, focused parser/lookup regression coverage, generated runtime parity, and live #1510 readback evidence; consumer boundary: suite validate, build checkpoint, review, merge-ready, PR/CI, target branch validation, issue closeout, #1555 closeout run consumption, and milestone closeout consumers may use this minimal suite plus Work Item evidence without research.md, readiness-checklist.md, or suite-index.md; recheck condition: require broader suite artifacts if scope expands into one-shot closeout run orchestration, hosted admission, classifier vocabulary, closeout profile semantics, release behavior, security/privacy behavior, or external host writes.

## Objective

Allow closeout and reconciliation commands to bind directly to a retained Work Item when issue-number based retained lookup is ambiguous.

## Acceptance Scenarios

### S1: Explicit item resolves historical issue mention ambiguity

Given multiple retained Work Items mention issue #1510 in recovery or metadata text, `closeout` and `reconciliation` resolve `--item WI-1510 --issue 1510` to `WI-1510` instead of failing on unrelated weak issue mentions.

### S2: Conflicting explicit item and issue fail closed

Given `--item` points to a retained Work Item that does not match the retained Work Item identified for `--issue`, closeout and reconciliation fail closed with a retained-item binding diagnostic.

### S3: Legacy issue lookup behavior remains fail-closed

Given no `--item` is provided, closeout and reconciliation continue using existing issue-based retained lookup, including ambiguity fail-closed behavior.

## Acceptance Criteria

- `closeout` and `reconciliation` runtime parsers accept `--item`.
- Explicit `--item` disambiguates weak issue mentions.
- Conflicting `--item` / `--issue` inputs fail closed.
- No-item retained lookup behavior is preserved.
- Generated runtime copies stay in sync.
- Live #1510 closeout/reconciliation readback no longer reports retained lookup ambiguity.

## Non-Goals

- No one-shot post-merge closeout run implementation (#1555).
- No release flow changes.
- No closeout evidence semantic changes.
- No hosted admission or broad failure classifier taxonomy changes.
