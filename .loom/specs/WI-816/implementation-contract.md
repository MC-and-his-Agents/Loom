# WI-816 Implementation Contract

## Allowed Change Surface

- `src/skills/shared/scripts/` runtime sources and generated `tools/` wrappers.
- Generated `skills/` distribution surfaces.
- `examples/new-project` adopted repo scaffold and gate artifacts.
- `packages/loom-installer` drift detection and tests.
- Documentation describing closeout gate provenance, runtime cache hygiene, and story carrier schema.
- Loom Work Item, progress, review, and status carriers for `WI-816`.

## Required Properties

- Repo-declared closeout gates remain first-class and are not bypassed by installed runtime fallback.
- Python cache prevention is enforced by runtime environment and by installer drift detection.
- Story carrier validation is schema-marker based and does not accept unfilled templates.
- Generated files must come from source truth through existing generation commands.

## Exit Criteria

- PR #834 is bound to `WI-816`.
- Merge checkpoint and PR gate consume fresh `WI-816` reviews.
- CI and local validation pass before merge.
- #816, #817, and #818 receive final evidence and closeout after merge.

