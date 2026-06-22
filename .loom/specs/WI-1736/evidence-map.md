# WI-1736 Evidence Map

## Context

- Work Item locator: .loom/work-items/WI-1736.md
- Host issue locator: https://github.com/MC-and-his-Agents/Loom/issues/1736
- Scope: carrier refresh apply readback.
- Suite path: minimal.
- Current branch: work/1736-carrier-refresh-readback
- PR locator: https://github.com/MC-and-his-Agents/Loom/pull/1745

## Input Snapshot

| Input | Locator | Status | Provenance | Freshness rule |
| --- | --- | --- | --- | --- |
| Work Item | .loom/work-items/WI-1736.md | required | authored Loom truth | Recheck after issue, branch, PR, or closeout state changes. |
| suite path decision | .loom/specs/WI-1736/spec.md | minimal | authored Loom truth | Recheck if scope expands beyond carrier refresh apply readback. |
| implementation contract | .loom/specs/WI-1736/implementation-contract.md | required | authored Loom truth | Recheck after runtime contract or output payload changes. |
| PR metadata | PR #1745 body | required | GitHub host truth | Recheck after PR body or head SHA changes. |

## Evidence Rows

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | src/skills/shared/scripts/loom_flow.py | apply/write readback semantics | work_item=WI-1736; issue=#1736 | present | review / merge-ready / PR gate / closeout | Re-run focused tests after runtime edits. |
| EV-002 | behavior_evidence | skills/shared/scripts/loom_flow.py | generated source mirror | branch=work/1736-carrier-refresh-readback | present | hosted checks / packaged runtime behavior | Run skills surface check after source edits. |
| EV-003 | behavior_evidence | plugins/loom/skills/shared/scripts/loom_flow.py | plugin runtime mirror | branch=work/1736-carrier-refresh-readback | present | plugin packaging / release judgment | Refresh plugin payload hash after plugin payload changes. |
| EV-004 | test_evidence | test/work_item_audit_test.py | apply readback regression | head / PR #1745 | present | review / merge-ready / PR gate | Re-run targeted test after carrier refresh changes. |
| EV-005 | test_evidence | tools/check_cli_contract.py --surface closeout-wrapper | wrapper contract regression | head / PR #1745 | present | review / merge-ready / PR gate | Re-run fixture after output contract changes. |
| EV-006 | package_evidence | plugins/loom/.codex-plugin/plugin.json | plugin payload hash readback | head / PR #1745 | present | release judgment / package gate | Recompute hash after plugin payload changes. |

## Suite Applicability

| Subject | Status | Rationale | Consumer boundary | Recheck condition | Follow-up locator |
| --- | --- | --- | --- | --- | --- |
| formal suite | minimal | Bounded runtime readback fix with focused regression and generated mirror/hash sync. | Suite path decision only; review, PR metadata, hosted checks, controlled merge, and closeout remain required. | Expand if scope grows into ship orchestration, review freshness policy, closeout policy, or release behavior. | .loom/specs/WI-1736/spec.md |
