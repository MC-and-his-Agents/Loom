# WI-1542 Implementation Contract

## Owned Changes

- Add the `work-item-audit` runtime payload in `src/skills/shared/scripts/loom_flow.py`.
- Expose `loom workspace audit` in `tools/loom.py`.
- Add CLI contract coverage in `tools/check_cli_contract.py`.
- Regenerate runtime copies under `skills/**/.loom-runtime/shared/scripts/loom_flow.py`, `skills/shared/scripts/loom_flow.py`, and `examples/new-project/.loom/bin/loom_flow.py`.
- Add focused startup audit regression coverage in `test/work_item_audit_test.py`.
- Update the harness CLI command matrix for the new read-only audit surface.

## Required Behavior

- The audit is read-only and does not mutate repo carriers, PR bodies, or host state.
- Host-complete but non-terminal retained carriers block startup with `carrier_closeout_required` and stable classifier `carrier_refresh_needed`.
- Unrelated stale terminal carriers are compact nonblocking samples, not startup blockers.
- Current shadow freshness drift blocks with classifier `shadow_stale`.
- The payload stays compact enough for operator readback by limiting nonblocking samples and summarizing diagnostics.

## Forbidden Changes

- Do not implement hosted freeze admission, closeout queue UX, one-shot post-merge closeout run, closeout profile semantics, release behavior, or external host writes.
- Do not change #1531-#1534 closeout profile semantics.
- Do not invent a duplicate classifier schema; consume existing stable names.
- Do not edit shared truth carriers outside WI-1542-owned carrier, review, shadow, and status refresh required for PR #1568.

## Validation Contract

- Compile affected Python entrypoints.
- Run focused startup audit regression tests.
- Run wrapper/runtime CLI contract checks for `work-item-audit`.
- Verify generated skill runtime parity and demo bootstrap fixture parity.
- Run workspace audit JSON readback, carrier refresh, shadow parity, fact-chain, PR metadata readback, and PR gate before merge-ready.
