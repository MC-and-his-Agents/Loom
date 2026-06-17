# WI-1542 Plan

## Implementation Steps

1. Split retained Work Item lookup evidence into strong canonical/exact issue ownership and weaker historical text references.
2. Resolve retained lookup from the highest-strength candidate set only.
3. Preserve fail-closed ambiguity when multiple candidates exist at the same highest strength.
4. Add a focused regression for the WI-1544 / WI-1529 / WI-1540 ambiguity.
5. Regenerate skills runtime copies from `src/skills`.

## Validation

- `python3 -m py_compile src/skills/shared/scripts/loom_flow.py skills/shared/scripts/loom_flow.py tools/loom_flow.py test/retained_item_lookup_test.py`
- `python3 test/retained_item_lookup_test.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_flow.py closeout check --target . --issue 1544 --pr 1548 --branch work/1544-lane-orchestration-protocol --gate-profile closeout-contract`
- `git diff --check`
- `python3 tools/skills_surface.py check --surface generated-tree-drift`
- `python3 tools/skills_surface.py check --surface package-metadata`

## Dependencies

- Consumes #1544 closeout evidence as the regression target.
- Soft dependency for #1543 closeout queue/status and #1515 final closeout readback.

## Scope Guard

- Do not edit `.loom/progress/**`, `.loom/status/current.md`, `.loom/reviews/**`, `.loom/shadow/**`, PR body, or issue body outside WI-1542 carrier admission/review.
- Do not implement queue orchestration or closeout profile semantics in this PR.
