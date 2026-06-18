# WI-1534 Plan

## Implementation Steps

1. Read back #1533/#1555/#1543/#1541 stable fields and identify closeout mode vocabulary already implemented.
2. Update closeout docs with canonical modes, queue/status mapping, closeout-specific gate verdict fields, and escalation boundaries.
3. Update closeout-related skills so merge-ready, pre-review, and retire flows consume closeout mode protocol without turning skills into truth carriers.
4. Add targeted fixture/documentation assertions for closeout mode vocabulary and closeout-specific gate field references.
5. Validate docs/skills references, targeted CLI contract surfaces, suite evidence/carrier, fact-chain, and shadow parity.

## Validation

- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface governance-closeout`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface pr-metadata`
- `python3 tools/skills_surface.py check --surface generated-tree-drift`
- `python3 tools/loom.py suite validate --target . --item WI-1534 --json`
- `python3 tools/loom.py suite evidence validate --target . --item WI-1534 --json`
- `python3 tools/loom.py suite carrier validate --target . --item WI-1534 --json`
- `python3 tools/loom.py fact-chain --target . --item WI-1534 --json`
- `python3 src/skills/shared/scripts/loom_flow.py shadow-parity --target . --surface all --blocking`
