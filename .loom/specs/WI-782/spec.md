# WI-782 Spec

## Goal

`loom_init verify` must prove stable Loom carriers are Git-visible, not only present on disk.

## Acceptance

- Verify fails closed when a required stable carrier is ignored by Git.
- Verify reports but does not block when a required stable carrier exists and is Git-visible but untracked, so a new write+verify bootstrap can complete before commit.
- Verify reports the concrete path, profile or capability, reason, and repair guidance.
- Verify does not require `.loom/runtime/**`, `.loom/tmp/**`, `.loom/cache/**`, `.loom/local/**`, `.loom/attempts/**/raw-logs/**`, or `.loom/attempts/**/scratch/**` to be tracked.
- Existing attach-only forbidden carrier checks and blanket `.loom` ignore checks remain intact.
