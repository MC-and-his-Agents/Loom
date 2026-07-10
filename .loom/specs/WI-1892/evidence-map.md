# WI-1892 Evidence Map

| Evidence ID | Evidence Type | Source Locator | Consumes | Binding | Freshness | Consumer Boundary | Remediation Direction |
|---|---|---|---|---|---|---|---|
| EV-001 | behavior_evidence | `README.md` | S1 / A1 / A2 | user install and upgrade boundary | present | review / PR gate / merge-ready / FR #1889 closeout | Recheck README after any install or upgrade documentation edit. |
| EV-002 | behavior_evidence | `docs/adoption/global-cli-user-plugin-contract.md` | S2 / A3 | global CLI and user-level plugin authority boundary | present | review / PR gate / merge-ready / future upgrade orchestration | Recheck contract after marketplace, CLI, plugin, or adoption authority changes. |
| EV-003 | behavior_evidence | `docs/adoption/host-adapter-matrix.md` | S3 / A4 | Codex install, discovery, upgrade, and verification surfaces | present | review / PR gate / merge-ready / host adapter consumers | Recheck matrix after Codex host install or marketplace behavior changes. |
| EV-004 | test_evidence | `rg -n "marketplace OR host install OR npm install -g OR repo adoption OR metadata-only" README.md docs/adoption/global-cli-user-plugin-contract.md docs/adoption/host-adapter-matrix.md` | S1-S3 / A1-A4 | targeted boundary text validation | present | review / PR gate | Rerun after docs edits. |
| EV-005 | test_evidence | `python3 tools/loom.py suite validate --target . --item WI-1892 --json` | A1-A5 | suite contract validation | present | review / merge-ready / closeout | Rerun after suite or carrier edits. |
| EV-006 | test_evidence | `python3 tools/loom.py suite evidence validate --target . --item WI-1892 --json` | A1-A5 | evidence map validation | present | review / merge-ready / closeout | Rerun after evidence map edits. |
| EV-007 | test_evidence | `python3 tools/loom.py suite carrier validate --target . --item WI-1892 --json` | A1-A5 | task carrier validation | present | review / merge-ready / closeout | Rerun after task carrier edits. |
| EV-008 | test_evidence | `python3 tools/loom.py fact-chain --target . --item WI-1892 --json` | A1-A5 | fact-chain validation | present | review / merge-ready / closeout | Rerun after docs, suite, carrier, progress, or review edits. |
| EV-009 | test_evidence | `git diff --check` | A5 | diff hygiene and payload-change review | present | review / PR gate | Rerun after any file edit. |
| EV-010 | fresh_verification_input | `.loom/progress/WI-1892.md` | EV-001-EV-009 / A1-A5 | current branch / current head / WI-1892 | present | review / merge-ready / closeout | Refresh after final validation, PR metadata, review, hosted checks, and merge readback. |

## Deferred Evidence

| Evidence | Status | Rationale | Consumer Boundary | Recheck Condition | Follow-up |
|---|---|---|---|---|---|
| Real user Codex marketplace plugin update | not_required | WI-1892 documents the authority boundary and does not mutate workstation state. | review / PR gate / closeout | Require if a future WI installs or upgrades a real workstation plugin. | FR #1902 |
| npm CLI upgrade execution | not_required | WI-1892 documents that npm owns the CLI but does not publish or upgrade the package. | review / PR gate / closeout | Require when release or workstation upgrade orchestration changes CLI version. | FR #1902 / #1914 |
| Per-repository adoption migration | deferred | Each adopted repository still validates independently; migration tooling is owned by FR #1908. | phase closeout | Require when implementing legacy migration behavior. | FR #1908 |
