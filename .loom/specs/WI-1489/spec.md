# WI-1489 Spec

## Suite Contract

- Suite path: minimal
- Full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: WI-1489 is a final closeout verification item that consumes already implemented and released milestone/11 work. consumer boundary: review, PR gate, #1489 issue closeout, parent #1480 closeout, and phase #1476 closeout. recheck condition: require full suite artifacts if scope expands into runtime behavior, release execution, package layout, downstream migration, or new closeout semantics.
- Consumes:
  - Work Item locator: https://github.com/MC-and-his-Agents/Loom/issues/1489
  - Parent FR locator: https://github.com/MC-and-his-Agents/Loom/issues/1480
  - Phase locator: https://github.com/MC-and-his-Agents/Loom/issues/1476
  - Story Readiness confirmed locator, blocking locator, or skip rationale: issue #1489 body plus closed milestone/11 child issues.
  - Story Business Confirmation confirmed locator, blocking locator, or skip rationale: not_applicable; product scope was confirmed by milestone/11 planning review and v0.17.0 baseline.
- Produces:
  - Scenario ids / locators: S1-S4 in this file.
  - Acceptance ids / locators: A1-A6 in this file.
  - Behavior evidence expectation: final regression evidence consumes CLI output safety, docs/help migration, skill payload, release evidence, and closeout resolver hardening.
- Locator:
  - Spec locator: .loom/specs/WI-1489/spec.md

## Goal

Complete final regression and closeout verification for milestone/11 after v0.17.1 has been published and WI-1658 release evidence is available.

## Scope

- In scope: regression matrix evidence, release evidence consumption, docs/help and skill payload boundary checks, closeout resolver hardening consumption, #1489 closeout, and parent/phase closeout readiness.
- Out of scope: new runtime implementation, republish, downstream migration, repo-local runtime/plugin/skills installation, single-skill package distribution, and old installer compatibility.

## Key Scenarios

### Scenario S1

Given milestone/11 reaches final closeout
When the regression matrix is read
Then it proves default agent-safe stdout, configurable budgets, artifact locator behavior, and explicit full-output behavior are covered.

### Scenario S2

Given v0.17.0 established the support boundary
When docs/help and skill payload evidence is consumed
Then supported operation is global `loom` CLI plus Codex user-level plugin with metadata-only host repositories.

### Scenario S3

Given #1493 was retained as a closeout blocker
When final closeout consumes it
Then it is recorded as identity-binding hardening, not as the context-budget runtime fix.

### Scenario S4

Given #1658 published v0.17.1
When final closeout runs
Then tag, GitHub Release, npm, workflow, installed CLI smoke, and #1658 closeout carrier evidence are all consumed before #1489 closes.

## Acceptance Criteria

- [ ] A1: Regression evidence covers output envelope, budget defaults, configurable overrides, artifact locator, and explicit `--full-output`.
- [ ] A2: Docs/help evidence confirms no supported-path recommendation for repo-local plugin/runtime/skills, single-skill package distribution, or old installer compatibility.
- [ ] A3: Skill payload evidence confirms Codex user-level plugin calls global `loom` CLI and does not vendor runtime into target repositories.
- [ ] A4: #1493 is consumed as closeout identity-binding hardening.
- [ ] A5: #1658 release evidence is consumed from tag, GitHub Release, npm, workflow, installed CLI smoke, issue closeout, and carrier sync.
- [ ] A6: #1489 can close before parent #1480 and phase #1476 close; parent/phase closeout waits for #1489 evidence.
