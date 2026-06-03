# Evidence Map

| evidence_id | evidence_type | source_locator | consumes | binding | freshness | consumer_boundary | remediation_direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | #1217 correction comment; `loom-cli-release` run 26888581620 | .loom/specs/WI-1294/spec.md S4 / AC-5 | WI-1294 / release diagnosis | present | build / review / closeout | Recheck if #1227 release failure diagnosis changes. |
| EV-002 | test_evidence | `VERSION`; `package.json`; `skills/*/loom-package.json`; local command output for release/version/package/skills checks | .loom/specs/WI-1294/spec.md S1 S2 / AC-1 AC-2 AC-3 | WI-1294 / branch work/1294-release-followup | present | build / review / merge-ready | Rerun local checks after version or generated metadata changes. |
| EV-003 | fresh_verification_input | .loom/progress/WI-1294.md | EV-001 EV-002 | WI-1294 / current branch local verification | present | review / merge-ready | Refresh after `check_cli_contract.py`, `git diff --check`, PR CI, and post-merge release checks. |
