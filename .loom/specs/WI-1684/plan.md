# WI-1684 Plan

## Suite Contract

- Suite path consumed: minimal
- Spec locator: .loom/specs/WI-1684/spec.md
- Scenario locators: .loom/specs/WI-1684/spec.md#s1-high-risk-classes-cannot-use-light and .loom/specs/WI-1684/spec.md#s2-existing-light-paths-still-work
- Acceptance locators: .loom/specs/WI-1684/spec.md#acceptance-criteria
- Plan locator: .loom/specs/WI-1684/plan.md
- Provenance: GitHub issue #1684.
- Freshness rule: Re-run validation after runtime, generated mirror, fixture, or contract doc changes.

## Implementation

1. Add `workflow`, `metadata_schema`, `host_write`, and `permissions` to the governance change-class vocabulary.
2. Treat those classes as high-risk for attempted `light` governance.
3. Reuse existing metadata and PR gate fixtures to prove the new classes block when declared as `light`.
4. Regenerate the checked-in skills/plugin surfaces.

## Validation

- A1 -> `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface pr-metadata`
- A2 -> `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface pr-metadata`
- A3 -> `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface aggregate`
- Acceptance mapping: A1 -> pr-metadata structural check; A2 -> pr-metadata and PR gate abuse fixtures; A3 -> aggregate CLI contract check.
- Generated surface -> `PYTHONDONTWRITEBYTECODE=1 python3 tools/skills_surface.py check`
- Syntax -> `PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py src/skills/shared/scripts/loom_flow.py skills/shared/scripts/loom_flow.py plugins/loom/skills/shared/scripts/loom_flow.py tools/check_cli_contract.py`

## Constraints

- Keep the change limited to classification vocabulary, fixtures, generated mirrors, and the contract doc.
- Do not implement ship, closeout policy, or host-write behavior in this Work Item.
