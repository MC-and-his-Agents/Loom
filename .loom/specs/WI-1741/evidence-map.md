# WI-1741 Evidence Map

- Suite path: full.

| evidence_id | evidence_type | source_locator | consumes | binding | freshness | consumer_boundary | remediation_direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | tools/loom.py | .loom/specs/WI-1741/spec.md S1 S2 S3 | WI-1741 / ship validation profile selection / branch work/1741-validation-profile | present | review / merge-ready / PR gate | Re-run after ship changed-path, profile mapping, output payload, or apply/dry-run sequencing changes. |
| EV-002 | test_evidence | tools/check_cli_contract.py | EV-001 | WI-1741 / ship-wrapper fixture group | present | review / merge-ready / PR gate | Re-run `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --fixture-group ship-wrapper` after selector or docs contract changes. |
| EV-003 | behavior_evidence | README.md | .loom/specs/WI-1741/spec.md S1 S2 S3 | WI-1741 / ship documentation contract across README.md, README.zh-CN.md, and docs/methodology/harness/cli-command-matrix.md | present | review / merge-ready / closeout | Re-run ship wrapper fixture after ship docs change. |
| EV-004 | test_evidence | tools/skills_surface.py | EV-003 | WI-1741 / generated skills/docs surface check | present | review / hosted checks | Re-run `PYTHONDONTWRITEBYTECODE=1 python3 tools/skills_surface.py check` after docs or skills surface changes. |
| EV-005 | test_evidence | tools/check_npm_package.py | tools/loom.py | WI-1741 / package payload hash readback | present | review / release-boundary readback | Re-run `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_npm_package.py --surface plugin-payload-hash` after package/plugin payload changes. |
| EV-006 | fresh_verification_input | .loom/progress/WI-1741.md | EV-001 EV-002 EV-003 EV-004 EV-005 | WI-1741 / latest validation summary | present | merge-ready / PR gate / closeout / status | Refresh latest validation summary, PR body machine carrier, and review record after every non-carrier PR head change. |
