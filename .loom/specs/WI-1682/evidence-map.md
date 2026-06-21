# WI-1682 Evidence Map

## Context

- Work Item locator: .loom/work-items/WI-1682.md
- Host issue locators: https://github.com/MC-and-his-Agents/Loom/issues/1682, https://github.com/MC-and-his-Agents/Loom/issues/1686, https://github.com/MC-and-his-Agents/Loom/issues/1695
- Scope: First hard dependency contracts for milestone #15.
- Suite path: minimal.
- Current branch: work/1682-intensity-binding-closeout-contracts

## Input Snapshot

| Input | Locator | Status | Provenance | Freshness rule |
| --- | --- | --- | --- | --- |
| Work Item | .loom/work-items/WI-1682.md | required | authored Loom truth | Recheck after issue, branch, PR, or closeout state changes. |
| suite path decision | .loom/specs/WI-1682/spec.md | minimal | authored Loom truth | Recheck if runtime behavior, host mutation, release, or public CLI/API compatibility enters scope. |
| task carrier | .loom/specs/WI-1682/task-carrier.md | required | authored Loom truth | Recheck before PR gate, controlled merge, and closeout. |
| metadata contract | .loom/companion/repo-interface.json | required | repo companion metadata | Re-run pr-metadata surface after metadata contract changes. |
| closeout contract | docs/methodology/harness/closeout-gate.md | required | harness contract | Re-run closeout-wrapper after policy wording or mirror changes. |

## Evidence Rows

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | .loom/specs/WI-1682/spec.md | #1682 classification contract, #1686 binding priority, #1695 closeout policy | work_item=WI-1682; issues=#1682/#1686/#1695 | present | review / merge-ready / PR gate / closeout | Recheck docs and mirrors after contract edits. |
| EV-002 | test_evidence | git diff --check; python3 -m json.tool .loom/companion/repo-interface.json; python3 tools/check_cli_contract.py --surface pr-metadata; python3 tools/check_cli_contract.py --surface closeout-wrapper; python3 tools/check_cli_contract.py --surface merge-wrapper; python3 tools/check_cli_contract.py --surface controlled-merge | metadata contract, safe repair fields, closeout policy snippets, existing wrapper compatibility | branch=work/1682-intensity-binding-closeout-contracts | present | review / merge-ready / PR gate / closeout | Re-run after contract, fixture, or carrier changes. |
| EV-003 | fresh_verification_input | .loom/progress/WI-1682.md | EV-001 EV-002 | work_item=WI-1682; branch=work/1682-intensity-binding-closeout-contracts | present | merge-ready / PR gate / closeout | Refresh after contract, fixture, PR metadata, or review input changes. |
| EV-004 | release_judgment | .loom/progress/WI-1682.md | no-release for this PR; v0.18.0 release remains owned by #1696 | issues=#1682/#1686/#1695 | present | closeout / milestone release planning | Recheck if this PR starts shipping runtime CLI behavior. |

## Suite Applicability

| Subject | Status | Rationale | Consumer boundary | Recheck condition | Follow-up locator |
| --- | --- | --- | --- | --- | --- |
| formal suite | minimal | Contract and fixture update with no runtime command mutation. | Suite path decision only; review, evidence map, task carrier, PR metadata, hosted checks, controlled merge, and closeout remain required. | Expand suite if runtime behavior, host mutation, release packaging, or public CLI/API compatibility enters scope. | .loom/specs/WI-1682/spec.md |
