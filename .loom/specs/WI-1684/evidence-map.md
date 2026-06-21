# WI-1684 Evidence Map

## Context

- Work Item locator: .loom/work-items/WI-1684.md
- Host issue locator: https://github.com/MC-and-his-Agents/Loom/issues/1684
- Scope: Governance intensity high-risk fixture coverage.
- Suite path: minimal.
- Current branch: work/1684-intensity-upgrade-fixtures

## Input Snapshot

| Input | Locator | Status | Provenance | Freshness rule |
| --- | --- | --- | --- | --- |
| Work Item | .loom/work-items/WI-1684.md | required | authored Loom truth | Recheck after issue, branch, PR, or closeout state changes. |
| suite path decision | .loom/specs/WI-1684/spec.md | minimal | authored Loom truth | Recheck if scope expands beyond classification fixtures. |
| implementation contract | .loom/specs/WI-1684/implementation-contract.md | required | authored Loom truth | Recheck after runtime contract or output payload changes. |
| task carrier | .loom/specs/WI-1684/task-carrier.md | required | authored Loom truth | Recheck before PR gate, controlled merge, and closeout. |
| governance intensity runtime | src/skills/shared/scripts/loom_flow.py | required | source runtime | Re-run pr-metadata surface and regenerate mirrors after edits. |
| CLI contract fixtures | tools/check_cli_contract.py | required | behavior evidence | Re-run pr-metadata and aggregate checks after fixture edits. |

## Evidence Rows

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | src/skills/shared/scripts/loom_flow.py | high-risk change-class classification | work_item=WI-1684; issue=#1684 | present | review / merge-ready / PR gate / closeout | Re-run focused contract tests after runtime edits. |
| EV-002 | behavior_evidence | skills/shared/scripts/loom_flow.py | generated mirror from source runtime | branch=work/1684-intensity-upgrade-fixtures | present | hosted checks / packaged plugin behavior | Run `python3 tools/skills_surface.py generate` and `check`. |
| EV-003 | behavior_evidence | plugins/loom/skills/shared/scripts/loom_flow.py | plugin mirror from source runtime | branch=work/1684-intensity-upgrade-fixtures | present | plugin packaging / hosted checks | Run `python3 tools/skills_surface.py check`. |
| EV-004 | test_evidence | tools/check_cli_contract.py | metadata validation and PR gate abuse fixtures | branch=work/1684-intensity-upgrade-fixtures | present | review / merge-ready / PR gate / closeout | Re-run targeted and aggregate contract checks after fixture changes. |
| EV-005 | release_judgment | .loom/progress/WI-1684.md | no standalone release for this PR; v0.18.0 release remains owned by #1696 | issue=#1684 | present | closeout / milestone release planning | Recheck if this PR starts publishing release artifacts. |
| EV-006 | fresh_verification_input | .loom/progress/WI-1684.md | EV-001 EV-002 EV-003 EV-004 | branch=work/1684-intensity-upgrade-fixtures | present | merge-ready / PR gate / closeout | Refresh after implementation, generated mirrors, PR metadata, or review input changes. |

## Suite Applicability

| Subject | Status | Rationale | Consumer boundary | Recheck condition | Follow-up locator |
| --- | --- | --- | --- | --- | --- |
| formal suite | minimal | Runtime vocabulary and fixture update with bounded issue acceptance. | Suite path decision only; review, PR metadata, hosted checks, controlled merge, and closeout remain required. | Expand suite if scope grows into ship orchestration, host writes, or release packaging. | .loom/specs/WI-1684/spec.md |
