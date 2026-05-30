# Execution Breakdown

| unit_id | objective | owner | inputs | outputs | validation |
| --- | --- | --- | --- | --- | --- |
| unit-1153-1 | Add non-mutating closeout/reconciliation fixture inputs | #1153 worker | `skills/shared/scripts/loom_flow.py` | issue/PR/Project payload fixture flags | focused closeout/reconciliation fixture checks |
| unit-1153-2 | Add governance chain integration fixture | #1153 worker | `tools/check_cli_contract.py` | pass and PR-merged-alone negative assertions | `python3 tools/check_cli_contract.py` |
| unit-1153-3 | Sync carriers and generated surfaces | #1153 worker | WI-1153 formal suite carriers | source/generated/runtime parity | `python3 tools/skills_surface.py check` |
