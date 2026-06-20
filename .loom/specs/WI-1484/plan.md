# WI-1484 Plan

## Suite Contract

- Suite path: minimal
- Full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: the change is a focused CLI runtime wrapper extension over #1477 output envelope primitives. consumer boundary: review, PR gate, merge-ready, #1478/#1484/#1485 closeout, and #1489 final regression. recheck condition: require full suite artifacts if scope expands into skills, migration docs, release, or output schema redesign.
- Consumes:
  - Work Item / FR locator: https://github.com/MC-and-his-Agents/Loom/issues/1484 and https://github.com/MC-and-his-Agents/Loom/issues/1485
  - Story Readiness confirmed locator, blocking locator, or skip rationale: issue bodies and milestone/11 review.
  - Story scenario locator, or skip rationale: scenarios are mapped in the spec.
  - Story Business Confirmation confirmed locator, blocking locator, or skip rationale: no external business semantics.
- Produces:
  - Scenario ids / locators: S1-S3 in `.loom/specs/WI-1484/spec.md`.
  - Acceptance ids / locators: A1-A5 in `.loom/specs/WI-1484/spec.md`.
  - Behavior evidence expectation: focused tests and real CLI smoke commands prove summary/artifact defaults and explicit full JSON mode.
- Locator:
  - Plan locator: .loom/specs/WI-1484/plan.md
- Provenance:
  - Source issue / PR / doc / conversation locator: #1478/#1484/#1485 and current milestone planning review.
  - Freshness rule: rerun validation after output wrapper, command router, help matrix, PR metadata, or carrier changes.

## Phases

- P1: Extend common flow/delegated dispatch paths to call `agent_safe_payload` by default and strip `--full-output` before delegated execution.
- P2: Add `--full-output` support to scenario, PR, merge, reconcile, carrier, and closeout queue handlers.
- P3: Expose command-level output policy and budget/artifact configuration in `loom help --json`.
- P4: Add focused regression tests plus real CLI smoke validation under a small stdout budget.
- P5: Refresh Loom carriers, PR metadata, review, hosted checks, and controlled merge evidence.

## Scenario Validation Mapping

- S1 -> automated: `test/output_envelope_test.py` covers flow, scenario, and dispatch default agent-safe output.
- S2 -> automated: `test/output_envelope_test.py` covers flow, scenario, and dispatch `--full-output` escape hatches.
- S3 -> automated: `test/output_envelope_test.py` validates help output policy fields.

## Acceptance Test Mapping

- A1 -> test evidence: small-budget real CLI smoke for `build` and `merge-ready`.
- A2 -> test evidence: real CLI smoke for `build --full-output`.
- A3 -> test evidence: `test/output_envelope_test.py`.
- A4 -> test evidence: `loom help --json` jq readback and `test/output_envelope_test.py`.
- A5 -> test evidence: `tools/check_cli_contract.py --surface merge-wrapper --surface pr-metadata --surface controlled-merge --surface closeout-wrapper`.
