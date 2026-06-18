# WI-1578 Spec

## Suite Path

- Suite path: minimal
- Full-suite-artifacts not_applicable: rationale: WI-1578 is a narrow PR metadata surface correction with deterministic CLI contract coverage and generated runtime parity; consumer boundary: suite validate, review, PR gate, hosted checks, #1577 closeout carrier sync, and milestone closeout may consume this minimal suite only for closeout metadata surface behavior; recheck condition: require broader suite artifacts if scope expands into hosted admission, release behavior, controlled merge behavior, or host mutations.

## Objective

Make `loom pr metadata-* --surface closeout` produce and consume a `closeout` metadata machine surface so terminal closeout-only PRs are not misclassified as merge-ready implementation PRs.

## Acceptance Scenarios

### S1: Closeout render emits closeout metadata

Given closeout metadata render inputs, the rendered PR body machine block uses `surface: closeout`.

### S2: Closeout preflight consumes closeout metadata

Given a closeout PR body artifact, metadata preflight passes for `--surface closeout`.

### S3: Review compatibility remains unchanged

Given review or pre-review metadata preflight, the existing merge-ready carrier compatibility remains available.

## Acceptance Criteria

- A1: Focused `tools/check_cli_contract.py --surface pr-metadata` covers closeout render/preflight behavior.
- A2: Generated runtime copies stay in sync with `src/skills`.
- A3: The change does not alter hosted admission, controlled merge, release judgment, or closeout carrier content.
