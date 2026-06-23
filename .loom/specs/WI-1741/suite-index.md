# Full Suite Index

## Suite Path Decision

- Schema marker: loom-full-suite-index/v1
- Suite path: full
- Work Item / FR locator: GitHub issue #1741 under parent FR #1734 / milestone #17.
- Path decision provenance: #1741 changes the user-facing `loom ship` delivery wrapper and validation diagnostics.
- Minimal path not sufficient because: the change touches CLI behavior, PR changed-path readback, validation profile selection, and docs consumed by delivery agents.
- Freshness rule: Recheck after PR head changes, ship wrapper behavior changes, validation profile taxonomy changes, review findings, or merge-ready gate updates.

## Consumes

- Story Readiness confirmed locator, blocking locator, or not-required rationale: not required; GitHub issue #1741 contains bounded acceptance criteria.
- Story Business Confirmation confirmed locator, blocking locator, or not-required rationale: not required; product semantics are limited to Loom CLI delivery friction.
- Delivery planning / issue-tree locator, or not-required rationale: parent FR #1734 and milestone #17 dependency tree.
- Existing spec / plan locator, or not-required rationale: this suite defines the WI-1741 spec and plan.
- Host issue / PR / Project locator, or not-required rationale: GitHub issue #1741; PR locator pending until PR creation.

## Produces

- Artifact inventory: `spec.md`, `plan.md`, `research.md`, `contracts.md`, `readiness-checklist.md`, `evidence-map.md`, `task-carrier.md`.
- Path selection rationale: full suite required for ship wrapper behavior and validation command selection.
- Story readiness consumed state: not required.
- Story business confirmation consumed state: not required.
- Deferred item table: #1739 repair chain, #1742 closeout e2e, and #1743 release remain separate issues.
- Not-required item table: release publish, repair chain execution, and closeout policy execution are outside WI-1741.
- Generated / skills integration requirements: no generated skill runtime copy changes are expected; `tools/skills_surface.py check` verifies docs/source surface consistency.

## Artifact Inventory

| Artifact | Locator | Status | Consumer | Provenance |
| --- | --- | --- | --- | --- |
| `spec.md` | .loom/specs/WI-1741/spec.md | required / present | `plan.md`, review, merge-ready, closeout | issue #1741 |
| `plan.md` | .loom/specs/WI-1741/plan.md | required / present | implementation, review, merge-ready, closeout | issue #1741 and local validation |
| `research.md` | .loom/specs/WI-1741/research.md | conditional / present | plan and review | changed-path validation inventory |
| `contracts.md` | .loom/specs/WI-1741/contracts.md | conditional / present | plan, review, CLI consumers | ship validation profile output contract |
| `readiness-checklist.md` | .loom/specs/WI-1741/readiness-checklist.md | conditional / present | build / review readiness consumers | local validation |
| `evidence-map.md` | .loom/specs/WI-1741/evidence-map.md | required / present | review, merge-ready, closeout | command evidence |
| `task-carrier.md` | .loom/specs/WI-1741/task-carrier.md | required / present | review, merge-ready, closeout | GitHub issue #1741 |

## Deferred Items

- Locator: GitHub issues #1739, #1742, #1743.
- Reason: each issue owns a separate lane and PR scope.
- Activation condition: their explicit dependencies merge and close out.
- Does not currently block: WI-1741 ship validation profile selection.
- Statement: deferred is not completed.

## Excluded Items

- Locator: release/tag/npm publish.
- Rationale: #1741 only changes validation profile diagnostics in `loom ship`.
- Recheck condition: release scope belongs to #1743 after all prior lanes close.
- Consumers that should not require it: WI-1741 review and merge-ready.

## Locator

- Suite index locator: .loom/specs/WI-1741/suite-index.md
- Repo-relative artifact root: .loom/specs/WI-1741
- Host comment / issue evidence locator: GitHub issue #1741

## Provenance

- Source issue / PR / doc / conversation locator: GitHub issue #1741; milestone #17 parent FR #1734.
- Trust boundary: repo-local suite artifacts define WI-1741 review inputs but do not replace GitHub issue/PR, checks, review, merge-ready, or closeout truth.
- Freshness rule: Refresh after PR head, issue state, review findings, validation commands, or ship profile contract changes.
- Recheck condition: Run suite validate/evidence/carrier validate before review and merge-ready.
