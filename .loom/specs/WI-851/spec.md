# WI-851 Spec

## Outcome

Governance Lint has versioned negative fixtures that prove common bypass attempts fail closed and remain derived evidence rather than a second authored truth source.

## Acceptance

- A machine-readable fixture manifest covers raw review approval bypass, PR body approval bypass, CI success approval bypass, repo companion bypass, repo interop locator misuse, downstream guardian hardcode, advanced architecture lint declaration missing, and stale evidence / head drift.
- Each fixture declares expected failure taxonomy, strength, surface, fallback, synthetic source mode, and no temporary authored truth carrier.
- `loom_check.py` consumes the fixture manifest and fails if any required case, taxonomy, source mode, or consumer binding is missing.
- repo-local runtime fixtures exercise PR body, CI-success-only, raw-only, `spec_review`, and stale review/head drift fail-closed behavior.
- companion boundary, interop locator misuse, advanced lint declaration, and hardcoding guard fixtures are consumed through existing repo-local governance surface and fixture-contract checks.
- The implementation does not add a standalone `loom lint` command and does not copy downstream guardian or business repository rules into Loom core.

## Non Goals

- Do not implement repo-specific architecture lint content.
- Do not use a real downstream repository as a problem detector.
- Do not make Governance Lint output an authored review, recovery, validation, merge-ready, or closeout truth source.
