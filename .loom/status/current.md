# Current Status

## Derived Fact Chain View

- Item ID: WI-1696
- Goal: Execute milestone #15 release closeout for the intensity-aware ship path and publish Loom CLI v0.18.0.
- Scope: Bump root CLI release authority to v0.18.0, add release readiness evidence, validate package/release surfaces, publish through the existing main-push release workflow, then close issue #1696 and phase #1680 after readback. Ownership: main executor owns VERSION, package.json, WI-1696 carriers, release evidence, PR metadata, release readback, and host closeout. Non-goals: no new ship path implementation, no release workflow semantic change, no plugin surface version bump, no installer release.
- Execution Path: issue #1696 -> branch work/1696-release-closeout -> PR -> controlled merge -> release workflow -> release readback -> issue/phase closeout
- Workspace Entry: ./WI-1696/..
- Recovery Entry: .loom/progress/WI-1696.md
- Review Entry: .loom/reviews/WI-1696.json
- Validation Entry: release readback; version surface; release surface; npm package check; npm package smoke; npm pack dry-run; suite validate/evidence/carrier; fact-chain; state-check; git diff --check.
- Closing Condition: PR is merged into main, v0.18.0 tag/GitHub Release/npm package publish successfully, issue #1696 is closed, phase #1680 is closed, and milestone #15 has no open issues.
- Current Checkpoint: merge checkpoint
- Current Stop: WI-1696 release PR inputs are locally validated in issue-scoped worktree /Users/mc/dev/Loom-WI-1696; review and PR metadata are next.
- Next Step: Record spec/implementation review, render PR metadata, open release PR, then run hosted checks, ship, release readback, and close #1696/#1680.
- Blockers: None recorded.
- Latest Validation Summary: 2026-06-22 local validation passed: `git diff --check`; `CODEX_EXPORT_GH_TOKEN=1 PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py release readback --target . --version v0.18.0 --package @mc-and-his-agents/loom --repo MC-and-his-Agents/Loom --release-judgment release_required --json`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/version_surface_check.py`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_release_surface.py`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_npm_package.py`; `npm run test:package`; `npm pack --dry-run --json --ignore-scripts`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite validate --target . --item WI-1696 --json`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite evidence validate --target . --item WI-1696 --json`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom.py suite carrier validate --target . --item WI-1696 --json`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_flow.py fact-chain --target . --item WI-1696`; `PYTHONDONTWRITEBYTECODE=1 python3 tools/loom_flow.py state-check --target . --item WI-1696`.
- Recovery Boundary: Work Item #1696 is active in `/Users/mc/dev/Loom-WI-1696` on branch `work/1696-release-closeout`; no work is performed in `/Users/mc/dev/Loom`.
- Current Lane: milestone-15-release-closeout

## Runtime Evidence

- Run Entry: 2026-06-22 WI-1696 release closeout started in issue-scoped worktree `/Users/mc/dev/Loom-WI-1696`.
- Logs Entry: Local command output retained in current Codex milestone #15 thread; concise validation commands will be listed in the Latest Validation Summary.
- Diagnostics Entry: `v0.18.0` is the release target for the completed intensity-aware ship path; `v0.18.0` was unoccupied before release PR preparation.
- Verification Entry: 2026-06-22 local validation passed for release readback, version/release/package surfaces, npm package smoke, npm pack dry-run, suite validate/evidence/carrier, fact-chain, state-check, and git diff whitespace check.
- Lane Entry: milestone-15-release-closeout

## Sources

- Static Truth: .loom/work-items/WI-1696.md
- Dynamic Truth: .loom/progress/WI-1696.md
- Locator Truth: .loom/bootstrap/init-result.json
- Fact Chain CLI: python3 .loom/bin/loom_init.py fact-chain --target .
