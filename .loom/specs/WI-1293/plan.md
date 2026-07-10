# WI-1293 Plan

## Phases

- P1: Read back milestone 9 GitHub truth and v0.16.0 release occupancy. Covers A3 and A4.
- P2: Advance version authority surfaces to v0.16.0 and record pre-merge release readiness evidence. Covers A3 and A4.
- P3: Update README/adoption/CLI help surfaces to describe controlled merge, semantic review boundaries, #1452 triggered-check behavior, and #1292 fixture consumption. Covers A1, A2, and A4.
- P4: Validate release, package, skills, CLI contract, fact-chain, suite, carrier, and PR metadata surfaces. Covers A1, A2, A3, and A4.
- P5: Review and merge the release PR only after explicit release authorization. Covers A3, A4, and A5.
- P6: After main-push release workflow completes, read back tag, GitHub Release, npm package, installed/global CLI smoke, target branch, and terminalize #1293/#1285 carriers. Covers A5.

## Acceptance Mapping

- A1 -> structural evidence: P3 and P4.
- A2 -> structural evidence: P3 and P4.
- A3 -> test evidence: P2 and P4.
- A4 -> validation evidence: P1, P2, P3, and P4.
- A5 -> validation evidence: P5 and P6.

## Validation

- `python3 tools/loom.py release readback --target . --version v0.16.0 --package @mc-and-his-agents/loom --repo MC-and-his-Agents/Loom --release-judgment release_required --json`
- `python3 tools/version_surface_check.py`
- `python3 tools/check_release_surface.py`
- `python3 tools/check_npm_package.py`
- `npm run test:package`
- `npm pack --dry-run --json --ignore-scripts`
- `node bin/loom.mjs version --json`
- `python3 tools/loom.py help --json`
- `python3 tools/loom.py skills release-check --json`
- `python3 tools/skills_surface.py check`
- `python3 tools/loom.py skills check --target . --json`
- `python3 tools/check_cli_contract.py --surface aggregate`
- `python3 tools/loom.py suite validate --target . --item WI-1293 --json`
- `python3 tools/loom.py suite evidence validate --target . --item WI-1293 --json`
- `python3 tools/loom.py suite carrier validate --target . --item WI-1293 --json`
- `git diff --check`
