# WI-1742 Evidence Map

- Suite path: full.
- Work Item locator: .loom/work-items/WI-1742.md
- Parent locator: https://github.com/MC-and-his-Agents/Loom/issues/1734
- Host issue locator: https://github.com/MC-and-his-Agents/Loom/issues/1742

| evidence_id | evidence_type | source_locator | consumes | binding | freshness | consumer_boundary | remediation_direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | tools/check_cli_contract.py | .loom/specs/WI-1742/spec.md S1 S2 S3 | WI-1742 / ship-wrapper fixture / branch work/1742-closeout-e2e | present | review / merge-ready / PR gate | Re-run after ship apply, closeout policy, or fixture sequencing changes. |
| EV-002 | test_evidence | tools/check_cli_contract.py | EV-001 | WI-1742 / ship-wrapper fixture group | present | review / merge-ready / PR gate | Re-run `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --fixture-group ship-wrapper` after fixture or ship changes. |
| EV-003 | fresh_verification_input | .loom/progress/WI-1742.md | EV-001 EV-002 | WI-1742 / latest validation summary | present | merge-ready / PR gate / closeout / status | Refresh latest validation summary, PR body machine carrier, and review record after every non-carrier PR head change. |

## Not Required Items

- Locator: real release publish, GitHub Release, npm publish, GitHub permission model changes.
- Rationale: #1742 only adds deterministic ship closeout regression coverage; #1743 owns release.
- Recheck condition: starting #1743 or a future permission-model issue.
- Consumers that should not require it: WI-1742 review, merge-ready, and closeout.
