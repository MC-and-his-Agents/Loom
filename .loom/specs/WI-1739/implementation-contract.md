# WI-1739 Implementation Contract

## Implementation Scope

- Add carrier refresh apply and blocking all-surface shadow parity to `loom ship --apply` after safe PR metadata repair and before PR metadata preflight.
- Preserve PR metadata preflight, PR gate, controlled merge check, controlled merge, and closeout sequencing after the repair chain passes.
- Return short blocking diagnostics and a single next action when carrier refresh or shadow parity blocks.
- Add focused ship wrapper contract coverage for the passing sequence and carrier refresh blocker path.
- Keep WI-1739 authored carriers, suite evidence, status, and shadow hashes aligned with the current branch head.

## Non-Goals

- Do not change #1741 validation profile selection.
- Do not implement #1742 inline or host-only closeout e2e regression.
- Do not publish, tag, or otherwise perform #1743 release closeout.
- Do not bypass current-head review, PR gate, or controlled merge requirements.
