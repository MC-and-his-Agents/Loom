# WI-1294 Plan

## Suite Contract

- Suite path: minimal
- Suite path consumed: minimal
- Spec locator: .loom/specs/WI-1294/spec.md
- Plan locator: .loom/specs/WI-1294/plan.md
- Full-suite-artifacts not_applicable: rationale: #1294 has a concrete release issue, version bump, generated metadata sync, and release evidence path; consumer boundary: build, review, merge-ready, PR/CI, target branch validation, publish verification, #1217 correction evidence, and #1294 closeout consume this plan plus release evidence; recheck condition: require full path if package naming, release workflow semantics, metadata-only behavior, or installer publishing changes enter scope.

## Steps

1. Record the #1217 correction that #1227's PR-event `release-judgment-only` was not final publish evidence and the post-merge push release failed closed on occupied `v0.13.9`.
2. Create issue #1294 and branch `work/1294-release-followup`.
3. Bump root `VERSION` to `v0.13.10` and root `package.json` to `0.13.10`.
4. Regenerate generated skill package surfaces so `skills/*/loom-package.json` `repo_version` matches `v0.13.10`.
5. Run local release/version/package/CLI/skills/npm dry-run checks.
6. Commit, push, open PR, validate CI, and merge.
7. Verify main `loom-cli-release`, `v0.13.10` tag, GitHub Release, npm package, and install smoke evidence.
8. Record final evidence on #1217 and #1294, then close #1294.

## Scenario Mapping

- S1 -> Steps 3 and 4.
- S2 -> Step 5 and PR CI.
- S3 -> Steps 6 and 7.
- S4 -> Steps 1 and 8.

## Acceptance Mapping

- AC-1 -> structural evidence: `VERSION`, `package.json`, `tools/version_surface_check.py`, and `tools/check_npm_package.py`.
- AC-2 -> structural evidence: `skills/*/loom-package.json`, `tools/skills_surface.py check`, and `tools/version_surface_check.py`.
- AC-3 -> test evidence: `tools/check_release_surface.py`, `tools/version_surface_check.py`, `tools/check_npm_package.py`, `tools/check_cli_contract.py`, `tools/skills_surface.py check`, `tools/loom.py skills check --target . --json`, `npm pack --dry-run --json --ignore-scripts`, `git diff --check`, and PR CI.
- AC-4 -> test evidence: main `loom-cli-release` workflow, GitHub tag `v0.13.10`, GitHub Release `v0.13.10`, and npm `@mc-and-his-agents/loom@0.13.10`.
- AC-5 -> manual evidence: #1217 and #1294 comments plus #1294 closed state.

## Applicability Boundary

- Full-suite-artifacts not_applicable: rationale: the implementation is constrained to version surfaces, generated release metadata, checks, and host release evidence; consumer boundary: no full research, contracts, readiness checklist, or suite index artifact is required to review this release follow-up; recheck condition: require full suite artifacts if this change introduces release workflow logic, package distribution changes beyond version bump, or metadata-only behavior changes.
