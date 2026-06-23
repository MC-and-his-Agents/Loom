# WI-1777 Evidence Map

## Context

- Work Item locator: `.loom/work-items/WI-1777.md`
- Host issue locator: `https://github.com/MC-and-his-Agents/Loom/issues/1777`
- Scope: read-only `loom ship status` / `loom ship preflight` status readback.
- Suite path: minimal.
- Current branch: `work/1777-ship-preflight-status`
- PR locator: `https://github.com/MC-and-his-Agents/Loom/pull/1779`

## Input Snapshot

| Input | Locator | Status | Provenance | Freshness rule |
| --- | --- | --- | --- | --- |
| Work Item | `.loom/work-items/WI-1777.md` | required | authored Loom truth | Recheck after issue, branch, PR, or closeout state changes. |
| suite path decision | `.loom/specs/WI-1777/spec.md` | minimal | authored Loom truth | Recheck if scope expands beyond read-only ship status/preflight diagnostics. |
| implementation contract | `.loom/specs/WI-1777/implementation-contract.md` | required | authored Loom truth | Recheck after command behavior, output payload, or readback classification changes. |
| PR metadata | PR #1779 body | required | GitHub host truth | Recheck after PR body or head SHA changes. |

## Evidence Rows

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | `tools/loom.py` | ship status/preflight command routing and readback diagnostics | WI-1777 / issue #1777 / branch `work/1777-ship-preflight-status` | present | review / merge-ready / PR gate / #1775 consumer | Re-run ship-wrapper and live preflight smoke after runtime edits. |
| EV-002 | test_evidence | `tools/check_cli_contract.py` | EV-001 | WI-1777 / ship-wrapper surface | present | review / merge-ready / PR gate | Re-run `python3 tools/check_cli_contract.py --surface ship-wrapper` after helper or payload changes. |
| EV-003 | carrier_evidence | `.loom/status/current.md` | current checkpoint, validation summary, and host-safe workspace entry | WI-1777 / current recovery | present | fact-chain / hosted freeze admission / closeout | Refresh carrier and shadow evidence after status changes. |
| EV-004 | review_evidence | `.loom/reviews/WI-1777.json` | current-head semantic review approval | reviewed implementation head / PR #1779 | present | merge-ready / PR gate | Refresh review only after non-carrier implementation changes or validation summary changes. |
| EV-005 | fresh_verification_input | `.loom/progress/WI-1777.md` | EV-001 EV-002 EV-003 EV-004 | WI-1777 / latest validation summary | present | merge-ready / PR gate / closeout | Keep recovery validation summary identical to the review-consumed validation summary after verification updates. |

## Suite Applicability

| Subject | Status | Rationale | Consumer boundary | Recheck condition | Follow-up locator |
| --- | --- | --- | --- | --- | --- |
| formal suite | minimal | Bounded read-only CLI status/preflight slice with direct regression coverage and no external write authority. | Suite path decision, evidence map, implementation contract, review, PR metadata, hosted checks, controlled merge, and closeout remain required. | Expand if scope grows into mutating closeout sync, release verdict taxonomy, PR metadata race handling, merge fallback behavior, publishing, credentials, or cross-command orchestration. | `.loom/specs/WI-1777/spec.md` |
