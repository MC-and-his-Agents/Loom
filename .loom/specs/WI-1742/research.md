# WI-1742 Research

## Existing Coverage

- `assert_ship_apply_wrapper_contract` already covers the main apply sequence through metadata repair, carrier refresh, shadow parity, PR gate, controlled merge, reconciliation, and closeout check for a light case.
- `assert_ship_closeout_policy_admission_contract` already verifies reinforced/security closeout policy blocks before merge.
- `assert_merge_closeout_run_wrapper_contract` covers explicit merge closeout run and host-only closeout wrapper behavior.

## Gap

The existing coverage did not make the #1742 acceptance explicit for standard ordinary delivery, target branch merge containment readback, release closeout admission, or versioned terminal carrier upgrade behavior.

## Decision

Add a focused ship-wrapper regression fixture that covers:

- light ordinary PR host-only readback;
- standard ordinary PR host-only readback;
- release and versioned terminal carrier admission blockers.
