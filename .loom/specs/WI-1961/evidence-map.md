# WI-1961 Evidence Map

| Evidence ID | Evidence Type | Source Locator | Consumes | Binding | Freshness | Consumer Boundary | Remediation Direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | .github/PULL_REQUEST_TEMPLATE.md | S1 / A1 | no authored PR body `head_sha` | present | PR metadata preflight / PR gate / review / merge-ready | Recheck after metadata contract or template changes. |
| EV-002 | test_evidence | `python3 tools/check_cli_contract.py --surface pr-metadata`; `--surface pr-gate-target-readback` | S1 / A1 A2 | metadata parser/readback behavior | present | local validation / hosted gate | Rerun after metadata parser, renderer, template, or repo-interface changes. |
| EV-003 | behavior_evidence | .loom/reviews/WI-1961.json | S2 / A3 | digest-bound review validation summary | present | review / PR gate / controlled merge | Refresh review after validation evidence or current head changes. |
| EV-004 | test_evidence | `python3 tools/check_cli_contract.py --surface governance-closeout`; `--surface merge-wrapper` | S2 / A3 | review disposition consumption | present | local validation / hosted gate | Rerun after review disposition or merge wrapper changes. |
| EV-005 | test_evidence | `python3 tools/check_cli_contract.py --surface ship-wrapper` | S3 / A4 | host-consumer and carrier-only profile routing | present | local validation / hosted gate | Rerun after `loom ship` validation profile changes. |
| EV-006 | test_evidence | `python3 tools/check_cli_contract.py --surface aggregate`; `python3 tools/loom.py skills release-check --json` | A5 | generated runtime/plugin/package consistency | present | release-check / hosted checks | Rerun after generated files or plugin payload metadata changes. |
| EV-007 | fresh_verification_input | .loom/progress/WI-1961.md | EV-001-EV-006 / A2 A5 | current branch and PR metadata state | present | review / merge-ready / closeout | Refresh after PR body, branch, head, validation, or hosted check changes. |

## Deferred / External Actions

| Subject | Status | Rationale | Consumer Boundary | Recheck Condition | Follow-up Locator |
| --- | --- | --- | --- | --- | --- |
| host tax core | deferred | #1957/#1958/#1959/#1960 have a later validation boundary and should consume this stabilizer first. | v0.28.0 milestone execution | Start after PR #1970 merges. | #1957 / #1958 / #1959 / #1960 |
| batch/taxonomy/migration/release | deferred | #1962/#1964/#1965/#1966 have separate rollback and validation boundaries. | v0.28.0 milestone execution | Start after their dependencies are ready. | #1962 / #1964 / #1965 / #1966 |
