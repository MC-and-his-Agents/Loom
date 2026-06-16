# Contracts

## Contract

- Schema marker: loom-full-suite-contracts/v1
- Consumes:
  - Suite index locator: .loom/specs/WI-1235/suite-index.md
  - Spec acceptance ids / locators: .loom/specs/WI-1235/spec.md#acceptance-criteria
  - Plan constraints locator: .loom/specs/WI-1235/plan.md#constraints
  - Existing contract locator, or `not required` rationale: `loom repair plan/apply` public CLI surface in `tools/loom.py`; shared runtime `repair` command in `src/skills/shared/scripts/loom_flow.py`.
- Produces:
  - Contract deltas: C1-C5 below.
  - Compatibility expectations: existing installed-surface repair plan behavior remains non-mutating and passable when carrier repair is not explicitly selected.
  - Consumer list: CLI callers, governance-closeout checks, aggregate CLI contract, skills generated runtime consumers, merge-ready gate.
- Locator:
  - Contracts locator: .loom/specs/WI-1235/contracts.md
- Provenance:
  - Source contract / issue / PR / doc locator: GitHub issue #1235; `tools/check_cli_contract.py`.
  - Freshness rule: Recheck after repair command schema/output, generated runtime, or gate parser changes.

## Contract Delta

### Contract C1

- Contract locator: `tools/loom.py` repair plan/apply JSON output.
- Consumed acceptance id / locator: A1, A2.
- Change type: add
- Compatibility expectation: `repair plan` remains non-mutating; `repair apply` mutates only explicit safe carrier closeout writes.
- Consumers: CLI callers, review, merge-ready.
- Validation expectation: governance-closeout and aggregate contracts.
- Provenance: #1235 implementation.

### Contract C2

- Contract locator: `src/skills/shared/scripts/loom_flow.py` repair command.
- Consumed acceptance id / locator: A1, A2, A3.
- Change type: add
- Compatibility expectation: active carrier repair requires explicit issue selector and host-complete truth.
- Consumers: generated skills runtimes and root CLI wrapper.
- Validation expectation: omitted issue, ambiguous retained item, multi-issue locator, invalid output fixtures.
- Provenance: #1235 implementation.

### Contract C3

- Contract locator: carrier write set.
- Consumed acceptance id / locator: A1.
- Change type: add
- Compatibility expectation: write set is limited to `.loom/progress/<item>.md`, `.loom/status/current.md`, and `.loom/bootstrap/init-result.json`.
- Consumers: fact-chain, status, closeout, merge-ready.
- Validation expectation: explicit apply fixture plus fact-chain idle readback.
- Provenance: #1235 implementation.

### Contract C4

- Contract locator: host interaction boundary.
- Consumed acceptance id / locator: A3.
- Change type: document-only
- Compatibility expectation: host truth readback is allowed; host mutation is forbidden.
- Consumers: review, merge-ready, security/permissions audit.
- Validation expectation: `host_mutations: false`, `host_actions: []`.
- Provenance: issue #1235.

### Contract C5

- Contract locator: generated skills runtime copies.
- Consumed acceptance id / locator: A4.
- Change type: change
- Compatibility expectation: generated `.loom-runtime/shared/scripts/loom_flow.py` copies match source behavior.
- Consumers: skills surface check, downstream skill execution.
- Validation expectation: aggregate CLI contract and `skills generate --apply`.
- Provenance: #1235 implementation.

## Non-Goals

- This file does not replace implementation contract.
- This file does not author recovery state.

