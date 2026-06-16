# Research

## Contract

- Schema marker: loom-full-suite-research/v1
- Consumes:
  - Suite index locator: .loom/specs/WI-1235/suite-index.md
  - Open question / risk locator: GitHub issue #1235; read-only review findings from current Codex thread.
  - Upstream issue / doc / host locator: GitHub issue #1235; parent FR #1228.
- Produces:
  - Resolved decision records: R1-R4 below.
  - Deferred unknowns: none inside #1235.
  - `not required` unknowns: release/tag/npm and host mutations by repair command.
- Locator:
  - Research locator: .loom/specs/WI-1235/research.md
- Provenance:
  - Source locator for each decision: issue #1235, local validation commands, read-only review.
  - Freshness rule: Recheck after repair semantics, host truth contract, or validation fixture changes.

## Questions And Decisions

### Question R1

- Question: Can repair infer carrier ownership without an explicit issue selector?
- Why it matters before implementation: omitted selectors can bypass retained-item ambiguity protection.
- Input locators: read-only review finding P1; issue #1235 acceptance criteria.
- Decision: resolved
- Decision summary: active carrier repair requires explicit `--issue`; omitted issue fails closed unless the root command is only planning unrelated installed-surface repair actions.
- Provenance: `carrier_repair_candidate` and `assert_repair_apply_carrier_closeout_contract`.
- Recheck condition: if repair starts supporting a separate explicit carrier selector.

### Question R2

- Question: Can `repair apply` report pass when installed-surface actions remain?
- Why it matters before implementation: callers could interpret partial repair as complete.
- Input locators: read-only review finding P2; aggregate CLI contracts.
- Decision: resolved
- Decision summary: root `repair apply` blocks before mutation when carrier closeout actions coexist with installed-surface repair actions.
- Provenance: `tools/loom.py`; mixed-action fixture.
- Recheck condition: if installed-surface mutating repair receives a separate apply contract.

### Question R3

- Question: What write preflight is required before carrier apply mutates files?
- Why it matters before implementation: partial progress/status writes without init-result would corrupt fact-chain.
- Input locators: read-only review finding P2/P3; invalid-output fixture.
- Decision: resolved
- Decision summary: resolve and load init-result before writing progress, status, or init-result; all three writes occur only after inputs are valid.
- Provenance: `load_idle_init_result_payload`; invalid-output regression.
- Recheck condition: if carrier write set expands beyond progress/status/init-result.

### Question R4

- Question: Are host mutations allowed?
- Why it matters before implementation: issue #1235 explicitly forbids closing issues or updating projects.
- Input locators: GitHub issue #1235.
- Decision: resolved
- Decision summary: repair plan/apply may read host truth through `gh api` but always reports `host_mutations: false` and `host_actions: []`.
- Provenance: governance-closeout fixture assertions.
- Recheck condition: only a future Work Item with explicit host mutation approval can change this.

## Deferred Unknowns

- None for #1235.

## Excluded Unknowns

- Unknown: release/tag/npm verification.
- Rationale: #1296 owns release/no-release closeout.
- Recheck condition: before #1296 starts.
- Consumers that should not require it: #1235 review and merge-ready.
