# WI-1739 Evidence Map

| Evidence ID | Evidence Type | Source Locator | Consumes | Binding | Freshness | Freshness Rule | Provenance | Consumer Boundary | Remediation Direction |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | tools/loom.py | .loom/specs/WI-1739/spec.md AC-1 AC-2 AC-3 AC-4 AC-5 AC-6 | WI-1739 / ship repair-chain sequencing / branch work/1739-ship-repair-chain | present |  |  | review / merge-ready / PR gate | Re-run ship-wrapper fixture after changing `handle_ship` repair-chain order. |
| EV-002 | test_evidence | tools/check_cli_contract.py | EV-001 | WI-1739 / ship-wrapper fixture group | present |  |  | review / merge-ready / hosted checks | Re-run `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --fixture-group ship-wrapper` after ship apply changes. |
| EV-003 | test_evidence | tools/check_cli_contract.py | metadata repair contract | WI-1739 / pr-metadata surface | present |  |  | review / merge-ready | Re-run `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface pr-metadata` after metadata update behavior changes. |
| EV-004 | test_evidence | tools/check_cli_contract.py | carrier closeout/readback contract | WI-1739 / closeout-wrapper fixture group | present |  |  | review / merge-ready | Re-run `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --fixture-group closeout-wrapper` after carrier refresh sequencing changes. |
| EV-005 | fresh_verification_input | .loom/progress/WI-1739.md | EV-001 EV-002 EV-003 EV-004 | WI-1739 / latest validation summary | present |  |  | merge-ready / PR gate / closeout / status | Refresh latest validation summary and review record after every non-carrier PR head change. |
