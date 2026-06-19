# WI-1599 Spec

## Suite Path

- Suite path: minimal
- Full-suite-artifacts not_applicable: rationale: WI-1599 is a focused closeout PR role contract/runtime slice with deterministic CLI contract coverage, closeout role fixtures, generated runtime parity, and demo fixture validation; consumer boundary: suite validate, spec review, implementation review, PR gate, hosted checks, #1598 convergence, and milestone closeout may consume this minimal suite only for closeout PR role readback and validation behavior; recheck condition: require broader suite artifacts if scope expands into release publishing, dependency parsing, PR metadata dry-run semantics, host auth, controlled merge behavior, or external release actions.

## Objective

Make closeout check/run distinguish implementation, release, carrier sync, and final closeout PR roles.

## Acceptance Scenarios

### S1: Closeout role input is explicit

Given a closeout check/run invocation, the current PR role is represented explicitly instead of inferred from one generic PR field.

### S2: Role-specific closeout readback is consumable

Given implementation, release, carrier sync, or final closeout PR roles, closeout output exposes role-specific readback that downstream gates can consume.

## Acceptance Criteria

- A1: closeout check/run accepts and reports explicit PR role values.
- A2: supported roles include `implementation_pr`, `release_pr`, `carrier_sync_pr`, and `final_closeout_pr` or an equivalent stable role model.
- A3: role-only closeout paths do not require legacy generic `--pr` semantics when role-specific inputs are sufficient.
- A4: fixtures cover role readback and invalid/missing role behavior.
