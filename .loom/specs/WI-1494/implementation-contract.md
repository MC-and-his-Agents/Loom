# WI-1494 Implementation Contract

## Contract Surface

- Runtime parser: `closeout` and `reconciliation` accept `--item`.
- Lookup behavior: explicit `--item` loads `.loom/work-items/<item>.md` directly and validates the file's authored item id.
- Consistency behavior: when `--issue` is also present, the explicit item must either match the unique issue lookup result or appear among issue lookup candidates; unrelated explicit items fail closed.
- Legacy behavior: no `--item` preserves the existing issue-based retained lookup and ambiguity fail-closed behavior.
- Facade behavior: `loom reconcile --work-item` forwards to runtime `--item`.

## Non-Goals

- No one-shot post-merge closeout run.
- No release flow changes.
- No closeout evidence semantic changes.
- No hosted gate admission or classifier taxonomy changes.

## Validation Binding

- Parser and lookup coverage: `test/retained_item_lookup_test.py`
- Runtime parity: `tools/skills_surface.py check --surface generated-tree-drift`
- Live readback: #1510 closeout/reconciliation commands recorded in `.loom/progress/WI-1494.md`
