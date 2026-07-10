# WI-1687 Evidence Map

## Context

- Work Item locator: .loom/work-items/WI-1687.md
- Host issue locator: https://github.com/MC-and-his-Agents/Loom/issues/1687
- Scope: PR metadata missing Issue backlink safe repair.
- Suite path: minimal.
- Current branch: work/1687-pr-backlink-safe-repair

## Input Snapshot

| Input | Locator | Status | Provenance | Freshness rule |
| --- | --- | --- | --- | --- |
| Work Item | .loom/work-items/WI-1687.md | required | authored Loom truth | Recheck after issue, branch, PR, or closeout state changes. |
| suite path decision | .loom/specs/WI-1687/spec.md | minimal | authored Loom truth | Recheck if scope expands beyond safe PR metadata backlink repair. |
| implementation contract | .loom/specs/WI-1687/implementation-contract.md | required | authored Loom truth | Recheck after runtime contract or output payload changes. |
| task carrier | .loom/specs/WI-1687/task-carrier.md | required | authored Loom truth | Recheck before PR gate, controlled merge, and closeout. |
| predecessor carrier | .loom/progress/WI-1684.md | required | consumed closeout residue | Recheck if #1684 host issue, PR, or merge commit readback changes. |
| PR metadata runtime | src/skills/shared/scripts/loom_flow.py | required | source runtime | Re-run pr-metadata surface and regenerate mirrors after edits. |
| CLI wrapper | tools/loom.py | required | repo-local CLI wrapper | Re-run wrapper fixture after argument passthrough changes. |
| CLI contract fixtures | tools/check_cli_contract.py | required | behavior evidence | Re-run pr-metadata and governance-closeout checks after fixture edits. |

## Evidence Rows

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | src/skills/shared/scripts/loom_flow.py | `--issue` propagation and safe repair action generation | work_item=WI-1687; issue=#1687 | present | review / merge-ready / PR gate / closeout | Re-run focused contract tests after runtime edits. |
| EV-002 | behavior_evidence | skills/shared/scripts/loom_flow.py | generated mirror from source runtime | branch=work/1687-pr-backlink-safe-repair | present | hosted checks / packaged runtime behavior | Run `python3 tools/skills_surface.py generate` and `check`. |
| EV-003 | behavior_evidence | plugins/loom/skills/shared/scripts/loom_flow.py | plugin mirror from source runtime | branch=work/1687-pr-backlink-safe-repair | present | plugin packaging / hosted checks | Run `python3 tools/skills_surface.py check`. |
| EV-004 | behavior_evidence | tools/loom.py | repo-local `loom pr metadata-* --issue` passthrough | branch=work/1687-pr-backlink-safe-repair | present | user CLI / review / PR gate | Re-run wrapper contract fixture after wrapper changes. |
| EV-005 | test_evidence | tools/check_cli_contract.py | missing Issue backlink safe repair fixture | branch=work/1687-pr-backlink-safe-repair | present | review / merge-ready / PR gate / closeout | Re-run `--surface pr-metadata`. |
| EV-006 | release_judgment | .loom/progress/WI-1687.md | no standalone release for this PR; v0.18.0 release remains owned by #1696 | issue=#1687 | present | closeout / milestone release planning | Recheck if this PR starts publishing release artifacts. |
| EV-007 | closeout_evidence | .loom/progress/WI-1684.md | predecessor carrier terminalized from PR #1702 / issue #1684 closeout readback | issue=#1684; pr=#1702 | present | state-check / workspace admission / closeout | Recheck if PR #1702 or issue #1684 host readback changes. |
| EV-008 | fresh_verification_input | .loom/progress/WI-1687.md | EV-001 EV-002 EV-003 EV-004 EV-005 EV-007 | branch=work/1687-pr-backlink-safe-repair | present | merge-ready / PR gate / closeout | Refresh after implementation, generated mirrors, PR metadata, or review input changes. |

## Suite Applicability

| Subject | Status | Rationale | Consumer boundary | Recheck condition | Follow-up locator |
| --- | --- | --- | --- | --- | --- |
| formal suite | minimal | Existing PR metadata path gains a bounded safe repair action and focused fixture coverage. | Suite path decision only; review, PR metadata, hosted checks, controlled merge, and closeout remain required. | Expand suite if scope grows into generic PR body rewriting, ship orchestration, or closeout policy. | .loom/specs/WI-1687/spec.md |
