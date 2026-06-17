# WI-1542 Implementation Contract

## Owned Changes

- Update retained Work Item lookup ranking in `src/skills/shared/scripts/loom_flow.py`.
- Regenerate runtime copies under `skills/**/.loom-runtime/shared/scripts/loom_flow.py` and `skills/shared/scripts/loom_flow.py`.
- Add focused retained lookup regression coverage in `test/retained_item_lookup_test.py`.

## Required Behavior

- Canonical issue ownership evidence wins over historical recovery text mentions.
- Same-strength retained lookup ambiguity remains blocking.
- Legacy weak-only retained lookup remains supported when no stronger candidate exists.
- Closeout readback for issue #1544 resolves to `WI-1544` instead of ambiguous historical mentions.

## Forbidden Changes

- Do not implement closeout queue UX, hosted admission, classifier vocabulary, closeout profile semantics, release behavior, or external host writes.
- Do not change #1531-#1534 closeout profile semantics.
- Do not edit shared truth carriers outside WI-1542-owned carrier, review, shadow, and status refresh required for this PR.

## Validation Contract

- Compile affected Python entrypoints.
- Run focused retained lookup regression tests.
- Run #1544 closeout check readback against the post-#1544 closeout state.
- Verify generated skill runtime parity and package metadata.
- Run suite validation, carrier refresh, shadow parity, fact-chain, PR metadata preflight, and PR gate before merge-ready.
