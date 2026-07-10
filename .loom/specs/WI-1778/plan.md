# WI-1778 Plan

## Phases

- P1: Establish WI-1778 carriers and minimal suite.
- P2: Bump root CLI release authority to v0.21.0.
- P3: Align plugin payload release metadata and deterministic hash.
- P4: Add v0.21.0 release readiness evidence.
- P5: Run release/package/local Loom validation and record reviews.
- P6: Open release PR, run hosted checks, controlled merge, read back publish, and close #1778/#1774/milestone #18.

## Scenario Mapping

- S1 -> P2, P5
- S2 -> P3, P5
- S3 -> P4, P6
- S4 -> P5
- S5 -> P6

## Acceptance Mapping

- A1 -> test evidence: `python3 tools/version_surface_check.py`; `python3 tools/check_npm_package.py`
- A2 -> test evidence: `python3 tools/check_npm_package.py --surface plugin-payload-hash`; `python3 tools/stamp_plugin_payload_metadata.py --source-git-sha unreleased --json`
- A3 -> behavior evidence: `docs/evidence/v0.21.0-release-readiness.md`
- A4 -> test evidence: release surface, package check, release-readback regression, ship-wrapper regression, npm smoke, npm pack dry-run, suite/fact-chain, PR metadata, hosted checks, and PR gate
- A5 -> manual/runtime evidence: post-merge release readback, npm readback, GitHub Release readback, and issue/FR/milestone closeout evidence

## Validation

- `CODEX_EXPORT_GH_TOKEN=1 PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py release readback --target . --version v0.21.0 --package @mc-and-his-agents/loom --repo MC-and-his-Agents/Loom --release-judgment release_required --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/stamp_plugin_payload_metadata.py --source-git-sha unreleased --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/version_surface_check.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_release_surface.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_npm_package.py`
- `npm run test:package`
- `npm pack --dry-run --json --ignore-scripts`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface release-readback`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --fixture-group ship-wrapper`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite validate --target . --item WI-1778 --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite evidence validate --target . --item WI-1778 --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite carrier validate --target . --item WI-1778 --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py fact-chain --target . --item WI-1778 --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_flow.py state-check --target . --item WI-1778`
- `git diff --check`

## Publish Closeout

- Main push publish is expected to create `v0.21.0`, publish `@mc-and-his-agents/loom@0.21.0`, and create GitHub Release `v0.21.0`.
- Post-merge closeout must prove release workflow, tag, GitHub Release, npm package, plugin payload metadata/hash, issue/FR closeout, and milestone #18 alignment.
