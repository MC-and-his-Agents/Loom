# Implementation Contract

## Work Item

- Item: `WI-561`
- Execution Entry: `.loom/work-items/WI-561.md`

## Approved Spec

- Spec Path: `.loom/specs/WI-561/spec.md`
- Spec Review Entry: `.loom/reviews/WI-561.spec.json`

## Implementation Scope

- In Scope: execution attempt contract, key flow attempt summaries, status latest-attempt read surface, attempt envelope fixtures, and generated installed-skill parity.
- Out Of Scope: dynamic tool handshake, approval/sandbox policy read surface, structured event evidence, review engine profile determinism, repeated blocker context packs, installed upgrade rehearsal, and `loom-build`.

## Validation Plan

- Automated Checks: `python3 -m py_compile`, `python3 tools/skills_surface.py check`, `python3 tools/loom_flow.py flow resume --target . --item WI-561`, `python3 tools/loom_status.py --target . --item WI-561`, `python3 tools/loom_check.py`, `make check`.
- Manual Verification: attempt evidence is ignored under `.loom/runtime/attempts/` and no tracked attempt output remains after checks.

## Risks And Rollback

- Risks: attempt evidence could accidentally duplicate recovery progress or be mistaken for a gate verdict.
- Mitigation: envelope validation rejects authored progress fields, status reports freshness separately, and attempts stay under runtime evidence paths.
- Rollback Boundary: remove attempt emission/status display and retain the documented contract as not implemented only if the runtime evidence path blocks existing flows.

## Host Binding

- Pull Request: to be created from `work/561-execution-attempt-envelope`.
- Reviewed Head: current branch head after validation.
