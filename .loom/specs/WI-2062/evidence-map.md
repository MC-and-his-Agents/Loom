# Evidence Map

| ID | Kind | Locator | Claim | Freshness |
| --- | --- | --- | --- | --- |
| EV-001 | hosted regression | Core PR #273 / App PR #281 gate runs | Explicit non-blocking text currently produces block with empty missing_inputs | Recheck after hosted CLI release |
| EV-002 | passing comparison | Harbor PR #253 | Exact `None recorded.` passes the same gate path | Stable at PR head acf0f605 |
| EV-003 | implementation | `src/skills/shared/scripts/loom_flow.py` | Blocker classifier owns checkpoint decision | Recheck after source edit |
| EV-004 | automated test | `tools/check_cli_contract.py` | Core/App pass and real blocker fails closed | Recheck after source/test edit |
