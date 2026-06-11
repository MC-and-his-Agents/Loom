# WI-1395 Spec

- Suite path: minimal
- Work Item / FR locator: #1395 / #1260
- Path decision provenance: issue #1395 scopes a bounded installed/global CLI smoke validation surface over the existing release checker and requires concrete command evidence for targeted and aggregate behavior.

## Scope

Add `installed-global-cli-smoke` as a targetable release validation surface while preserving aggregate release/package validation behavior and the #1383 release validation evidence contract.

## Scenarios

- Scenario S1: `python3 tools/check_release_surface.py --surface installed-global-cli-smoke` validates a temporary global install of the locally packed root `@mc-and-his-agents/loom` package and runs installed `loom version --json` plus `loom help --json` smoke.
- Scenario S2: `python3 tools/check_release_surface.py` remains an aggregate compatibility check that consumes the #1393 release surfaces plus `installed-global-cli-smoke`.
- Scenario S3: `make release-surface-installed-global-cli-smoke-check` targets only the installed/global CLI smoke surface.

## Acceptance Criteria

- AC-1: Installed/global CLI smoke is a stable targetable surface named `installed-global-cli-smoke`.
- AC-2: The surface emits stable failure labels and evidence locators under `python3 tools/check_release_surface.py --surface installed-global-cli-smoke`.
- AC-3: The no-argument aggregate release validator remains available and compatible with release/package validation consumers.
- AC-4: The surface consumes the #1383 evidence label without redefining release/no-release semantics or implementing #1396 convergence/closeout.
- AC-5: The smoke uses temporary local package install evidence only; it does not publish npm, cut tags, create GitHub Releases, or mutate the user's global npm prefix.

## Full Suite Artifact Applicability

- Full suite artifacts not_applicable: rationale: WI-1395 is a narrow executable checker surface split with issue-authored acceptance criteria, minimal spec/plan coverage, the existing #1383 evidence label, and direct command validation; separate suite-index, research, readiness-checklist, consistency-analysis, execution-breakdown, or full-suite artifact inventory would duplicate the issue and command evidence for this slice. consumer boundary: suite validate, review, merge-ready, PR gate, hosted CI, parent #1260 closeout, and release-required downstream work may consume this minimal suite plus PR metadata, command output, hosted checks, and scheduler-owned review/gate evidence; fact-chain, current-head review, PR metadata/readback, hosted checks, release/no-release judgment, controlled merge, and closeout evidence remain required. recheck condition: require a full suite if the scope expands into #1393 release validator semantics, #1394 npm manifest/payload semantics, #1396 evidence convergence, release workflow semantics, npm publishing, package runtime behavior beyond local smoke validation, external-visible release actions, or parent #1260/#1255 closeout.
