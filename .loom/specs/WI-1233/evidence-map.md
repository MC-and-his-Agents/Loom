# Evidence Map

## Context

- Work Item locator: .loom/work-items/WI-1233.md
- FR / parent locator: GitHub issue #1228
- Scope: GitHub issue #1233 diagnostics only; classify host-complete non-terminal carriers as `carrier_closeout_required` while preserving `stale_carrier`, `shared_workspace_conflict`, and `closeout_required` semantics.
- Suite path: minimal
- Current `HEAD`: PR #1474 head, read back from the PR body machine carrier after each worker commit.
- PR locator: https://github.com/MC-and-his-Agents/Loom/pull/1474
- Host state locator: GitHub issue #1233 and PR #1474 readback.

## Input Snapshot

| Input | Locator | Status | Provenance | Freshness rule |
| --- | --- | --- | --- | --- |
| `spec.md` | .loom/specs/WI-1233/spec.md | required | WI-1233 minimal suite path | Refresh after #1233 requirements or suite path changes. |
| `plan.md` | .loom/specs/WI-1233/plan.md | required | WI-1233 minimal validation plan | Refresh after validation strategy or required checks change. |
| suite path decision | .loom/specs/WI-1233/spec.md | required | `Suite path: minimal` with explicit rationale for skipped full-suite artifacts | Recheck if scope expands beyond #1233 diagnostics or scheduler requires full suite evidence. |
| execution breakdown / task carrier | .loom/specs/WI-1233/task-carrier.md | optional | GitHub issue #1233 primary carrier | Recheck issue, PR, branch, and recovery state before merge-ready or closeout. |
| review record | .loom/reviews/WI-1233.json | optional before scheduler review | Scheduler-owned current-head review artifact | Required only after scheduler records or consumes current-head review. |
| merge-ready basis | PR #1474 / scheduler gate | optional before scheduler gate | Scheduler-owned PR gate and merge-ready flow | Required before merge or closeout consumption. |
| host state | GitHub issue #1233; PR #1474 | required | GitHub readback | Refresh after PR head/body, issue state, hosted checks, or review state changes. |

## Evidence Rows

| evidence_id | evidence_type | source_locator | consumes | binding | freshness | consumer_boundary | remediation_direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | skills/shared/scripts/loom_flow.py; docs/methodology/harness/workspace-and-purity.md | .loom/specs/WI-1233/spec.md requirements for `carrier_closeout_required`, preserved `stale_carrier`, preserved `shared_workspace_conflict`, and unchanged `closeout_required` semantics | WI-1233 / #1233 diagnostics scope / PR #1474 current head | present | review / merge-ready / PR gate / closeout / status | Recheck active workspace diagnostics and docs after changing host-truth classification or remediation text. |
| EV-002 | test_evidence | .loom/progress/WI-1233.md | .loom/specs/WI-1233/plan.md validation: `git diff --check`; Python compile; focused retire-workspace fixture; suite validate; suite carrier validate; fact-chain; CLI contract; PR metadata preflight/readback | WI-1233 / #1233 validation summary / PR #1474 current head | present | review / merge-ready / PR gate / closeout / status | Rerun validation and refresh progress/status after code, runtime copy, carrier, evidence map, or PR head changes. |
| EV-003 | fresh_verification_input | PR #1474 body machine carrier; .loom/progress/WI-1233.md | EV-001 EV-002 plus PR body metadata readback for current PR head | WI-1233 / PR #1474 current head / scheduler-owned review pending | present | review / merge-ready / PR gate / closeout / status | Refresh PR body machine carrier and rerun metadata preflight/readback after every commit before scheduler-owned review or gate consumption. |

## Suite Applicability

- Full-suite-artifacts not_applicable: artifacts `suite-index.md`, `research.md`, `contracts.md`, and `readiness-checklist.md`; rationale: WI-1233 is a narrow diagnostics vocabulary and carrier-evidence correction under a granted contract lane, with minimal suite evidence sufficient to prove the #1233 behavior and validation surface; consumer boundary: suite validate, review, merge-ready, PR metadata, hosted checks, PR gate, merge, closeout, and status consume this evidence map only as the minimal-suite artifact rationale and must still require current-head review, PR metadata, hosted checks, PR gate, merge, and closeout evidence; recheck condition: require full suite artifacts if scope expands beyond #1233 diagnostics/evidence readiness, scheduler upgrades review requirements, or the change starts altering unrelated parser, schema, release, runtime, permission, or downstream issue semantics.

## Deferred Scheduler-Owned Artifacts

- Review artifacts deferred: `.loom/reviews/WI-1233.json` and `.loom/reviews/WI-1233.spec.json` are scheduler-owned and explicitly forbidden in this worker correction. Consumer boundary: review / merge-ready / PR gate. Recheck condition: scheduler records current-head review artifacts.

## #1020 Follow-up Requirements

- Skills / GitHub profile consumption: consume the table rows as evidence-map contract rows, not as review approval.
- Generated surface sync: out of scope for this correction; no generated runtime copy changes are included.
- Drift check requirement: rerun suite evidence validation and PR metadata preflight/readback after each PR head change.
