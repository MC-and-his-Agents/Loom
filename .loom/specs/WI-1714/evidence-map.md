# Evidence Map

## Context

- Work Item locator: `.loom/work-items/WI-1714.md`
- FR / parent locator: GitHub issue #1711
- Scope: deterministic plugin payload hash generation, package validation surface, release evidence label, and focused regression tests.
- Suite path: minimal, documented in `.loom/specs/WI-1714/spec.md` and `.loom/specs/WI-1714/plan.md`
- Current `HEAD`: current PR head after push and PR metadata readback
- PR locator: pending PR for branch `work/1714-plugin-payload-hash`
- Host state locator: issue #1714 and pending PR readback

## Input Snapshot

| Input | Locator | Status | Provenance | Freshness rule |
| --- | --- | --- | --- | --- |
| `spec.md` | `.loom/specs/WI-1714/spec.md` | required | suite inspect | Recheck if #1714 scope or suite path changes. |
| `plan.md` | `.loom/specs/WI-1714/plan.md` | required | suite inspect | Recheck if validation strategy changes. |
| execution breakdown / task carrier | `.loom/specs/WI-1714/task-carrier.md` | optional | suite carrier inspect | Recheck issue, PR, branch, head SHA, hosted checks, review, and closeout before merge-ready. |
| review record | `.loom/reviews/WI-1714.json` | required before merge-ready | authored review truth | Required before PR gate, merge-ready, and closeout consumption. |
| host state | issue #1714 and pending PR | required | host mirror | Recheck before merge-ready, controlled merge, and closeout. |

## Evidence Rows

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | `tools/check_npm_package.py` | S1 S2 S3 / A1 A2 A3 A4 | WI-1714 / package validation behavior / current head | present | review / merge-ready / closeout / status | Re-run package hash surface and unit tests after checker changes. |
| EV-002 | test_evidence | `test/plugin_payload_hash_test.py` | A1 A2 A3 | WI-1714 / deterministic hash algorithm / current head | present | review / merge-ready / closeout / status | Run `PYTHONDONTWRITEBYTECODE=1 python3 test/plugin_payload_hash_test.py`. |
| EV-003 | test_evidence | `tools/check_npm_package.py` | A4 | WI-1714 / package validation output / current head | present | review / merge-ready / closeout / status | Run `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_npm_package.py --surface plugin-payload-hash`. |
| EV-004 | test_evidence | `tools/check_npm_package.py` | aggregate package validation | WI-1714 / release package aggregate / current head | present | review / merge-ready / closeout / status | Run `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_npm_package.py`. |
| EV-005 | fresh_verification_input | `.loom/progress/WI-1714.md` | EV-001 EV-002 EV-003 EV-004 | WI-1714 / latest validation summary / current head | present | merge-ready / closeout / status | Refresh progress summary, PR metadata, review record, and shadow carriers after any head drift. |

## Out Of Scope / Deferred

| Subject | Status | Rationale | Consumer boundary | Recheck condition | Follow-up locator |
| --- | --- | --- | --- | --- | --- |
| Plugin metadata writeback | deferred | #1714 only computes and validates the digest. | release metadata generation | Recheck when manifest metadata is added. | #1713 |
| Host source/cache readback | deferred | Requires release metadata and host cache inspection semantics. | version/doctor/host readback | Recheck when source/cache readback is implemented. | #1721 |
