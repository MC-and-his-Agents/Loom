# WI-1217 Plan

## Suite Contract

- Suite path: minimal
- Suite path consumed: minimal
- Spec locator: .loom/specs/WI-1217/spec.md
- Plan locator: .loom/specs/WI-1217/plan.md
- Full-suite-artifacts not_applicable: rationale: #1217 has an explicit child issue tree and concrete verification commands; consumer boundary: build, review, merge-ready, PR/CI, target branch validation, issue closeout, and release/no-release decision consume this plan plus fixture evidence; recheck condition: require full path if migration apply, workstation registration semantics, or release publication mechanics change.

## Steps

1. Freeze installation taxonomy and authority boundaries for metadata-only and embedded adoption.
2. Extend installed-state to express metadata-only repository adoption and user-level skills provider dependency.
3. Split CLI behavior so metadata-only install writes only repository adoption metadata and embedded payload remains opt-in.
4. Update detect, doctor, verify, host verify, and skills check to validate metadata-only without repo skills payload.
5. Formalize skills provider, embedded bundle, compatibility export, and single-skill boundaries in docs and diagnostics.
6. Preserve embedded payload mode and legacy runtime carrier policy without deleting repo-owned governance evidence.
7. Update README, Codex install docs, unified install docs, host adapter matrix, installed-state docs, CLI matrix, and plugin manifest.
8. Add regression fixtures for metadata-only, unexpected embedded payload pollution, and embedded payload compatibility.
9. Run required local checks, validate PR/CI, merge, validate target branch, close #1218-#1226/#1217 with evidence, then publish or record no-release decision.

## Scenario Mapping

- S1 -> Steps 2, 3, and metadata-only fixture install assertions.
- S2 -> Steps 2 and installed-state graph assertions.
- S3 -> Steps 3, 4, `installed-state validate`, `host verify`, `skills check`, and `detect` fixture assertions.
- S4 -> Steps 4 and unexpected payload pollution fixture.
- S5 -> Steps 3, 4, embedded host install/verify fixture.
- S6 -> Steps 1, 5, 6, 7, docs checks, release surface checks, and plugin manifest validation.

## Acceptance Mapping

- AC-1 -> structural evidence: `docs/adoption/installation-taxonomy.md`.
- AC-2 -> test evidence: metadata-only installed-state fixture and validation assertions.
- AC-3 -> test evidence: targeted metadata-only CLI commands and `tools/check_cli_contract.py` fixture.
- AC-4 -> behavior evidence: `tools/loom.py` provider mode and doctor/workstation separation.
- AC-5 -> manual evidence: README/adoption/CLI docs and plugin manifest self-description.
- AC-6 -> test evidence: metadata-only, pollution, and embedded fixtures.
- AC-7 -> test evidence: `git diff --check`, `check_release_surface.py`, `skills_surface.py check`, `check_cli_contract.py`, `make loom-check`, PR/CI, target branch validation, and release/no-release record.

## Applicability Boundary

- Full-suite-artifacts not_applicable: rationale: the implementation is constrained to metadata-only adoption mode, installed-state, checks, docs, fixtures, and root governance carriers; consumer boundary: no full research or contracts artifact is required to review this bounded change; recheck condition: require full suite artifacts if the change introduces destructive repair apply, new package release automation, or a new host profile system.
