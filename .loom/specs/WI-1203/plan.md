# WI-1203 Plan

## Suite Contract

- Suite path: minimal
- Suite path consumed: minimal
- Spec locator: .loom/specs/WI-1203/spec.md
- Plan locator: .loom/specs/WI-1203/plan.md
- Full-suite-artifacts not_applicable: rationale: WI-1203 is limited to release metadata, WI-1196 terminal carrier cleanup, validation, PR/CI, main release workflow readback, and closeout evidence; consumer boundary: build checkpoint, spec review, implementation review, merge-ready, PR/CI, release workflow, and issue closeout should consume the minimal suite plus implementation contract rather than require full-path planning artifacts; recheck condition: require full suite artifacts if implementation scope expands into CLI behavior, workstation registration semantics, target repository layout migration, #1204 downstream plugin layout, or cross-artifact evidence design.

## Steps

1. Bump `VERSION` to `v0.13.8` and `package.json` to `0.13.8`.
2. Sync `repo_version` in each `skills/*/loom-package.json` to `v0.13.8`.
3. Validate release and package contracts locally.
4. Open and merge the follow-up PR after CI passes.
5. Validate `main` release workflow and close the #1197-#1203 issue tree with evidence.

## Scenario Mapping

- S1 -> `python3 tools/version_surface_check.py`.
- S2 -> `python3 tools/check_release_surface.py`, `python3 tools/check_npm_package.py`, `python3 tools/check_cli_contract.py`, and `git diff --check`.
- S3 -> PR checks, main branch release workflow readback, and issue closeout comments.

## Acceptance Mapping

- AC-1 -> test evidence: `python3 tools/version_surface_check.py`.
- AC-2 -> test evidence: `python3 tools/check_release_surface.py`, `python3 tools/check_npm_package.py`, `python3 tools/check_cli_contract.py`, and `git diff --check`.
- AC-3 -> manual evidence: PR checks, main branch workflow readback, and child-to-parent issue closeout evidence.

## Applicability Boundary

- Full-suite-artifacts not_applicable: rationale: `suite-index.md`, `research.md`, `contracts.md`, and `readiness-checklist.md` are not needed because this item only repairs release version authority required by the main branch release workflow; consumer boundary: suite validate, review record, merge-ready, PR/CI, main release workflow readback, and issue closeout must not require those full-path artifacts for WI-1203; recheck condition: require the full path if the item starts carrying product behavior, CLI behavior, host registration semantics, or downstream layout changes.
