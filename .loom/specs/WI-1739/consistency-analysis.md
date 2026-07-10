# WI-1739 Consistency Analysis

## Scope Boundary

WI-1739 changes the ship apply preflight repair chain only. It does not change release publication, closeout PR policy, validation profile selection, or review freshness classification.

## Consistency Checks

- Metadata repair remains first because PR body readback can affect downstream preflight.
- Carrier refresh follows metadata repair so derived carrier/shadow inputs are based on repaired metadata.
- Shadow parity follows carrier refresh so stale shadow evidence is caught before PR gate and controlled merge check.
- PR gate remains responsible for implementation drift and current-head review semantics.

## Residual Risk

The repair-chain commands are delegated to `loom_flow.py`; failures are surfaced as blockers rather than retried automatically.
