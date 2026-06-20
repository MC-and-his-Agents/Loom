# WI-1483 Spec

## Suite Contract

- Suite path: minimal
- Full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: WI-1483 is a bounded CLI output contract Work Item using already-frozen #1481/#1482 helpers. consumer boundary: suite validate, review, PR gate, merge-ready, dependent #1484/#1485, and issue closeout may consume this minimal suite plus focused CLI contract validation. recheck condition: require full suite artifacts if scope expands into flow gate implementation, plugin text migration, release execution, or external host writes.
- Consumes:
  - Work Item / FR locator: https://github.com/MC-and-his-Agents/Loom/issues/1483
  - Story Readiness confirmed locator, blocking locator, or skip rationale: issue body and v0.17.0 scope amendment define the product boundary.
  - Story scenario locator, or skip rationale: scenarios are defined below.
  - Story Business Confirmation confirmed locator, blocking locator, or skip rationale: no external business semantics.
- Produces:
  - Scenario ids / locators: S1-S3 in this file.
  - Acceptance ids / locators: A1-A4 in this file.
  - Behavior evidence expectation: global `loom` CLI summary/artifact output for fact-chain, status, and shadow-parity.
- Locator:
  - Spec locator: .loom/specs/WI-1483/spec.md
- Provenance:
  - Source issue / PR / doc / conversation locator: issue #1483.
  - Freshness rule: recheck after output envelope, budget, artifact locator, or full-output escape hatch changes.

## Goal

- Keep high-noise fact-chain, status, and shadow parity reads safe for agent default stdout.
- Preserve full raw diagnostics through explicit `--full-output` or artifact locators for scripts and human debugging.

## Scope

- In scope: global `loom` CLI wrappers for `fact-chain`, `status`, and `shadow-parity`; summary envelope fields; artifact locator preservation; configurable budget coverage; contract tests that request full output when consuming nested payloads.
- Out of scope: flow gate command families owned by #1484, unified default entry rollout owned by #1485, plugin text migration owned by #1486, repo-local wrapper compatibility, and old installer paths.

## Key Scenarios

### Scenario S1

Given a user or agent runs `loom fact-chain --json`, `loom status --json`, or `loom shadow-parity --json`
When the raw payload exceeds the configured agent-safe stdout budget
Then stdout returns a bounded envelope with result, summary, key gaps, diagnostic counts, key locators, and a full artifact locator.

### Scenario S2

Given a script or debugger needs the complete nested structure
When it passes `--full-output`
Then the command returns the raw delegated JSON without the summary envelope.

### Scenario S3

Given contract tests need nested fact-chain or status fields
When they consume those commands as machine inputs
Then they request `--full-output` explicitly instead of depending on default stdout.

## Behavior Evidence

- Scenario coverage:
  - S1 -> `tools/loom.py` agent-safe wrapper integration and `test/output_envelope_test.py`.
  - S2 -> `--full-output` handler tests and real fact-chain full-output probe.
  - S3 -> `tools/check_cli_contract.py` machine consumer updates.
- Expected evidence locator: .loom/specs/WI-1483/evidence-map.md
- Freshness rule: rerun focused tests, real stdout probes, and CLI contract after changes to wrapper output, artifact locator fields, or consumer command flags.

## Exceptions And Boundaries

- Default summary mode is for the global `loom` CLI surface only.
- Full diagnostics are diagnostic artifacts, not authoritative truth carriers.
- No repo-local plugin/runtime/skills path or old installer compatibility is restored.

## Acceptance Criteria

- [x] A1: Default `fact-chain`, `status`, and `shadow-parity` stdout stays below the 16 KiB agent-safe budget on the current repo probes.
- [x] A2: Full raw payloads remain available through artifact locators and explicit `--full-output`.
- [x] A3: Failure summaries include key gaps, diagnostic counts, and key locators.
- [x] A4: Machine contract tests that need nested JSON opt into full output.
