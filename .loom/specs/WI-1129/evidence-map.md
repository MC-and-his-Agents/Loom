# WI-1129 Evidence Map

## Context

- Work Item locator: .loom/work-items/WI-1129.md
- FR parent locator: https://github.com/MC-and-his-Agents/Loom/issues/1126
- Scope: suite evidence scaffold dry-run / apply CLI automation
- Suite path: minimal
- Current HEAD: branch `work/1129-suite-evidence-scaffold`
- PR locator: pending
- Host state locator: https://github.com/MC-and-his-Agents/Loom/issues/1129

## Evidence Rows

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | .loom/specs/WI-1129/spec.md | Scenario S1; Scenario S2; Scenario S3 | WI-1129 current branch | present | #1129 suite evidence scaffold only | Refresh spec scenarios if the command scope changes. |
| EV-002 | test_evidence | tools/check_cli_contract.py | A1; A2; A3; A4; A5 | WI-1129 current branch | present | #1129 suite evidence scaffold only | Rerun CLI contract checks after changing command output or fixtures. |
| EV-003 | fresh_verification_input | .loom/progress/WI-1129.md | EV-001 EV-002 | WI-1129 current branch | present | #1129 suite evidence scaffold only | Update Latest Validation Summary with current command results before PR gate. |
