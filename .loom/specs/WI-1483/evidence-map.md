# WI-1483 Evidence Map

## Context

- Work Item locator: .loom/work-items/WI-1483.md
- FR / parent locator: https://github.com/MC-and-his-Agents/Loom/issues/1483
- Scope: global CLI fact-chain/status/shadow-parity default summary output.
- Suite path: minimal
- Current `HEAD`: 2eeafe3a8d0c251a74332729c7611c6a034ce322
- PR locator: https://github.com/MC-and-his-Agents/Loom/pull/1662
- Host state locator: GitHub issue #1483 and PR #1662

## Input Snapshot

| Input | Locator | Status | Provenance | Freshness rule |
| --- | --- | --- | --- | --- |
| `spec.md` | `.loom/specs/WI-1483/spec.md` | required | issue #1483 | Recheck after output contract scope changes. |
| `plan.md` | `.loom/specs/WI-1483/plan.md` | required | issue #1483 | Recheck after validation strategy changes. |
| suite path decision | `.loom/specs/WI-1483/spec.md` | minimal suite | minimal suite rationale | Recheck if scope expands beyond target CLI wrappers. |
| implementation contract | `.loom/specs/WI-1483/implementation-contract.md` | required | review gate input | Recheck after wrapper contract changes. |
| execution breakdown / task carrier | `.loom/specs/WI-1483/task-carrier.md` | optional | issue #1483 | Recheck before closeout. |
| review record | `.loom/reviews/WI-1483.json` | required before merge | review gate | Recheck after head changes. |
| host state | GitHub issue #1483 / PR #1662 | required | GitHub | Recheck before closeout. |

## Evidence Rows

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | `tools/loom.py`; `test/output_envelope_test.py`; `tools/check_cli_contract.py` | S1-S3 and A1-A4 in `.loom/specs/WI-1483/spec.md` | work_item=WI-1483; scope=global-cli-output; head_sha=2eeafe3a8d0c251a74332729c7611c6a034ce322; pr=1662 | present | review; merge-ready; closeout; #1484/#1485 | Recheck after target command wrapper, budget, artifact locator, or full-output behavior changes. |
| EV-002 | test_evidence | `PYTHONDONTWRITEBYTECODE=1 python3 test/output_envelope_test.py`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py test/output_envelope_test.py`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py`; `git diff --check` | validation strategy in `.loom/specs/WI-1483/plan.md` | work_item=WI-1483; scope=global-cli-output; head_sha=2eeafe3a8d0c251a74332729c7611c6a034ce322 | present | review; merge-ready; closeout | Rerun after code, contract, carrier, or metadata changes. |
| EV-003 | fresh_verification_input | `fact-chain=1150 bytes`; `status=1138 bytes`; `shadow-parity=1132 bytes`; `fact-chain --full-output=40892 bytes`; artifact locators under `.loom/tmp/output-artifacts` verified readable | EV-001 EV-002 current validation summary and PR head binding | work_item=WI-1483; reviewed_head=2eeafe3a8d0c251a74332729c7611c6a034ce322; pr=1662 | present | merge-ready; closeout; status | Mark stale and rerun validation/review if PR head or output envelope changes. |

## Deferred

| Subject | Status | Rationale | Consumer boundary | Recheck condition | Follow-up locator |
| --- | --- | --- | --- | --- | --- |
| Flow gate command summary output | deferred | #1483 is limited to fact-chain/status/shadow-parity wrappers. | #1484 | Recheck when flow gate command families are wired. | https://github.com/MC-and-his-Agents/Loom/issues/1484 |
| Unified default command entry | deferred | #1483 prepares command surfaces but does not change all entry defaults. | #1485 | Recheck after #1483/#1484 merge. | https://github.com/MC-and-his-Agents/Loom/issues/1485 |
