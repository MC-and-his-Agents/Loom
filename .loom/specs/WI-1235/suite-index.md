# Full Suite Index

## Suite Path Decision

- Schema marker: loom-full-suite-index/v1
- Suite path: full
- Work Item / FR locator: GitHub issue #1235; parent FR #1228
- Path decision provenance: `python3 tools/loom.py suite scaffold --target . --item WI-1235 --suite full --apply --json`; issue #1235 acceptance criteria.
- Minimal path not sufficient because: #1235 changes public CLI repair/apply semantics, generated skills runtime payloads, repo-local carrier mutation behavior, and fail-closed ownership contracts consumed by later #1236/#1237/#1296 work.
- Freshness rule: Recheck after source/runtime copy changes, PR head changes, repair contract changes, review findings, or merge-ready gate updates.

## Consumes

- Story Readiness confirmed locator, blocking locator, or `not required` rationale: not required; #1235 is an executable Work Item with acceptance criteria in GitHub issue #1235.
- Story Business Confirmation confirmed locator, blocking locator, or `not required` rationale: not required; no product/business semantic change beyond Loom governance CLI behavior.
- Delivery planning / issue-tree locator, or `not required` rationale: GitHub parent FR #1228 and Round 9 milestone dependency order.
- Existing spec / plan locator, or `not required` rationale: not required before this suite; this file creates the WI-1235 full-suite decision.
- Host issue / PR / Project locator, or `not required` rationale: GitHub issue #1235; PR locator pending until PR creation.

## Produces

- Artifact inventory: `spec.md`, `plan.md`, `implementation-contract.md`, `research.md`, `contracts.md`, `readiness-checklist.md`, `evidence-map.md`, `task-carrier.md`.
- Path selection rationale: full suite required for CLI mutation and fail-closed contract changes.
- Story readiness consumed state: not required.
- Story business confirmation consumed state: not required.
- Deferred item table: no deferred scope inside #1235; downstream #1236/#1237/#1296 remain separate issues and are not completed by this suite.
- `not required` item table: live host mutation by repair command; release/tag/npm actions; issue/project mutation from repair command.
- #1020 generated / skills integration requirements: generated `skills/loom-*/.loom-runtime/shared/scripts/loom_flow.py` must stay synchronized with `src/skills/shared/scripts/loom_flow.py`.

## Artifact Inventory

| Artifact | Locator | Status | Consumer | Provenance |
| --- | --- | --- | --- | --- |
| `spec.md` | .loom/specs/WI-1235/spec.md | required | `plan.md`, review, merge-ready, closeout | issue #1235 |
| `plan.md` | .loom/specs/WI-1235/plan.md | required | implementation, review, merge-ready, closeout | issue #1235 and local validation |
| `implementation-contract.md` | .loom/specs/WI-1235/implementation-contract.md | required | review, merge-ready, rollback | issue #1235 and implementation scope |
| `research.md` | .loom/specs/WI-1235/research.md | conditional | `plan.md`, `contracts.md`, readiness checklist | read-only review findings and local diagnostics |
| `contracts.md` | .loom/specs/WI-1235/contracts.md | conditional | `plan.md`, readiness checklist, CLI consumers | repair plan/apply schema and fail-closed behavior |
| `readiness-checklist.md` | .loom/specs/WI-1235/readiness-checklist.md | conditional | build / review readiness consumers | local validation and carrier state |
| `evidence-map.md` | .loom/specs/WI-1235/evidence-map.md | required | review, merge-ready, closeout | command evidence |
| `task-carrier.md` | .loom/specs/WI-1235/task-carrier.md | required | review, merge-ready, closeout | GitHub issue #1235 |

## Deferred Items

- Locator: GitHub issues #1236, #1237, #1296
- Reason: dependency order requires #1235 behavior to merge first.
- Activation condition: #1235 PR merged and issue #1235 closed/completed.
- Does not currently block: #1235 implementation and PR validation.
- Statement: deferred is not completed.

## Excluded Items

- Locator: release/tag/npm publish
- Rationale: #1235 only implements source and generated runtime repair behavior; release/no-release closeout is #1296.
- Recheck condition: after #1236 and #1237 merge, before #1296 closeout.
- Consumers that should not require it: #1235 review and merge-ready.

## Locator

- Suite index locator: .loom/specs/WI-1235/suite-index.md
- Repo-relative artifact root: .loom/specs/WI-1235
- Host comment / issue evidence locator: GitHub issue #1235

## Provenance

- Source issue / PR / doc / conversation locator: GitHub issue #1235; current Codex Round 9 goal.
- Trust boundary: repo-local suite artifacts define #1235 review inputs but do not replace GitHub issue/PR, checks, review, merge-ready, or closeout truth.
- Freshness rule: Refresh after PR head, issue state, review findings, validation commands, or repair contract changes.
- Recheck condition: Run suite validate/evidence/carrier validate before review and merge-ready.
