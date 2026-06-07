# Execution Breakdown

| Unit | Scope | Owner | Status | Validation |
| --- | --- | --- | --- | --- |
| unit-1322-1 | Docs-governance lite metadata and PR gate consumption behavior. | R3-T8 | done | `python3 tools/check_cli_contract.py --surface aggregate`; pr-gate fixture |
| unit-1322-2 | Runtime copy and generated skill surface synchronization. | R3-T8 | done | `python3 tools/skills_surface.py check`; targeted py compile |
| unit-1322-3 | WI-1322 carrier/status/review evidence. | R3-T8 | in_progress | fact-chain; suite validate; current-head review; PR gate dry check |
