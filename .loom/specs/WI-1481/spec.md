# WI-1481 Spec

## Suite Contract

- Suite path: minimal
- Full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: WI-1481 is a bounded helper-layer Work Item with deterministic focused tests and no external host contract, research, or readiness discovery need. consumer boundary: suite validate, review, PR gate, merge-ready, dependent issues #1482/#1483/#1484/#1487, and issue closeout may consume this minimal suite plus focused test evidence for the reusable helper contract only. recheck condition: require full suite artifacts if scope expands into command-by-command integration, configurable budget policy, plugin/skill protocol changes, release execution, security/privacy policy, or external-visible host writes.
- Consumes:
  - Work Item / FR locator: https://github.com/MC-and-his-Agents/Loom/issues/1481
  - Story Readiness confirmed locator, blocking locator, or skip rationale: issue body is the planning source for this hardening item.
  - Story scenario locator, or skip rationale: scenarios are defined below.
  - Story Business Confirmation confirmed locator, blocking locator, or skip rationale: no external business semantics.
- Produces:
  - Scenario ids / locators: S1, S2, S3 in this file.
  - Acceptance ids / locators: A1-A3 in this file.
  - Behavior evidence expectation: focused unit tests in `test/output_envelope_test.py`.
- Locator:
  - Spec locator: .loom/specs/WI-1481/spec.md
- Provenance:
  - Source issue / PR / doc / conversation locator: issue #1481.
  - Freshness rule: recheck after changes to `tools/loom.py` output helpers or artifact locator semantics.

## Goal

- Provide reusable output envelope and artifact writer helpers for the global `loom` CLI.
- Preserve full output availability through explicit artifacts without making artifacts a truth carrier.

## Scope

- In scope: `tools/loom.py` helper functions and focused tests.
- Out of scope: connecting all high-noise commands, configurable budget policy, skill/plugin documentation changes, release execution, repo-local runtime/plugin/skills compatibility.

## Key Scenarios

### Scenario S1

Given a command has a concise result
When Loom builds an agent-facing envelope
Then the envelope includes summary, result, failure classification, key gaps, and full-output availability.

### Scenario S2

Given a command has full diagnostic payload
When Loom writes an output artifact
Then the artifact is JSON, includes the original payload, and is written to an ignored artifact path or explicit artifact directory.

### Scenario S3

Given a full payload exceeds the agent-safe stdout budget
When Loom builds an agent-safe payload
Then stdout returns only a summary envelope and artifact locator while the full payload is available in the artifact.

## Behavior Evidence

- Scenario coverage:
  - S1 -> `test_output_envelope_contains_agent_safe_fields`
  - S2 -> `test_write_output_artifact_persists_full_payload`
  - S3 -> `test_agent_safe_payload_writes_artifact_when_over_budget`
- Expected evidence locator: .loom/specs/WI-1481/evidence-map.md
- Freshness rule: evidence must be rerun after output helper or artifact path changes.

## Exceptions And Boundaries

- Failure modes: artifact directory cannot be created or written; later command integration must fail closed rather than silently drop full output.
- Operational boundaries: default artifacts use `.loom/tmp/output-artifacts` or `LOOM_OUTPUT_ARTIFACT_DIR`; they are ignored local artifacts, not Loom truth carriers.
- Rollback or fallback expectations: remove helpers and focused tests if not consumed by later command work.

## Acceptance Criteria

- [x] A1: Output envelope helper includes required agent-facing fields.
- [x] A2: Artifact writer persists full payload and returns a locator.
- [x] A3: Over-budget helper returns summary plus artifact locator without inline diagnostic payload.
