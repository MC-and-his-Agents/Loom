# WI-775 Spec

## Goal

Expose adoption intent as an explicit bootstrap input and output so Loom does not silently choose heavy execution-control adoption from repository signals alone.

## Acceptance Criteria

- `loom-init bootstrap` accepts `--intent observe-only|skill-install-only|attach-only|light-governance|execution-control|strong-governance`.
- Intake JSON can declare `adoption_intent`, and CLI intent overrides intake intent when both are present.
- Bootstrap output includes detected repository mode, requested/effective adoption intent, risk summary, planned writes, and intentionally absent targets.
- Dry-run planned writes include the stable Loom, companion, release, shadow, runtime, PR-template, and gitignore carriers the bootstrap path may write.
- Ambiguous full-bootstrap writes block when intent is unspecified and do not create heavy execution-control carriers.
- Explicit `attach-only` can write companion/read surfaces without authoring Loom work item, progress, or status truth.
- Explicit `execution-control` can still write full-bootstrap execution carriers.
- Generated skills surfaces and the example new-project fixture are regenerated from source.

## Non-goals

- Do not define the full scaffold profile matrix for every intent; #778 owns profile formalization.
- Do not enforce all attach-only forbidden carrier checks; #784 owns host truth protection hardening.
- Do not stop placeholder release target generation; #780 owns that behavior change.
