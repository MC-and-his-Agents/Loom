# WI-1785 Evidence Map

## Context

- Work Item locator: `.loom/work-items/WI-1785.md`
- Host issue locator: `https://github.com/MC-and-his-Agents/Loom/issues/1785`
- Scope: closeout PR hosted gate surface inference.
- Suite path: minimal.
- Current branch: `work/1785-closeout-gate-surface`
- PR locator: pending

## Input Snapshot

| Input | Locator | Status | Provenance | Freshness rule |
| --- | --- | --- | --- | --- |
| Work Item | `.loom/work-items/WI-1785.md` | required | authored Loom truth | Recheck after issue, branch, PR, or workflow changes. |
| suite path decision | `.loom/specs/WI-1785/spec.md` | minimal | authored Loom truth | Recheck if scope expands beyond hosted gate surface inference. |
| implementation contract | `.loom/specs/WI-1785/implementation-contract.md` | required | authored Loom truth | Recheck after workflow argument or metadata inference changes. |
| hosted workflow | `.github/workflows/pr-merge-gate.yml` | required | repository CI truth | Re-run local smoke and hosted gate after workflow edits. |
| PR metadata | PR body | pending | GitHub host truth | Recheck after PR body or head SHA changes. |

## Evidence Rows

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | `.github/workflows/pr-merge-gate.yml` | PR body metadata surface inference and pr-gate surface argument | WI-1785 / issue #1785 / branch `work/1785-closeout-gate-surface` | present | hosted merge gate / #1784 closeout PR | Re-run local workflow surface inference smoke and hosted gate after workflow edits. |
| EV-002 | test_evidence | local Python smoke | closeout, merge_ready, and malformed metadata inference | WI-1785 / workflow surface inference | present | review / PR gate | Re-run after workflow parser changes. |
| EV-003 | regression_evidence | #1784 local closeout-surface gate proof and post-merge hosted rerun | closeout PR terminal carrier consumption | WI-1785 / #1784 blocker | present | #1784 / #1778 | Re-run after PR body or #1784 head changes. |
| EV-004 | carrier_evidence | `.loom/status/current.md` | current checkpoint, validation summary, and workspace entry | WI-1785 / current recovery | present | fact-chain / hosted freeze admission / closeout | Refresh carrier and shadow evidence after status changes. |
| EV-005 | review_evidence | `.loom/reviews/WI-1785.json` | current-head semantic review approval | WI-1785 / implementation review | present | merge-ready / PR gate | Refresh review after non-carrier implementation changes. |
| EV-006 | fresh_verification_input | `.loom/progress/WI-1785.md` | EV-001 EV-002 EV-003 EV-004 EV-005 | WI-1785 / latest validation summary | present | merge-ready / PR gate / closeout | Keep recovery validation summary identical to the review-consumed validation summary after verification updates. |

## Suite Applicability

| Subject | Status | Rationale | Consumer boundary | Recheck condition | Follow-up locator |
| --- | --- | --- | --- | --- | --- |
| formal suite | minimal | Bounded hosted workflow glue fix with direct smoke coverage and hosted #1784 proof after merge. | Suite path decision, evidence map, implementation contract, review, PR metadata, hosted checks, controlled merge, and closeout remain required. | Expand if scope grows into metadata schema, gate framework, or broader CI orchestration changes. | `.loom/specs/WI-1785/spec.md` |
