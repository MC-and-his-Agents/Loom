# WI-1683 Evidence Map

## Context

- Work Item locator: .loom/work-items/WI-1683.md
- Host issue locator: https://github.com/MC-and-his-Agents/Loom/issues/1683
- Scope: Governance intensity gate runtime and fixture generalization.
- Suite path: minimal.
- Current branch: work/1683-governance-intensity-gate

## Input Snapshot

| Input | Locator | Status | Provenance | Freshness rule |
| --- | --- | --- | --- | --- |
| Work Item | .loom/work-items/WI-1683.md | required | authored Loom truth | Recheck after issue, branch, PR, or closeout state changes. |
| suite path decision | .loom/specs/WI-1683/spec.md | minimal | authored Loom truth | Recheck if scope expands into host mutation, release, workflow, or public CLI design. |
| task carrier | .loom/specs/WI-1683/task-carrier.md | required | authored Loom truth | Recheck before PR gate, controlled merge, and closeout. |
| governance intensity runtime | src/skills/shared/scripts/loom_flow.py | required | source runtime | Re-run pr-metadata surface and regenerate mirrors after edits. |
| CLI contract fixtures | tools/check_cli_contract.py | required | behavior evidence | Re-run pr-metadata surface after fixture edits. |

## Evidence Rows

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | src/skills/shared/scripts/loom_flow.py | #1683 generalized governance intensity gate | work_item=WI-1683; issue=#1683 | present | review / merge-ready / PR gate / closeout | Re-run focused contract tests after runtime edits. |
| EV-002 | behavior_evidence | skills/shared/scripts/loom_flow.py | generated mirror from source runtime | branch=work/1683-governance-intensity-gate | present | hosted checks / packaged plugin behavior | Run `python3 tools/skills_surface.py generate` and `check`. |
| EV-003 | test_evidence | tools/check_cli_contract.py | metadata validation and PR gate fixtures | branch=work/1683-governance-intensity-gate | present | review / merge-ready / PR gate / closeout | Re-run after runtime or fixture changes. |
| EV-004 | release_judgment | .loom/progress/WI-1683.md | no standalone release for this PR; v0.18.0 release remains owned by #1696 | issue=#1683 | present | closeout / milestone release planning | Recheck if this PR starts publishing release artifacts. |
| EV-005 | fresh_verification_input | .loom/progress/WI-1683.md | EV-001 EV-002 EV-003 | branch=work/1683-governance-intensity-gate; head=5e9c9d1494766f7221c846e8835e07e7cc9e47f4 | present | merge-ready / PR gate / closeout | Refresh after implementation, generated mirrors, PR metadata, or review input changes. |

## Suite Applicability

| Subject | Status | Rationale | Consumer boundary | Recheck condition | Follow-up locator |
| --- | --- | --- | --- | --- | --- |
| formal suite | minimal | Runtime gate and fixture update with bounded issue acceptance. | Suite path decision only; review, PR metadata, hosted checks, controlled merge, and closeout remain required. | Expand suite if scope grows into host mutation, release packaging, workflow enforcement, or public CLI command design. | .loom/specs/WI-1683/spec.md |
