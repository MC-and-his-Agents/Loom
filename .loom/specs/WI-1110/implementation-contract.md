# WI-1110 Implementation Contract

## Owned Files

- `tools/loom.py`
- `tools/check_cli_contract.py`
- `.loom/work-items/WI-1110.md`
- `.loom/progress/WI-1110.md`
- `.loom/status/current.md`
- `.loom/specs/WI-1110/spec.md`
- `.loom/specs/WI-1110/plan.md`
- `.loom/specs/WI-1110/implementation-contract.md`
- `.loom/reviews/WI-1110.spec.json`
- `.loom/reviews/WI-1110.json`

## Contract

- `loom suite inspect` remains read-only and emits `mutates: false`.
- Suite artifact locators inside payload remain repo-relative.
- Explicit path decisions may be read from `suite-index.md`, `spec.md`, or `plan.md`.
- Missing required locators are reported as inspect-only gaps, not readiness verdicts.
- Unknown path fallback remains compatible with #1109.

## Non-Goals

- No `suite validate`.
- No scaffold apply behavior.
- No evidence freshness, HEAD binding, PR binding, review, merge-ready, closeout, or Project truth decisions.
