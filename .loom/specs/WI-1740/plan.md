# WI-1740 Plan

- Suite path consumed: minimal

## Implementation

| phase | work | validation |
| --- | --- | --- |
| P1 | Extend review head binding payloads with carrier, generated, and semantic drift path buckets. | `python3 -m py_compile skills/shared/scripts/loom_flow.py src/skills/shared/scripts/loom_flow.py .loom/bin/loom_flow.py` |
| P2 | Allow generated-only freshness through semantic disposition, approval lint, retained PR gate, and closeout backlink consumers while preserving semantic drift blockers. | `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --fixture-group pr-metadata` |
| P3 | Add a focused generated-only fixture next to existing carrier-only and implementation drift regression coverage. | `git diff --check`; pr-metadata fixture group |

## Merge Boundary

This issue is limited to review freshness classification and focused regression coverage. Ship repair-chain automation, validation profile selection, e2e closeout behavior, and release closeout remain in their own issues.
