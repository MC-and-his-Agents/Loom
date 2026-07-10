# WI-1494 Plan

## Implementation Steps

1. Add `--item` parser support to runtime `closeout` and `reconciliation`.
2. Add explicit retained Work Item lookup that validates the Work Item file and item id.
3. Thread `expected_item` through closeout and reconciliation payloads.
4. Validate explicit item and issue consistency while preserving no-item ambiguity fail-closed behavior.
5. Forward facade `loom reconcile --work-item` into runtime `--item`.
6. Add focused retained lookup and parser regression coverage.
7. Regenerate skills runtime copies from `src/skills`.

## Validation

- `PYTHONDONTWRITEBYTECODE=1 python3 test/retained_item_lookup_test.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py src/skills/shared/scripts/loom_flow.py skills/shared/scripts/loom_flow.py tools/loom_flow.py tools/loom.py test/retained_item_lookup_test.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/skills_surface.py check --surface generated-tree-drift`
- `CODEX_EXPORT_GH_TOKEN=1 GH_TOKEN="$(gh auth token)" PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_flow.py reconciliation sync --target . --item WI-1510 --issue 1510 --pr 1557 --branch work/1510-carrier-shadow-freeze --dry-run`
- `CODEX_EXPORT_GH_TOKEN=1 GH_TOKEN="$(gh auth token)" PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py closeout --target . --item WI-1510 --issue 1510 --pr 1557 --json`
- `git diff --check`

## Test Strategy

- Parser support maps to `test_closeout_and_reconciliation_parse_explicit_item`.
- Explicit disambiguation maps to `test_explicit_item_disambiguates_weak_issue_mentions`.
- Conflict handling maps to `test_explicit_item_conflicting_issue_lookup_fails_closed` and `test_explicit_unrelated_item_does_not_bypass_ambiguous_issue_lookup`.
- Legacy behavior maps to existing historical/canonical/ambiguous retained lookup tests.
- Generated runtime parity maps to `tools/skills_surface.py check --surface generated-tree-drift`.
- Live readback maps to #1510 commands recorded in `.loom/progress/WI-1494.md`.

## Dependencies

- Consumes issue #1494.
- Unblocks #1555 after merge.
- #1554 still owns broader wrapper/default/help contract hardening.
- #1513 still owns broader failure classifier and token bridge taxonomy.

## Scope Guard

- Do not implement #1555 one-shot closeout run.
- Do not change release flow, closeout evidence semantics, hosted admission, or classifier taxonomy.
- Do not update GitHub issue bodies, PR bodies, or shared milestone carriers from implementation code.
