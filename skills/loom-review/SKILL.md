---
name: loom-review
description: Perform semantic review and consume a current-head GitHub host attestation.
---

# Loom Review

After `loom pre-review` passes, perform the semantic review, publish its verdict
through the approved GitHub review/check workflow, then authenticate it:

```bash
loom review \
  --target <repo> \
  --item <owner/repo/work_item/id> \
  --issue <id> \
  --pr <pr> \
  --branch <branch> \
  --attestation-artifact-input <artifact.json> \
  --review-policy approved \
  --json
```

Single-maintainer repositories may use `--review-policy single_maintainer` only
when the host artifact proves the allowed assertion. The attestation binds the
current PR head, semantic tree, workflow run, artifact digest, verifier, and
verdict.

Raw review output is not truth. Repo review JSON, current, progress, status,
shadow, authored head fields, and compatibility profiles are not fallbacks.
Pass produces host proof consumable by merge-ready; it does not merge.
