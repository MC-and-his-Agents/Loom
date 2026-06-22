# WI-1696 Plan

## Phases

- P1: Establish WI-1696 carriers and minimal suite.
- P2: Bump root CLI release authority to v0.18.0.
- P3: Add release readiness evidence for milestone #15.
- P4: Run release/package/local Loom validation.
- P5: Record spec and implementation review.
- P6: Open release PR, run hosted checks, ship merge, read back publish, and close #1696/#1680.

## Scenario Mapping

- S1 -> P2, P4
- S2 -> P3, P4
- S3 -> P6

## Acceptance Mapping

- A1 -> test evidence: `python3 tools/version_surface_check.py`; `python3 tools/check_npm_package.py`
- A2 -> behavior evidence: `docs/evidence/v0.18.0-release-readiness.md`
- A3 -> test evidence: release surface, package check, npm smoke, npm pack dry-run
- A4 -> test evidence: suite validate/evidence/carrier, fact-chain, state-check, review record, PR metadata, hosted checks, PR gate
- A5 -> manual evidence: post-merge release readback and host closeout evidence

## Validation

- `CODEX_EXPORT_GH_TOKEN=1 PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py release readback --target . --version v0.18.0 --package @mc-and-his-agents/loom --repo MC-and-his-Agents/Loom --release-judgment release_required --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/version_surface_check.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_release_surface.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_npm_package.py`
- `npm run test:package`
- `npm pack --dry-run --json --ignore-scripts`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite validate --target . --item WI-1696 --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite evidence validate --target . --item WI-1696 --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite carrier validate --target . --item WI-1696 --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_flow.py fact-chain --target . --item WI-1696`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_flow.py state-check --target . --item WI-1696`
- `git diff --check`
