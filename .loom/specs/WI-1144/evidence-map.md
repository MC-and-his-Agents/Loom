# Evidence Map

| evidence_id | evidence_type | source_locator | consumes | binding | freshness | consumer_boundary | remediation_direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | tools/check_npm_package.py | .loom/specs/WI-1144/spec.md S1 / A1-A2 | WI-1144 / package payload suite docs | present | package evidence only | Re-run python3 tools/check_npm_package.py after package manifest changes. |
| EV-002 | behavior_evidence | tools/loom.py | .loom/specs/WI-1144/spec.md S2 / A3 | WI-1144 / release-check aggregation | present | release-check evidence only | Re-run python3 tools/loom.py skills release-check --json after release surface changes. |
| EV-003 | test_evidence | tools/check_cli_contract.py | .loom/specs/WI-1144/plan.md validation commands | WI-1144 / CLI contract fixtures | present | CLI contract evidence only | Re-run python3 tools/check_cli_contract.py. |
| EV-004 | test_evidence | test/npm-package-smoke.test.mjs | .loom/specs/WI-1144/spec.md S3 / A4 | WI-1144 / npm smoke | present | npm package smoke evidence only | Re-run node --test test/npm-package-smoke.test.mjs. |
| EV-005 | fresh_verification_input | .loom/progress/WI-1144.md | EV-001 EV-002 EV-003 EV-004 | WI-1144 / latest validation summary | present | review / merge-ready / closeout evidence | Refresh progress summary after final validation. |
