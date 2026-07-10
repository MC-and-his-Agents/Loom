# WI-1487 Evidence Map

## Context

- Work Item locator: .loom/work-items/WI-1487.md
- FR / parent locator: https://github.com/MC-and-his-Agents/Loom/issues/1487
- Scope: docs/contract-only thread rotation and handoff package rules.
- Suite path: minimal
- Current `HEAD`: current PR head at review time
- Host state locator: GitHub issue #1487 and implementation PR

## Input Snapshot

| Input | Locator | Status | Provenance | Freshness rule |
| --- | --- | --- | --- | --- |
| `spec.md` | `.loom/specs/WI-1487/spec.md` | required | issue #1487 | Recheck after thread rotation contract changes. |
| `plan.md` | `.loom/specs/WI-1487/plan.md` | required | issue #1487 | Recheck after validation strategy changes. |
| suite path decision | `.loom/specs/WI-1487/spec.md` | minimal suite | minimal suite rationale | Recheck if scope expands. |
| implementation contract | `.loom/specs/WI-1487/implementation-contract.md` | required | review gate input | Recheck after handoff package field changes. |
| execution breakdown / task carrier | `.loom/specs/WI-1487/task-carrier.md` | optional | issue #1487 | Recheck before closeout. |
| review record | `.loom/reviews/WI-1487.json` | required before merge | review gate | Recheck after head changes. |
| host state | GitHub issue #1487 / implementation PR | required | GitHub | Recheck before closeout. |

## Evidence Rows

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | `docs/methodology/harness/recovery-model.md`; `skills/shared/references/harness/recovery-model.md`; `skills/loom-handoff/references/output-contract.md` | S1-S3 and A1-A4 in `.loom/specs/WI-1487/spec.md` | work_item=WI-1487; scope=docs-contract; head_sha=current PR head at review time | present | review; merge-ready; closeout; #1486 | Recheck source and generated/plugin mirrors after thread rotation or handoff package wording changes. |
| EV-002 | test_evidence | `git diff --check`; `python3 tools/py_compile_clean.py tools/loom.py test/output_envelope_test.py`; `python3 tools/loom.py fact-chain --target . --json`; `python3 .loom/bin/loom_flow.py shadow-parity --target . --surface all --blocking`; `python3 tools/skills_surface.py check --surface generated-tree-drift`; `python3 tools/loom.py suite validate --target . --item WI-1487 --json`; `python3 tools/loom.py suite evidence validate --target . --item WI-1487 --json`; `python3 tools/loom.py suite carrier validate --target . --item WI-1487 --json` | validation and test strategy in `.loom/specs/WI-1487/plan.md` | work_item=WI-1487; scope=docs-contract; head_sha=current PR head at review time; validation_summary=.loom/progress/WI-1487.md | present | review; merge-ready; closeout | Rerun the listed checks after documentation, suite, carrier, or review input changes. |
| EV-003 | fresh_verification_input | `.loom/progress/WI-1487.md` | EV-001 EV-002 current validation summary and PR head binding | work_item=WI-1487; reviewed_head=current PR head at review time | present | merge-ready; closeout; status | Mark stale and rerun validation/review if PR head, scope, or validation summary changes. |

## Deferred

| Subject | Status | Rationale | Consumer boundary | Recheck condition | Follow-up locator |
| --- | --- | --- | --- | --- | --- |
| Plugin command example updates | deferred | #1487 freezes handoff rules only. | #1486 | Recheck when updating Codex user-level plugin payload text. | https://github.com/MC-and-his-Agents/Loom/issues/1486 |
| CLI command output integration | deferred | #1487 consumes the output envelope and artifact locator contract but does not wire CLI surfaces. | #1483/#1484/#1485 | Recheck when command output summaries are implemented. | https://github.com/MC-and-his-Agents/Loom/issues/1483 |
