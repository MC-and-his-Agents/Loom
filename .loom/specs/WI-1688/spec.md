# WI-1688 Spec

## Suite Contract

- Suite path: minimal
- Suite index locator, or N/A rationale: `.loom/specs/WI-1688`
- Full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: WI-1688 is a bounded root CLI output hardening change for existing wrapper surfaces rather than a new workflow, release, or host-write design. consumer boundary: suite validate, review, PR gate, controlled merge, and closeout may consume this minimal spec, plan, evidence map, task carrier, and focused validation output. recheck condition: require full suite artifacts if scope expands into `loom ship`, host mutation execution, closeout policy, release packaging, or public workflow design.
- Consumes:
  - Work Item / FR locator: issue #1688 under FR #1685
  - Story Readiness confirmed locator, blocking locator, or N/A rationale: N/A; this is a bounded CLI hardening item created from milestone #15 execution friction.
  - Story scenario locator, or N/A rationale: N/A; scenarios are authored below.
  - Story Business Confirmation confirmed locator, blocking locator, or N/A rationale: N/A; no product-domain business semantics change.
- Produces:
  - Scenario ids / locators: S1, S2
  - Acceptance ids / locators: A1-A5
  - Behavior evidence expectation: CLI block/fix-needed output is compact and actionable while full JSON remains retained.
- Locator:
  - Spec locator: `.loom/specs/WI-1688/spec.md`
- Provenance:
  - Source issue / PR / doc / conversation locator: GitHub issue #1688
  - Freshness rule: Recheck before PR metadata, PR gate, controlled merge, closeout, and closeout queue outputs are consumed by review or merge-ready.

## Goal

- Reduce CLI diagnostic noise for common metadata and gate blockers.
- Preserve full machine-readable evidence through artifact locators and `--full-output`.

## Scope

- In scope:
  - Compact non-passing wrapper output into an agent-safe envelope with `actionable_findings`.
  - Extract the most useful action fields from findings, repair plans, sync plans, `next_action`, `next_command`, and `fallback_to`.
  - Keep full runtime payloads available through output artifacts.
  - Update contract tests that consume agent-safe envelopes.
- Out of scope:
  - Changing gate decisions or host reconciliation semantics.
  - Implementing `loom ship`.
  - Automatically applying native dependency edge cleanup.
  - Rewriting all downstream runtime payload schemas.

## Key Scenarios

### Scenario S1

Given a PR metadata, PR gate, controlled merge, or closeout command returns a non-passing payload with findings or repair actions

When the user runs the root `loom` wrapper without `--full-output`

Then stdout contains a short envelope with summary, key gaps, actionable findings, key locators, and a full-output artifact locator.

### Scenario S2

Given the same command is run with `--full-output`

When full machine-readable detail is needed for debugging or gate review

Then the wrapper returns the original payload without the compact envelope.

## Behavior Evidence

- Story scenario mapping: N/A; scenarios S1-S2 are authored in this spec.
- Story readiness locator or N/A rationale: N/A; issue #1688 is already scoped and accepted as a milestone #15 work item.
- Story business confirmation locator or N/A rationale: N/A; no user-domain business semantics change.
- Scenario coverage:
  - S1 -> `test/output_envelope_test.py`
  - S2 -> `test/output_envelope_test.py`
- Expected evidence locator: `.loom/specs/WI-1688/evidence-map.md`
- Freshness rule: Refresh validation after changes to `tools/loom.py`, `tools/check_cli_contract.py`, or output envelope tests.
- Execution ledger acceptance locator: `.loom/progress/WI-1688.md`
- N/A rationale, if this is not a behavior-bearing change: N/A; this is a CLI behavior change.

## Exceptions And Boundaries

- Failure modes: Missing artifact locator, oversized compact output, lost full payload, or action extraction that invents commands.
- Operational boundaries: The wrapper may summarize; it must not change delegated command results.
- Rollback or fallback expectations: `--full-output` remains the escape hatch; artifacts preserve original JSON for review and debugging.

## Acceptance Criteria

- [x] A1: Non-passing payloads with actionable details emit compact `actionable_findings`.
- [x] A2: Full payloads are written to artifacts when stdout is compacted.
- [x] A3: `--full-output` returns the original payload.
- [x] A4: Existing over-budget stdout remains within the configured budget.
- [x] A5: Contract tests consume agent-safe envelopes where wrapper output may now be compacted.
