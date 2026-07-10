# Spec

## Suite Contract

- Suite path: minimal
- Consumes:
  - Work Item / FR locator: issue #1900 / FR #1897 / Phase #1888
  - Story Readiness confirmed locator, blocking locator, or not-required rationale: not required; #1900 is scoped by the GitHub Work Item and WI-1899 runtime/global locator contract.
  - Story scenario locator, or not-required rationale: not required; scenarios below are direct carrier-output contract scenarios.
  - Story Business Confirmation confirmed locator, blocking locator, or not-required rationale: not required; internal operating-layer behavior.
- Produces:
  - Scenario ids / locators: S1-S3 in this file.
  - Acceptance ids / locators: A1-A5 in this file.
  - Behavior evidence expectation: focused CLI contract fixtures prove long diagnostics are summarized and artifact-backed.
- Locator:
  - Spec locator: .loom/specs/WI-1900/spec.md
- Provenance:
  - Source issue / PR / doc / conversation locator: issue #1900; issue #1899; docs/methodology/harness/repo-global-artifact-classification.md
  - Freshness rule: Recheck when agent-safe output, runtime path resolution, artifact metadata, or repo carrier validators change.

## Goal

Prevent repo-facing Loom carriers from becoming long-log storage. When CLI or gate output is too large for agent-safe stdout or repo truth, the repo-facing surface exposes a concise summary plus a verifiable artifact locator and hash for the complete payload.

## Scope

- Add verifiable artifact metadata to agent-safe full-output envelopes.
- Preserve logical locators that resolve through the global runtime cache for `.loom/tmp/**`.
- Add focused contract coverage that proves full payloads are artifact-backed, hash-verifiable, and not inlined into short carrier output.
- Keep repo truth consumable by review, merge-ready, and closeout without reading long log bodies.
- Do not redesign every status/progress carrier format.
- Do not implement multi-repo workstation orchestration or legacy migration.
- Do not change user-facing command semantics beyond additive metadata fields.

## Key Scenarios

### Scenario S1

Given a Loom command produces diagnostics larger than the agent-safe stdout budget

When the command is emitted through the agent-safe wrapper

Then stdout contains a short envelope with command, result, summary, diagnostic counts, key locators, an artifact locator, and a SHA-256 hash for the complete output.

### Scenario S2

Given the artifact locator points under `.loom/tmp/**`

When a consumer resolves the locator from the target repository

Then the locator resolves through the global runtime cache path and the artifact hash verifies against the saved artifact bytes.

### Scenario S3

Given a review, merge-ready, or closeout carrier consumes the short command output

When the carrier records diagnostic evidence

Then it can retain the short envelope or summary fields without embedding the complete long payload in repo truth.

## Behavior Evidence

- Scenario coverage:
  - S1 -> `governance-closeout` surface or focused agent-safe output contract.
  - S2 -> `runtime-paths` surface plus artifact hash verification in the agent-safe output contract.
  - S3 -> suite evidence/carrier validators and focused contract assertions that short output excludes long payload bodies.
- Expected evidence locator: .loom/specs/WI-1900/evidence-map.md
- Freshness rule: Recheck before review, merge-ready, and closeout; stale when agent-safe output metadata, artifact resolver, or focused fixtures change.
- Execution ledger acceptance locator: .loom/specs/WI-1900/spec.md#acceptance-criteria

## Exceptions And Boundaries

- Missing artifact locator blocks contract validation.
- Missing or mismatched artifact hash blocks contract validation.
- Unresolvable `.loom/tmp/**` locator blocks contract validation.
- Short envelope that embeds the complete long payload blocks contract validation.
- Sensitive payloads keep the existing sensitive marker.
- `--full-output` remains an explicit debugging/audit override and may emit full payloads.
- Logical repo locators stay stable even when physical storage is global.

## Acceptance Criteria

- [x] A1: Agent-safe envelopes include a full-output artifact locator and SHA-256 hash.
- [x] A2: `.loom/tmp/**` locators resolve through the target repo's global runtime cache path.
- [x] A3: Contract tests fail if the artifact is missing, unreadable, or hash-mismatched.
- [x] A4: Short envelopes remain concise and do not inline the complete long payload.
- [x] A5: Suite evidence and carrier validators can consume the new contract for review, merge-ready, and closeout.
