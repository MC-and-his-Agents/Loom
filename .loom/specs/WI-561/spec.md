# Spec

## Goal

Make Loom's v0.8.0 execution start from a real `#531` / `#561` Work Item and make the checked-in demo bootstrap reproducible across local branches and machines.

## Scope

- In scope: root self-governance carrier activation for `WI-561`, historical retirement of `INIT-0001`, portable demo bootstrap metadata, and validation that repeated demo bootstrap runs do not rewrite tracked paths or branch names.
- Out of scope: the full `execution_attempt` feature surface for `#562` through `#565`; those remain the next implementation step after this baseline repair.

## Key Scenarios

### Scenario 1

Given Loom root self-governance has a real v0.8.0 Work Item

When status, review, merge-ready, or closeout reads the active fact chain

Then the active item is `WI-561` and `INIT-0001` is only historical bootstrap evidence.

### Scenario 2

Given a developer runs `make loom-demo-new-project` from any branch or workspace path

When the demo bootstrap rewrites checked-in demo metadata

Then the written bootstrap metadata uses portable placeholders for machine-local paths and branch names.

## Behavior Evidence

- Scenario coverage: `python3 tools/loom_status.py --target . --item WI-561` and repeated `make loom-demo-new-project`.
- Expected evidence locator: this Work Item's recovery entry and validation summary.
- Freshness rule: evidence must be collected on the current branch head before review.
- Execution ledger acceptance locator: `.loom/specs/WI-561/spec.md`.

## Acceptance Criteria

- [ ] Root status reads `WI-561` as the active item.
- [ ] `INIT-0001` no longer conflicts as an active work item.
- [ ] Demo bootstrap metadata is portable across path and branch changes.
- [ ] Re-running demo bootstrap does not introduce additional tracked drift.
