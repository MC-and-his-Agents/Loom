# WI-1071 Plan

## Steps

1. Update the controlled merge contract so `DIRTY` and `DRAFT` remain hard-block mergeability states while `BLOCKED` is interpreted as host policy evidence after the rest of the Loom gate/readback chain passes.
2. Update `loom_flow.py` on source, generated, shared, and installed runtime surfaces.
3. Extend `loom_check` fixtures with the `COMMENTED` guardian plus green checks plus GitHub `BLOCKED` positive case and hard-block mergeability negative cases.
4. Update harness methodology and shared reference docs.
5. Validate py-compile, skills surface, diff hygiene, runtime/reference parity, `source-self-fixture`, and `contract-only`.
6. Open PR #1081, consume required checks, merge, and close #1071-#1076 with PR/head/merge evidence.

## Non-goals

- Do not change GitHub branch protection.
- Do not replace `loom-pr-merge-gate`.
- Do not treat raw guardian, GitHub review comment, or CI evidence as authored approval truth.
