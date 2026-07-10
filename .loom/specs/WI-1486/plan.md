# WI-1486 Plan

## Suite Contract

- Suite path consumed: minimal
- Full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: WI-1486 is a bounded executable-skill payload text update. consumer boundary: suite validate, review, PR gate, merge-ready, #1488 docs follow-up, #1658 release, and #1489 final closeout may consume this minimal suite and focused skills validation. recheck condition: require full suite artifacts if scope expands into CLI runtime behavior, user docs/help migration, release execution, package metadata, or external-visible host writes.
- Consumes:
  - Spec locator: .loom/specs/WI-1486/spec.md
  - Scenario ids / locators: S1-S3
  - Acceptance ids / locators: A1-A4
  - Story Readiness consumed state: issue #1486 body and v0.17.0 baseline.
  - Story Business Confirmation consumed state: not_applicable.
- Produces:
  - Validation strategy by scenario: focused skills surface checks, stale-command searches, py_compile for generated shared script mirrors, suite validation, carrier validation, and diff check.
  - Test strategy by acceptance: generated tree drift check plus targeted rg checks for old executable command examples and old repo-local CLI JSON wording.
  - Fresh verification evidence expectation: rerun at current PR head before review and PR gate.
- Locator:
  - Plan locator: .loom/specs/WI-1486/plan.md
- Provenance:
  - Source spec / issue / PR / doc locator: .loom/specs/WI-1486/spec.md; issue #1486.
  - Freshness rule: recheck after skill source, generated mirror, plugin payload, or WI carrier changes.

## Implementation Goal

- Replace executable skill command examples and contracts with global `loom` CLI agent-safe summary/artifact locator defaults.
- Synchronize `src/skills`, `skills`, and `plugins/loom/skills`.
- Defer README, migration docs, ordinary help text, release evidence, and final milestone closeout to their owning issues.

## Phases

### Phase 1

- Objective: Update canonical skill source text and shared skill references.
- Deliverable: `src/skills` command examples and output contracts.
- Exit condition: no stale repo-local script examples or repo-local CLI JSON wording remain in the skill payload.

### Phase 2

- Objective: Generate mirrors and record WI-1486 evidence.
- Deliverable: generated `skills`, `plugins/loom/skills`, and Loom carriers.
- Exit condition: targeted skills surface checks, suite checks, and review binding pass.

## Constraints

- Do not update #1488 docs/help/migration content in this PR.
- Do not change CLI runtime behavior, budget constants, artifact writer logic, release metadata, package publishing, or downstream repositories.
- Do not restore repo-local plugin/runtime/skills install paths, single-skill packages, old installer compatibility, or vendored runtime semantics.
- Do not make diagnostic artifacts authored truth carriers.

## Validation

- Automated checks:
  - `python3 tools/skills_surface.py generate`
  - `python3 tools/skills_surface.py check --surface generated-tree-drift --surface plugin-payload-metadata --surface reference-integrity`
  - `rg -n 'python3 scripts/loom-(resume|build|pre-review|review|spec-review|merge-ready|handoff)|repo-local `loom|repo-local CLI JSON' src/skills skills plugins/loom/skills`
  - `python3 -m py_compile src/skills/shared/scripts/loom_flow.py skills/shared/scripts/loom_flow.py plugins/loom/skills/shared/scripts/loom_flow.py`
  - `python3 tools/loom.py suite validate --target . --item WI-1486 --json`
  - `python3 tools/loom.py suite evidence validate --target . --item WI-1486 --json`
  - `python3 tools/loom.py suite carrier validate --target . --item WI-1486 --json`
  - `python3 tools/loom.py fact-chain --target . --json`
  - `python3 .loom/bin/loom_flow.py shadow-parity --target . --surface all --blocking`
  - `git diff --check`
- Manual checks: inspect diff scope remains skills payload plus WI-1486 carriers only.
- Runtime evidence: no live runtime evidence required; this is skill payload text.
- Behavior evidence: .loom/specs/WI-1486/evidence-map.md
- Scenario validation mapping:
  - S1 -> structural: targeted rg check and source/plugin diff.
  - S2 -> structural: output contract diff and targeted rg check.
  - S3 -> structural: handoff output contract diff and targeted rg check.

## Test Strategy

- TDD or test-first expectation: contract text update uses structural checks rather than new runtime unit tests.
- Regression coverage to add or preserve: generated-tree drift, plugin payload metadata, reference integrity, and stale command-string checks.
- Cases intentionally not automated: semantic readability of skill prose; covered by review.
- Acceptance test mapping:
  - A1 -> structural check: targeted rg stale-command check.
  - A2 -> structural check: output contract diff plus generated-tree drift check.
  - A3 -> structural check: handoff output contract diff plus targeted rg stale-output check.
  - A4 -> structural check: skills surface plugin payload checks.

## Dependencies

- Blocking inputs: #1481/#1482 output envelope and budget contract, #1484/#1485 global CLI agent-safe command behavior, and #1487 handoff/thread rotation rules are closed.
- Required coordination: #1488 consumes this skill payload wording when updating user docs/help/migration text.
- Rollback boundary: revert source skill text, generated mirrors, shared skill references, and WI-1486 carriers.

## Ready For Implementation

- [x] Spec is stable enough to implement
- [x] Scope and non-goals are clear
- [x] Story Readiness is covered by issue #1486
- [x] Story business semantics do not apply
- [x] Validation path is defined
- [x] BDD outer-loop scenarios map to validation
- [x] TDD inner-loop expectations are covered by structural checks
- [x] Risks and dependencies are explicit
