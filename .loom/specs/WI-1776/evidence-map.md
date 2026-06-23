# WI-1776 Evidence Map

## Context

- Work Item locator: `.loom/work-items/WI-1776.md`
- Host issue locator: `https://github.com/MC-and-his-Agents/Loom/issues/1776`
- Scope: release readback verdict and short diagnostics.
- Suite path: minimal.
- Current branch: `work/1776-release-readback-verdict`
- PR locator: pending

## Input Snapshot

| Input | Locator | Status | Provenance | Freshness rule |
| --- | --- | --- | --- | --- |
| Work Item | `.loom/work-items/WI-1776.md` | required | authored Loom truth | Recheck after issue, branch, PR, or release readback behavior changes. |
| suite path decision | `.loom/specs/WI-1776/spec.md` | minimal | authored Loom truth | Recheck if scope expands beyond release readback verdict classification. |
| implementation contract | `.loom/specs/WI-1776/implementation-contract.md` | required | authored Loom truth | Recheck after output payload, readback classification, or fixture changes. |
| release fixtures | `docs/evidence/fixtures/release-readback-fixtures.json` | required | authored regression evidence | Re-run release-readback contract after fixture changes. |
| PR metadata | PR body | pending | GitHub host truth | Recheck after PR body or head SHA changes. |

## Evidence Rows

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | `tools/loom.py` | release verdict classification, package surface readback, carrier terminal readback, and diagnostic fields | WI-1776 / issue #1776 / branch `work/1776-release-readback-verdict` | present | review / merge-ready / PR gate / #1778 consumer | Re-run release-readback contract and live dry-run readback after runtime edits. |
| EV-002 | test_evidence | `tools/check_cli_contract.py` | EV-001 and release fixtures | WI-1776 / release-readback surface | present | review / merge-ready / PR gate | Re-run `python3 tools/check_cli_contract.py --surface release-readback` after helper or payload changes. |
| EV-003 | fixture_evidence | `docs/evidence/fixtures/release-readback-fixtures.json` | published, missing, drifted, blocked, fallback, and no-release scenarios | WI-1776 / release-readback surface | present | contract test / review / #1778 | Validate JSON and contract output after fixture edits. |
| EV-004 | carrier_evidence | `.loom/status/current.md` | current checkpoint, validation summary, and workspace entry | WI-1776 / current recovery | present | fact-chain / hosted freeze admission / closeout | Refresh carrier and shadow evidence after status changes. |
| EV-005 | review_evidence | `.loom/reviews/WI-1776.json` | current-head semantic review approval | implementation head `92ca131c` with carrier-only follow-up | present | merge-ready / PR gate | Refresh review after non-carrier implementation changes or validation summary changes. |
| EV-006 | fresh_verification_input | `.loom/progress/WI-1776.md` | EV-001 EV-002 EV-003 EV-004 EV-005 | WI-1776 / latest validation summary | present | merge-ready / PR gate / closeout | Keep recovery validation summary identical to the review-consumed validation summary after verification updates. |

## Suite Applicability

| Subject | Status | Rationale | Consumer boundary | Recheck condition | Follow-up locator |
| --- | --- | --- | --- | --- | --- |
| formal suite | minimal | Bounded CLI release readback verdict slice with direct fixture coverage and no publish or destructive cleanup authority. | Suite path decision, evidence map, implementation contract, review, PR metadata, hosted checks, controlled merge, and closeout remain required. | Expand if scope grows into publishing, version bump automation, credential handling, destructive cleanup mutations, release workflow design, or new host API write behavior. | `.loom/specs/WI-1776/spec.md` |
