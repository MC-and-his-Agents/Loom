# WI-1031 Implementation Contract

## Ownership

This WI owns the `loom-story` skill instructions and references that decide whether story semantics may enter formal spec / plan shaping.

## Allowed Files

- `src/skills/loom-story/SKILL.md`
- `src/skills/loom-story/references/input-signals.md`
- `src/skills/loom-story/references/output-contract.md`
- generated `skills/loom-story/**` copies of the same surfaces
- generated `skills/*/.loom-runtime/loom-story/**` copies of the same surfaces
- `.loom/work-items/WI-1031.md`
- `.loom/progress/WI-1031.md`
- `.loom/specs/WI-1031/**`
- `.loom/reviews/WI-1031*.json`
- `.loom/status/current.md`
- `.loom/bootstrap/init-result.json`
- `.loom/progress/WI-1030.md` only to terminalize inherited closed #1030 carrier state

## Forbidden Scope

- #1029 story intake authority redesign.
- #1030 user-story scaffold locator fields.
- #1032 spec-suite entry consumption rules.
- Delivery planning, task carrier, evidence-map, consistency-analysis, gate-chain, or CLI automation changes.

## Completion Evidence

- PR #1098 merged to `main`.
- #1031 closed as completed and Project Done.
- #1015 progress comment links #1031 closeout.
- #1032 remains the next open Work Item for spec-suite entry consumption.
