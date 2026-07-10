# WI-1582 Spec

## Suite Path

- Suite path: minimal
- Full-suite-artifacts not_applicable: rationale: WI-1582 is a narrow hosted closeout admission correction with deterministic CLI fixture coverage, generated runtime parity, and no host mutation or migration behavior; consumer boundary: suite validate, spec review, implementation review, PR gate, hosted checks, #1580 closeout carrier recheck, and milestone closeout may consume this minimal suite only for terminal closeout admission behavior; recheck condition: require broader suite artifacts if scope expands into one-shot closeout run, controlled merge behavior, release behavior, host mutations, or new schema fields.

## Objective

Make hosted gate admission preserve and consume `surface=closeout` for closeout-only terminal carrier PRs without weakening ordinary merge-ready review freshness.

## Acceptance Scenarios

### S1: Closeout recomputation preserves closeout surface

Given a closeout-only terminal carrier PR body with `surface=closeout`, hosted freeze recomputation keeps the snapshot subject on `closeout`.

### S2: Terminal closeout review freshness is surface-aware

Given terminal closeout carrier drift and retained review, closeout surface accepts the terminal closeout allowlist while ordinary merge-ready remains strict.

### S3: Public CLI surfaces expose closeout freeze checks

Given a caller needs to refresh or check closeout freeze input, `carrier refresh --surface closeout` and hosted `gate-freeze check --surface closeout` are available and return closeout evidence.

## Acceptance Criteria

- A1: Targeted terminal closeout hosted fixture covers closeout recomputation and carrier refresh behavior.
- A2: Focused PR metadata surface check still passes.
- A3: Generated runtime copies stay in sync with `src/skills`.
- A4: Demo bootstrap runtime fixture stays in sync.
- A5: Aggregate CLI contract checks pass after local cache cleanup.
