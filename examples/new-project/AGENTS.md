# Loom Execution

This repository uses Loom to coordinate Work Items, admission/spec, build, review, merge-ready, and closeout.

Before editing files:

1. Run `loom route --target . --task "<request>" --json`; when resuming existing work, run `loom resume --target . --json` first.
2. Advance one clear Work Item at a time; keep unrelated fixes and new scope out of the PR.
3. On the formal spec path, do not implement until `spec.md`, `plan.md`, and `spec_review approved` exist.
4. Follow Loom `next_action` / `fallback_to`; a `block` means repair earlier truth carriers, not bypass the gate.
5. Record validation command, result, and head sha or timestamp in the relevant carrier.
6. After changing code, PR body, review inputs, or carriers, recheck whether review/gate evidence is still fresh.
7. Merge is not completion; run Loom closeout to sync issue, PR, target branch, and carriers.

Use `loom doctor --target . --json` for environment or plugin problems.
