# WI-1481 Evidence Map

## Context

- Work Item locator: .loom/work-items/WI-1481.md
- FR / parent locator: https://github.com/MC-and-his-Agents/Loom/issues/1481
- Scope: helper-only output envelope and artifact writer support.
- Suite path: minimal
- Current `HEAD`: current PR head at review time
- PR locator: https://github.com/MC-and-his-Agents/Loom/pull/1659
- Host state locator: GitHub issue #1481 and PR #1659

## Input Snapshot

| Input | Locator | Status | Provenance | Freshness rule |
| --- | --- | --- | --- | --- |
| `spec.md` | `.loom/specs/WI-1481/spec.md` | required | issue #1481 | Recheck after helper contract changes. |
| `plan.md` | `.loom/specs/WI-1481/plan.md` | required | issue #1481 | Recheck after validation strategy changes. |
| suite path decision | `.loom/specs/WI-1481/spec.md` | minimal suite | minimal suite rationale | Recheck if scope expands. |
| implementation contract | `.loom/specs/WI-1481/implementation-contract.md` | required | review gate input | Recheck after helper API changes. |
| execution breakdown / task carrier | `.loom/specs/WI-1481/task-carrier.md` | optional | issue #1481 | Recheck before closeout. |
| review record | `.loom/reviews/WI-1481.json` | required before merge | review gate | Recheck after head changes. |
| merge-ready basis | PR #1659 checks | required before merge | GitHub PR gate | Recheck after PR head changes. |
| host state | GitHub issue #1481 / PR #1659 | required | GitHub | Recheck before closeout. |

## Evidence Rows

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | `test/output_envelope_test.py` | S1-S3 and A1-A3 in `.loom/specs/WI-1481/spec.md` | work_item=WI-1481; scope=helper-only; head_sha=current PR head at review time; pr=#1659 | present | review; merge-ready; closeout | Rerun focused tests after `tools/loom.py` helper or artifact path changes. |
| EV-002 | test_evidence | `python3 test/output_envelope_test.py`; `python3 -m unittest discover -s test -p 'output_envelope_test.py'`; `python3 tools/py_compile_clean.py tools/loom.py test/output_envelope_test.py`; `git diff --check`; `python3 tools/loom.py suite validate --target . --item WI-1481 --json`; `python3 tools/loom.py suite carrier validate --target . --item WI-1481 --json` | validation and test strategy in `.loom/specs/WI-1481/plan.md` | work_item=WI-1481; scope=helper-only; head_sha=current PR head at review time; validation_summary=.loom/progress/WI-1481.md | present | review; merge-ready; closeout | Rerun the listed checks after code, suite, carrier, or review input changes. |
| EV-003 | fresh_verification_input | `.loom/progress/WI-1481.md` | EV-001 EV-002 current validation summary and PR #1659 head binding | work_item=WI-1481; reviewed_head=current PR head at review time; pr=#1659 | present | merge-ready; closeout; status | Mark stale and rerun validation/review if PR head, scope, or validation summary changes. |

## Deferred

| Subject | Status | Rationale | Consumer boundary | Recheck condition | Follow-up locator |
| --- | --- | --- | --- | --- | --- |
| Command-by-command integration | deferred | #1481 only introduces reusable helpers. | #1483/#1484/#1485 | Recheck when wiring high-noise command output. | https://github.com/MC-and-his-Agents/Loom/issues/1483 |
| Configurable budget policy | deferred | Budget policy belongs to #1482. | #1482 | Recheck before budget protection closeout. | https://github.com/MC-and-his-Agents/Loom/issues/1482 |
| Plugin/skill payload updates | deferred | Codex user-level plugin payload belongs to #1486. | #1486 | Recheck before plugin documentation closeout. | https://github.com/MC-and-his-Agents/Loom/issues/1486 |
