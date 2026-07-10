# WI-1487 Spec

## Suite Contract

- Suite path: minimal
- Full-suite-artifacts not_applicable: artifacts: suite-index.md, research.md, contracts.md, readiness-checklist.md; rationale: WI-1487 is a bounded docs/contract Work Item for thread rotation and handoff rules, with no external host contract, research, or readiness discovery need. consumer boundary: suite validate, review, PR gate, merge-ready, dependent issue #1486, and issue closeout may consume this minimal suite plus focused documentation validation for the thread handoff contract only. recheck condition: require full suite artifacts if scope expands into scheduler behavior, CLI implementation, plugin command examples, security/privacy policy, or external-visible host writes.
- Consumes:
  - Work Item / FR locator: https://github.com/MC-and-his-Agents/Loom/issues/1487
  - Story Readiness confirmed locator, blocking locator, or skip rationale: issue body and milestone dependency update are the planning source for this docs/contract item.
  - Story scenario locator, or skip rationale: scenarios are defined below.
  - Story Business Confirmation confirmed locator, blocking locator, or skip rationale: no external business semantics.
- Produces:
  - Scenario ids / locators: S1, S2, S3 in this file.
  - Acceptance ids / locators: A1-A4 in this file.
  - Behavior evidence expectation: updated recovery model and handoff output contract documentation.
- Locator:
  - Spec locator: .loom/specs/WI-1487/spec.md
- Provenance:
  - Source issue / PR / doc / conversation locator: issue #1487.
  - Freshness rule: recheck after changes to thread rotation triggers, handoff package fields, artifact locator rules, or generated/plugin mirrors.

## Goal

- Define when an agent should rotate to a new thread and what minimum handoff package the next thread must consume.
- Preserve the v0.17.0 runtime boundary: global `loom` CLI plus Codex user-level plugin, with host repositories limited to adoption metadata and work fact carriers.

## Scope

- In scope: recovery model rules, handoff output contract fields, summary/artifact locator relationship, new-thread read boundary, and source/generated/plugin documentation mirrors.
- Out of scope: scheduler implementation, command example updates owned by #1486, CLI output implementation, release execution, repo-local plugin/runtime/skills compatibility, single-skill package distribution, and old installer compatibility.

## Key Scenarios

### Scenario S1

Given an agent is approaching context budget risk, tool output pollution, rising handoff/resume cost, or a required executor change
When the current thread reaches a safe stop
Then it must prepare a bounded thread rotation handoff package instead of relying on prior conversation history.

### Scenario S2

Given a new thread resumes the Work Item
When it consumes the handoff package
Then it reads the summary and authoritative locators first, and only reads old full turns when explicitly auditing prior conversation content.

### Scenario S3

Given a handoff package points to full diagnostics
When the new thread needs details beyond the bounded summary
Then it uses the explicit artifact locator, while treating artifacts as diagnostic evidence rather than authoritative truth carriers.

## Behavior Evidence

- Scenario coverage:
  - S1 -> recovery model thread rotation trigger rules.
  - S2 -> recovery model new-thread consumption boundary.
  - S3 -> handoff output contract `thread_rotation_package` artifact locator rules.
- Expected evidence locator: .loom/specs/WI-1487/evidence-map.md
- Freshness rule: evidence must be rerun after recovery model, handoff output contract, or generated/plugin mirror changes.

## Exceptions And Boundaries

- Failure modes: missing handoff package fields require the new thread to stop and rebuild from authoritative fact carriers before continuing.
- Operational boundaries: full diagnostics are opt-in artifacts, not repo-local runtime directories and not replacement truth carriers.
- Rollback or fallback expectations: revert documentation and mirror changes if a later implementation defines a different handoff package contract.

## Acceptance Criteria

- [x] A1: Thread rotation triggers are documented for context budget risk, tool output pollution, rising handoff/resume cost, and executor change.
- [x] A2: Minimal handoff package fields are documented, including item id, branch, PR, `head_sha`, optional `run_id`, fact carrier locators, bounded summary, artifact locator, stop/next/blockers, and validation summary.
- [x] A3: New-thread consumption rules prioritize summary and authoritative locators before old conversation turns.
- [x] A4: Full diagnostics remain explicit artifacts and do not restore repo-local plugin/runtime/skills paths.
