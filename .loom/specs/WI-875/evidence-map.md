# Evidence Map

| evidence_id | evidence_type | source_locator | consumes | binding | freshness | consumer_boundary | remediation_direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | src/skills/shared/scripts/loom_flow.py | .loom/specs/WI-875/spec.md S2 / A2 / A4 | WI-875 / parser unsupported-version diagnostic | present | pre-review / review / merge-ready / closeout / status | Re-run direct unsupported parser-version smoke after parser changes. |
| EV-002 | test_evidence | src/skills/shared/scripts/loom_check.py | .loom/specs/WI-875/spec.md S1 S2 S3 / A1 A2 A3 | WI-875 / focused PR metadata fixture expansion | present | review / merge-ready / closeout / status | Re-run `python3 tools/loom_check.py --profile source --source-surface contract-only .` after fixture changes. |
| EV-003 | fresh_verification_input | .loom/progress/WI-875.md | EV-001 EV-002 plus git diff, focused rg, skills surface, loom_check, CLI contract, suite, fact-chain, and shadow parity checks | WI-875 / latest validation summary / PR #1194 | present | merge-ready / closeout / status | Refresh progress summary after PR creation, head changes, or additional validation. |
