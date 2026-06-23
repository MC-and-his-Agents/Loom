# WI-1742 Suite Index

## Suite Path Decision

- Schema marker: loom-full-suite-index/v1
- Suite path: full
- Work Item / FR locator: .loom/work-items/WI-1742.md; https://github.com/MC-and-his-Agents/Loom/issues/1742
- Path decision provenance: milestone #17 child issue under parent FR #1734.
- Minimal path not sufficient because: #1742 verifies ship closeout behavior across merge, host reconciliation, closeout readback, and explicit closeout admission.
- Freshness rule: re-run ship-wrapper fixture and carrier validation after any `loom ship`, closeout policy, or fixture change.

## Consumes

- Story Readiness consumed state: not required; issue #1742 is a regression coverage work item with explicit acceptance.
- Story Business Confirmation consumed state: not required; no separate business story exists.
- Delivery planning / issue-tree locator: https://github.com/MC-and-his-Agents/Loom/issues/1734 and https://github.com/MC-and-his-Agents/Loom/issues/1742.
- Existing spec / plan locator: this suite defines the WI-1742 spec and plan.
- Host issue / PR / Project locator: issue #1742; PR locator pending until opened.

## Produces

- Artifact inventory: spec, plan, research, contracts, readiness checklist, evidence map, consistency analysis, execution breakdown, task carrier.
- Path selection rationale: full path is used because ship closeout admission and post-merge host readback are product-facing delivery behavior.
- Story readiness consumed state: not required with issue acceptance as source.
- Story business confirmation consumed state: not required.
- Deferred item table: no deferred items in WI-1742.
- Not-required item table: real release publish and GitHub permission model changes are not required.
- #1020 generated / skills integration requirements: not required; no generated skill payload changes.

## Artifact Inventory

| Artifact | Locator | Status | Consumer | Provenance |
| --- | --- | --- | --- | --- |
| `spec.md` | .loom/specs/WI-1742/spec.md | required / present | `plan.md`, review, merge-ready, closeout | issue #1742 |
| `plan.md` | .loom/specs/WI-1742/plan.md | required / present | implementation, review, merge-ready, closeout | issue #1742 |
| `implementation-contract.md` | .loom/specs/WI-1742/implementation-contract.md | required / present | implementation, review, merge-ready | issue #1742 |
| `research.md` | .loom/specs/WI-1742/research.md | conditional / present | plan and review | existing ship/closeout fixture inventory |
| `contracts.md` | .loom/specs/WI-1742/contracts.md | conditional / present | plan, review, CLI consumers | ship closeout e2e contract |
| `readiness-checklist.md` | .loom/specs/WI-1742/readiness-checklist.md | conditional / present | build / review readiness consumers | local validation |
| `evidence-map.md` | .loom/specs/WI-1742/evidence-map.md | required / present | review, merge-ready, closeout | command evidence |
| `consistency-analysis.md` | .loom/specs/WI-1742/consistency-analysis.md | required / present | review, merge-ready | scope and drift classification |
| `execution-breakdown.md` | .loom/specs/WI-1742/execution-breakdown.md | required / present | implementation and closeout | issue #1742 |
| `task-carrier.md` | .loom/specs/WI-1742/task-carrier.md | required / present | carrier validate and PR gate | issue #1742 |

## Deferred Items

No deferred items are introduced by WI-1742.

## Not Required Items

| Subject | Rationale | Recheck condition | Consumers that should not require it |
| --- | --- | --- | --- |
| Real release publish | #1742 is regression coverage only; #1743 owns v0.20.0 release. | Starting #1743 release closeout. | WI-1742 review and merge-ready |
| GitHub permission model changes | The fixture verifies existing host readback consumption without changing permissions. | A future issue changes host permissions. | WI-1742 review and merge-ready |

## Locator

- Suite index locator: .loom/specs/WI-1742/suite-index.md
- Repo-relative artifact root: .loom/specs/WI-1742
- Host comment / issue evidence locator: https://github.com/MC-and-his-Agents/Loom/issues/1742

## Provenance

- Source issue / PR / doc / conversation locator: issue #1742 under parent FR #1734.
- Trust boundary: repo-local suite artifacts define WI-1742 review inputs but do not replace GitHub issue/PR, checks, review, merge-ready, or closeout truth.
- Freshness rule: re-run targeted validation and refresh review after any head change.
- Recheck condition: changes to `handle_ship`, `ship_closeout_policy`, closeout wrappers, or ship fixture expectations.
