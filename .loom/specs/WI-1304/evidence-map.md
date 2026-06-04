# WI-1304 Evidence Map

| evidence_id | evidence_type | source_locator | consumes | binding | freshness | consumer_boundary | remediation_direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | `python3 .loom/bin/loom_flow.py governance-profile status --target /Users/mc/dev/Loom-worktrees/1264-regression-surface-contract --host github` | .loom/specs/WI-1304/spec.md S1 / A1 A5 | WI-1304 / PR-A docs-only maturity target / current branch head | present | review / merge-ready / closeout evidence for maturity consumption only | Re-run after governance_surface, PR-A carrier, or suite decision changes. |
| EV-002 | test_evidence | `python3 tools/loom_check.py --profile source --source-surface bootstrap-regression .` | .loom/specs/WI-1304/spec.md S2 / A2 A3 A4 | WI-1304 / source bootstrap-regression / root-self-adoption | present | review / merge-ready / closeout evidence for source runtime regression only | Re-run after runtime copy, manifest, init-result, or carrier changes. |
| EV-003 | fresh_verification_input | .loom/progress/WI-1304.md | EV-001 EV-002 | WI-1304 / latest validation summary / current head | present | merge-ready / closeout / status | Refresh progress summary and re-run validation after final review or PR head changes. |
