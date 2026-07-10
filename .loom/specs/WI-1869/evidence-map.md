# WI-1869 Evidence Map

| Evidence ID | Evidence Type | Source Locator | Consumes | Binding | Freshness | Consumer Boundary | Remediation Direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | test_evidence | tools/check_cli_contract.py | S1 / S3 / A1 / A3 / A4 | WI-1869 / current branch | present | review / PR gate / closeout | Rerun `python3 tools/check_cli_contract.py --surface governance-closeout` after reconciliation, review, closeout, or hosted freeze changes. |
| EV-002 | test_evidence | docs/evidence/fixtures/release-readback-fixtures.json | S2 / A2 | WI-1869 / current branch | present | review / release follow-up | Rerun `python3 tools/check_cli_contract.py --surface release-readback` after release readback classification or fixtures change. |
| EV-003 | test_evidence | tools/check_cli_contract.py | A1-A6 | WI-1869 / current branch | present | review / merge-ready | Rerun `python3 tools/check_cli_contract.py --surface aggregate` after any gate, CLI, or payload surface change. |
| EV-004 | test_evidence | plugins/loom/.codex-plugin/plugin.json | plugin payload hash / runtime copy parity | WI-1869 / current branch | present | review / release follow-up | Rerun `python3 tools/loom.py skills release-check --json` after runtime copy changes. |
| EV-005 | behavior_evidence | README.md | S4 / A5 | WI-1869 / docs/help surfaces | present | operator UX | Keep README, README.zh-CN, CLI matrix, and help task routes aligned. |
| EV-006 | carrier_evidence | .loom/bootstrap/init-result.json | runtime carrier refresh | WI-1869 / source runtime copy | present | hosted freeze / package checks | Rerun `carrier refresh --write` after `.loom/bin` runtime changes. |
| EV-007 | fresh_verification_input | .loom/progress/WI-1869.md | EV-001, EV-002, EV-003, EV-004, EV-005, EV-006 / A6 | WI-1869 / current branch | present | review / merge-ready / closeout | Refresh progress validation summary after any verification rerun. |
