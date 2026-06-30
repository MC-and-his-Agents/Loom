# Evidence Map

## Context

- Work Item locator: .loom/work-items/WI-1822.md
- FR / parent locator:
- Scope: normalize `closeout` checkpoint input to `closed_out` and lock the behavior with one focused CLI contract check.
- Suite path: focused bugfix contract
- Current `HEAD`: 37c6acb11c212afb25ac669243662460c36bbc0d
- PR locator, or `not_applicable` rationale: pending PR creation for issue #1822.
- Host state locator, or `not_applicable` rationale: https://github.com/MC-and-his-Agents/Loom/issues/1822

## Input Snapshot

| Input | Locator | Status | Provenance | Freshness rule |
| --- | --- | --- | --- | --- |
| `spec.md` | .loom/specs/WI-1822/evidence-map.md#evidence-rows | not_applicable | focused bugfix scope | The behavior contract is the normalized input/output row below; recheck when scope grows beyond checkpoint normalization. |
| `plan.md` | .loom/progress/WI-1822.md | not_applicable | focused bugfix validation record | The validation plan is the focused checks listed in progress; recheck before review and release. |
| suite path decision | .loom/specs/WI-1822/evidence-map.md#not-applicable--deferred | present | authored focused bugfix path | Recheck when suite path changes. |
| execution breakdown / task carrier | .loom/specs/WI-1822/task-carrier.md | present | authored task carrier | Recheck when branch, PR, head, or issue binding changes. |
| review record | .loom/reviews/WI-1822.json | required | authored review truth | Refresh after PR metadata is stable and before merge-ready consumption. |
| merge-ready basis | pending PR gate | required | merge-ready truth | Required before merge. |
| host state | https://github.com/MC-and-his-Agents/Loom/issues/1822 | present | host issue | Recheck before PR creation, merge, release, and issue closeout. |

## Evidence Rows

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | src/skills/shared/scripts/loom_flow.py; skills/shared/scripts/loom_flow.py; plugins/loom/skills/shared/scripts/loom_flow.py; .loom/bin/loom_flow.py | `normalize_checkpoint("closeout") -> "closed_out"` and terminal resume/state-check consumption | WI-1822 / branch `work/1822-normalize-closeout-checkpoint` / head `37c6acb11c212afb25ac669243662460c36bbc0d` | present | review / merge-ready / release / closeout / status | Re-run focused contract and runtime-copy parity after checkpoint normalization changes. |
| EV-002 | test_evidence | tools/check_cli_contract.py; local validation output in .loom/progress/WI-1822.md | `assert_closeout_checkpoint_normalization_contract()` plus governance-closeout contract suite | WI-1822 / focused bugfix validation / head `37c6acb11c212afb25ac669243662460c36bbc0d` | present | review / merge-ready / release / closeout / status | Re-run `python3 tools/check_cli_contract.py --surface governance-closeout` after CLI flow or contract changes. |
| EV-003 | fresh_verification_input | .loom/progress/WI-1822.md | EV-001 EV-002 plus runtime-copy-parity, generated-tree/reference-integrity, py-compile-clean, diff whitespace, and live resume repro | WI-1822 / latest validation summary / PR pending | present | merge-ready / release / closeout / status | Refresh progress summary and PR metadata after head changes, PR creation, review, merge, or release checks. |

## Not Applicable / Deferred

| Subject | Status | Rationale | Consumer boundary | Recheck condition | Follow-up locator |
| --- | --- | --- | --- | --- | --- |
| formal full suite | not_applicable | Focused patch bugfix has no separate product spec/plan beyond the one-row checkpoint normalization contract and task carrier. This does not skip review, PR gate, merge-ready, release readback, or closeout evidence. | review / merge-ready / release / closeout | Recheck if scope expands beyond checkpoint normalization or touches unrelated resume state semantics. | #1822 |

## #1020 Follow-up Requirements

- Skills / GitHub profile consumption:
- Generated surface sync:
- Drift check requirement:
