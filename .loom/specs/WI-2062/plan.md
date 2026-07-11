# Plan

## Suite Contract

- Suite path consumed: minimal
- Spec locator: `.loom/specs/WI-2062/spec.md`
- Freshness: rerun focused and generated-surface checks after any source or test change.

## Phases

1. Add a small blocker-state classifier and use it in merge checkpoint evaluation.
2. Add focused regressions for Core, App, and real-blocker shapes.
3. Sync generated distribution surfaces and run targeted plus repository checks.
4. Author current-head review carrier, push a ready PR, and read back hosted checks.

## Constraints

- Preserve fail-closed behavior for ambiguous or genuinely blocking text.
- Do not modify WebEnvoy product repositories.
- Do not alter review binding, required checks, or closeout eligibility.
