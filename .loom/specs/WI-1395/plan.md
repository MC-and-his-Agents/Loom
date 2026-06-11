# WI-1395 Plan

- Suite path: minimal

## Implementation

1. Add `installed-global-cli-smoke` to `tools/check_release_surface.py` as a named surface.
2. Implement the smoke with `npm pack --json --ignore-scripts`, temporary `npm install --global --prefix <tmp> <pack.tgz>`, and installed `loom version --json` / `loom help --json` checks.
3. Keep `python3 tools/check_release_surface.py` as the aggregate release validation entrypoint and include the new surface in aggregate execution.
4. Add a narrowly named Make target for the smoke surface.
5. Update the #1383 evidence table locator to point at the new targetable command without changing release/no-release semantics.
6. Validate targeted smoke, aggregate release/package checks, package smoke tests, suite inspect/validate, PR metadata readback, and hosted check classification.

## Validation Mapping

- S1 -> automated validation evidence: `python3 tools/check_release_surface.py --surface installed-global-cli-smoke --show-surface-evidence`.
- S2 -> automated validation evidence: `python3 tools/check_release_surface.py`, plus `python3 tools/check_npm_package.py` and `npm run test:package` for package aggregate compatibility.
- S3 -> automated validation evidence: `make release-surface-installed-global-cli-smoke-check`.
- AC-1 -> structural and command evidence: `python3 tools/check_release_surface.py --list-surfaces` lists `installed-global-cli-smoke`.
- AC-2 -> structural check: targeted failure paths emit `surface_label=installed-global-cli-smoke`, stable `failure_label` values, and `evidence_locator=python3 tools/check_release_surface.py --surface installed-global-cli-smoke`.
- AC-3 -> test evidence: the aggregate release validator keeps `python3 tools/check_release_surface.py` available and returns `release surface check: OK` after running the #1393 surfaces plus installed/global CLI smoke.
- AC-4 -> manual evidence: `docs/adoption/loom-cli-release-surface.md` maps #1383 label `installed-global-cli-smoke` to the new command without redefining release/no-release semantics.
- AC-5 -> manual and command evidence: changed files do not modify `VERSION`, release workflows, npm publish behavior, tags, GitHub Releases, or the user's global npm prefix; the smoke uses a temporary npm global prefix.

## Minimal Path Applicability Records

- full-path-artifacts not_applicable rationale: WI-1395 is bounded to an existing release checker surface addition and can be verified through focused command outputs, Makefile target, aggregate compatibility, npm package smoke tests, PR metadata, and hosted checks. consumer boundary: suite validate, review, merge-ready, PR gate, hosted CI, parent #1260 closeout, and release-required downstream work consume this minimal spec/plan plus command and PR evidence; fact-chain, current-head review, release/no-release judgment, controlled merge, and closeout remain separately required. recheck condition: require a full suite if scope expands into release workflow semantics, npm publish behavior, package runtime behavior beyond local smoke validation, external-visible actions, #1393/#1394/#1396 scope, or parent #1260/#1255 closeout.

## Deferred Items

- #1396 docs/evidence convergence remains out of scope. Statement: deferred is not completed.
- Parent #1260 and umbrella #1255 closeout remain scheduler-owned/out of scope. Statement: deferred is not completed.
- Release cutting, npm publish, `VERSION`/tag/GitHub Release changes, and `.loom/reviews/**` remain out of scope. Statement: deferred is not completed.
