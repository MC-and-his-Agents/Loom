# WI-1876 Evidence Map

## Context

- Work Item locator: .loom/work-items/WI-1876.md
- FR / parent locator: https://github.com/MC-and-his-Agents/Loom/issues/1876
- Scope: target-aware Loom CLI full_output artifact emission and readback contract.
- Suite path: see `.loom/specs/WI-1876/spec.md` for the formal-suite bypass decision.
- Current `HEAD`: current PR head at merge-ready.
- PR locator: https://github.com/MC-and-his-Agents/Loom/pull/1878
- Host state locator: GitHub issue #1876 and PR #1878

## Input Snapshot

| Input | Locator | Status | Provenance | Freshness rule |
| --- | --- | --- | --- | --- |
| `spec.md` | `.loom/specs/WI-1876/spec.md` | formal-suite bypass decision | issue #1876 and WI-1876 carrier | Recheck if the PR expands beyond target-aware artifact locator emission/readback. |
| `plan.md` | `.loom/specs/WI-1876/plan.md` | present | issue #1876 and implementation plan | Recheck after validation strategy or scope changes. |
| suite path decision | `.loom/specs/WI-1876/spec.md` | formal-suite bypass | rationale in `.loom/specs/WI-1876/spec.md` | Recheck if full suite artifacts become required by scope, release mechanics, host writes, permissions, or downstream behavior changes. |
| execution breakdown / task carrier | `.loom/specs/WI-1876/task-carrier.md` | optional | WI-1876 carrier | Recheck before closeout. |
| review record | `.loom/reviews/WI-1876.json` | required before merge | implementation review | Recheck after semantic code changes. Carrier-only drift is consumed by PR gate head binding. |
| merge-ready basis | PR #1878 hosted and local PR gate | required before merge | PR metadata and gate readback | Recheck after PR body, branch head, review, shadow, or evidence-map changes. |
| host state | GitHub issue #1876 / PR #1878 | required | GitHub | Recheck before merge, release, and closeout. |

## Evidence Rows

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | `tools/loom.py`; `tools/check_cli_contract.py`; `docs/methodology/harness/cli-command-matrix.md` | target-bound artifact locator contract and acceptance in `.loom/specs/WI-1876/spec.md` | work_item=WI-1876; scope=target-aware-output-artifacts; head=current PR head at merge-ready; pr_head=current PR head at merge-ready; pr=1878 | present | review; merge-ready; release closeout; status | Recheck after target resolution, output artifact directory, PR metadata, or command matrix contract changes. |
| EV-002 | test_evidence | `test/output_envelope_test.py`; `test/target_resolution_test.py`; `python3 tools/check_cli_contract.py --surface aggregate`; real `node bin/loom.mjs build --target <tmp> --item WI-test --json`; real `node bin/loom.mjs fact-chain --target <tmp> --json` | validation strategy in `.loom/specs/WI-1876/plan.md` | work_item=WI-1876; scope=target-aware-output-artifacts; head=current PR head at merge-ready; pr_head=current PR head at merge-ready; pr=1878 | present | review; merge-ready; release closeout | Rerun focused unit tests, Node wrapper probes, aggregate contract, and compile checks after code, wrapper, or contract-helper changes. |
| EV-003 | fresh_verification_input | `.loom/progress/WI-1876.md` | EV-001 EV-002 current validation summary and PR head binding | work_item=WI-1876; head=current PR head at merge-ready; pr_head=current PR head at merge-ready; validation_summary_sha256=b0d109e488a9897d71d029d3ffa4266f05452e154dd24c8fbb1c73c51b2a9926; pr=1878 | present | merge-ready; release closeout; status | Refresh evidence-map, PR metadata, shadow carriers, review consumption, and hosted checks after branch head, validation summary, or PR body changes. |

## Deferred

No deferred evidence rows are claimed for WI-1876. The formal-suite bypass rationale is authored in `.loom/specs/WI-1876/spec.md` and mirrored in PR #1878 metadata.
