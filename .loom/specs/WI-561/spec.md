# Spec

## Goal

Deliver the `#561` execution attempt envelope for v0.8.0/#531 so Loom can observe key command attempts without letting those attempts become a second authored truth source.

## Scope

- In scope: `execution_attempt` contract documentation, runtime attempt evidence persistence, flow output summaries, status latest-attempt read surface, and fixtures for evidence boundaries.
- In scope: flow operations `resume`, `pre-review`, `spec-review`, `review`, and `merge-ready`.
- In scope: generated installed-skill surface parity for shared runtime scripts and references.
- Out of scope: dynamic tool handshake result vocabulary, approval/sandbox read surface, structured event evidence, deterministic review engine profile evidence, context-pack repeated blocker semantics, installed upgrade rehearsal, and `loom-build`.

## Key Scenarios

### Scenario 1

Given a Loom flow command consumes the current Work Item fact chain

When the flow emits its result

Then the output includes an `execution_attempt` summary with an attempt id, result, failure category, fallback target, and evidence locator.

### Scenario 2

Given a latest attempt evidence file exists for the current item and current HEAD

When `loom_status` reads the repository

Then status exposes the latest attempt as fresh runtime evidence without treating it as a gate verdict.

### Scenario 3

Given latest attempt evidence is missing or bound to an older HEAD

When status reads the attempt surface

Then the attempt is marked `missing` or `stale` and is not displayed as fresh.

### Scenario 4

Given an attempt envelope duplicates recovery-authored fields such as `next_step`

When the envelope is validated

Then validation blocks the envelope as parallel truth risk.

## Behavior Evidence

- Scenario coverage: `python3 tools/loom_flow.py flow resume --target . --item WI-561`, `python3 tools/loom_status.py --target . --item WI-561`, and `python3 tools/loom_check.py`.
- Expected evidence locator: `.loom/runtime/attempts/<item-id>/latest.json` for local runtime evidence and `loom_check` execution-attempt fixtures for contract coverage.
- Freshness rule: latest attempt evidence is fresh only when `item_id` and `head_sha` match the current fact-chain item and current git HEAD.
- Execution ledger acceptance locator: `.loom/specs/WI-561/spec.md`.

## Acceptance Criteria

- [x] `execution_attempt` contract documents the stable fields and forbids authored progress duplication.
- [x] Key `flow` operations emit attempt summaries with evidence locators.
- [x] `loom_status` exposes latest attempt evidence with fresh/stale/missing status.
- [x] Fixtures reject `next_step` duplication and mark missing evidence correctly.
- [x] `make check` passes without tracked runtime attempt drift.
