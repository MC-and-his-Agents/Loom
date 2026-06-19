# WI-1595 Spec

## Suite Path

- Suite path: minimal
- Full-suite-artifacts not_applicable: rationale: WI-1595 is a narrow PR metadata runtime/gate hardening slice with deterministic CLI contract coverage, PR body readback evidence, and generated runtime parity; consumer boundary: suite validate, spec review, implementation review, PR gate, hosted checks, #1598 convergence, and milestone closeout may consume this minimal suite only for PR metadata dry-run/preflight behavior; recheck condition: require broader suite artifacts if scope expands into host API auth, closeout PR role model, release resume/publishing, issue dependency parsing, controlled merge behavior, permissions, or external-visible host mutations.

## Objective

Make PR metadata update safe by default and make preflight diagnostics actionable before a host PR body is mutated.

## Acceptance Scenarios

### S1: Metadata preflight reports actionable drift

Given a Loom PR body with governance metadata requirements, metadata render/update/preflight reports enum, expected surface, branch, and head drift with stable next actions before host mutation.

## Acceptance Criteria

- A1: `metadata-update` is non-mutating unless `--apply` is passed.
- A2: preflight diagnostics include classifier, allowed values, expected surface, and next action for enum/head/branch/surface drift.
- A3: PR metadata render/readback/preflight fixtures prove the current head and machine carrier match after update.
