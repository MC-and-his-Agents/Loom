# WI-1737 Plan

- Suite path consumed: minimal

## Implementation

| phase | work | validation |
| --- | --- | --- |
| P1 | Centralize checkpoint normalization on the existing canonical enum helper. | `PYTHONDONTWRITEBYTECODE=1 python3 test/checkpoint_canonicalization_test.py` |
| P2 | Update generated/demo fixtures to persist canonical values. | `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_demo_bootstrap_fixture.py` |
| P3 | Confirm retained item lookup and skills surface remain compatible. | `PYTHONDONTWRITEBYTECODE=1 python3 test/retained_item_lookup_test.py`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/skills_surface.py check` |

## Merge Boundary

This issue is limited to checkpoint value canonicalization and the generated fixture/readback needed by PR #1746.
