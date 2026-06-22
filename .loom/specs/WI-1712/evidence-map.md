# Evidence Map

## Context

- Work Item locator: `.loom/work-items/WI-1712.md`
- FR / parent locator: GitHub issue #1711
- Scope: Freeze the plugin payload version/hash authority contract, update install-surface/version docs, mirror the skills distribution contract, update the version surface guard, and keep WI-1712 fact-chain carriers aligned.
- Suite path: documented by the formal suite decision in `.loom/specs/WI-1712/spec.md` and `.loom/specs/WI-1712/plan.md`
- Current `HEAD`: current PR #1723 head, proven by PR metadata readback after each push
- PR locator: PR #1723
- Host state locator: PR #1723 and issue #1712 readback

## Input Snapshot

| Input | Locator | Status | Provenance | Freshness rule |
| --- | --- | --- | --- | --- |
| `spec.md` | `.loom/specs/WI-1712/spec.md` | required | suite inspect | Recheck if WI-1712 scope or suite path changes. |
| `plan.md` | `.loom/specs/WI-1712/plan.md` | required | suite inspect | Recheck if validation strategy or suite path changes. |
| suite path decision | `.loom/specs/WI-1712/spec.md` | documented in spec and plan | authored WI-1712 suite decision | Recheck if scope expands into runtime behavior, release mechanics, fixtures, legacy installer behavior, or external-visible behavior. |
| execution breakdown / task carrier | `.loom/specs/WI-1712/task-carrier.md` | optional | suite carrier inspect | Recheck issue, PR, branch, head SHA, hosted checks, review, and closeout before merge-ready. |
| review record | `.loom/reviews/WI-1712.json` | required | authored review truth | Required before PR gate, merge-ready, and closeout consumption. |
| merge-ready basis | PR #1723 PR gate / merge-ready readback | required | merge-ready truth | Required before controlled merge. |
| host state | PR #1723 and issue #1712 | required | host mirror | Recheck before merge-ready, controlled merge, and closeout. |

## Evidence Rows

| Evidence id | Type | Source locator | Consumes | Binding | Freshness | Consumer boundary | Remediation direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | behavior_evidence | `docs/adoption/version-authority-map.md` | `.loom/specs/WI-1712/spec.md#formal-suite-decision` | WI-1712 / contract freeze scope / current PR #1723 head | present | review / merge-ready / closeout / status | Re-run `python3 tools/version_surface_check.py` and `python3 tools/skills_surface.py check` after changing version authority or skill distribution contract wording. |
| EV-002 | test_evidence | `tools/version_surface_check.py` | `.loom/specs/WI-1712/plan.md#formal-suite-decision` | WI-1712 / contract docs and generated skills mirrors / current PR #1723 head | present | review / merge-ready / closeout / status | Re-run `python3 tools/version_surface_check.py`, `python3 tools/skills_surface.py check`, and `npm --prefix packages/loom-installer run check:docs` after doc, generated skill, or doc-sync guard changes. |
| EV-003 | test_evidence | `tools/check_release_surface.py` | `.loom/specs/WI-1712/plan.md#formal-suite-decision` | WI-1712 / release-no-release boundary / current PR #1723 head | present | review / merge-ready / closeout / status | Re-run `git diff --check`, release surface checks, and `python3 tools/check_npm_package.py --surface npm-package-manifest` if release docs, package manifest surfaces, or release judgment changes. |
| EV-004 | fresh_verification_input | `.loom/progress/WI-1712.md` | EV-001 EV-002 EV-003 plus fact-chain and CLI contract freshness | WI-1712 / latest validation summary / current PR #1723 head | present | merge-ready / closeout / status | Refresh progress summary, PR metadata, evidence-map, review record, and shadow carriers after any new commit or head drift. |

## Out Of Scope / Deferred

| Subject | Status | Rationale | Consumer boundary | Recheck condition | Follow-up locator |
| --- | --- | --- | --- | --- | --- |
| Full formal suite artifacts | out_of_scope | WI-1712 is a docs-governance contract freeze and does not implement runtime behavior. | suite validate / review / merge-ready / PR gate / hosted CI / closeout | Recheck if scope expands beyond the contract docs, generated skills mirrors, version surface guard, fact-chain carriers, doc-sync guard, or workspace binding repair. | #1713-#1722 |
| Release publication | out_of_scope | WI-1712 freezes the contract only; release is handled by #1718 after implementation issues close. | release judgment / merge-ready / closeout | Recheck if this PR starts changing `VERSION`, npm package version, release notes, tags, or publish workflow. | #1718 |

## #1020 Follow-up Requirements

- Skills / GitHub profile consumption: outside WI-1712; downstream implementation issues consume this contract.
- Generated surface sync: `src/skills/distribution-and-adapter-contract.md`, `skills/distribution-and-adapter-contract.md`, and `plugins/loom/skills/distribution-and-adapter-contract.md` remain aligned by `python3 tools/skills_surface.py check`.
- Drift check requirement: PR #1723 metadata, evidence-map, review record, and shadow carriers must be refreshed after any head change.
