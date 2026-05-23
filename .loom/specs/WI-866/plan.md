# WI-866 Plan

1. Update harness closeout documentation to freeze the closeout gate profile layers.
2. Extend `loom_flow.py closeout` with gate profile selection and host evidence fixture inputs.
3. Add structured gate/subcheck output for retained evidence backlink consumption.
4. Add adversarial closeout fixtures for fresh, stale, drifted, unreadable, source profile, and no implicit pre-review cases.
5. Regenerate the root `skills/` installation surface and stable demo runtime copies.
6. Validate with compile checks, skills surface checks, targeted closeout fixtures, `make loom-check`, `make check`, PR checks, and post-merge closeout.
