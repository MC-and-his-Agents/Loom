# Evidence Map

## Context

- Work Item locator: .loom/work-items/WI-1235.md
- FR / parent locator: GitHub issue #1228
- Scope: GitHub issue #1235 safe repair/sync flow only.
- Suite path: full
- Current `HEAD`: branch `work/1235-safe-repair-sync`; exact PR head pending until commit/push.
- PR locator, or `not required` rationale: pending PR creation.
- Host state locator, or `not required` rationale: GitHub issue #1235; parent FR #1228.

## Input Snapshot

| Input | Locator | Status | Provenance | Freshness rule |
| --- | --- | --- | --- | --- |
| `spec.md` | .loom/specs/WI-1235/spec.md | required | WI-1235 full suite | Refresh after requirements or repair contract changes. |
| `plan.md` | .loom/specs/WI-1235/plan.md | required | WI-1235 validation plan | Refresh after validation strategy changes. |
| `implementation-contract.md` | .loom/specs/WI-1235/implementation-contract.md | required | WI-1235 implementation contract | Refresh after write scope, runtime contract, validation plan, or host binding changes. |
| suite path decision | .loom/specs/WI-1235/suite-index.md | required | full suite scaffold and issue #1235 risk profile | Recheck if scope narrows or gate requirements change. |
| execution breakdown / task carrier | .loom/specs/WI-1235/task-carrier.md | required | GitHub issue #1235 primary carrier | Recheck issue, PR, branch, review, gate, and closeout state. |
| review record | .loom/reviews/WI-1235.json | required before merge-ready | Current-head semantic review | Refresh after final commit/head. |
| merge-ready basis | PR / checks / merge-ready gate | required before merge | Host PR and gate readback | Refresh after PR body/head/check changes. |
| host state | GitHub issue #1235; PR pending | required | GitHub readback | Refresh after PR creation, merge, issue closeout, or Project status changes. |

## Evidence Rows

| evidence_id | evidence_type | source_locator | consumes | binding | freshness | consumer_boundary | remediation_direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | src/skills/shared/scripts/loom_flow.py | S1-S3; A1-A3 | WI-1235 / branch `work/1235-safe-repair-sync` / PR head pending | present | review / merge-ready / closeout / status | Recheck after repair CLI, host truth, or carrier write behavior changes. |
| EV-002 | test_evidence | tools/check_cli_contract.py | A1-A4 | WI-1235 / local worktree / 2026-06-16T06:55Z validation | present | review / merge-ready / closeout / status | Rerun after code, test, generated runtime, or carrier changes. |
| EV-003 | fresh_verification_input | .loom/progress/WI-1235.md | EV-001 EV-002 plus generated-tree drift | WI-1235 / local worktree / 2026-06-16T06:55Z validation | present | review / merge-ready / closeout / status | Rerun after generated runtime or CLI contract changes. |
| EV-004 | structural_evidence | .loom/status/current.md | suite, fact-chain, review, merge-ready | WI-1235 carrier set / current branch | present | review / merge-ready / closeout / status | Rerun suite validate/evidence/carrier validate and fact-chain after carrier changes. |
| EV-005 | build_evidence | .loom/progress/WI-1235-build-evidence.json | delegated findings and integration ownership | WI-1235 / build checkpoint / integrated findings | present | build / pre-review / review | Recheck after implementation, validation evidence, or ownership changes. |
| EV-006 | fixture_evidence | examples/new-project/.loom/bin/loom_flow.py | generated runtime demo fixture sync | WI-1235 / hosted demo-bootstrap failure / local fixture sync | present | hosted checks / merge-ready | Rerun `make loom-demo-new-project-check` after runtime or demo bootstrap fixture changes. |

## Excluded / Deferred

| Subject | Status | Rationale | Consumer boundary | Recheck condition | Follow-up locator |
| --- | --- | --- | --- | --- | --- |
| release/tag/npm publish | not required | #1296 owns release/no-release closeout after #1236/#1237 merge. | #1235 review/merge-ready | Before #1296 | GitHub issue #1296 |
| #1236 fixture inventory | deferred | Must consume #1235 stable behavior after merge. | Round 9 dependency order | After #1235 closeout | GitHub issue #1236 |
| #1237 docs outline | deferred | Must consume #1235 stable behavior after merge. | Round 9 dependency order | After #1235 closeout | GitHub issue #1237 |
| PR merge and issue closeout readback | deferred | This evidence is produced after PR creation, checks, merge-ready, merge, and issue closeout; it must not be represented as pre-merge validation. | closeout / milestone | After #1235 PR merge | GitHub issue #1235 and its PR |

## #1020 Follow-up Requirements

- Skills / GitHub profile consumption: generated skills runtime copies must be synchronized for repair command behavior.
- Generated surface sync: `python3 tools/loom.py skills generate --apply --json` was run after source changes.
- Drift check requirement: aggregate CLI contract must pass before PR review/merge-ready.
