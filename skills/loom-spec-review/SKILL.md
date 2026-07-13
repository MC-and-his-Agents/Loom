---
name: loom-spec-review
description: Review specification semantics through the public review and host-attestation path.
---

# Loom Spec Review

This scenario applies the repository's semantic review policy to specification
or contract changes. The review kind belongs to the host artifact, not a repo
`.loom/reviews/**` record.

1. Pass `loom pre-review` for the real PR/current head.
2. Review scope, invariants, dependencies, failure behavior, and validation
   claims using the repository-native diff and tests.
3. Publish the verdict through the approved GitHub review/check workflow.
4. Consume it with `loom review` or `loom attestation readback` using the
   current-head artifact locator.

Fail closed when the artifact cannot authenticate the PR/head, review kind,
semantic tree, run, verifier, and digest. Never restore `spec-review`, `review
record`, suite carrier, or spec carrier commands.
