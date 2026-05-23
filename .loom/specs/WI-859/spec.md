# WI-859 Spec

## Outcome

`loom_check.py` supports explicit source and consumer scopes without letting bootstrapped consumer repositories fall into Loom source/distribution asset failures.

## Acceptance

- `loom_check.py [repo-root]` auto-detects Loom source repositories and bootstrapped consumer repositories.
- `--profile source` preserves the Loom source/distribution self-check surface.
- `--profile consumer` validates consumer runtime/adoption carriers and does not require source-only assets such as `examples`, `packages`, `skills`, or `tools`.
- Consumer-facing README, closeout, recovery, and automation guidance describe the consumer validation chain instead of presenting raw source self-check as the default adoption gate.
- Generated skills runtime copies and `examples/new-project` stay synchronized with the source runtime.
- CI source self-check fixtures remain stable in clean runner environments without relying on global git identity.
- Installer version metadata is bumped when generated runtime payload behavior changes.

## Non Goals

- Do not upgrade Syvert's vendored runtime in this Loom PR.
- Do not redesign controlled merge, review approval, or closeout authority.
- Do not add a JSON output mode to `loom_check.py`.
