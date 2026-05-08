# Plan

## Implementation Goal

Complete the first FR-scoped v0.8.0 batch by adding execution attempt observability while preserving the Work Item and recovery fact chain as the only authored progress truth.

## Phases

### Phase 1

- Objective: freeze the attempt contract.
- Deliverable: `docs/methodology/harness/execution-attempt.md` and shared runtime reference.
- Exit condition: the contract names stable fields, freshness rules, failure vocabulary, and forbidden authored progress fields.

### Phase 2

- Objective: emit runtime attempt evidence from key flows.
- Deliverable: shared `loom_flow.py` attempt envelope builder/persister and flow output summaries.
- Exit condition: flow output includes `execution_attempt.evidence.locator` and the persisted latest envelope can be re-read.

### Phase 3

- Objective: expose latest attempt evidence in status.
- Deliverable: `loom_status` latest-attempt payload with fresh/stale/missing classifications.
- Exit condition: status reports fresh evidence for current item/HEAD and refuses to present stale evidence as fresh.

### Phase 4

- Objective: prove attempts remain evidence only.
- Deliverable: `loom_check` fixtures for fresh, missing, stale, and forbidden-authored-field envelopes.
- Exit condition: `next_step` duplication fails validation and missing evidence is marked missing.

## Constraints

- Do not write authored progress fields into attempt envelopes.
- Keep attempt evidence under runtime evidence paths; do not add tracked attempt output.
- Do not broaden into `#566` dynamic tool handshake semantics.
- Close only child Work Items whose truth is absorbed by this PR after merge.

## Validation

- Automated checks: `python3 -m py_compile`, `python3 tools/skills_surface.py check`, `python3 tools/loom_flow.py flow resume --target . --item WI-561`, `python3 tools/loom_status.py --target . --item WI-561`, `python3 tools/loom_check.py`, and `make check`.
- Manual checks: inspect `git status` after attempt emission to confirm `.loom/runtime/attempts/` is ignored and no tracked attempt evidence appears.
- Runtime evidence: `.loom/runtime/attempts/WI-561/latest.json` is local runtime evidence and not a committed truth carrier.
- Behavior evidence: `loom_check` execution-attempt fixtures cover fresh/missing/stale/forbidden-field boundaries.
- Fresh verification evidence: current branch `HEAD` after all implementation and generated surface edits.
- Execution ledger plan locator: `.loom/specs/WI-561/plan.md`.
- Execution ledger validation evidence locator: `make check`.

## Test Strategy

- Preserve existing repo checks and installed-skill positive/negative samples.
- Add focused synthetic fixture coverage for attempt envelope validation.
- Verify installed skill flows expose attempt summaries through generated runtime packages.
- Run full `make check` before review and merge-ready.

## Ready For Implementation

- [x] Spec is stable enough to implement.
- [x] Scope and non-goals are clear.
- [x] Validation path is defined.
- [x] BDD outer-loop scenarios map to validation.
- [x] TDD inner-loop expectations map to repository checks.
- [x] Risks and dependencies are explicit.
