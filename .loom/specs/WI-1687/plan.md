# WI-1687 Plan

## Suite Contract

- Suite path consumed: minimal
- Spec locator: .loom/specs/WI-1687/spec.md
- Scenario locators: .loom/specs/WI-1687/spec.md#s1-missing-issue-backlink-gets-a-safe-repair-action, .loom/specs/WI-1687/spec.md#s2-render-and-update-preserve-machine-carrier-safety, .loom/specs/WI-1687/spec.md#s3-conflicting-bindings-stay-blocked
- Acceptance locators: .loom/specs/WI-1687/spec.md#acceptance-criteria
- Plan locator: .loom/specs/WI-1687/plan.md
- Provenance: GitHub issue #1687.
- Freshness rule: Re-run validation after runtime, wrapper, generated mirror, fixture, or carrier changes.

## Implementation

1. Add `--issue` to repo-local and runtime PR metadata commands.
2. Render the deterministic `Issue: #N` backlink through the existing PR body artifact path.
3. Extend metadata preflight to identify missing issue backlinks and expose a safe repair action only when machine carrier validation and host readback inputs are trustworthy.
4. Regenerate checked-in skills/plugin mirrors.
5. Add focused CLI contract fixtures.

## Validation

- Acceptance test mapping:
  - A1 -> test evidence: `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface pr-metadata`
  - A2 -> test evidence: `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface pr-metadata`
  - A3 -> test evidence: `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface pr-metadata`
- A1 -> `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface pr-metadata`
- A2 -> `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface pr-metadata`
- A3 -> `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface pr-metadata`
- Generated surface -> `PYTHONDONTWRITEBYTECODE=1 python3 tools/skills_surface.py check`
- Syntax -> `PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py src/skills/shared/scripts/loom_flow.py skills/shared/scripts/loom_flow.py plugins/loom/skills/shared/scripts/loom_flow.py tools/loom.py tools/check_cli_contract.py`
- Closeout regression -> `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface governance-closeout`

## Constraints

- Keep the change limited to PR metadata safe repair.
- Do not implement short human diagnostics, `loom ship`, closeout policy, or release behavior in this Work Item.
