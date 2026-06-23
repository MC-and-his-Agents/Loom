# WI-1740 Implementation Contract

## Implementation Scope

- Add explicit generated-only drift classification to review head binding payloads.
- Preserve carrier-only behavior and existing semantic drift blockers.
- Surface generated-only validation actions without running broad policy engines inside the classifier.
- Keep classification path-based and deterministic for #1740.

## Non-Goals

- Do not auto-run generated repair or carrier refresh from the classifier.
- Do not weaken source, behavior, test, workflow, permission, release, or host-write review requirements.
- Do not introduce a new review artifact schema.
