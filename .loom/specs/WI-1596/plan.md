# WI-1596 Plan

## Phases

- P1: Read back milestone #13 GitHub truth, merged PRs, target branch, hosted checks, and release occupancy. Covers A3.
- P2: Advance version authority surfaces to v0.15.0 and record pre-merge release readiness evidence. Covers A1 and A2.
- P3: Validate release, package, skills, CLI contract, fact-chain, carrier, and PR metadata surfaces. Covers A1, A2, A3, and A4.
- P4: Review and merge the release PR only after explicit release authorization. Covers A2, A3, and A5.
- P5: After main-push release workflow completes, read back tag, GitHub Release, npm package, installed/global CLI smoke, and terminalize #1596/#1598/#1594 carriers. Covers A5.

## Acceptance Mapping

- A1 -> test evidence: P2 and P3 validate that version authority surfaces and package metadata agree on v0.15.0.
- A2 -> structural evidence: P2, P3, and P4 record readiness evidence with candidate occupancy, validation commands, publish path, and authorization boundary.
- A3 -> validation evidence: P1, P3, and P4 read back milestone #13 host truth and hosted checks before release PR merge.
- A4 -> structural check: P3 confirms WI-1598 terminal carrier metadata before #1596/#1594 closeout.
- A5 -> validation evidence: P4 and P5 bind post-merge workflow, tag, GitHub Release, npm, target branch, and installer non-advancement.

## Validation

- `python3 tools/version_surface_check.py`
- `python3 tools/check_release_surface.py`
- `python3 tools/check_npm_package.py`
- `npm run test:package`
- `npm pack --dry-run --json --ignore-scripts`
- `node bin/loom.mjs version --json`
- `python3 tools/loom.py skills release-check --json`
- `python3 tools/skills_surface.py check`
- `python3 tools/loom.py skills check --target . --json`
- `python3 tools/check_cli_contract.py --surface aggregate`
- `python3 tools/loom.py suite validate --target . --item WI-1596 --json`
- `python3 tools/loom.py suite evidence validate --target . --item WI-1596 --json`
- `python3 tools/loom.py suite carrier validate --target . --item WI-1596 --json`
- `git diff --check`
