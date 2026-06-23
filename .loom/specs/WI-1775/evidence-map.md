# WI-1775 Evidence Map

## Context

- Work Item locator: `.loom/work-items/WI-1775.md`
- Host issue locator: `https://github.com/MC-and-his-Agents/Loom/issues/1775`
- Scope: closeout status/sync readback and repair orchestration.
- Suite path: minimal.
- Current branch: `work/1775-closeout-sync`
- PR locator: pending

## Input Snapshot

| Input | Locator | Status | Provenance | Freshness rule |
| --- | --- | --- | --- | --- |
| Work Item | `.loom/work-items/WI-1775.md` | required | authored Loom truth | Recheck after issue, branch, PR, or closeout state changes. |
| suite path decision | `.loom/specs/WI-1775/spec.md` | minimal | authored Loom truth | Recheck if scope expands beyond closeout status/sync diagnostics and repair orchestration. |
| implementation contract | `.loom/specs/WI-1775/implementation-contract.md` | required | authored Loom truth | Recheck after command behavior, output payload, or readback classification changes. |
| PR metadata | PR body | pending | GitHub host truth | Recheck after PR body or head SHA changes. |

## Evidence Rows

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | `tools/loom.py` | closeout status/sync command routing, metadata race repair, closeout run composition, and terminal cleanup readback | WI-1775 / issue #1775 / branch `work/1775-closeout-sync` | present | review / merge-ready / PR gate / #1776 consumer | Re-run closeout-wrapper and smoke checks after runtime edits. |
| EV-002 | test_evidence | `tools/check_cli_contract.py` | EV-001 | WI-1775 / closeout-wrapper surface | present | review / merge-ready / PR gate | Re-run `python3 tools/check_cli_contract.py --surface closeout-wrapper` after helper or payload changes. |
| EV-003 | carrier_evidence | `.loom/status/current.md` | current checkpoint, validation summary, and workspace entry | WI-1775 / current recovery | present | fact-chain / hosted freeze admission / closeout | Refresh carrier and shadow evidence after status changes. |
| EV-004 | review_evidence | `.loom/reviews/WI-1775.json` | current-head semantic review approval | reviewed implementation head / PR pending | present | merge-ready / PR gate | Refresh review after non-carrier implementation changes or validation summary changes. |
| EV-005 | fresh_verification_input | `.loom/progress/WI-1775.md` | EV-001 EV-002 EV-003 EV-004 | WI-1775 / latest validation summary | present | merge-ready / PR gate / closeout | Keep recovery validation summary identical to the review-consumed validation summary after verification updates. |

## Suite Applicability

| Subject | Status | Rationale | Consumer boundary | Recheck condition | Follow-up locator |
| --- | --- | --- | --- | --- | --- |
| formal suite | minimal | Bounded CLI closeout status/sync slice with direct regression coverage and no new publish or destructive cleanup authority. | Suite path decision, evidence map, implementation contract, review, PR metadata, hosted checks, controlled merge, and closeout remain required. | Expand if scope grows into release verdict taxonomy, publishing, credentials, automatic cleanup mutations, multi-worktree merge fallback, or new closeout state-machine semantics. | `.loom/specs/WI-1775/spec.md` |
