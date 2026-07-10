# WI-1776 Plan

## Phases

- P1: Extend release readback classification with verdict, diagnostic, and next_action fields.
- P2: Add package surface and carrier terminal readbacks to the release evidence set.
- P3: Preserve no-release and release resume as non-mutating readback paths.
- P4: Add fixture coverage for published, missing, drifted, blocked, and main-worktree-busy fallback states.
- P5: Run local CLI contract, package surface, suite, fact-chain, shadow, and live v0.21.0 dry-run readback validation.
- P6: Open PR, stabilize metadata/review, merge, and close out #1776 before #1778 release closeout.

## Scenario Mapping

- S1 -> P1, P2, P4, P5
- S2 -> P1, P4, P5
- S3 -> P1, P4, P5
- S4 -> P1, P2, P4, P5
- S5 -> P1, P3, P4, P5
- S6 -> P1, P3, P4, P5

## Acceptance Mapping

- A1 -> test evidence: `python3 tools/check_cli_contract.py --surface release-readback`
- A2 -> test evidence: `python3 tools/check_cli_contract.py --surface release-readback` covers fixtures in `docs/evidence/fixtures/release-readback-fixtures.json`
- A3 -> test evidence: `python3 tools/check_cli_contract.py --surface release-readback` covers package_surface and carrier readbacks
- A4 -> test evidence: `python3 tools/check_cli_contract.py --surface release-readback` covers fixture `multi-worktree-main-busy`
- A5 -> test evidence: `python3 tools/check_cli_contract.py --surface release-readback` covers fixture `no-release-docs-only`
- A6 -> validation evidence: py compile, JSON fixture validation, release-readback contract, live dry-run readback, and diff check

## Validation

- `PYTHONDONTWRITEBYTECODE=1 python3 tools/py_compile_clean.py tools/loom.py tools/check_cli_contract.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface release-readback`
- `python3 -m json.tool docs/evidence/fixtures/release-readback-fixtures.json >/dev/null`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py release readback --target . --version v0.21.0 --package @mc-and-his-agents/loom --repo MC-and-his-Agents/Loom --commit $(git rev-parse HEAD) --json --full-output`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py fact-chain --target . --item WI-1776 --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite validate --target . --item WI-1776 --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite evidence validate --target . --item WI-1776 --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite carrier validate --target . --item WI-1776 --json`
- `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_flow.py shadow-parity --target . --surface all --blocking`
- `git diff --check`

## Deferred

- #1778 owns v0.21.0 version bump, tag, GitHub Release, npm publish, and terminal release closeout.
- #1774 parent backlog owns automatic host-safe worktree locator generation and destructive cleanup automation.
- Follow-up milestone work may refine release workflow selection beyond the current latest-run readback heuristic if real release evidence shows ambiguity.
