# WI-1643 Evidence Map

## Context

- Work Item locator: .loom/work-items/WI-1643.md
- FR / parent locator: https://github.com/MC-and-his-Agents/Loom/issues/1643
- Scope: v0.17.0 version-only release PR for milestone #14.
- Suite path: release-only; formal suite bypass is declared in .loom/specs/WI-1643/spec.md.
- Current `HEAD`: current PR #1656 metadata binding
- PR locator: https://github.com/MC-and-his-Agents/Loom/pull/1656
- Host state locator: https://github.com/MC-and-his-Agents/Loom/issues/1643

## Input Snapshot

| Input | Locator | Status | Provenance | Freshness rule |
| --- | --- | --- | --- | --- |
| `spec.md` | .loom/specs/WI-1643/spec.md | required | suite inspect | Bind to current Work Item, scope, and head before consumption. |
| `plan.md` | release-only bypass | not required | suite path decision | Recheck if release PR stops being version-only. |
| suite path decision | .loom/specs/WI-1643/spec.md | present | suite inspect | Recheck when suite path changes. |
| execution breakdown / task carrier | .loom/specs/WI-1643/task-carrier.md | required | authored release carrier | Recheck before merge-ready consumption. |
| review record | .loom/reviews/WI-1643.json | required | authored review truth | Required only after review consumption. |
| merge-ready basis | .loom/progress/WI-1643.md | required | merge-ready truth | Required only for merge-ready or closeout consumption. |
| host state | https://github.com/MC-and-his-Agents/Loom/pull/1656 | required | host mirror | Required when PR / issue / Project exists. |

## Evidence Rows

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | VERSION | .loom/specs/WI-1643/spec.md release scope | WI-1643 / v0.17.0 / PR #1656 / current PR metadata head | present | review / merge-ready / closeout / status | Re-run version and release surface checks if release target or version files change. |
| EV-002 | test_evidence | .loom/progress/WI-1643.md | WI-1643 release validation commands: `git diff --check`; `python3 tools/version_surface_check.py`; `python3 tools/check_release_surface.py`; `python3 tools/check_npm_package.py`; `npm run test:package`; `npm pack --dry-run --json --ignore-scripts`; `python3 tools/loom.py suite evidence validate --target . --item WI-1643 --json`; `python3 tools/loom.py suite carrier validate --target . --item WI-1643 --json` | WI-1643 / v0.17.0 / PR #1656 / current PR metadata head | present | review / merge-ready / closeout / status | Re-run release/package/suite validation if release carrier, package surface, or version files change. |
| EV-003 | fresh_verification_input | .loom/progress/WI-1643.md | EV-001 EV-002 | PR #1656 / validation summary / PR body metadata readback | present | merge-ready / closeout / status | Refresh progress, review, PR body, and readback after any new commit. |

## Formal Suite Bypass

| Subject | Status | Rationale | Consumer boundary | Recheck condition | Follow-up locator |
| --- | --- | --- | --- | --- | --- |
| formal suite artifacts | not_applicable | Release PR only bumps `VERSION` and `package.json` after release_required judgment #1636. | formal suite bypass only; does not bypass review, PR gate, hosted checks, merge, or post-merge release readback | Recheck if files beyond version surface or WI-1643 carriers change. | .loom/specs/WI-1643/spec.md |

## #1020 Follow-up Requirements

- Skills / GitHub profile consumption: not required for release PR.
- Generated surface sync: not required for version-only release PR.
- Drift check requirement: rerun release/package/readback checks before merge and release readback after main publishes v0.17.0.
