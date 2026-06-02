# WI-1203 Spec

## Suite Contract

- Suite path: minimal
- Work Item / FR locator: #1203 / #1196
- Path decision provenance: PR #1212 changed CLI behavior and the main release workflow required a new unpublished Loom CLI version.
- Full-suite-artifacts not_applicable: rationale: WI-1203 is a narrow release metadata closeout with no behavior, downstream plugin layout, workstation registration semantic, or cross-artifact design change; consumer boundary: suite validate, spec review, implementation review, merge-ready, release workflow validation, and issue closeout should require only `spec.md`, `plan.md`, implementation contract, Loom carriers, version metadata, and validation evidence; recheck condition: promote to full suite if this item starts owning CLI behavior, host registration semantics, target repository layout migration, #1204 downstream plugin layout, evidence-map freshness design, task carrier decomposition, or cross-issue contract changes.

## Scope

Minimal release-readiness closeout for #1196 after PR #1212 changed CLI behavior and main release judgment required a new unpublished Loom CLI version.

## Scenarios

- S1: VERSION, package.json, and every skill loom-package repo_version agree on v0.13.8 / 0.13.8.
- S2: Release surface, npm package contract, CLI contract, and diff hygiene pass on the release bump branch.
- S3: The follow-up PR merges to main and the main release workflow passes for the new merge commit.

## Acceptance Criteria

- AC-1: `python3 tools/version_surface_check.py` passes.
- AC-2: `python3 tools/check_release_surface.py`, `python3 tools/check_npm_package.py`, `python3 tools/check_cli_contract.py`, and `git diff --check` pass.
- AC-3: Main branch validation passes after merge; #1197-#1203 and #1196 receive closeout evidence.

## Applicability Boundary

- Full-suite-artifacts not_applicable: rationale: `suite-index.md`, `research.md`, `contracts.md`, and `readiness-checklist.md` are not needed because WI-1203 only bumps release version metadata and records closeout evidence for already-merged PR #1212; consumer boundary: suite validate, review record, merge-ready, PR/CI, main release workflow readback, and issue closeout must not require those full-path artifacts for this narrow item; recheck condition: require the full path if the scope expands beyond release metadata and closeout evidence.
