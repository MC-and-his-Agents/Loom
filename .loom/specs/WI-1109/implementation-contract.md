# WI-1109 Implementation Contract

## Owned Files

- `tools/loom.py`
- `tools/check_cli_contract.py`
- `.loom/work-items/WI-1109.md`
- `.loom/progress/WI-1109.md`
- `.loom/status/current.md`
- `.loom/specs/WI-1109/spec.md`
- `.loom/specs/WI-1109/plan.md`
- `.loom/specs/WI-1109/implementation-contract.md`
- `.loom/runtime/build/WI-1109.json`

## Contract

- `loom suite inspect` is read-only.
- The command emits `loom-cli-output/v1`.
- Unknown suite state remains `payload.suite_path: unknown`.
- Unsupported `suite` actions fail closed.

## Non-Goals

- No readiness validation.
- No scaffold writes.
- No artifact inventory derivation beyond the unknown fallback.
- No host mutation.
- No review, merge-ready, or closeout truth replacement.
- No spec-kit command names or layout.
