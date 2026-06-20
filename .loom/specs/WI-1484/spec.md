# WI-1484 Spec

## Suite Contract

- Suite path: minimal
- Full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: WI-1484 is a narrow CLI runtime output behavior change over an already-defined output envelope contract from #1477. consumer boundary: review, PR gate, merge-ready, #1478/#1484/#1485 closeout, and later #1489 regression matrix. recheck condition: require full suite artifacts if scope expands into skill protocol text, migration docs, release behavior, or new output schema semantics.
- Consumes:
  - Work Item / FR locator: https://github.com/MC-and-his-Agents/Loom/issues/1484 and https://github.com/MC-and-his-Agents/Loom/issues/1485
  - Story Readiness confirmed locator, blocking locator, or skip rationale: milestone/11 planning review and issue bodies define this CLI runtime scope.
  - Story scenario locator, or skip rationale: scenarios are defined below.
  - Story Business Confirmation confirmed locator, blocking locator, or skip rationale: no external business semantics.
- Produces:
  - Scenario ids / locators: S1, S2, S3 in this file.
  - Acceptance ids / locators: A1-A5 in this file.
  - Behavior evidence expectation: default agent-safe stdout on high-noise global CLI paths, artifact locator on over-budget output, and explicit full JSON diagnostics through `--full-output`.
- Locator:
  - Spec locator: .loom/specs/WI-1484/spec.md
- Provenance:
  - Source issue / PR / doc / conversation locator: issues #1478/#1484/#1485 and milestone/11 dependency review.
  - Freshness rule: recheck after changes to `tools/loom.py` output wrapping, command routing, help matrix, output envelope tests, or CLI contract surfaces.

## Key Scenarios

- S1: A high-noise flow or scenario command exceeds the effective agent-safe stdout budget and returns a small envelope with failure classification, key gaps, and a full output artifact locator.
- S2: A caller explicitly requests full diagnostics with `--full-output`, and the global CLI emits full JSON without an envelope while stripping that flag before calling delegated runtimes.
- S3: `loom help --json` exposes the default output mode, configurable budget env vars, artifact directory env var, and command-level `--full-output` support for wrapped command families.

## Acceptance Criteria

- A1: `build` and `merge-ready` default paths return `loom-agent-output-envelope/v1` and an artifact locator under a small stdout budget.
- A2: `build --full-output` returns full JSON and no `envelope_schema`.
- A3: `emit_flow`, `emit_delegated`, scenario handlers, dispatch, PR gate, merge, reconcile, carrier, and closeout queue paths strip `--full-output` before delegated execution.
- A4: `loom help --json` marks wrapped command families with `artifact_on_over_budget=true` and `full_output_flag=--full-output`.
- A5: Existing merge wrapper, PR metadata, controlled merge, and closeout wrapper CLI contracts continue to pass.
