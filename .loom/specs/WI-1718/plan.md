# WI-1718 Plan

## Phases

- P1: Establish WI-1718 carriers and minimal suite.
- P2: Bump root CLI release authority to v0.19.0.
- P3: Align plugin payload release metadata and deterministic hash.
- P4: Add publish-time `source_git_sha` stamping before npm publish.
- P5: Add v0.19.0 release readiness evidence.
- P6: Run release/package/local Loom validation and record reviews.
- P7: Open release PR, run hosted checks, controlled merge, read back publish, and close #1718/#1711.

## Scenario Mapping

- S1 -> P2, P6
- S2 -> P3, P6
- S3 -> P4, P6, P7
- S4 -> P5, P7
- S5 -> P7

## Acceptance Mapping

- A1 -> test evidence: `python3 tools/version_surface_check.py`; `python3 tools/check_npm_package.py`
- A2 -> test evidence: `python3 tools/check_npm_package.py --surface plugin-payload-hash`; `python3 tools/stamp_plugin_payload_metadata.py --source-git-sha unreleased --json`
- A3 -> test evidence: `python3 tools/stamp_plugin_payload_metadata.py --source-git-sha <sha> --write --json`; `python3 tools/check_release_surface.py --surface release-workflow-contract`
- A4 -> behavior evidence: `docs/evidence/v0.19.0-release-readiness.md`
- A5 -> test evidence: release surface, package check, npm smoke, npm pack dry-run, suite/fact-chain, PR metadata, hosted checks, and PR gate
- A6 -> manual/runtime evidence: post-merge release readback, npm readback, GitHub Release readback, host doctor/readback, and issue closeout evidence

## Validation

- `CODEX_EXPORT_GH_TOKEN=1 PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py release readback --target . --version v0.19.0 --package @mc-and-his-agents/loom --repo MC-and-his-Agents/Loom --release-judgment release_required --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/stamp_plugin_payload_metadata.py --source-git-sha unreleased --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/version_surface_check.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_release_surface.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_npm_package.py`
- `npm run test:package`
- `npm pack --dry-run --json --ignore-scripts`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite validate --target . --item WI-1718 --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite evidence validate --target . --item WI-1718 --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite carrier validate --target . --item WI-1718 --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py fact-chain --target . --item WI-1718 --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_flow.py state-check --target . --item WI-1718`
- `git diff --check`

## Publish Closeout

- Main push publish is expected to create `v0.19.0`, publish `@mc-and-his-agents/loom@0.19.0`, and create GitHub Release `v0.19.0`.
- Post-merge closeout must prove release workflow, tag, GitHub Release, npm package, plugin payload metadata/hash, and issue/FR closeout alignment.
- `npm deprecate @mc-and-his-agents/loom-installer` is intentionally not run automatically; request explicit user confirmation before executing that external registry action.
