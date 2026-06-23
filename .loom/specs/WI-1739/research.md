# WI-1739 Research

## Inputs

- Issue #1739 requires metadata repair, carrier refresh, and shadow parity in the ship preflight repair chain.
- Prior lanes provide stable binding inference, carrier refresh readback, and review freshness classification.

## Findings

- `handle_ship` already performs safe PR metadata update on `--apply`.
- Carrier refresh and shadow parity are available through `loom_flow.py` and can be sequenced before PR metadata preflight.
- Existing ship wrapper tests can stub the delegated flow calls without adding external dependencies.
